from ariadne import make_executable_schema, gql, load_schema_from_path
from ariadne.asgi import GraphQL
#from resolvers import query as resolvers_query
from resolvers import query,mutation,subscription
from fastapi import FastAPI
from ariadne.asgi.handlers import GraphQLTransportWSHandler

app=FastAPI()

type_defs = load_schema_from_path("schema.graphql")

schema = make_executable_schema(type_defs, [query,mutation,subscription])

class CustomGraphQLTransportWSHandler(GraphQLTransportWSHandler):
    async def on_connect(self, payload):
        # Handle the WebSocket connection
        print("WebSocket connection established")
        
        # Perform any additional actions here
        
        # Call the parent on_connect method
        await super().on_connect(payload)

# graphql=GraphQL(schema,debug=True)

graphql= GraphQL(
    schema,
    debug=True,
    websocket_handler=CustomGraphQLTransportWSHandler()
    
)

# app.add_route('/graphql',graphql)

app.mount('/graphql', graphql)



