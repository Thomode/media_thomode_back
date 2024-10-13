from typing import List
from pydantic import BaseModel


class Series(BaseModel):
    name: str
    name_id: str
    image_url: str


class Episode(BaseModel):
    title: str
    series_name_id: str
    episode_id: str


class SeriesDetails(BaseModel):
    name: str
    name_id: str
    synopsis: str
    status: str
    profile_image_url: str
    cover_image_url: str
    last_episode: str
    episodes: List[Episode]


class VideoEpisode(BaseModel):
    series_name_id: str
    episode_id: str
    video_url: str
    video_direct: bool
    server_name: str