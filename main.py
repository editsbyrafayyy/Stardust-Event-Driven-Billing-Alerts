from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import uuid

app = FastAPI()

@app.get("/")
def read_root():
	return {"Hey" : "Working"}

temp_db = {}

class Subscriptions(BaseModel):
	name: str
	cost: float	
	billing_cycle: str
	description: str


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
def read_subscriptions(id: uuid.UUID): # we make sure that the id is mapped currently to its type, what this does is that fastapi will parse the inputs into
# a UUID object and reject requests that don't fit the UUID shape 
	if id in temp_db:
		return {"id": id, **temp_db[id]} # here the temp_db[id] gives us the user-data (that is what I implemented in the post req) so we should return the id as well
	else:
		raise HTTPException(status_code = 404, detail = "The Subscription was not Found")

@app.delete("/subscriptions/{id}")
def delete_subscriptions(id: uuid.UUID):
	if id in temp_db:
		deleted_data = temp_db[id] #storing it temporarily so I can reference it in a message then
		del temp_db[id] # we use the del built in function to delete the entry
		return {"message": f"Subscription '{deleted_data['name']}' has been deleted", "id": id, **deleted_data}
		# Subscription 'Netflix' has been deleted, this is how it will look like, this could have been made simplier if we didn't add the name
	else:
		raise HTTPException(status_code = 404, detail = "The Subscription was not Found")
