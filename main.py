from fastapi import FastAPI, HTTPException, status, Depends, WebSocket, WebSocketDisconnect, Query, Request
from contextlib import asynccontextmanager
from rate_limiter import check_rate_limit
from pydantic import BaseModel, Field
import uuid # assigning unique ids to each entry in the table
from typing import Optional # we use this for are patch requests, we set all the attr as optional so the user can modify only what they need to
from models import Subscription, User # the subs class from models.py
from db import Base, engine, get_db, SessionLocal # the Base class alongside engine from db.py
from sqlalchemy.orm import Session
from schemas import UserCreate, UserOut
from auth import create_access_token, get_current_user, get_user_from_token, hash_password, verify_password
from config import settings
from fastapi.security import OAuth2PasswordRequestForm
from datetime import date
from ws_manager import ConnectionManager
import redis.asyncio as aioredis
import asyncio
import json
import redis
from redis.exceptions import RedisError
from datetime import timedelta as td

# plain (blocking) redis client for caching
cache_client = redis.from_url(settings.redis_url, decode_responses=True, socket_timeout=5.0)
CACHE_TTL_SECONDS = 300  # 5 min safety net, in case an invalidation path is ever missed

def invalidate_user_summary_cache(user_id: uuid.UUID) -> None:
	"""
	Evicts the user's cached summary from Redis upon any mutation (create, update, delete).
	Catches RedisError to ensure DB transactions succeed even if the cache layer has hiccups.
	"""
	try:
		cache_client.delete(f"summary:{user_id}")
	except RedisError as e:
		print(f"[Cache Warning] Failed to invalidate cache for user {user_id}: {e}")

def normalize_to_monthly_cost(cost: float, billing_cycle: str) -> float:
	"""
	Normalizes different billing frequencies (yearly, quarterly, weekly, daily) into a standard monthly figure.
	"""
	cycle = billing_cycle.lower().strip()
	if cycle in ("yearly", "annual", "annually"):
		return cost / 12.0
	elif cycle in ("quarterly",):
		return cost / 3.0
	elif cycle in ("weekly",):
		return (cost * 52.0) / 12.0
	elif cycle in ("daily",):
		return cost * 30.0
	return cost  # default assumed monthly

manager = ConnectionManager() # single shared instance holding all active WebSocket connections, keyed by user id

async def redis_listener():
	# Runs for the lifetime of the app, independent of any single request.
	# Subscribes to the "alerts" channel that tasks.py publishes to when an Alert is created.
	while True:
		try:
			redis_conn = aioredis.from_url(settings.redis_url)
			pubsub = redis_conn.pubsub()
			await pubsub.subscribe("alerts")
			print("[WebSocket] Successfully subscribed to Redis 'alerts' channel.")
			async for message in pubsub.listen():
				if message["type"] != "message":  # skip subscribe confirmation messages
					continue
				try:
					data = json.loads(message["data"])
					user_id = uuid.UUID(data["user_id"])
					await manager.send_to_user(user_id, data["message"])
				except Exception as parse_err:
					print(f"[WebSocket] Error parsing Redis alert message: {parse_err}")
		except asyncio.CancelledError:
			break
		except Exception as conn_err:
			print(f"[WebSocket] Redis pubsub connection error: {conn_err}. Retrying in 5s...")
			try:
				await asyncio.sleep(5)
			except asyncio.CancelledError:
				break

@asynccontextmanager
async def lifespan(app: FastAPI):
	# Startup: Ensure tables exist and spawn background Redis Pub/Sub listener
	try:
		Base.metadata.create_all(bind=engine)
	except Exception as e:
		print(f"[DB Startup Warning] Could not initialize tables against primary DB: {e}")
	redis_task = asyncio.create_task(redis_listener())
	yield
	# Shutdown: Cleanly cancel background tasks
	if redis_task:
		redis_task.cancel()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
	return {"Hey" : "Working"}

# PYDANTIC MODEL CLASSES (PROVIDE INPUT AND OUTPUT SHAPE)

class Subscriptions(BaseModel): # the base class that is used for get/post/delete as we modify/add all the attributes at once instead of specific ones
	name: str
	cost: float	
	billing_cycle: str
	description: str
	renewal_date: date = Field(default_factory=date.today) # default factory runs the function at produces a fresh value for each each time
	# if a value depends on randommness, time or a mutable object default factory is needed to be used.

class SubscriptionsUpdate(BaseModel): # this class is introduced as there will be a difference in the input/output shape for when we add a patch request
	# the way a patch request works is that it only changes specific attr, instead of all, which means we can't just overwrite everything instead only
	# certain attr that the user wants to, for that to work we need to ensure that the attr are set to None by default so only set attr can be changed
	name: Optional[str] = None
	cost: Optional[float] = None	
	billing_cycle: Optional[str] = None
	description: Optional[str] = None
	renewal_date: Optional[date] = None 
	model_config = {"from_attributes": True}

