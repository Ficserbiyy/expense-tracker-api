from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from config import User, UserCreate, settings
from jwt_auth import verify_password, create_access_token, hash_password, decode_access_token
from database import get_session
from sqlmodel import select
from typing import Final


router: Final = APIRouter(prefix="/auth", tags=["Authentication"])




async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    ''' Get user by email '''
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    return result.scalars().first()


async def get_current_user(request: Request, session: AsyncSession = Depends(get_session)) -> User:
    ''' Get current user '''
    token = request.cookies.get("shopping_session")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not Authorized",
        )
    email = decode_access_token(token)
    user = await get_user_by_email(session, email)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User Not Found",
        )
    return user


@router.post("/register", status_code=201)
async def register(user_data: UserCreate, session: AsyncSession = Depends(get_session)):
    ''' Registration '''
    existing_user = await get_user_by_email(session, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email registered")
    
    hashed = hash_password(user_data.password)
    db_user = User(email=user_data.email, hashed_password=hashed, is_active=True)
    
    session.add(db_user)
    await session.commit()
    return {"detail": "Successfully registered"}


