from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid # assigning unique ids to each entry in the table
from typing import Optional # we use this for are patch requests, we set all the attr as optional so the user can modify only what they need to

app = FastAPI()

@app.get("/")
def read_root():
	return {"Hey" : "Working"}

temp_db = {}

class Subscriptions(BaseModel): # the base class that is used for get/post/delete as we modify/add all the attributes at once instead of specific ones
	name: str
	cost: float	
	billing_cycle: str
	description: str

class SubscriptionsUpdate(BaseModel): # this class is introduced as there will be a difference in the input/output shape for when we add a patch request
	# the way a patch request works is that it only changes specific attr, instead of all, which means we can't just overwrite everything instead only
	# certain attr that the user wants to, for that to work we need to ensure that the attr are set to None by default so only set attr can be changed
	name: Optional[str] = None
	cost: Optional[float] = None	
	billing_cycle: Optional[str] = None
	description: Optional[str] = None


def get_subscription_or_404(id: uuid.UUID) -> dict: # I have created a  helper function to reduce redundancy in the code, as this part is used in almost all the requests
	if id in temp_db:
		return temp_db[id]
	else: 
		raise HTTPException(status_code= 404, detail= "Id not found!")


@app.post("/subscriptions")
def write_subscriptions(sub: Subscriptions):
	id = uuid.uuid4() # generates a random id
	user_data = sub.model_dump() # the newer version of changing a model obj into a dict 
	temp_db[id] = user_data 

	return {"id": id, **user_data} 
	''' 
	instead of 	return {"id": id, "name": sub.name, "cost": sub.cost, "billing_cycle": sub.billing_cycle, "description":sub.description} we use dict unpacking 
	that makes the code easier to read as we already did turn the obj into a dict using the model.dump function
	'''

@app.get("/subscriptions/{id}") # {id} is the path parameter, anything inside the {} is treated as a variable by fastapi
def get_subscriptions(id: uuid.UUID): # we make sure that the id is mapped currently to its type, what this does is that fastapi will parse the inputs into
# a UUID object and reject requests that don't fit the UUID shape 
	data_get = get_subscription_or_404(id) # we simply pass the id into the function to get the entry that we are looking for  
	return {"id": id, **data_get}

@app.delete("/subscriptions/{id}") # delete
def delete_subscriptions(id: uuid.UUID):
	deleted_data = get_subscription_or_404(id)
	del temp_db[id] # we use the del built in function to delete the entry
	return {"message": f"Subscription '{deleted_data['name']}' has been deleted", "id": id, **deleted_data}
		# Subscription 'Netflix' has been deleted, this is how it will look like, this could have been made simplier if we didn't add the name

@app.patch("/subscriptions/{id}") # patch
def update_subscriptions(id: uuid.UUID, update_data: SubscriptionsUpdate): # we will need to convert the pydantic model into a dict hence the parameters
	old_data = get_subscription_or_404(id)
	new_data = update_data.model_dump(exclude_unset=True)  
	''' this allows pydantic to identify which field the user wants to explicity change, instead
	of returning all the fields which would result in all the remaining fields being overwritten with None which we don't want '''
	temp_db[id] = {**old_data, **new_data} 
	return {"id":id, **temp_db[id]} # we still follow the same pattern we did for other requests key:values id: all attr in the temp_db for that id
