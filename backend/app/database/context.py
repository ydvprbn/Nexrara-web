class GraphQLContext:
    def __init__(self, request):
        self.request = request
        self.db = request.state.db
