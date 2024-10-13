from fastapi import APIRouter

from core.exceptions import NotFoundError, BadRequestError
from schemas.series_scheme import Series, SeriesDetails, VideoEpisode
from services.animeflv_service import AnimeflvService
from services.mundo_donghua_service import MundoDonghuaService

router = APIRouter()

@router.get("/{series_type}/search/{search_name}", response_model=list[Series])
def search_series(series_type: str,search_name: str):
    if series_type == "donghua":
        mundo_donghua = MundoDonghuaService()
        series = mundo_donghua.search_series(search_name)
        mundo_donghua.close()

    elif series_type == "anime":
        animeflv = AnimeflvService()
        series = animeflv.search_series(search_name)

    else:
        raise BadRequestError("Undefined series type")

    return series


@router.get("/{series_type}/{name_id}", response_model=SeriesDetails)
def get_series_detail(series_type: str, name_id: str):
    if series_type == "donghua":
        mundo_donghua = MundoDonghuaService()
        series_details = mundo_donghua.get_series_details(name_id)
        mundo_donghua.close()

    elif series_type == "anime":
        animeflv = AnimeflvService()
        series_details = animeflv.get_series_details(name_id)

    else:
        raise BadRequestError("Undefined series type")

    if series_details is None:
        raise NotFoundError(f"Series not found: {name_id}")

    return series_details


@router.get("/{series_type}/{series_name_id}/{episode_id}", response_model=list[VideoEpisode])
def get_video_servers(series_type: str, series_name_id: str , episode_id: str):

    if series_type == "donghua":
        mundo_donghua = MundoDonghuaService()
        servers = mundo_donghua.get_video_servers(series_name_id, episode_id)
        mundo_donghua.close()

    elif series_type == "anime":
        animeflv = AnimeflvService()
        servers = animeflv.get_video_servers(series_name_id, episode_id)

    else:
        raise BadRequestError("Undefined series type")

    if servers is None:
        raise NotFoundError(f"Video series not found: {series_name_id}/{episode_id}")

    return servers