from typing import *
from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordBearer
from controllers.movie_genres.get_all_genres import get_all_genres_controller
from controllers.movie_genres.get_genre_by_id import get_genre_by_id_controller
from controllers.movie_genres.create_genre import create_genre_controller
from controllers.movie_genres.update_genre_by_id import update_genre_by_id_controller
from controllers.movie_genres.delete_genre_by_id import delete_genre_by_id_controller
from helpers.token import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def current_user_dep(token: str = Depends(oauth2_scheme)):
    return get_current_user(token)

@router.get("/all")
async def get_all_genres(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return get_all_genres_controller(data)

@router.post("/by_id")
async def get_genre_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return get_genre_by_id_controller(data)

@router.post("/create")
async def create_genre(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return create_genre_controller(data)

@router.put("/update")
async def update_genre_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return update_genre_by_id_controller(data)

@router.delete("/delete")
async def delete_genre_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return delete_genre_by_id_controller(data)
