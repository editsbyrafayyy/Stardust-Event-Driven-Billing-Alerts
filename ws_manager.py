# The goal with websockets in this application is to send real-time updates to the user such as subscription has been added or
# payment failed, etc. Websockets allow the server to push updates to the client instantly instead of the client having to ask
# for any new updates.

from fastapi import WebSocket
from uuid import UUID

class ConnectionManager:
	def __init__(self) -> None:
		# Dict mapping user_id to a list of active WebSocket connections for that user
		self.active_connections: dict[UUID, list[WebSocket]] = {}

	async def connect(self, user_id: UUID, websocket: WebSocket):
		await websocket.accept()
		if user_id not in self.active_connections:
			self.active_connections[user_id] = []
		self.active_connections[user_id].append(websocket)

	def disconnect(self, user_id: UUID, websocket: WebSocket):
		if user_id in self.active_connections:
			if websocket in self.active_connections[user_id]:
				self.active_connections[user_id].remove(websocket)
			if not self.active_connections[user_id]:
				del self.active_connections[user_id]

	async def send_to_user(self, user_id: UUID, message: str):
		# If user has no active connections, silently return (live-or-nothing delivery)
		connections = list(self.active_connections.get(user_id, []))
		for connection in connections:
			try:
				await connection.send_text(message)
			except Exception:
				# Socket failed or disconnected abruptly — clean it up
				self.disconnect(user_id, connection)