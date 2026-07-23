from db import Base
from uuid import uuid4, UUID
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class User(Base):
	__tablename__ = "users"
	id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
	username: Mapped[str] = mapped_column(String(20), unique=True) 
	hashed_password: Mapped[str] = mapped_column()

	subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="owner") 
	model_config = {"from_attributes": True}

	''' 
	relationship works only for python by establishing a relation between the classes, we are able to retrieve a list of Subscriptions.
	The relation is 1 to many (1 user can have many subscriptions), relationship exists on the python layer only. Additionally, back populate creates a two
	way relation between the classes (it is needed in both classes), in python's ram. If the relation is modified on one side, in instantly syncs for the other class
	'''
class Subscription(Base):
	__tablename__ = "subscriptions" 

	''' 
	Mapped is used to tell python and sqlalchemy what the data type is. While, 
	mapped_column allows for proper parameters that define configurations for the column
	'''
	id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, index = True)
	name: Mapped[str] = mapped_column(String(50))
	cost: Mapped[float] = mapped_column()
	billing_cycle: Mapped[str] = mapped_column(String(50))
	description: Mapped[str | None] = mapped_column(String(100))

	owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id")) # we create a relation between the tables using the user.id as our foreign key

	owner : Mapped["User"] = relationship(back_populates="subscriptions")