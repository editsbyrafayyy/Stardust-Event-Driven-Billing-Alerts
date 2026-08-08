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
		# this proess more or less looks like: user sends a HTTP request with a websocket upgrade header, which is received by 
		# FastAPI. It provides the user with a WebSocket obj then. After which the code calls the websocket.accept() function and
		# the server accepts the upgrade request and then the connection becomes duplex (allowing for 2 way communication)
		if user_id not in self.active_connections: # checks for if the id is already present in the active connections dict
			self.active_connections[user_id] = [] # if it isn't then create a list for connections
		self.active_connections[user_id].append(websocket) # else just append a new connection in the list 

	def disconnect(self, user_id: UUID, websocket: WebSocket):
		if user_id in self.active_connections: # if the connection already exists in the dict 
			self.active_connections[user_id].remove(websocket) # just remove that specific connection

			if not self.active_connections[user_id]:  # if there are no connections left in the list
				del self.active_connections[user_id]   # remove the user id too from the dict completely so there are no empty slots in the dict

	async def send_to_user(self, user_id: UUID, message: str):
		# if the user has no open connection right now, this silently does nothing -
		# there's no queueing/persistence here, it's live-or-nothing
		for connection in self.active_connections.get(user_id, []):
			await connection.send_text(message)