class SubscriptionOut(Subscriptions):
	id: uuid.UUID
	model_config = {"from_attributes": True} # this allows pydantic model to read objects from SQLalchemy instead of just python dict


class SubscriptionDelete(SubscriptionOut): # as we also need id which SubOut has not the main Sub class
	message: str
	model_config = {"from_attributes": True}

class Token(BaseModel): # defining a shape for the Token
	access_token: str
	token_type: str = "bearer" # conventional value to use, it tells the client to attach the token to the authorization header as Bearer <token>	


# ========================= Helper Function

def get_subscription_or_404(id: uuid.UUID, db: Session, curr_user : User) -> Subscription: # I have created a  helper function to reduce redundancy in the code, as this part is used in almost all the requests
	# returns an object of type Subscription (SQLalchemy type)
	result = db.query(Subscription).filter(Subscription.id == id,  Subscription.owner_id == curr_user.id).first() # this fetches the first row that meets the condition
	# we use the db.query() method to find the data and filter is based on if id == id, then return the first row that meets the filter criteria
	# The added condition checks if the user logged in is the same user fetching the data, if the id's are different 404 is raised automatically
	if result:
		return result
	else: 
		raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Id not found!")



@app.post("/subscriptions", status_code = status.HTTP_201_CREATED, response_model = SubscriptionOut)
# its important to note that a response model strictly binds what the output schema will be for the request type
def write_subscriptions(sub: Subscriptions, db: Session = Depends(get_db), curr_user: User = Depends(get_current_user)):
	'''
	Depends() is the core function for dependency injection, it manages the automatic lifecycle for shared resources, in this case
	the db session. It is able to extract yielded session objects, injects into route parameter, and guarantees cleanup. It shifts
	the burden of resource lifetime management from the user to the framework instead. 
	'''	
	user_data = sub.model_dump() # the newer version of changing a model obj into a dict 
	# removed id generation from the function as it is being generated by default in the Subscription Class (model.py)	
	user_data["owner_id"] = curr_user.id
	data_insertion = Subscription(**user_data) # allows us to map the user-data onto the Subs class fields (DB Fields directly)
	
	db.add(data_insertion)
	db.commit()
	db.refresh(data_insertion)

	invalidate_user_summary_cache(curr_user.id)  # this user's cached summary is now stale — evict it
	''' 
	instead of 	return {"id": id, "name": sub.name, "cost": sub.cost, "billing_cycle": sub.billing_cycle, "description":sub.description} we use dict unpacking 
	that makes the code easier to read as we already did turn the obj into a dict using the model.dump function
	'''
	return data_insertion 


# ========================== Summary (Milestone 7 — Caching)
# Note: /subscriptions/summary MUST be defined BEFORE /subscriptions/{id}, otherwise FastAPI
# matches "summary" as an {id} path parameter and attempts to parse it as a UUID (causing 422 errors).

class UpcomingRenewal(BaseModel):
	id: uuid.UUID
	name: str
	cost: float
	renewal_date: date

class SummaryOut(BaseModel):
	total_monthly_spend: float
	upcoming_renewals: list[UpcomingRenewal]
	cached: bool  # included so you can SEE the cache actually working, not just trust it silently

@app.get("/subscriptions/summary", response_model=SummaryOut)
def get_summary(db: Session = Depends(get_db), curr_user: User = Depends(get_current_user)):
	# Enforce rate limit (30 requests/minute per user) to prevent DoS
	check_rate_limit(f"rl:summary:{curr_user.id}", limit=30, window_seconds=60)

	cache_key = f"summary:{curr_user.id}"

	# 1. Try reading from cache with graceful degradation if Redis is down
	try:
		cached_value = cache_client.get(cache_key)
		if cached_value:
			data = json.loads(cached_value)
			data["cached"] = True
			return data
	except RedisError as e:
		print(f"[Cache Warning] Redis get failed: {e}. Falling back to DB.")

	# 2. Cache miss or Redis unavailable — compute from PostgreSQL
	subs = db.query(Subscription).filter(Subscription.owner_id == curr_user.id).all()

	# Accurately normalize yearly, quarterly, weekly subscriptions into a monthly total
	total_monthly_spend = round(
		sum(normalize_to_monthly_cost(s.cost, s.billing_cycle) for s in subs), 2
	)
	upcoming = [
		s for s in subs
		if date.today() <= s.renewal_date <= date.today() + td(days=7)
	]

	result = {
		"total_monthly_spend": total_monthly_spend,
		"upcoming_renewals": [
			{"id": str(s.id), "name": s.name, "cost": s.cost, "renewal_date": s.renewal_date.isoformat()}
			for s in upcoming
		],
	}

	# 3. Store freshly computed summary in Redis with TTL
	try:
		cache_client.setex(cache_key, CACHE_TTL_SECONDS, json.dumps(result))
	except RedisError as e:
		print(f"[Cache Warning] Redis setex failed: {e}")

	result["cached"] = False
	return result


