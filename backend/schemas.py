from pydantic import BaseModel


class Artwork(BaseModel):
    object_id: int
    title: str
    artist: str
    artist_role: str | None = None
    artist_nationality: str | None = None
    date: str
    medium: str
    image_url: str | None = None
    image_small_url: str | None = None
    dimensions: str | None = None
    department: str | None = None
    gallery: str | None = None
    tags: list[str] = []