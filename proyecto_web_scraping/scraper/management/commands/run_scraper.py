from django.core.management.base import BaseCommand

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

from bs4 import BeautifulSoup
from scraper.models import IndustrialSpace
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
        self.divs = []

    def get_page(self, sUrl: str):
        self.driver.get(sUrl)
    
    def get_html(self):
        return self.driver.page_source
    
    def get_cards(self, sSelectors: str):
        elements=[]
        
        elements.extend(self.driver.find_elements(By.CSS_SELECTOR, sSelectors))
        url = f"https://www.cbcworldwide.com/search/lease?product_types[]=industrial&market=lease&page=2"
        self.driver.get(url)
        time.sleep(3)
        elements.extend(self.driver.find_elements(By.CSS_SELECTOR, sSelectors))

        return elements
            
    # Función para desplazarse y hacer clic en "Next"
    def click_next_button(self):
        try:
            # # Encuentra el elemento del div que tiene el scroll
            # scrollable_div = self.driver.find_element(By.CLASS_NAME, "full-height-scroll")

            # # Usa JavaScript para desplazar el scroll hasta el final del div
            # self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)

            # # Espera hasta que el elemento UL esté presente
            # pagination_ul = WebDriverWait(self.driver, 10).until(
            #     EC.presence_of_element_located((By.CLASS_NAME, "pagination"))
            # )

            # # Encuentra todos los <li> dentro del <ul> de paginación
            # li_elements = pagination_ul.find_elements(By.TAG_NAME, "li")

            # # Accede al último <li> (que debería ser el botón "Next")
            # last_li = li_elements[-1]  # último índice

            # # Encuentra el <a> dentro del último <li>
            # next_button = last_li.find_element(By.TAG_NAME, "a")

            # # Haz clic en el botón "Next"
            # next_button.click()
            # print('Click')
            #wait = WebDriverWait(self.driver, 10)
            time.sleep(2)
            # pagination_link = self.driver.find_element(By.CSS_SELECTOR, 'a.pagination-link[data-page="2"]')
            # self.driver.execute_script("arguments[0].click();", pagination_link)

            # Espera hasta que el contenido se actualice, por ejemplo, buscando un elemento de la nueva página
            #wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'elemento_nuevo_selector')))

        except (TimeoutException, StaleElementReferenceException):
            print("No se pudo encontrar el botón 'Next'. Tal vez ya no hay más páginas o el elemento está obsoleto.")
            return False

        except ElementClickInterceptedException:
            print("El clic en el botón 'Next' fue interceptado. Posiblemente no es visible.")
            return False

        return True

    
    def write_file(self, aElements, sFileName: str):
        with open(sFileName, "w", encoding="utf-8") as file:
            #file.write("<html><body>\n")  # Inicia el archivo HTML
            for element in aElements:
                div_html = element.get_attribute("outerHTML")  # Obtiene el HTML de cada div
                file.write(div_html + "\n")  # Escribe el HTML en el archivo
            #file.write("</body></html>\n")  # Cierra el archivo HTML
            #file.write(self.driver.page_source) 
            
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
    
    def get_attributes(self):
    
        # Abre el archivo HTML
        with open(self.sFile, 'r', encoding='utf-8') as file:
            contenido_html = file.read()

        # Analiza el HTML con BeautifulSoup
        soup = BeautifulSoup(contenido_html, 'html.parser')

        # Encuentra todas las tarjetas
        tarjetas = soup.find_all('div', class_='sc-wrap')

        # Recorre cada tarjeta
        for tarjeta in tarjetas:
            name_tag = tarjeta.find('h3', class_='cbc1__price cbc1__price-2')
            name = name_tag.get_text(strip=True) if name_tag else 'N/A'
            
            price_tag = tarjeta.find('div', class_='cbc1__address cbc1__address-2')
            price = price_tag.get_text(strip=True) if price_tag else 'N/A'
            
            location_tag = tarjeta.find('div', class_='cbc1__address cbc1__address-3')
            location = location_tag.get_text(strip=True) if location_tag else 'N/A'
            
            link_tag = tarjeta.find('a', class_='cbc1__link')
            url = link_tag['href'] if link_tag and 'href' in link_tag.attrs else None  # Deja en blanco si no hay URL
            print(name+' for '+price+' at '+location+'. See more in: '+url)
            # Crea y guarda el registro
            # espacio = IndustrialSpace(name=name, location=location, price=price, url=url)
            # espacio.save()

        print("Datos guardados.")

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

            #"--window-size=1920,1080",  # Especifica el tamaño de ventana
        )
        sc.open_driver()
        sc.get_page("https://www.cbcworldwide.com/search/lease?product_types[]=industrial&country=United+States&market=lease")
        #sc.get_cards("div.cbc1__content.cbc1__content-2")
        #sc.write_file(sc.get_cards("div.cbc1__content.cbc1__content-2"), "cards.html")
        sc.write_file(sc.get_cards("div.sc-wrap.cbc1.pc-onmarket"), "cards.html")
        #class="div.sc-wrap.cbc1.pc-onmarket"
        hs = HtmlScanner("cards.html")
        hs.get_attributes()
        sc.close_driver()
