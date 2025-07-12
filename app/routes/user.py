from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate
from app.core.database import get_async_session
from app.routes.auth import pwd_context
from app.routes.auth import current_active_user

router = APIRouter(prefix="/users", tags=["users"])

# Make current user superuser (DEV ONLY)
@router.patch("/make-me-superuser")
async def make_me_superuser(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_active_user),
):
    current_user.is_superuser = True
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return {"detail": "You are now a superuser"}


# GET /users/
@router.get("/", response_model=List[UserRead])
async def get_all_users(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(User))
    return result.scalars().all()

# GET /users/{user_id}
@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, session: AsyncSession = Depends(get_async_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# PUT /users/{user_id}
@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, data: UserUpdate, session: AsyncSession = Depends(get_async_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = data.dict(exclude_unset=True)

    if "password" in update_data:
        update_data["hashed_password"] = pwd_context.hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

# DELETE /users/{user_id}
@router.delete("/{user_id}")
async def delete_user(user_id: int, session: AsyncSession = Depends(get_async_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await session.delete(user)
    await session.commit()
    return {"detail": f"User {user_id} deleted successfully"}
