from fastapi import FastAPI, Request, Response
from starlette_graphene3 import GraphQLApp, make_playground_handler
from app.graphql.schema import schema
from app.database.connection import engine
from app.database.dependencies import get_db
from app.models import usermodel

usermodel.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Database session middleware
@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        # Add database session to request state
        db_session = next(get_db())
        request.state.db = db_session
        print("Middleware: Database session attached")  # Debugging
        response = await call_next(request)
    finally:
        # Close the session
        if hasattr(request.state, "db"):
            request.state.db.close()
    return response


# Custom GraphQL middleware to handle context
class CustomGraphQLApp(GraphQLApp):
    async def handle_graphql(self, request: Request):
        context = {"db": getattr(request.state, "db", None)}
        return await super().handle_graphql(request, context=context)


app.mount("/graphql", CustomGraphQLApp(schema=schema))

app.mount("/", GraphQLApp(schema, on_get=make_playground_handler()))  # Playground IDE


@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI GraphQL API"}
