from pydantic import BaseModel, ConfigDict
import uuid

class UserCreate(BaseModel):
	username: str
	password: str

class UserOut(BaseModel): # we remove the password attribute 
	id: uuid.UUID
	username: str

	model_config = ConfigDict(from_attributes=True) # pydantic expects dict by default, this switches it to dot notation (used by SQLAlchmey - getting data from db)
