import pytest
from fastapi import status
from unittest.mock import patch
from redis.exceptions import RedisError
from rate_limiter import check_rate_limit

def test_login_rate_limiting_blocks_after_threshold(client, test_user):
	"""
	Verifies that /login allows 5 attempts per window, and blocks the 6th attempt with HTTP 429.
	"""
	# Attempts 1 through 5: Processed normally (returns 401 for wrong password)
	for _ in range(5):
		resp = client.post(
			"/login",
			data={"username": "testuser", "password": "wrongpassword"}
		)
		assert resp.status_code == status.HTTP_401_UNAUTHORIZED

	# Attempt 6: Blocked by rate limiter with 429 Too Many Requests
	resp_blocked = client.post(
		"/login",
		data={"username": "testuser", "password": "wrongpassword"}
	)
	assert resp_blocked.status_code == status.HTTP_429_TOO_MANY_REQUESTS
	assert "Rate limit exceeded" in resp_blocked.json()["detail"]
	assert "Retry-After" in resp_blocked.headers
	assert resp_blocked.headers["Retry-After"] == "60"

def test_rate_limiter_fails_open_on_redis_error():
	"""
	Ensures graceful degradation: If Redis is down, check_rate_limit catches the error
	and allows the request through rather than raising a 500 error.
	"""
	with patch("rate_limiter.rate_limit_client.pipeline", side_effect=RedisError("Connection refused")):
		# Must complete without raising an unhandled exception or HTTPException
		check_rate_limit("rl:test:key", limit=5, window_seconds=60)
