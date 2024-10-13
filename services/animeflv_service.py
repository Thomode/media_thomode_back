import subprocess
from animeflv import AnimeFLV
import yt_dlp

from schemas.series_scheme import Series, Episode, SeriesDetails, VideoEpisode


class AnimeflvService:
    def search_series(self, search_name):
        try:
            with AnimeFLV() as api:
                series_list_api = api.search(search_name)

                series_list = []
                for series_api in series_list_api:
                    series = Series(
                        name=series_api.title,
                        name_id=series_api.id,
                        image_url=series_api.poster
                    )
                    series_list.append(series)
                return series_list

        except Exception as e:
            print(f"Error occurred: {e}")
            return []


    def get_series_details(self, name_id):
        try:
            with AnimeFLV() as api:
                series_details_api = api.get_anime_info(name_id)

                episodes = []
                for episodes_api in series_details_api.episodes:
                    episode = Episode(
                        title=f"{episodes_api.anime} - {episodes_api.id}",
                        series_name_id=name_id,
                        episode_id=str(episodes_api.id)
                    )
                    episodes.append(episode)

                last_episode = episodes[0].episode_id if episodes else None

                series_details = SeriesDetails(
                    name=series_details_api.title,
                    name_id=series_details_api.id,
                    synopsis=series_details_api.synopsis,
                    status= "Status not available",
                    profile_image_url=series_details_api.poster,
                    cover_image_url=series_details_api.banner,
                    last_episode=last_episode,
                    episodes=episodes
                )
                return series_details

        except Exception as e:
            print(f"Error occurred: {e}")
            return None


    def __get_video_url(self, url):
        try:
            # Ejecutar youtube-dl para obtener el enlace directo
            result = subprocess.run(['youtube-dl', '-g', url], capture_output=True, text=True)
            direct_url = result.stdout.strip()  # URL directa del video

            return direct_url
        except Exception as e:
            print(f"Error al obtener URL directa: {e}")
            return None

    def obtener_enlace_directo(self, url):
        # Definir las opciones para obtener el enlace del video sin descargarlo
        opciones = {
            'quiet': True,  # Mantener la salida limpia
            'no_warnings': True,  # Evitar mostrar warnings
            'skip_download': True,  # Evitar la descarga, solo obtener el enlace
            'geturl': True  # Obtener solo el enlace directo
        }

        # Crear una instancia de yt-dlp con las opciones
        with yt_dlp.YoutubeDL(opciones) as ydl:
            try:
                # Extraer la información del video, incluyendo el enlace directo
                info_dict = ydl.extract_info(url, download=False)
                video_url = info_dict.get('url', None)

                if video_url:
                    return video_url
                else:
                    return "No se encontró el enlace directo del video."
            except Exception as e:
                return f"Error al obtener el enlace del video: {e}"


    def get_video_servers(self, series_name_id, episode_id):
        try:
            with AnimeFLV() as api:
                episode_api = api.get_video_servers(series_name_id, int(episode_id))

                servers = []
                for server in episode_api[0]:
                    video_episode = VideoEpisode(
                        series_name_id=series_name_id,
                        episode_id=episode_id,
                        video_url=server["code"],
                        video_direct=False,
                        server_name=server["title"]
                    )
                    servers.append(video_episode)

                return servers

        except Exception as e:
            print(f"Error occurred: {e}")
            return None