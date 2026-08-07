# The goal with websockets in this application is to send real-time updates to the user such as subscription has been added or
# payment failed, etc. Websockets allow the server to push updates to the client instantly instead of the client having to ask
# for any new updates.

from fastapi import WebSocket
from uuid import UUID

class ConnectionManager: # this is the class responsible for managing the web socket connections
	# this class basically answers the question who owns the connection that has been made.

	def __init__(self) -> None:
		 # dict mapping user_id against a list of connections that belong to that user
		self.active_connections: dict[UUID, list[WebSocket]] = {} # 

	async def connect(self, user_id: UUID, websocket: WebSocket):
		await websocket.accept()  # completes the WebSocket handshake - required before send/receive work
		if user_id not in self.active_connections:
			self.active_connections[user_id] = []
		self.active_connections[user_id].append(websocket)