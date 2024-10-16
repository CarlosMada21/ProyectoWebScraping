# Importación de librerías para crear un comando Django
from django.core.management.base import BaseCommand

# Importación de librerías de Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    TimeoutException,
    StaleElementReferenceException,
    WebDriverException,
    InvalidArgumentException,
)

# Importación de BeautifulSoup
from bs4 import BeautifulSoup

# Importamos modelo Django para guardar datos
from scraper.models import IndustrialSpace
from django.db import IntegrityError, DataError, DatabaseError

import time


class RealStateScraper:
    """Clase para realizar scraping de propiedades inmobiliarias."""

    def __init__(self, sWebDriver: str, sBinaryLocation: str) -> None:
        """
        Inicializa el scraper con la ubicación del WebDriver y el ejecutable de Chrome.

        Args:
            sWebDriver (str): Ruta al ejecutable de ChromeDriver.
            sBinaryLocation (str): Ruta al ejecutable de Chrome.
        """
        self.sUrl = None
        self.service = Service(sWebDriver)  # Ruta completa al ejecutable de ChromeDriver
        self.chrome_options = Options()
        self.chrome_options.binary_location = sBinaryLocation
        self.driver = None

    def get_page(self, sUrl: str) -> bool:
        """
        Intenta acceder a la URL proporcionada.

        Args:
            sUrl (str): URL a cargar.

        Returns:
            bool: True si la página se carga exitosamente, False en caso contrario.
        """
        try:
            self.driver.get(sUrl)
            return True
        except InvalidArgumentException:
            print("Error: La URL proporcionada no es válida.")
            return False
        except TimeoutException:
            print("Error: La carga de la página ha tardado demasiado tiempo.")
            return False
        except WebDriverException as e:
            print(f"Error al intentar abrir la URL: {e}")
            return False

    def get_html(self) -> str:
        """Devuelve el HTML de la página actual."""
        return self.driver.page_source

    def get_cards(self, sSelectors: str) -> list:
        """
        Obtiene todos los elementos que coinciden con el selector CSS proporcionado.

        Args:
            sSelectors (str): Selector CSS para encontrar los elementos.

        Returns:
            list: Lista de elementos encontrados.
        """
        elements = []
        while True:
            elements.extend(self.driver.find_elements(By.CSS_SELECTOR, sSelectors))
            i = 2
            try:
                if self.click_next_button(i):
                    print('Éxito cambiando de página')
                    elements.extend(self.driver.find_elements(By.CSS_SELECTOR, sSelectors))
                    i += 1
                else:
                    break
            except Exception:
                print('Error con el paginador')
                
        return elements

    def click_next_button(self, i: int) -> bool:
        """
        Intenta hacer clic en el botón "Next" para cargar la siguiente página de resultados.

        Args:
            i (int): Número de página para intentar hacer clic.

        Returns:
            bool: True si se hizo clic exitosamente, False en caso contrario.
        """
        try:

            pagination_links = WebDriverWait(self.driver, 3).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "pagination-link"))
            )

            # Encuentra el enlace de la página correspondiente
            for link in pagination_links:
                if link.text == str(i):
                    # Desplaza la vista hasta el enlace
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
                    WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(link))  # Asegúrate de que es clickeable
                    link.click()  # Hacer clic en el enlace
                    return True  # Retorna True al hacer clic
        except StaleElementReferenceException as e:
            print(f"Error de referencia obsoleta: {e}. Reintentando...")
            return False
        except Exception as e:
            print(f"Error inesperado al hacer clic, no se pudo cambiar la página")
            return False

        return False  # Retorna False si no se pudo hacer clic


    def write_file(self, aElements: list, sFileName: str) -> None:
        """
        Escribe el HTML de los elementos en un archivo.

        Args:
            aElements (list): Lista de elementos cuyos HTML se van a guardar.
            sFileName (str): Nombre del archivo donde se guardarán los datos.
        """
        with open(sFileName, "w", encoding="utf-8") as file:
            for element in aElements:
                div_html = element.get_attribute("outerHTML")  # Obtiene el HTML de cada div
                file.write(div_html + "\n")  # Escribe el HTML en el archivo

    def add_options(self, *args: str) -> None:
        """
        Agrega opciones de configuración al WebDriver.

        Args:
            *args (str): Opciones a agregar.
        """
        for arg in args:
            self.chrome_options.add_argument(arg)

    def open_driver(self) -> None:
        """Abre el driver de Chrome."""
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)

    def close_driver(self) -> None:
        """Cierra el navegador."""
        self.driver.quit()


