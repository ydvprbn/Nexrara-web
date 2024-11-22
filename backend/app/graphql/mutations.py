import graphene
from fastapi import status, HTTPException
from app.graphql.types.user import UserType
from app.models.usermodel import User
from sqlalchemy.orm import Session
from app.utils.security import hash, verify
from .. import oauth2
import secrets
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
import smtplib


class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        usertype = graphene.String(required=True)
        email = graphene.String()
        password = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    status_code = graphene.Int()
    user = graphene.Field(UserType)

    def mutate(self, info, username, usertype, email, password):
        print("Resolver Context:", info.context)
        db = info.context.get("db")
        if db is None:
            raise Exception("Database session is not available in the context.")

        hashed_password = hash(password)

        # Check if user already exists
        existing_user = (
            db.query(User)
            .filter(User.username == username)
            .filter(User.usertype == usertype)
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
        try:
            user = User.create_user(
                username=username,
                usertype=usertype,
                email=email,
                password=hashed_password,
            )

            return CreateUser(
                success=True,
                message="User created successfully",
                status_code=201,
                user=user,
            )
        except Exception as e:
            # Rollback in case of an error
            db.rollback()
            raise Exception(f"Error creating record: {str(e)}")


class UpdateUser(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        username = graphene.String()
        usertype = graphene.String()
        email = graphene.String()

    user = graphene.Field(UserType)

    def mutate(self, info, id, username, usertype, email):

        # Check if user exists or not
        user = User.get_by_id(id=id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id: {id} does not exist",
            )
        user = User.update_user(
            id=id,
            username=username,
            usertype=usertype,
            email=email,
        )
        return UpdateUser(user=user)


class DeleteUser(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    user = graphene.Field(UserType)

    def mutate(self, info, id):
        user = User.get_by_id(id=id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id: {id} does not exist",
            )

        user = User.delete_user(id=id)

        return DeleteUser(user=user)


class Login(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        usertype = graphene.String(required=True)
        password = graphene.String(required=True)

    token = graphene.String()
    token_type = graphene.String()
    user = graphene.Field(UserType)

    def mutate(
        root,
        info,
        session: Session,
        username,
        usertype,
        password,
    ):
        user = (
            session.query(User)
            .filter(User.username == username)
            .filter(User.usertype == usertype)
            .first()
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid Credentials",
            )

        if not verify(password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        # Generate access token
        access_token = oauth2.create_access_token(
            data={"user_id": user["id"], "username": user["username"]},
        )

        return Login(token=access_token, token_type="bearer", user=user)


# class ForgotPasswordInput(graphene.InputObjectType):
#     email = graphene.String(required=True)


# class ForgotPasswordResponse(graphene.ObjectType):
#     success = graphene.Boolean()
#     message = graphene.String()


# class ForgotPasswordMutation(graphene.Mutation):
#     class Arguments:
#         input = ForgotPasswordInput(required=True)

#     Output = ForgotPasswordResponse

#     async def mutate(self, info, input):
#         try:
#             email = input.email

#             # Generate a password reset token
#             reset_token = secrets.token_urlsafe(32)

#             # Set token expiration
#             token_expiry = datetime.now(timezone.utc) + timedelta(minutes=30)

#             # Save token and expiry to database
#             user = User.get_all(email=email)
#             if not user:
#                 return ForgotPasswordResponse(
#                     success=False, message="No account found with this email address."
#                 )

#             await db.users.update_one(
#                 {"email": email},
#                 {
#                     "$set": {
#                         "reset_token": reset_token,
#                         "reset_token_expires": token_expiry,
#                     }
#                 },
#             )

#             # Create reset password link
#             reset_link = f"https://yourapp.com/reset-password?token={reset_token}"

#             # Email configuration
#             SMTP_SERVER = "smtp.gmail.com"
#             SMTP_PORT = 587
#             SMTP_USERNAME = "your-email@gmail.com"
#             SMTP_PASSWORD = "your-app-specific-password"

#             # Create email message
#             message = MIMEText(
#                 f"""
#                 Hello,

#                 You have requested to reset your password. Please click the link below to reset it:

#                 {reset_link}

#                 This link will expire in 1 hour.

#                 If you didn't request this, please ignore this email.

#                 Best regards,
#                 Your App Team
#                 """
#             )

#             message["Subject"] = "Password Reset Request"
#             message["From"] = SMTP_USERNAME
#             message["To"] = email

#             # Send email
#             """
#             with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#                 server.starttls()
#                 server.login(SMTP_USERNAME, SMTP_PASSWORD)
#                 server.send_message(message)
#             """

#             return ForgotPasswordResponse(
#                 success=True,
#                 message="Password reset instructions have been sent to your email.",
#             )

#         except Exception as e:
#             return ForgotPasswordResponse(
#                 success=False, message=f"An error occurred: {str(e)}"
#             )


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()
    # forgot_password = ForgotPasswordMutation.Field()

    login = Login.Field()