# ========================== Individual Subscription Operations

# the shape of the data is a template that the return data has to fit in, any access data is filtered out/removed 
@app.get("/subscriptions/{id}", response_model = SubscriptionOut) # {id} is the path parameter, anything inside the {} is treated as a variable by fastapi
def get_subscriptions(id: uuid.UUID, db: Session = Depends(get_db), curr_user: User = Depends(get_current_user)): # we make sure that the id is mapped currently to its type, what this does is that fastapi will parse the inputs into
# a UUID object and reject requests that don't fit the UUID shape 
	data_get = get_subscription_or_404(id, db, curr_user) # we simply pass the id into the function to get the entry that we are looking for  
	return data_get # returns us an object with the 

@app.delete("/subscriptions/{id}", response_model = SubscriptionDelete) # delete
def delete_subscriptions(id: uuid.UUID, db: Session = Depends(get_db), curr_user: User = Depends(get_current_user)):
	deleted_data = get_subscription_or_404(id, db, curr_user)
	clean_data = SubscriptionOut.model_validate(deleted_data).model_dump(exclude={"id"}) # this will return a python dict 
	# model_validate converts the data into a pydantic model and model_dump then into a dict
	db.delete(deleted_data) # we use .delete() method to remove the specific row
	db.commit()

	invalidate_user_summary_cache(curr_user.id)  # deletion changes total spend + renewal list — evict

	return {"message": f"Subscription '{clean_data['name']}' has been deleted", "id": id, **clean_data}
	# Subscription 'Netflix' has been deleted, this is how it will look like, this could have been made simplier if we didn't add the name

@app.patch("/subscriptions/{id}", response_model = SubscriptionOut) # patch
def update_subscriptions(id: uuid.UUID, update_data: SubscriptionsUpdate, db: Session = Depends(get_db), curr_user: User = Depends(get_current_user)): # we will need to convert the pydantic model into a dict hence the parameters
	existing_data = get_subscription_or_404(id, db, curr_user)
	new_data = update_data.model_dump(exclude_unset=True)
	# exclude_unset only includes the fields that the client explicitly sent in the request

	for key, val in new_data.items():
		setattr(existing_data, key, val) # settattr bypasses the conventional dot notation limitations. As in this instance, we don't know the attr "key" has
		# but using settatrr we can simply get that column name on runtime and modify the value

	db.commit()
	db.refresh(existing_data)

	invalidate_user_summary_cache(curr_user.id)  # cost/renewal_date may have changed — evict

	return existing_data

# ========================== Register

@app.post("/register", response_model=UserOut) # we use the userout shape to ensure that pass never gets seen
def add_user(user: UserCreate, db: Session = Depends(get_db)):
	existing_user = db.query(User).filter(User.username == user.username).first()
	if existing_user:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Username already registered"
		)

	user_data = user.model_dump() # convert the python obj into a dict
	hashed_password = hash_password(user_data["password"]) # we pass the password for hashing

	data_insertion = User(
		username=user_data["username"],
		hashed_password=hashed_password
		)

	db.add(data_insertion)
	db.commit()
	db.refresh(data_insertion)

	return data_insertion

@app.post("/login", response_model=Token)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
	# Enforce rate limit (5 attempts/minute per IP) to prevent brute-force attacks
	client_ip = request.client.host if request.client else "unknown"
	check_rate_limit(f"rl:login:{client_ip}", limit=5, window_seconds=60)

	result = db.query(User).filter(User.username == form_data.username).first() # fetch the results if user matches

	if result and verify_password(form_data.password, result.hashed_password): 

		return Token ( # we create a Token shape to return and match with the response model
			access_token= create_access_token(data={"sub":result.username}),
			token_type= "bearer" # bearer follows standard compliance, interoperability and clear HTTP semantics
		)

	else:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect Credentials")

# ========================== WebSocket (Milestone 6 — Real-time)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...), db: Session = Depends(get_db)):
	# WebSockets can't send a normal Authorization header from browser JS, so the token travels as
	# a query param: ws://.../ws?token=<jwt>.
	try:
		user = get_user_from_token(token, db)
	except HTTPException:
		await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
		return

	await manager.connect(user.id, websocket)
	try:
		while True:
			await websocket.receive_text()  # keeps the connection alive / lets us detect disconnects
	except WebSocketDisconnect:
		manager.disconnect(user.id, websocket)