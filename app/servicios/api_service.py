import requests, time, re, json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
#from selenium.webdriver.chrome.options import Options

class ApiService:
    def __init__(self, api_base_url_combo_city, api_key, api_type, api_base_url_weather, api_key_weather, api_type_weather):
        self.api_base_url_combo_city = api_base_url_combo_city
        self.api_key = api_key
        self.api_type = api_type
        self.api_base_url_weather = api_base_url_weather
        self.api_key_weather = api_key_weather
        self.api_type_weather = api_type_weather

    def buscar_coord_ciudad(self, city):
        url = f"{self.api_base_url_combo_city}{city}{self.api_type}&apiKey={self.api_key}"
        response = requests.get(url)
        return response.json()

    def clima(self, coordinates):
        url = f"{self.api_base_url_weather}key={self.api_key_weather}&q={coordinates}{self.api_type_weather}"
        response = requests.get(url)
        return response.json()

    # def scrape(self, cat, latitud_origen, longitud_origen, radio, cant_busquedas):
    #     # Ruta de ChromeDriver
    #     self.driver = webdriver.Chrome(service=Service(
    #         "C:\\Users\\Mariano\\PycharmProjects\\tesis3.0\\chromedriver-win64\\chromedriver.exe"))
    #     consultar_url = "https://www.google.es/maps/search/" + cat.replace(" ", "+") + "/@{0},{1},19z".format(
    #         latitud_origen, longitud_origen)
    #     data = {'Coordinates': []}
    #     self.driver.get(consultar_url)
    #     time.sleep(2)
    #     i = 0
    #     encontrados = 0
    #     while encontrados < cant_busquedas:
    #         try:
    #             self.scroll_the_page(i)
    #             place = self.driver.find_elements(By.CLASS_NAME, "Nv2PK")[i]
    #             place.click()
    #             time.sleep(3)
    #             coords = self.get_geocoder(self.driver.current_url)
    #             if self.consulta_distancia(latitud_origen, longitud_origen, coords[0], coords[1],
    #                                        radio):  # coords[0] = latitud origen y coords[1] = longitud origen
    #                 name = self.get_name()
    #                 address = self.get_address()
    #                 phone_number = self.get_phone()
    #                 website = self.get_website()
    #                 # email = ""
    #                 # if website != "":
    #                 #    email = self.get_email('http://'+website)
    #                 data['Coordinates'].append({'name':name, 'address':address, 'phone_number':phone_number, 'lat': coords[0], 'lon': coords[1], 'website':website})
    #                 # time.sleep(2)
    #                 encontrados += 1
    #             # else:
    #             # print("No se carga ubicacion por estar lejos")
    #             i += 1
    #         except Exception:
    #             i -= 1

    #     self.driver.quit()
    #     return data


    # def scroll_the_page(self, i):
    #     try:
    #         section_loading = self.driver.find_elements(By.CLASS_NAME, "Nv2PK")
    #         while True:
    #             if i >= len(self.driver.find_elements(By.CLASS_NAME, "Nv2PK")):
    #                 self.driver.execute_script("arguments[0].scrollIntoView(true);", section_loading[i - 1])
    #                 time.sleep(2)
    #             else:
    #                 break
    #     except:
    #         pass

    # @staticmethod
    # def get_geocoder(url_location):  # gets geographical lat/long coordinates
    #     try:
    #         coords = re.search(r"!3d-?\d\d?\.\d{4,8}!4d-?\d\d?\.\d{4,8}", url_location).group()
    #         lat_destino = coords.split('!3d')[1]

    #         return tuple(lat_destino.split('!4d'))
    #     except (TypeError, AttributeError):
    #         return "", ""

    # def get_name(self):
    #     try:
    #         if len(self.driver.find_element(By.XPATH, "//h1[contains(@class,'DUwDvf')]").text) == 0:
    #             raise ValueError("Campo nombre esta vacío")
    #         else:
    #             return self.driver.find_element(By.XPATH, "//h1[contains(@class,'DUwDvf')]").text
    #     except ValueError as e:
    #         print("Error nombre vacio: ", e)
    #         return ""

    # def get_address(self):
    #     try:
    #         if len(self.driver.find_element(By.CSS_SELECTOR, "[data-item-id='address']").text) == 0:
    #             raise ValueError("Campo direccion vacio")
    #         else:
    #             text = self.driver.find_element(By.CSS_SELECTOR, "[data-item-id='address']").text
    #             eliminar_caracteres_especiales = re.sub(r'[^\x00-\x7F]+', '', text)
    #             return eliminar_caracteres_especiales.replace('\n', '')
    #     except (ValueError, NoSuchElementException):
    #         # print("Error direccion vacia: ", e)
    #         return ""

    # def get_phone(self):
    #     try:
    #         if len(self.driver.find_element(By.CSS_SELECTOR,
    #                                         "[data-tooltip='Copiar el número de teléfono']").text) == 0:
    #             raise ValueError("Campo telefono vacio")
    #         else:
    #             text = self.driver.find_element(By.CSS_SELECTOR, "[data-tooltip='Copiar el número de teléfono']").text
    #             eliminar_caracteres_especiales = re.sub(r'[^\x00-\x7F]+', '', text)
    #             return eliminar_caracteres_especiales.replace('\n', '')
    #     except (ValueError, NoSuchElementException):
    #         # print("Error telefono vacio: ", e)
    #         return ""

    # def get_website(self):
    #     try:
    #         if len(self.driver.find_element(By.CSS_SELECTOR, "[data-item-id='authority']").text) == 0:
    #             raise ValueError("Campo sitio web vacio")
    #         else:
    #             text = self.driver.find_element(By.CSS_SELECTOR, "[data-item-id='authority']").text
    #             eliminar_caracteres_especiales = re.sub(r'[^\x00-\x7F]+', '', text)
    #             return eliminar_caracteres_especiales.replace('\n', '')
    #     except (ValueError, NoSuchElementException):
    #         # print("Error sitio web vacio: ", e)
    #         return ""
    
    # @staticmethod
    # def consulta_distancia(lat_origen, long_origen, lat_destino, long_destino, radio):
    #     coord = str(lat_origen) + "," + str(long_origen) + "|" + lat_destino + "," + long_destino
    #     solicitud = requests.get(
    #         "https://api.geoapify.com/v1/routing?waypoints=" + coord + "&mode=walk&apiKey=3ea460fd6ee1440ba1999a9c39c0cebe")
    #     datos_distancia = json.loads(solicitud.text)
    #     distancia = datos_distancia['features'][0]['properties']['distance']
    #     if distancia < int(radio):
    #         return True
    #     else:
    #         return False