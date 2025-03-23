from sqlalchemy import delete, select
from src.database import async_session_maker
from fastapi.responses import JSONResponse
from src.users.models import User


class UsersServices:
    async def create_user(data):
        async with async_session_maker() as session:
            new_user = User(
                name=data["name"],
                email=data["email"],
                number=data["number"],
                hashed_password=data["hashed_password"],
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
        return new_user.id

    async def get_user_by_id(id):
        async with async_session_maker() as session:
            stmt = select(User).where(User.id == id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            return user

    async def delete_user_by_number(number):
        async with async_session_maker() as session:
            await session.execute(delete(User).where(User.number == number))
            await session.commit()
        return JSONResponse(
            status_code=200, content={"detail": "User deleted successfully"}
        )

    async def get_user_by_number(number):
        async with async_session_maker() as session:
            stmt = select(User).where(User.number == number)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            return user 
            


    async def get_user_by_email(email):
        async with async_session_maker() as session:
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            return user 