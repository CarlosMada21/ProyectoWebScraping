#Importación de librerías para crear un comando django
from django.core.management.base import BaseCommand
#Importación de librerías selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException, TimeoutException, InvalidArgumentException

#Importación de BeautifulSoup
from bs4 import BeautifulSoup
#Importamos modelo Django para guardar datos
from scraper.models import IndustrialSpace
from django.db import IntegrityError, DataError, DatabaseError

import time

class RealStateScraper:
    def __init__(self, sWebDriver: str, sBinaryLocation: str) -> None:
        self.sUrl = None
        # Ruta completa al ejecutable de ChromeDriver
        self.service = Service(sWebDriver)
        self.chrome_options = None
        self.driver=None
        self.chrome_options = Options()
        self.chrome_options.binary_location = sBinaryLocation
       
    def get_page(self, sUrl: str) -> bool:
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
            
    def get_html(self):
        return self.driver.page_source
    
    def get_cards(self, sSelectors: str):
        elements=[]
        while True:
            elements.extend(self.driver.find_elements(By.CSS_SELECTOR, sSelectors))
            # if self.click_next_button():
            #     print('Exito')
                #elements.extend(self.driver.find_elements(By.CSS_SELECTOR, sSelectors))
            break
            
        return elements
            
    # Función para desplazarse y hacer clic en "Next"
    def click_next_button(self) -> bool:
        try:
            pagination_element = self.driver.find_element(By.CSS_SELECTOR, "div.pagination-row")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", pagination_element)

            # Esperamos a que el botón sea clickable
            wait = WebDriverWait(self.driver, 5)
            element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"a[data-page='2']")))

            # Intentamos hacer click con execute_script para evitar problemas con Selenium directamente
            self.driver.execute_script("arguments[0].click();", element)
            time.sleep(3)
            element=None
        except StaleElementReferenceException as e:
            print(f"Error de referencia obsoleta: {e}. Reintentando...")
            # Si el elemento ya no está en el DOM, intentamos volver a capturarlo
            return False
        except Exception as e:
            print(f"Error inesperado: {e}")
            return False

        return True

    
    def write_file(self, aElements, sFileName: str):
        with open(sFileName, "w", encoding="utf-8") as file:
            for element in aElements:
                div_html = element.get_attribute("outerHTML")  # Obtiene el HTML de cada div
                file.write(div_html + "\n")  # Escribe el HTML en el archivo
            
    def add_options(self, *args: str):

        for arg in args:
            self.chrome_options.add_argument(arg)
    
    def open_driver(self):
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)

    def close_driver(self):
        # Cerrar el navegador
        self.driver.quit()

class HtmlScanner:
    
    
    def __init__(self, sFile: str):
        self.sFile=sFile
    
    def get_attributes(self) -> bool:
    
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
                print(name+' for '+price+' at '+location+'. See more in: '+url)
                
                #self.save_industrial_space_register(sName=name, sLocation=location, sPrice=price, sUrl=url)
                
        else:
            print('Sin elementos')
            return False
        return True

    def save_industrial_space_register(self, sName: str, sLocation: str, sPrice: str, sUrl: str):
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
        sc = RealStateScraper("/usr/local/bin/chromedriver-linux64/chromedriver", "/usr/local/bin/chrome-headless-shell-linux64/chrome-headless-shell")
        
        sc.add_options(
            "--headless", # Sin gui
           # "--disable-gpu",  # Evita que use GPU
            "--no-sandbox", # Necesario en algunos entornos
            #"--disable-dev-shm-usage",  # Evita problemas en algunos sistemas
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
            "--window-size=1920,1080",  # Especifica el tamaño de ventana
        )
        sc.open_driver()
        if sc.get_page("https://www.cbcworldwide.com/search/lease?product_types[]=industrial&country=United+States&market=lease"):
            
            sc.write_file(sc.get_cards("div.sc-wrap.cbc1.pc-onmarket"), "cards.html")
            hs = HtmlScanner("cards.html")
            if hs.get_attributes():
                print('Datos guardados con éxito')
            else:
                print('Error al guardar')
            
        else:
            print("No se pudo acceder a la página")
        sc.close_driver()