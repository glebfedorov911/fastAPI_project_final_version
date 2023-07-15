import json
import math

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.operators import and_

from src.auth.models import User
from src.database import get_async_session
from src.posts.models import Post, Like
from src.app import current_active_user
from src.posts.schemas import PostCreate, PostUpdate

templates = Jinja2Templates(directory="src/templates")

router = APIRouter(
    tags=["Posts"],
    prefix="/posts"
)

@router.post("/addpost")
async def add_post(
        user: User = Depends(current_active_user), session: AsyncSession = Depends(get_async_session),
        head: str = Form(...), description: str = Form(...), post: PostCreate = None
):
    try:
        data = {"head": head, "description": description, "user_id": user.id}
        stmt = insert(Post).values(**data)
        await session.execute(stmt)
        await session.commit()

        return {
            "status": "success",
            "detail": None,
            "data": None,
        }
    except:
        return HTTPException(status_code=500, detail={
            "status": "not success",
            "detail": None,
            "data": None,
        })

@router.get("/form-addpost")
async def form_post(request: Request):
    return templates.TemplateResponse("add-post.html", {"request":request, "title":"Добавить статью"})

@router.get("/feed-posts/{page}")
async def posts(
        request: Request, session: AsyncSession = Depends(get_async_session), limit: int = 10, page: int = 1,
        user: User = Depends(current_active_user)
):
    query = select(Post, Like).join(Like, isouter=True).distinct(Post.head)
    result = await session.execute(query)

    posts = result.all()[::-1][(page-1)*10:][:limit]

    pages = await session.execute(query)
    pages = json.dumps(math.ceil(len(pages.scalars().all())/10))

    context = {"request":request, "posts":posts, "pages":pages, "user": user.id, "like_posts":result.scalars().all()}

    return templates.TemplateResponse("feed.html", context)

@router.post("/edit-post/{id}")
async def edit_post(
        id:int, head: str = Form(...), description: str = Form(...), session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user), post: PostUpdate = None
                    ):
    try:
        query = select(Post).where(Post.id == id)
        result = await session.execute(query)

        if not (result.scalars().all()[0].user_id == user.id):
            raise Exception

        data = {"head": head, "description": description, "user_id": user.id}
        stmt = update(Post).values(**data).where(Post.id==id)
        await session.execute(stmt)
        await session.commit()

        return {
            "status": "success",
            "detail": None,
            "data": None
        }

    except Exception:
        return HTTPException(status_code=500, detail={
            "status": "not success",
            "detail": None,
            "data": None
        })

@router.get("/edit-form/{id}")
async def edit_form(
        id: int, request: Request, user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session)
                    ):

    query = select(Post).where(Post.id == id)
    result = await session.execute(query)

    context = {"request":request, "id":id, "user_id":user.id, "author":result.scalars().all()[0].user_id}

    return templates.TemplateResponse("edit-post.html", context)

@router.get("/delete/{id}")
async def delete_post(
        id: int, session: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user)
):
    try:
        query = select(Post).where(Post.id == id)
        result = await session.execute(query)

        if user.id != result.scalars().all()[0].user_id:
            raise Exception

        stmt = delete(Post).where(Post.id==id)
        await session.execute(stmt)
        await session.commit()

        return {
            "status": "success",
            "detail": None,
            "data": None
        }

    except Exception:
        return HTTPException(status_code=500, detail={
            "status": "not success",
            "detail": None,
            "data": None
        })

@router.get("/addlike/{id}")
async def like_post(
        id: int, session: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user)
):
    try:

        query = select(Post).where(Post.id==id)
        result = await session.execute(query)

        if result.scalars().all()[0].user_id == user.id:
            raise Exception

        data = {"user_id": user.id, "post_id": id}

        stmt = insert(Like).values(**data)
        await session.execute(stmt)
        await session.commit()

        return {
            "status": "success",
            "detail": None,
            "data": None
        }

    except Exception:
        return HTTPException(status_code=500, detail={
            "status": "not success",
            "detail": None,
            "data": None
        })

@router.get("/deletelike/{id}")
async def like_post(
        id: int, session: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user)
):
    try:

        stmt = delete(Like).where(and_(user.id == Like.user_id, Like.post_id == id))
        await session.execute(stmt)
        await session.commit()

        return {
            "status": "success",
            "detail": None,
            "data": None
        }

    except Exception:
        return HTTPException(status_code=500, detail={
            "status": "not success",
            "detail": None,
            "data": None
        })