from fastapi import Depends
from sqlalchemy import TIMESTAMP, Column, Integer, String, text, update, delete, select
from sqlalchemy.orm import Session
from ..database.connection import Base
from ..database.dependencies import get_db


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(16), nullable=False)
    usertype = Column(String(16), nullable=False)
    email = Column(String(255), unique=True)
    password = Column(String(64), nullable=False)
    create_time = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

    def create_user(
        username: str,
        usertype: str,
        email: str,
        password: str,
        db: Session = Depends(get_db),
    ):
        new_user = User(
            username=username,
            usertype=usertype,
            email=email,
            password=password,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

        # cur.execute(
        #     """
        #         INSERT INTO users (username, usertype, email, password)
        #         VALUES (%s, %s, %s, %s)
        #         RETURNING id, username, usertype, email, password, create_time
        #     """,
        #     (username, usertype, email, password),
        # )
        # user_data = cur.fetchone()
        # conn.commit()
        # return User(**user_data)

    def update_user(
        id: int, username: str, usertype: str, email: str, db: Session = Depends(get_db)
    ):
        stmt = (
            update(User)
            .where(User.id == id)
            .values(username=username, usertype=usertype, email=email)
            .returning(User)
        )
        result = db.execute(stmt).scalar_one()
        db.commit()
        return result

    # cur.execute(
    #     """UPDATE users SET username = %s, usertype = %s, email = %s WHERE id = %s RETURNING id, username, usertype, email""",
    #     (username, usertype, email, id),
    # )
    # user_data = cur.fetchone()
    # conn.commit()
    # return User(**user_data)

    def delete_user(id: int, db: Session = Depends(get_db)):
        stmt = delete(User).where(User.id == id).returning(User)
        result = db.execute(stmt)
        deleted_user = result.scalar_one()
        return deleted_user

        # cur.execute("""DELETE FROM users where id = %s returning *""", (id,))
        # user_data = cur.fetchone()
        # conn.commit()
        # return User(**user_data)

    def get_by_id(id: int, db: Session = Depends(get_db)):
        stmt = select(User).where(User.id == id)
        result = db.execute(stmt).scalar_one_or_none()

        return result

        # cur.execute(
        #     """
        #         SELECT id, username, usertype, email, password, create_time
        #         FROM users WHERE id = %s
        #     """,
        #     (id,),
        # )
        # user_data = cur.fetchone()
        # return User(**user_data) if user_data else None

    def get_all(db: Session = Depends(get_db)):
        stmt = select(User)
        users = db.execute(stmt).scalars().all()
        return list(users)

        # cur.execute(
        #     """
        #         SELECT id, username, usertype, email, password, create_time
        #         FROM users
        #     """
        # )
        # return [User(**row) for row in cur.fetchall()]
