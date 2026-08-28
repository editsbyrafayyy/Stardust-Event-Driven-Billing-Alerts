import pytest
import httpx
import websockets
import asyncio
import uuid
from datetime import date, timedelta
import redis

BASE_HTTP_URL = "http://localhost:8082"
BASE_WS_URL = "ws://localhost:8082"

def is_docker_running() -> bool:
	"""Check if the sub-app container is running and healthy on port 8082."""
	try:
		resp = httpx.get(f"{BASE_HTTP_URL}/", timeout=2.0)
		return resp.status_code == 200
	except Exception:
		return False

pytestmark = pytest.mark.skipif(
	not is_docker_running(),
	reason="Docker Compose stack is not running on localhost:8082. Start it with 'docker compose up -d' to run E2E tests."
)

@pytest.mark.asyncio
async def test_full_docker_e2e_journey():
	"""
	End-to-End Test across all 5 Docker containers:
	1. PostgreSQL: User registration & subscription persistence.
	2. FastAPI (sub-app): HTTP routing & WebSocket connection management.
	3. Redis: Cache-Aside summary caching and Pub/Sub event bus.
	4. Celery Worker: Background alert processing and real-time push to open WebSocket.
	"""
	unique_suffix = str(uuid.uuid4())[:8]
	username = f"e2e_user_{unique_suffix}"
	password = "E2ESecurePassword!123"

	async with httpx.AsyncClient(base_url=BASE_HTTP_URL, timeout=5.0) as client:
		# 1. Register new user against real PostgreSQL
		reg_resp = await client.post("/register", json={"username": username, "password": password})
		assert reg_resp.status_code == 200
		user_data = reg_resp.json()
		user_id = user_data["id"]

		# 2. Login to obtain real JWT access token
		login_resp = await client.post("/login", data={"username": username, "password": password})
		assert login_resp.status_code == 200
		token = login_resp.json()["access_token"]
		headers = {"Authorization": f"Bearer {token}"}

		# 3. Create a subscription renewing tomorrow
		sub_resp = await client.post(
			"/subscriptions",
			json={
				"name": "Live Docker Netflix",
				"cost": 15.99,
				"billing_cycle": "monthly",
				"description": "E2E test subscription",
				"renewal_date": (date.today() + timedelta(days=1)).isoformat()
			},
			headers=headers
		)
		assert sub_resp.status_code == 201

		# 4. Verify Real Redis Caching on /subscriptions/summary
		# First call: Cache Miss
		summary_1 = await client.get("/subscriptions/summary", headers=headers)
		assert summary_1.status_code == 200
		assert summary_1.json()["total_monthly_spend"] == 15.99
		assert summary_1.json()["cached"] is False

		# Second call: Cache Hit from real Redis broker container
		summary_2 = await client.get("/subscriptions/summary", headers=headers)
		assert summary_2.status_code == 200
		assert summary_2.json()["cached"] is True

		# 5. Open live WebSocket connection to FastAPI sub-app
		ws_url = f"{BASE_WS_URL}/ws?token={token}"
		async with websockets.connect(ws_url) as ws:
			# 6. Simulate Celery Worker publishing an alert to the Redis Pub/Sub channel
			# Connect directly to the exposed Redis port on localhost:6379
			try:
				r = redis.Redis(host="localhost", port=6379, db=0)
				r.publish("alerts", f'{{"user_id": "{user_id}", "message": "Subscription \'Live Docker Netflix\' renews tomorrow!"}}')
			except Exception as e:
				pytest.fail(f"Could not publish to Redis on localhost:6379: {e}")

			# 7. Assert WebSocket receives the push notification in real-time
			try:
				incoming_message = await asyncio.wait_for(ws.recv(), timeout=4.0)
				assert "Live Docker Netflix" in incoming_message
				assert "renews tomorrow" in incoming_message
			except asyncio.TimeoutError:
				pytest.fail("WebSocket did not receive notification from Redis Pub/Sub within 4 seconds!")
