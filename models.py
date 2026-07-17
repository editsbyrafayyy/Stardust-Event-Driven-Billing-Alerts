from db import Base
from uuid import uuid4, UUID
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

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
