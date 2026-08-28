# Graph Report - StarDust  (2026-08-28)

## Corpus Check
- Corpus is ~3,967 words - fits in a single context window. You may not need a graph.

## Summary
- 81 nodes · 163 edges · 8 communities (7 shown, 1 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 25 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- API Schemas & Event Handlers
- User & Subscription CRUD Endpoints
- Database Models & Celery Tasks
- Docker Infrastructure & Dependencies
- WebSocket Connection Manager
- Authentication & Login
- Token Verification & WebSocket Auth
- Security & Crypto Dependencies

## God Nodes (most connected - your core abstractions)
1. `User` - 14 edges
2. `get_subscription_or_404()` - 8 edges
3. `login()` - 8 edges
4. `Subscription` - 8 edges
5. `Base` - 7 edges
6. `write_subscriptions()` - 7 edges
7. `update_subscriptions()` - 7 edges
8. `get_user_from_token()` - 6 edges
9. `get_subscriptions()` - 6 edges
10. `delete_subscriptions()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `get_user_from_token()` --uses--> `User`  [INFERRED]
  auth.py → models.py
- `get_current_user()` --uses--> `User`  [INFERRED]
  auth.py → models.py
- `get_subscription_or_404()` --uses--> `Subscription`  [INFERRED]
  main.py → models.py
- `get_summary()` --uses--> `Subscription`  [INFERRED]
  main.py → models.py
- `add_user()` --uses--> `UserCreate`  [INFERRED]
  main.py → schemas.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Celery Asynchronous Task Processing Stack** — docker_compose_worker, docker_compose_beat, docker_compose_redis, requirements_celery [INFERRED 0.95]
- **StarDust Multi-Service Docker Architecture** — docker_compose_sub_app, docker_compose_db, docker_compose_redis, docker_compose_worker, docker_compose_beat [EXTRACTED 1.00]

## Communities (8 total, 1 thin omitted)

### Community 0 - "API Schemas & Event Handlers"
Cohesion: 0.19
Nodes (15): BaseModel, read_root(), redis_listener(), start_redis_listener(), SubscriptionDelete, SubscriptionOut, Subscriptions, SubscriptionsUpdate (+7 more)

### Community 1 - "User & Subscription CRUD Endpoints"
Cohesion: 0.24
Nodes (16): hash_password(), delete, get, add_user(), delete_subscriptions(), get_subscription_or_404(), get_subscriptions(), get_summary() (+8 more)

### Community 2 - "Database Models & Celery Tasks"
Cohesion: 0.24
Nodes (9): BaseSettings, Settings, Base, get_db(), DeclarativeBase, Alert, Subscription, task (+1 more)

### Community 3 - "Docker Infrastructure & Dependencies"
Cohesion: 0.19
Nodes (13): Celery Beat Periodic Scheduler Service, PostgreSQL Database Service, PostgreSQL Data Volume, Redis Message Broker Service, FastAPI Web Application Service, Celery Asynchronous Worker Service, Celery Distributed Task Queue, FastAPI Web Framework (+5 more)

### Community 4 - "WebSocket Connection Manager"
Cohesion: 0.39
Nodes (3): ConnectionManager, UUID, WebSocket

### Community 5 - "Authentication & Login"
Cohesion: 0.40
Nodes (5): create_access_token(), verify_password(), login(), OAuth2PasswordRequestForm, timedelta

### Community 6 - "Token Verification & WebSocket Auth"
Cohesion: 0.50
Nodes (5): get_current_user(), get_user_from_token(), Session, websocket, websocket_endpoint()

## Knowledge Gaps
- **5 isolated node(s):** `PostgreSQL Data Volume`, `SQLAlchemy ORM & Database Toolkit`, `Pydantic Data Validation`, `python-jose JWT Library`, `Passlib Password Hashing Library`
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ConnectionManager` connect `WebSocket Connection Manager` to `API Schemas & Event Handlers`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Why does `Subscription` connect `Database Models & Celery Tasks` to `API Schemas & Event Handlers`, `User & Subscription CRUD Endpoints`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `User` connect `User & Subscription CRUD Endpoints` to `API Schemas & Event Handlers`, `Database Models & Celery Tasks`, `Authentication & Login`, `Token Verification & WebSocket Auth`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `User` (e.g. with `get_current_user()` and `get_user_from_token()`) actually correct?**
  _`User` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `get_subscription_or_404()` (e.g. with `Subscription` and `User`) actually correct?**
  _`get_subscription_or_404()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Subscription` (e.g. with `get_subscription_or_404()` and `get_summary()`) actually correct?**
  _`Subscription` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `PostgreSQL Data Volume`, `SQLAlchemy ORM & Database Toolkit`, `Pydantic Data Validation` to the rest of the system?**
  _5 weakly-connected nodes found - possible documentation gaps or missing edges._