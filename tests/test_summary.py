import pytest
from fastapi import status
from datetime import date, timedelta

def test_summary_billing_normalization(client, auth_headers):
	# 1. Add yearly sub ($120/year -> $10/month)
	client.post(
		"/subscriptions",
		json={
			"name": "Amazon Prime Yearly",
			"cost": 120.00,
			"billing_cycle": "yearly",
			"description": "Annual membership",
			"renewal_date": (date.today() + timedelta(days=2)).isoformat()
		},
		headers=auth_headers
	)

	# 2. Add monthly sub ($15/month)
	client.post(
		"/subscriptions",
		json={
			"name": "HBO Max",
			"cost": 15.00,
			"billing_cycle": "monthly",
			"description": "Monthly movies",
			"renewal_date": (date.today() + timedelta(days=5)).isoformat()
		},
		headers=auth_headers
	)

	# 3. Add far-future sub (renewal in 30 days — should NOT appear in upcoming_renewals)
	client.post(
		"/subscriptions",
		json={
			"name": "Gym Annual",
			"cost": 300.00,
			"billing_cycle": "yearly",
			"description": "Annual gym",
			"renewal_date": (date.today() + timedelta(days=30)).isoformat()
		},
		headers=auth_headers
	)

	# Total monthly spend = (120/12) + 15 + (300/12) = 10 + 15 + 25 = 50.00
	response = client.get("/subscriptions/summary", headers=auth_headers)
	assert response.status_code == status.HTTP_200_OK
	data = response.json()
	assert data["total_monthly_spend"] == 50.00
	
	# Only the two renewals within 7 days should be returned in upcoming_renewals
	upcoming_names = [sub["name"] for sub in data["upcoming_renewals"]]
	assert "Amazon Prime Yearly" in upcoming_names
	assert "HBO Max" in upcoming_names
	assert "Gym Annual" not in upcoming_names
	assert len(data["upcoming_renewals"]) == 2

def test_summary_cache_hit_and_eviction_lifecycle(client, auth_headers):
	# Add initial subscription
	client.post(
		"/subscriptions",
		json={
			"name": "Spotify",
			"cost": 10.00,
			"billing_cycle": "monthly",
			"description": "Music"
		},
		headers=auth_headers
	)

	# 1. First GET: Cache Miss (computed from DB, stored in Redis)
	resp1 = client.get("/subscriptions/summary", headers=auth_headers)
	assert resp1.status_code == status.HTTP_200_OK
	assert resp1.json()["total_monthly_spend"] == 10.00
	assert resp1.json()["cached"] is False

	# 2. Second GET: Cache Hit (served directly from Redis cache)
	resp2 = client.get("/subscriptions/summary", headers=auth_headers)
	assert resp2.status_code == status.HTTP_200_OK
	assert resp2.json()["total_monthly_spend"] == 10.00
	assert resp2.json()["cached"] is True

	# 3. Mutation: POST new subscription triggers active cache eviction
	client.post(
		"/subscriptions",
		json={
			"name": "Netflix",
			"cost": 20.00,
			"billing_cycle": "monthly",
			"description": "Video"
		},
		headers=auth_headers
	)

	# 4. Third GET: Cache Miss (recalculated from DB with updated total)
	resp3 = client.get("/subscriptions/summary", headers=auth_headers)
	assert resp3.status_code == status.HTTP_200_OK
	assert resp3.json()["total_monthly_spend"] == 30.00
	assert resp3.json()["cached"] is False

