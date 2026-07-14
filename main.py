from fastapi import FastAPI
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

	return temp_db


@app.get("/subscriptions")
def read_subscriptions():
	return temp_db


