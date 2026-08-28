import pytest
from fastapi import status

def test_register_user_success(client):
	response = client.post(
		"/register",
		json={"username": "newuser", "password": "securepassword123"}
	)
	assert response.status_code == status.HTTP_200_OK
	data = response.json()
	assert data["username"] == "newuser"
	assert "id" in data
	assert "password" not in data  # password must NEVER be returned in response

def test_register_duplicate_username_fails(client):
	# First registration succeeds
	client.post(
		"/register",
		json={"username": "duplicateuser", "password": "password123"}
	)
	# Second registration with identical username must fail
	response = client.post(
		"/register",
		json={"username": "duplicateuser", "password": "differentpassword"}
	)
	assert response.status_code == status.HTTP_400_BAD_REQUEST
	assert response.json()["detail"] == "Username already registered"

def test_login_success(client, test_user):
	response = client.post(
		"/login",
		data={"username": "testuser", "password": "password123"}
	)
	assert response.status_code == status.HTTP_200_OK
	data = response.json()
	assert "access_token" in data
	assert data["token_type"] == "bearer"

def test_login_incorrect_password(client, test_user):
	response = client.post(
		"/login",
		data={"username": "testuser", "password": "wrongpassword"}
	)
	assert response.status_code == status.HTTP_401_UNAUTHORIZED
	assert response.json()["detail"] == "Incorrect Credentials"

def test_login_nonexistent_user(client):
	response = client.post(
		"/login",
		data={"username": "nonexistent", "password": "password123"}
	)
	assert response.status_code == status.HTTP_401_UNAUTHORIZED
	assert response.json()["detail"] == "Incorrect Credentials"
