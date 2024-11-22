import graphene
from app.graphql.types.user import UserType
from app.models.usermodel import User

# Query to get users


class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    user = graphene.Field(UserType, id=graphene.Int())

    def resolve_users(self, info):
        return User.get_all()

    def resolve_user(self, info, id):
        return User.get_by_id(id)
