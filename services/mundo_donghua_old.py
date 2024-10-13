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


# Configurar las opciones de Chrome
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Ejecutar en modo headless (sin interfaz gráfica)
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-extensions')
options.add_argument('--disable-application-cache')
options.add_argument('--log-level=3')  # Suprime la mayoría de los logs del navegador

# Crear una instancia del controlador de Chrome usando webdriver-manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)


def get_link_player_tamamo(url):
    # Esperar a que la imagen esté disponible y hacer clic en ella
    try:
        driver.get(url)

        # Esperar hasta que la imagen con ID `tamamoplay` esté presente
        image_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'tamamoplay')))

        # Moverse a la imagen y hacer clic para cargar el contenido del iframe
        ActionChains(driver).move_to_element(image_element).click().perform()
        time.sleep(1)  # Ajusta este tiempo según sea necesario para que el contenido se cargue después del clic

        # Esperar hasta que el iframe con ID `tamamo_player` esté visible y tenga el nuevo `src`
        iframe_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'tamamo_player')))

        # Obtener el nuevo `src` del iframe después de hacer clic en la imagen
        video_url = iframe_element.get_attribute('src')

        return video_url
    except Exception as e:
        return None
    finally:
        # Cierra el navegador
        driver.quit()


def get_link_player(url, player):
    try:
        driver.get(url)

        # Cambiar a la pestaña del reproductor correspondiente
        tab_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, f'{player}_tab')))
        ActionChains(driver).move_to_element(tab_element).click().perform()

        # Esperar un momento para asegurarse de que la pestaña se haya activado
        time.sleep(1)

        # Esperar a que la imagen del reproductor esté disponible
        image_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, f'{player}play')))

        # Hacer clic en la imagen para cargar el contenido del iframe
        ActionChains(driver).move_to_element(image_element).click().perform()
        time.sleep(1)  # Ajusta este tiempo según sea necesario para que el contenido se cargue

        # Esperar hasta que el iframe correspondiente esté visible y tenga el nuevo `src`
        iframe_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, f'{player}_player')))

        # Obtener el nuevo `src` del iframe después de hacer clic en la imagen
        video_url = iframe_element.get_attribute('src')

        return video_url
    except Exception as e:
        print(f"Error: {e}")  # Imprimir error para depuración
        return None
    finally:
        # Cierra el navegador
        driver.quit()



def get_list_players(url):
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


def get_iframe_src(video_url):
    try:
        # Abre la URL del video
        driver.get(video_url)

        # Espera a que el iframe se cargue
        iframe = WebDriverWait(driver, 10).until(
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
    finally:
        # Cierra el navegador
        driver.quit()


def get_direct_url(url):
    # Ejecutar youtube-dl para obtener el enlace directo
    result = subprocess.run(['youtube-dl', '-g', url], capture_output=True, text=True)
    direct_url = result.stdout.strip()  # URL directa del video

    return direct_url


def buscar_series(nombre_serie):
    # Construye la URL de búsqueda basada en el nombre de la serie
    url_busqueda = f"https://www.mundodonghua.com/busquedas/{nombre_serie}"

    # Realiza la solicitud GET a la URL de búsqueda
    response = requests.get(url_busqueda)

    # Verifica si la solicitud fue exitosa
    if response.status_code == 200:
        # Analiza el contenido HTML de la respuesta
        soup = BeautifulSoup(response.text, 'html.parser')

        # Encuentra todos los elementos <a> que contienen las series
        series = soup.find_all("a", class_="angled-img")

        # Lista para almacenar el nombre, enlace y URL de la imagen de las series
        lista_series = []

        # Itera a través de los resultados y extrae la información
        for serie in series:
            # Extrae el nombre de la serie
            nombre = serie.find("h5", class_="sf fc-dark f-bold fs-14").text.strip()

            # Extrae el enlace de la serie
            enlace = "https://www.mundodonghua.com" + serie.get("href")

            # Extrae la URL de la imagen de la serie
            img_tag = serie.find("img")
            imagen_url = "https://www.mundodonghua.com" + img_tag.get("src") if img_tag else None

            # Agrega la información de la serie a la lista
            lista_series.append({
                "nombre": nombre,
                "enlace": enlace,
                "imagen": imagen_url
            })

        # Retorna la lista de series encontradas
        return lista_series
    else:
        print(f"Error en la solicitud: {response.status_code}")
        return []


def obtener_detalles_serie(url):
    # Realizar la solicitud HTTP para obtener el contenido de la página
    response = requests.get(url)

    # Si la solicitud es exitosa (código 200), continuamos
    if response.status_code == 200:
        # Parsear el contenido de la página con BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Obtener el nombre de la serie
        nombre_serie = soup.find('div', class_='sf fc-dark ls-title-serie').text.strip() if soup.find('div',
                                                                                                      class_='sf fc-dark ls-title-serie') else "Nombre no disponible"

        # Obtener la sinopsis de la serie
        sinopsis = soup.find('p', class_='text-justify fc-dark').text.strip() if soup.find('p',
                                                                                           class_='text-justify fc-dark') else "Sinopsis no disponible"

        # Obtener la lista de episodios y sus enlaces
        episodios = []
        # Buscar todos los enlaces dentro de la lista con la clase `donghua-list`
        episodios_lista = soup.find('ul', class_='donghua-list')

        if episodios_lista:
            for episodio in episodios_lista.find_all('a', href=True):
                # Título del episodio dentro del bloque <blockquote>
                titulo = episodio.find('blockquote', class_='message sf fc-dark f-bold fs-16').text.strip()
                # Enlace del episodio
                link = episodio['href']
                # Agregar episodio a la lista
                episodios.append({'titulo': titulo, 'link': f"https://www.mundodonghua.com{link}"})

        # Retornar los detalles en un diccionario
        detalles_serie = {
            'nombre': nombre_serie,
            'sinopsis': sinopsis,
            'episodios': episodios
        }
        return detalles_serie
    else:
        return {'error': f"No se pudo acceder a la página, código de estado: {response.status_code}"}