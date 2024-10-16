# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
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
        # Bucle para ir navegando entre páginas
        while True:
            
            try:
                elements=self.driver.find_elements(By.CSS_SELECTOR, sSelectors)
                # for element in elements:
                #     div_html = element.get_attribute("outerHTML")  # Obtiene el HTML de cada div
                #     print(div_html + "\n") 
                # Encuentra el enlace "Next"
                next_button = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@aria-label="Next"]'))
                )

                # Desplázate hasta el enlace para asegurarte de que es visible
                self.driver.execute_script("arguments[0].scrollIntoView();", next_button)

                # Haz clic en el enlace "Next"
                next_button.click()
                print('Hola ')
                # Espera un momento para que la página cargue el nuevo lote de resultados
                WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'cbc1__content'))
                )
            
            except (NoSuchElementException, ElementClickInterceptedException) as e:
                # Si no se encuentra el botón "Next", significa que no hay más páginas o el clic fue bloqueado
                print(f"No hay más páginas para navegar {e}")
                break  # Sal del bucle cuando ya no haya más páginas
            
        # with open('cards.html', "w", encoding="utf-8") as file:
        # #file.write("<html><body>\n")  # Inicia el archivo HTML
        #     for element in elements:
        #         div_html = element.get_attribute("outerHTML")  # Obtiene el HTML de cada div
        #         file.write(div_html + "\n")
                
        return elements
    
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

            # Crea y guarda el registro
            espacio = IndustrialSpace(name=name, location=location, price=price, url=url)
            espacio.save()

        print("Datos guardados.")

        
if __name__ == '__main__':
    # Objeto scrapper, como argumentos las paths de los ejecutables
    sc = RealStateScraper("/usr/local/bin/chromedriver-linux64/chromedriver", "/usr/local/bin/chrome-headless-shell-linux64/chrome-headless-shell")
    
    sc.add_options(
        "--headless", # Sin gui
        "--disable-gpu",  # Evita que use GPU
        "--no-sandbox", # Necesario en algunos entornos
        "--disable-dev-shm-usage",  # Evita problemas en algunos sistemas
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