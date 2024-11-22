import graphene


# Schema definition for User
class UserType(graphene.ObjectType):
    id = graphene.Int()
    username = graphene.String()
    usertype = graphene.String()
    email = graphene.String()
    password = graphene.String()
    create_time = graphene.DateTime()