class HtmlScanner:
    """Clase para analizar archivos HTML y extraer atributos específicos."""

    def __init__(self, sFile: str) -> None:
        """
        Inicializa el escáner HTML con la ruta del archivo.

        Args:
            sFile (str): Ruta al archivo HTML a analizar.
        """
        self.sFile = sFile

    def get_attributes(self) -> bool:
        """
        Extrae atributos de tarjetas del archivo HTML.

        Returns:
            bool: True si se encontraron tarjetas, False en caso contrario.
        """
        # Abre el archivo HTML
        with open(self.sFile, 'r', encoding='utf-8') as file:
            contenido_html = file.read()
        try:
            # Analiza el HTML con BeautifulSoup
            soup = BeautifulSoup(contenido_html, 'html.parser')
        except Exception as e:
            print(f"Error al parsear el HTML: {e}")
            return False

        # Encuentra todas las tarjetas
        cards = soup.find_all('div', class_='sc-wrap')
        if cards:
            # Recorre cada tarjeta
            for card in cards:
                name_tag = card.find('h3', class_='cbc1__price cbc1__price-2')
                name = name_tag.get_text(strip=True) if name_tag else None

                price_tag = card.find('div', class_='cbc1__address cbc1__address-2')
                price = price_tag.get_text(strip=True) if price_tag else None

                location_tag = card.find('div', class_='cbc1__address cbc1__address-3')
                location = location_tag.get_text(strip=True) if location_tag else None

                link_tag = card.find('a', class_='cbc1__link')
                url = link_tag['href'] if link_tag and 'href' in link_tag.attrs else None  # Deja en blanco si no hay URL
                print(name + ' for ' + price + ' at ' + location + '. See more in: ' + url)

                # self.save_industrial_space_register(sName=name, sLocation=location, sPrice=price, sUrl=url)

        else:
            print('Sin elementos')
            return False
        return True

    def save_industrial_space_register(self, sName: str, sLocation: str, sPrice: str, sUrl: str) -> None:
        """
        Guarda un registro de espacio industrial en la base de datos.

        Args:
            sName (str): Nombre del espacio.
            sLocation (str): Ubicación del espacio.
            sPrice (str): Precio del espacio.
            sUrl (str): URL del espacio.

        Captura excepciones relacionadas con la base de datos.
        """
        try:
            space = IndustrialSpace(name=sName, location=sLocation, price=sPrice, url=sUrl)
            space.save()  # Intenta guardar el registro
        except IntegrityError as e:
            print(f"Error de integridad: {e}")
        except DataError as e:
            print(f"Error de datos: {e}")
        except DatabaseError as e:
            print(f"Error de base de datos: {e}")
        except Exception as e:  # Captura cualquier otro tipo de excepción
            print(f"Ocurrió un error inesperado: {e}")

class Command(BaseCommand):
    help = 'Run the web scraper'

    def handle(self, *args, **kwargs):
        # Objeto scrapper, como argumentos las paths de los ejecutables
        sc = RealStateScraper(
            "/usr/local/bin/chromedriver-linux64/chromedriver", "/usr/local/bin/chrome-headless-shell-linux64/chrome-headless-shell"
        )
        
        sc.add_options(
            "--headless", # Sin gui
            "--no-sandbox", # Necesario en algunos entornos
            # Cambiamos el user-agent si no nos bloquea la conexión
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
        )
        
        sc.open_driver()
        if sc.get_page("https://www.cbcworldwide.com/search/lease?product_types[]=industrial&country=United+States&market=lease"):
            cards=sc.get_cards("div.sc-wrap.cbc1.pc-onmarket")
            if cards is None:
                print('Error al cambiar de páginas')
            else:
                sc.write_file(cards, "cards.html")
                hs = HtmlScanner("cards.html")
                if hs.get_attributes():
                    print('Datos guardados con éxito')
                else:
                    print('Error al guardar')
                
        else:
            print("No se pudo acceder a la página")
        
        sc.close_driver()