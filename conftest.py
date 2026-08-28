import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from db import Base, get_db
from main import app
from auth import create_access_token, hash_password
from models import User

# In-memory SQLite database for isolated and fast tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
	SQLALCHEMY_DATABASE_URL,
	connect_args={"check_same_thread": False},
	poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

@pytest.fixture(scope="function")
def db_session():
	"""
	Creates a fresh database schema before each test and tears it down after.
	Ensures 100% test isolation between runs.
	"""
	Base.metadata.create_all(bind=engine)
	session = TestingSessionLocal()
	try:
		yield session
	finally:
		session.close()
		Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
	"""
	FastAPI TestClient with overridden get_db dependency pointing to the test DB.
	"""
	def override_get_db():
		try:
			yield db_session
		finally:
			pass

	app.dependency_overrides[get_db] = override_get_db
	with TestClient(app) as test_client:
		yield test_client
	app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(db_session) -> User:
	"""
	Creates a primary test user in the test database.
	"""
	user = User(
		username="testuser",
		hashed_password=hash_password("password123")
	)
	db_session.add(user)
	db_session.commit()
	db_session.refresh(user)
	return user

@pytest.fixture(scope="function")
def auth_headers(test_user: User) -> dict[str, str]:
	"""
	Generates a valid Authorization header for the primary test user.
	"""
	token = create_access_token(data={"sub": test_user.username})
	return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def test_user_2(db_session) -> User:
	"""
	Creates a secondary test user to verify multi-tenant isolation.
	"""
	user = User(
		username="otheruser",
		hashed_password=hash_password("password456")
	)
	db_session.add(user)
	db_session.commit()
	db_session.refresh(user)
	return user

@pytest.fixture(scope="function")
def auth_headers_2(test_user_2: User) -> dict[str, str]:
	"""
	Generates a valid Authorization header for the secondary test user.
	"""
	token = create_access_token(data={"sub": test_user_2.username})
	return {"Authorization": f"Bearer {token}"}

@pytest.fixture(autouse=True)
def mock_background_redis_listener():
	"""
	Mocks the background redis_listener async loop during tests so tests don't spend
	seconds waiting on connection timeouts to redis:6379.
	"""
	from unittest.mock import patch
	async def noop_listener():
		return
	with patch("main.redis_listener", noop_listener):
		yield

@pytest.fixture(autouse=True)
def mock_redis_cache():
	"""
	Mocks synchronous Redis cache operations in-memory during tests for instant execution
	and realistic cache hit/miss/eviction testing.
	"""
	from unittest.mock import patch
	fake_redis_storage = {}

	def mock_get(key):
		return fake_redis_storage.get(key)

	def mock_setex(key, time, value):
		fake_redis_storage[key] = value
		return True

	def mock_delete(key):
		fake_redis_storage.pop(key, None)
		return True

	with patch("main.cache_client.get", side_effect=mock_get), \
	     patch("main.cache_client.setex", side_effect=mock_setex), \
	     patch("main.cache_client.delete", side_effect=mock_delete):
		yield fake_redis_storage


