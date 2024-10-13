from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import time
import subprocess

from schemas.series_scheme import Series, Episode, SeriesDetails, VideoEpisode


class MundoDonghuaService:
    def __init__(self):
        self.__driver = None


    def __get_browser(self, headless=True):
        if self.__driver is None:
            # Configurar las opciones de Chrome
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument('--headless')  # Ejecutar en modo headless (sin interfaz gráfica)
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-application-cache')
            options.add_argument('--log-level=3')

            # Crear una instancia del controlador de Chrome usando webdriver-manager
            service = Service(ChromeDriverManager().install())
            self.__driver = webdriver.Chrome(service=service, options=options)


    def close(self):
        if self.__driver is not None:
            self.__driver.quit()


    def __get_link_player_tamamo(self, url):
        # Esperar a que la imagen esté disponible y hacer clic en ella
        try:
            self.__get_browser()
            self.__driver.get(url)

            # Esperar hasta que la imagen con ID `tamamoplay` esté presente
            image_element = WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.ID, 'tamamoplay')))

            # Moverse a la imagen y hacer clic para cargar el contenido del iframe
            ActionChains(self.__driver).move_to_element(image_element).click().perform()

            time.sleep(1)  # Ajusta este tiempo según sea necesario para que el contenido se cargue después del clic

            # Esperar hasta que el iframe con ID `tamamo_player` esté visible y tenga el nuevo `src`
            iframe_element = WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.ID, 'tamamo_player')))

            # Obtener el nuevo `src` del iframe después de hacer clic en la imagen
            video_url = iframe_element.get_attribute('src')

            return video_url
        except Exception as e:
            print(f"Error: {e}")
            return None

    def __get_link_player_first(self, url, player):
        # Esperar a que la imagen esté disponible y hacer clic en ella
        try:
            self.__get_browser()
            self.__driver.get(url)

            # Esperar hasta que la imagen con ID `tamamoplay` esté presente
            image_element = WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.ID, f'{player}play')))

            # Moverse a la imagen y hacer clic para cargar el contenido del iframe
            ActionChains(self.__driver).move_to_element(image_element).click().perform()

            time.sleep(1)  # Ajusta este tiempo según sea necesario para que el contenido se cargue después del clic

            # Esperar hasta que el iframe con ID `tamamo_player` esté visible y tenga el nuevo `src`
            iframe_element = WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.ID, f'{player}_player')))

            # Obtener el nuevo `src` del iframe después de hacer clic en la imagen
            video_url = iframe_element.get_attribute('src')

            return video_url
        except Exception as e:
            print(f"Error: {e}")
            return None


    def __get_link_player(self, url, player):
        try:
            self.__get_browser()
            self.__driver.get(url)
            # Cambiar a la pestaña del reproductor correspondiente
            tab_element = WebDriverWait(self.__driver, 10).until(
                EC.element_to_be_clickable((By.ID, f'{player}_tab'))
            )
            ActionChains(self.__driver).move_to_element(tab_element).click().perform()

            # Esperar un momento para asegurarse de que la pestaña se haya activado
            time.sleep(1)

            # Esperar a que la imagen del reproductor esté disponible
            image_element = WebDriverWait(self.__driver, 10).until(
                EC.presence_of_element_located((By.ID, f'{player}play'))
            )

            # Hacer clic en la imagen para cargar el contenido del iframe
            ActionChains(self.__driver).move_to_element(image_element).click().perform()
            time.sleep(1)  # Ajusta este tiempo según sea necesario para que el contenido se cargue

            # Esperar hasta que el iframe correspondiente esté visible y tenga el nuevo `src`
            iframe_element = WebDriverWait(self.__driver, 10).until(
                EC.presence_of_element_located((By.ID, f'{player}_player'))
            )

            # Obtener el nuevo `src` del iframe después de hacer clic en la imagen
            video_url = iframe_element.get_attribute('src')

            return video_url
        except Exception as e:
            print(f"Error: {e}")
            return None


    def get_list_players(self, url):
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')

            # Encontrar la lista de reproductores (elementos <li> dentro de la clase 'nav nav-tabs scrollmenu')
            reproductores = soup.find('ul', class_='nav nav-tabs scrollmenu').find_all('li')

            # Crear una lista para almacenar la información de cada reproductor
            listado_reproductores = []

            for reproductor in reproductores:
                # Obtener el ID y el nombre del reproductor
                reproductor_id = reproductor.get('id').split("_")[0]

                # Almacenar la información en la lista
                listado_reproductores.append(reproductor_id)

            return listado_reproductores
        except Exception as e:
            print(f"Error al obtener la lista de reproductores: {e}")
            return []


    def __get_iframe_src(self, video_url):
        try:
            # Abre la URL del video
            self.__get_browser()
            self.__driver.get(video_url)

            # Espera a que el iframe se cargue
            iframe = WebDriverWait(self.__driver, 10).until(
                EC.presence_of_element_located((By.ID, "player"))
            )

            # Obtiene el atributo src del iframe
            iframe_src = iframe.get_attribute('src')

            if iframe_src:
                return iframe_src.split("?")[0]
            else:
                print("No se encontró el src del iframe.")
                return None
        except Exception as e:
            print(f"Ocurrió un error: {e}")
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


    def get_video_servers(self, series_name_id, episode_id):
        try:
            servers = []
            url = f"https://www.mundodonghua.com/ver/{series_name_id}/{episode_id}"
            players = self.get_list_players(url)
            player = players[0]

            # Obtener el enlace del reproductor
            self.__get_browser()

            if player == "tamamo":
                player_url = self.__get_link_player_tamamo(url)
            else:
                player = players[1]
                player_url = self.__get_link_player(url, player)

            if not player_url:
                print(f"Error: No se pudo obtener el enlace del reproductor {player}.")
                return None

            video_episode = VideoEpisode(
                series_name_id=series_name_id,
                episode_id=episode_id,
                video_url=player_url,
                video_direct=False,
                server_name=player
            )
            servers.append(video_episode)

            # Obtener el enlace directo
            dailymotion_url = self.__get_iframe_src(player_url)
            if dailymotion_url:
                video_url = self.__get_video_url(dailymotion_url)
                if video_url:
                    video_episode_direct = VideoEpisode(
                        series_name_id=series_name_id,
                        episode_id=episode_id,
                        video_url=video_url,
                        video_direct=True,
                        server_name=player
                    )
                    servers.append(video_episode_direct)
            return servers

        except Exception as e:
            print(f"Error inesperado al obtener la URL directa de 'tamamo': {e}")
            return None


    def search_series(self, search_name):
        try:
            # Construct the search URL based on the series name
            search_url = f"https://www.mundodonghua.com/busquedas/{search_name}"

            # Make the GET request to the search URL
            response = requests.get(search_url)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the HTML content of the response
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find all <a> elements that contain the series information
                series_elements = soup.find_all("a", class_="angled-img")

                # List to store the series name, link, and image URL
                series_list = []

                # Iterate through the results and extract the information
                for series in series_elements:
                    # Extract the name of the series
                    name = series.find("h5", class_="sf fc-dark f-bold fs-14").text.strip()

                    # Extract the link to the series
                    name_id = series.get("href").split("/")[-1]

                    # Extract the image URL of the series
                    img_tag = series.find("img")
                    image_url = "https://www.mundodonghua.com" + img_tag.get("src") if img_tag else None

                    # Add the series information to the list
                    series = Series(
                        name = name,
                        name_id = name_id,
                        image_url = image_url
                    )

                    series_list.append(series)

                # Return the list of found series
                return series_list
            else:
                print(f"Request error: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error searching series: {e}")
            return []


    def get_series_details(self, name_id):
        try:
            url = f"https://www.mundodonghua.com/donghua/{name_id}"
            # Make the HTTP request to get the page content
            response = requests.get(url)

            # If the request is successful (status code 200), continue
            if response.status_code == 200:
                # Parse the page content with BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')

                # Get the series name
                name = soup.find('div', class_='sf fc-dark ls-title-serie').text.strip() if soup.find(
                    'div', class_='sf fc-dark ls-title-serie') else "Name not available"

                if name == "":
                    return None

                # Get the series synopsis
                synopsis = soup.find('p', class_='text-justify fc-dark').text.strip() if soup.find(
                    'p', class_='text-justify fc-dark') else "Synopsis not available"

                # Get the series status (e.g., "Ongoing" or "Completed")
                status = soup.find('span', class_='badge bg-success').text.strip() if soup.find(
                    'span', class_='badge bg-success') else "Status not available"

                # Get profile and cover images
                side_banner = soup.find('div', class_='side-banner')
                if side_banner:
                    # Extract profile image URL
                    profile_image = side_banner.find('div', class_='banner-side-serie').get('style', '').split("url(")[
                                        1][
                                    :-1] if side_banner.find(
                        'div', class_='banner-side-serie') else None
                    profile_image_url = f"https://www.mundodonghua.com{profile_image}" if profile_image else "Cover image not available"

                    # Extract cover image URL
                    cover_image = side_banner.find('div', class_='image').get('style', '').split("url('")[1][
                                    :-2] if side_banner.find(
                        'div', class_='image') else None
                    cover_image_url = f"https://www.mundodonghua.com{cover_image}" if cover_image else "Profile image not available"
                else:
                    profile_image_url = "Profile image not available"
                    cover_image_url = "Cover image not available"

                # Get the list of episodes and their links
                episodes = []
                episodes_list = soup.find('ul', class_='donghua-list')

                if episodes_list:
                    for episode in episodes_list.find_all('a', href=True):
                        title = episode.find('blockquote', class_='message sf fc-dark f-bold fs-16').text.strip()
                        episode_id = episode['href'].split("/")[-1]

                        episode = Episode(
                            title = title,
                            series_name_id = name_id,
                            episode_id = episode_id
                        )

                        episodes.append(episode)

                last_episode = episodes[0].episode_id

                # Return the details in a dictionary
                series_details = SeriesDetails(
                    name = name,
                    name_id = name_id,
                    synopsis = synopsis,
                    status = status,
                    profile_image_url = profile_image_url,
                    cover_image_url = cover_image_url,
                    last_episode = last_episode,
                    episodes = episodes
                )

                return series_details

            else:
                print(f"Failed to access the page, status code: {response.status_code}")
                return None

        except Exception as e:
            print(f"Error retrieving series details: {e}")
            return None

