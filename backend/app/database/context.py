# from fastapi import Request


# class GraphQLContext:
#     def __init__(self, request: Request):
#         self.request: Request = request
#         # Get db from request state
#         self.db = getattr(request.state, "db", None)

#     @property
#     def get_db(self):
#         if self.db is None:
#             raise Exception("Database session is not available in the context")
#         return self.db
