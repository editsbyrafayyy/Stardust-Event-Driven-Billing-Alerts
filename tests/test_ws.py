import pytest
from starlette.websockets import WebSocketDisconnect
from auth import create_access_token

def test_websocket_connect_success_with_valid_token(client, test_user):
	token = create_access_token(data={"sub": test_user.username})
	with client.websocket_connect(f"/ws?token={token}") as websocket:
		assert websocket is not None

def test_websocket_rejected_with_invalid_token(client):
	with pytest.raises(WebSocketDisconnect) as exc_info:
		with client.websocket_connect("/ws?token=invalid_expired_token"):
			pass
	assert exc_info.value.code == 1008  # 1008 = WS_1008_POLICY_VIOLATION (Auth failed)
