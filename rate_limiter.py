import redis
from redis.exceptions import RedisError
from fastapi import HTTPException, status
from config import settings

# Dedicated Redis client for rate limiting
rate_limit_client = redis.from_url(settings.redis_url, decode_responses=True, socket_timeout=3.0)

def check_rate_limit(key: str, limit: int, window_seconds: int = 60) -> None:
	"""
	Enforces a fixed-window rate limit in Redis for a specific key (e.g. IP or User ID).

	Algorithm:
	1. Atomic pipeline increments the request count for this key.
	2. Sets a TTL on the key if it was just created (first request in the window).
	3. If the request count exceeds the limit, raises HTTP 429 Too Many Requests
	   with a 'Retry-After' header indicating when the window resets.

	Resilience (Fail-Open):
	- If Redis is unavailable, logs a warning and allows the request through
	  rather than failing with a 500 error for legitimate users.
	"""
	try:
		pipe = rate_limit_client.pipeline()
		pipe.incr(key)
		pipe.expire(key, window_seconds)
		results = pipe.execute()
		current_count = results[0]

		if current_count > limit:
			raise HTTPException(
				status_code=status.HTTP_429_TOO_MANY_REQUESTS,
				detail=f"Rate limit exceeded. Maximum {limit} requests per {window_seconds}s.",
				headers={"Retry-After": str(window_seconds)}
			)
	except RedisError as e:
		# Fail-open: Never block user requests if the caching/broker service has a network blip
		print(f"[RateLimiter Warning] Redis unavailable ({e}). Failing open.")
