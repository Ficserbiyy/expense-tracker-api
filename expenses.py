from fastapi import APIRouter, Depends, Response, HTTPException, status, Request
from sqlmodel import select, col, and_
from datetime import datetime, timezone, date
from sqlmodel.ext.asyncio.session import AsyncSession
from database import get_session, redis_client
from config import Expense, ExpenseCreate, User
from auth import get_current_user
from typing import Final
import json, hashlib
from fastapi.encoders import jsonable_encoder


router: Final = APIRouter(prefix="/expenses", tags=["Expenses"])
now: Final = datetime.now(timezone.utc) #.replace(tzinfo=None)




@router.get("/")
async def get_all_expenses(
    request: Request, 
    response: Response, 
    search: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    sort_by: str | None = None,
    page: int = 1,
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    ''' Get all the expenses from the store. '''
    statement = select(Expense).where(Expense.owner_id == current_user.id)
    filters = []
    
    if search:
        filters.append(
            col(Expense.category).ilike(f"%{search}%")
        )


    if start_date:
        filters.append(
            Expense.created_at >= datetime.combine(
                start_date,
                datetime.min.time(),
                tzinfo=timezone.utc
            )
        )

    if end_date:
        filters.append(
            Expense.created_at <= datetime.combine(
                end_date,
                datetime.max.time(),
                tzinfo=timezone.utc,
            )
        )

    if filters:
        statement = statement.where(and_(*filters))
    

    match sort_by:
        case "amount_asc":
            statement = statement.order_by(col(Expense.amount))
        case "amount_desc":
            statement = statement.order_by(col(Expense.amount).desc())
        case "id_desc":
            statement = statement.order_by(col(Expense.id).desc())
        case _:
            statement = statement.order_by(col(Expense.id))
        
        
    offset = (page - 1) * limit
    statement = statement.offset(offset).limit(limit)
    result = await session.execute(statement)
    expenses = result.scalars().all()
    
    result_data = {
        "page": page,
        "limit": limit,
        "search_query": search,
        "expenses": [p.model_dump() for p in expenses]
    }
    
    # ETag generation
    json_bytes = json.dumps(jsonable_encoder(result_data), sort_keys=True).encode("utf-8")
    generated_etag = f'W/"{hashlib.md5(json_bytes).hexdigest()}"'
    
    # If-None-Match check
    client_etag = request.headers.get("If-None-Match")
    if client_etag == generated_etag:
        response.status_code = 304
        return Response(status_code=304)
        
    response.headers["ETag"] = generated_etag
    response.headers["Cache-Control"] = "no-cache"
    return result_data






@router.post("/", response_model=Expense)
async def create_expense(
    expense_in: ExpenseCreate, 
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user) 
):
    ''' Add a new expense '''
    
    limit_key = f"limit:expenses:{current_user.id}"
    current_count = await redis_client.incr(limit_key)
    
    if current_count == 1:
        await redis_client.expire(limit_key, 60)
    
    if current_count > 30:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests at this minute"
        )
    db_expense = Expense.model_validate(expense_in, update={"owner_id": current_user.id})
    
    session.add(db_expense)
    await session.commit()
    await session.refresh(db_expense)
    return db_expense

