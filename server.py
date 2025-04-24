from ariadne import (
    load_schema_from_path,
    make_executable_schema,
)

from resolvers import query,mutation,subscription,initialize_broadcast
from ariadne.asgi import GraphQL
from ariadne.asgi.handlers import GraphQLTransportWSHandler
from starlette.applications import Starlette
from broadcaster import Broadcast

broadcast = Broadcast("redis://localhost:6379")

type_defs = load_schema_from_path("schema.graphql")
schema = make_executable_schema(type_defs, [query, mutation, subscription])

graphql_app = GraphQL(
            schema=schema,
            debug=True,
            websocket_handler=GraphQLTransportWSHandler(),
        )

async def startup():
    await initialize_broadcast()

async def shutdown():
    await broadcast.disconnect()

app = Starlette(debug=True, on_startup=[startup], on_shutdown=[shutdown])

app.mount("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)       