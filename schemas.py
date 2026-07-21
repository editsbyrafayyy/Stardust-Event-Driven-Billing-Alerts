from pydantic import BaseModel
import uuid

class UserCreate(BaseModel):
	username: str
	password: str

class UserOut(BaseModel): # we remove the password attribute 
	id: uuid.UUID
	username: str

	model_config = {"from_attributes": True}