from enum import Enum
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, validator


class PersonRole(str, Enum):
    actor = "actor"
    director = "director"
    writer = "writer"


class AbstractModel(BaseModel):
    id: UUID


class PersonFilm(AbstractModel):
    name: str


class GenresES(AbstractModel):
    name: str


class PersonsES(PersonFilm):
    role: Optional[List[PersonRole]] = None
    film_ids: Optional[List[UUID]] = None


class MoviesES(AbstractModel):
    title: str
    imdb_rating: Optional[float] = None
    description: Optional[str] = None
    genre: Optional[list] = None
    director: Optional[list] = []
    actors: Optional[List[PersonFilm]] = None
    actors_names: Optional[list] = None
    writers: Optional[List[PersonFilm]] = None
    writers_names: Optional[list] = None

    class Config:
        validate_assignment = True

    @validator('director')
    def set_director(cls, director):
        return director or []
