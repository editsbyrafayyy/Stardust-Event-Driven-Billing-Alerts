import pytest
from fastapi import status
from datetime import date, timedelta

def test_create_subscription_success(client, auth_headers):
	payload = {
		"name": "Netflix",
		"cost": 15.99,
		"billing_cycle": "monthly",
		"description": "Streaming movies and TV shows",
		"renewal_date": date.today().isoformat()
	}
	response = client.post("/subscriptions", json=payload, headers=auth_headers)
	assert response.status_code == status.HTTP_201_CREATED
	data = response.json()
	assert data["name"] == "Netflix"
	assert data["cost"] == 15.99
	assert "id" in data

def test_create_subscription_unauthenticated(client):
	payload = {
		"name": "Spotify",
		"cost": 9.99,
		"billing_cycle": "monthly",
		"description": "Music streaming"
	}
	response = client.post("/subscriptions", json=payload)
	assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_subscription_by_id(client, auth_headers):
	create_resp = client.post(
		"/subscriptions",
		json={
			"name": "GitHub Copilot",
			"cost": 10.00,
			"billing_cycle": "monthly",
			"description": "AI pair programmer"
		},
		headers=auth_headers
	)
	sub_id = create_resp.json()["id"]

	get_resp = client.get(f"/subscriptions/{sub_id}", headers=auth_headers)
	assert get_resp.status_code == status.HTTP_200_OK
	assert get_resp.json()["id"] == sub_id
	assert get_resp.json()["name"] == "GitHub Copilot"

def test_patch_subscription(client, auth_headers):
	create_resp = client.post(
		"/subscriptions",
		json={
			"name": "AWS",
			"cost": 50.00,
			"billing_cycle": "monthly",
			"description": "Cloud hosting"
		},
		headers=auth_headers
	)
	sub_id = create_resp.json()["id"]

	patch_resp = client.patch(
		f"/subscriptions/{sub_id}",
		json={"cost": 75.50},
		headers=auth_headers
	)
	assert patch_resp.status_code == status.HTTP_200_OK
	assert patch_resp.json()["cost"] == 75.50
	assert patch_resp.json()["name"] == "AWS"  # name remains unchanged

def test_delete_subscription(client, auth_headers):
	create_resp = client.post(
		"/subscriptions",
		json={
			"name": "Gym",
			"cost": 40.00,
			"billing_cycle": "monthly",
			"description": "Fitness membership"
		},
		headers=auth_headers
	)
	sub_id = create_resp.json()["id"]

	del_resp = client.delete(f"/subscriptions/{sub_id}", headers=auth_headers)
	assert del_resp.status_code == status.HTTP_200_OK
	assert "deleted" in del_resp.json()["message"]

	# Verify it is no longer retrievable
	get_resp = client.get(f"/subscriptions/{sub_id}", headers=auth_headers)
	assert get_resp.status_code == status.HTTP_404_NOT_FOUND

def test_multi_tenant_isolation(client, auth_headers, auth_headers_2):
	"""
	Security check: User 2 must NEVER be able to read, update, or delete User 1's subscription.
	Must return uniform 404 to avoid leaking existence of private resources.
	"""
	# User 1 creates a subscription
	create_resp = client.post(
		"/subscriptions",
		json={
			"name": "Private Vault",
			"cost": 100.00,
			"billing_cycle": "monthly",
			"description": "User 1 secret subscription"
		},
		headers=auth_headers
	)
	sub_id = create_resp.json()["id"]

	# User 2 tries to GET User 1's subscription -> 404
	get_resp = client.get(f"/subscriptions/{sub_id}", headers=auth_headers_2)
	assert get_resp.status_code == status.HTTP_404_NOT_FOUND

	# User 2 tries to PATCH User 1's subscription -> 404
	patch_resp = client.patch(f"/subscriptions/{sub_id}", json={"cost": 0.0}, headers=auth_headers_2)
	assert patch_resp.status_code == status.HTTP_404_NOT_FOUND

	# User 2 tries to DELETE User 1's subscription -> 404
	del_resp = client.delete(f"/subscriptions/{sub_id}", headers=auth_headers_2)
	assert del_resp.status_code == status.HTTP_404_NOT_FOUND
