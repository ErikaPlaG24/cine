from typing import *
from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordBearer
from controllers.movies.get_all_movies import get_all_movies_controller
from controllers.movies.get_movie_by_id import get_movie_by_id_controller
from controllers.movies.create_movie import create_movie_controller
from controllers.movies.update_movie_by_id import update_movie_by_id_controller
from controllers.movies.delete_movie_by_id import delete_movie_by_id_controller
from controllers.movies.search_movies import search_movies_controller
from helpers.token import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def current_user_dep(token: str = Depends(oauth2_scheme)):
    return get_current_user(token)

@router.get("/all")
async def get_all_movies(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return get_all_movies_controller(data)

@router.post("/by_id")
async def get_movie_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return get_movie_by_id_controller(data)

@router.post("/create")
async def create_movie(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return create_movie_controller(data)

@router.put("/update")
async def update_movie_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return update_movie_by_id_controller(data)

@router.delete("/delete")
async def delete_movie_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return delete_movie_by_id_controller(data)

@router.post("/search")
async def search_movies(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return search_movies_controller(data)
