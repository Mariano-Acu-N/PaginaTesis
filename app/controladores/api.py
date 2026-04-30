from flask import Blueprint, request, jsonify
from app.servicios.api_service import ApiService
from app.config import Config
import folium
import math
from shapely.geometry import Point, Polygon


class ApiController:
    def __init__(self):
        self.api_bp = Blueprint('api', __name__)
        self.register_routes()
        self.b = 0
        self.seed = 0

    def register_routes(self):
        self.api_bp.route('/checkboxTempHum', methods=['POST'])(self.checkboxTempHum)
        self.api_bp.route('/noncheckboxTempHum', methods=['POST'])(self.noncheckboxTempHum)
        self.api_bp.route('/simularContextoGeografico', methods=['POST'])(self.simularContextoGeografico)
        self.api_bp.route('/simularContextoTemporal', methods=['POST'])(self.simularContextoTemporal)
        self.api_bp.route('/api', methods=['POST'])(self.api)
        self.api_bp.route('/apiUbicaciones', methods=['GET'])(self.apiUbicaciones)

############################# --- CONTEXTO TEMPORAL --- #############################
    def simularContextoTemporal(self):
        data = {'tiempo': []}
        info = request.get_json()
        i = 0
        #Tiempo libre o disponible
        # menor a 15 min, entre 15 a 30 min, entre 30 a 50 min y mas de 1hr
        #while i < len(info.get('filas')) - 1:
        # hrdesde, mdesde = map(int,info.get('hrdesde').split(":"))
        # hrhasta, mhasta = map(int,info.get('hrhasta').split(":"))
        try:
            hrdesde, mdesde = self.procesar_hora(info.get('hrdesde'))
            hrhasta, mhasta = self.procesar_hora(info.get('hrhasta'))
            total_min_desde = hrdesde * 60 + mdesde
            total_min_hasta = hrhasta * 60 + mhasta
            total_min_nuevo = self.uniforme(total_min_desde, total_min_hasta)
            hrnueva = int((total_min_nuevo // 60) % 24)
            minnuevos = int(total_min_nuevo % 60)
            data['tiempo'].append({'hr_del_dia': f"{hrnueva}:{minnuevos}", 'unidad_medida_hr_del_dia': '24hr'})
        except Exception as e:
            print(f"Error procesando formato de hora: {e}")
        if info.get('b') == 0:
            #Hora del día
            # hrdesde, mdesde = map(int,info.get('hrdesde').split(":"))
            # hrhasta, mhasta = map(int,info.get('hrhasta').split(":"))
            # total_min_desde = hrdesde * 60 + mdesde
            # total_min_hasta = hrhasta * 60 + mhasta
            # total_min_nuevo = self.uniforme(total_min_desde, total_min_hasta)
            # hrnueva = int((total_min_nuevo // 60) % 24)
            # minnuevos = int(total_min_nuevo % 60)
            # data['tiempo'].append({'hr_del_dia': f"{hrnueva}:{minnuevos}", 'unidad_medida_hr_del_dia': '24hr'})
            while i < info.get('cantTLibre'):
                tiempo_libre = self.transInvFunDiscSinProb() #minutos
                data['tiempo'].append({'tiempo_libre': tiempo_libre})
                i+=1
            data['tiempo'].append({'unidad_medida_tiempo_libre': 'minutos'})
        else:
            #Hora del día
            #hrdesde, mdesde = map(int,info.get('hrdesde').split(":"))
            #hrhasta, mhasta = map(int,info.get('hrhasta').split(":"))
            # total_min_desde = 0 # La hora 00:00
            # total_min_hasta = 23 * 60 + 59 #La hora 23:59
            # total_min_nuevo = self.uniforme(total_min_desde, total_min_hasta)
            # hrnueva = int((total_min_nuevo // 60) % 24)
            # minnuevos = int(total_min_nuevo % 60)
            # data['tiempo'].append({'hr_del_dia': f"{hrnueva}:{minnuevos}", 'unidad_medida_hr_del_dia': '24hr'})
            while i < info.get('cantTLibre'):
                tiempo_libre = self.transInvFunDiscConProb(info.get('p1'),info.get('p2'),info.get('p3')) #minutos
                data['tiempo'].append({'tiempo_libre': tiempo_libre})
                i+=1
            data['tiempo'].append({'unidad_medida_tiempo_libre': 'minutos'})
        return jsonify(data['tiempo'])

    def procesar_hora(self, hora_str):
    # Verificamos si la cadena contiene los dos puntos
        if ":" in hora_str:
            hr, m = map(int, hora_str.split(":"))
        else:
            # Si no hay ":", asumimos que son solo horas y ponemos 0 minutos
            hr = int(hora_str)
            m = 0
        return hr, m


############################# --- CONTEXTO AMBIENTAL --- #############################

    def checkboxTempHum(self):
        info = request.get_json()
        temp = self.uniforme(info.get('tempmin'), info.get('tempmax'))
        hum = self.normal(info.get('humDeseada'), info.get('humFluctuacion')) # No aplico la multiplicacion por 0.1 porque ya debería conocer la desviación estandar, diferente el caso de que cuando la obtengo de la API
        if hum > 100:
            hum = 100
        elif hum < 0:
            hum = 0
        data = [{'temp': int(temp), 'unidad_medida_temp': 'grados', 'hum': int(hum), 'unidad_medida_hum': 'porcentaje'}]
        return jsonify(data)

    def noncheckboxTempHum(self):
        apiser = ApiService(Config.api_base_url_combo_city, Config.api_key, Config.api_type,
                            Config.api_base_url_weather, Config.api_key_weather, Config.api_type_weather)
        info = request.get_json()
        if info.get('ciudad'):
            pronostico = apiser.clima(info.get('ciudad'))
        else:
            latlon = info.get('lat') + ", " + info.get('lng')
            pronostico = apiser.clima(latlon)
        temp = self.uniforme(pronostico['forecast']['forecastday'][0]['day']['mintemp_c'], pronostico['forecast']['forecastday'][0]['day']['maxtemp_c'])
        desviacion_estandar = pronostico['forecast']['forecastday'][0]['day']['avghumidity'] * 0.1 # se multiplica por 0.1 (10%) = 5% de desviacion propuesta por el fabricante + 5% para abarcar posibles ruidos provenientes del ambiente
        hum = self.normal(pronostico['forecast']['forecastday'][0]['day']['avghumidity'], desviacion_estandar)
        if hum > 100:
            hum = 100
        elif hum < 0:
            hum = 0
        data = [{'temp': int(temp), 'unidad_medida_temp': 'grados', 'hum': int(hum), 'unidad_medida_hum': 'porcentaje'}]
        return jsonify(data)    

############################# --- CONTEXTO GEOGRAFICO --- #############################

    def simularContextoGeografico(self):
        data = {'puntos': []}
        etiqueta_nombre = 1
        encontrados = 0
        lim_inf = 0
        lim_sup = 2 * math.pi
        info = request.get_json()
        # (Longitud, Latitud) -> (x, y), el primer y ultimo punto deben ser iguales para cerrar el poligono
        # Coordenas del poligono para abarcar la UNSE
        coords_area = [(-64.25139019422534, -27.802016156660176),
                   (-64.24979830318135, -27.801239131635974),
                   (-64.2506405168068, -27.80078359070808),
                   (-64.25107771687492, -27.80023314287963),
                   (-64.25148675374945, -27.80046565997414),
                   (-64.2510911279212, -27.800924761144014),
                   (-64.25099859171084, -27.800962722915106),
                   (-64.25169596605048, -27.801462156179742),
                   (-64.25139019422534, -27.802016156660176)]
        poligono = Polygon(coords_area)
        apiser = ApiService(Config.api_base_url_combo_city, Config.api_key, Config.api_type,
                            Config.api_base_url_weather, Config.api_key_weather, Config.api_type_weather)
        if (info.get('city')):            
            citydata = apiser.buscar_coord_ciudad(info.get('city'))
            lat = citydata['results'][0]['lat']
            lon = citydata['results'][0]['lon']
        elif (info.get('cp')):
            cpdata = apiser.buscar_coord_ciudad(info.get('cp'))
            lat = cpdata['results'][0]['lat']
            lon = cpdata['results'][0]['lon']
        else:
            lat = float(info.get('lat'))
            lon = float(info.get('lon'))
        radio = info.get('radio')
        while encontrados < info.get('cant'):
            posX, posY = self.uniformPosGeograficas(lim_inf, lim_sup, lat, lon, radio)
            punto = Point(posY, posX)
            esta_dentro = poligono.contains(punto)
            if (esta_dentro):
                data['puntos'].append({'nombre': f'Ubicacion {etiqueta_nombre}', 'lat': posX, 'lon': posY, 'en_UNSE': 'Si'})
            else:
                data['puntos'].append({'nombre': f'Ubicacion {etiqueta_nombre}', 'lat': posX, 'lon': posY, 'en_UNSE': 'No'})
            etiqueta_nombre += 1
            encontrados += 1
        self.generate_map(lat, lon, radio, data['puntos'])
        data['puntos'].append({'unidad_medida_coordendas': 'grados'})
        return jsonify(data['puntos'])

############################# --- SOLAPA API QUE EMULA LO PEDIDO POR LUCIANO DESDE LA INTERFAZ --- #############################

    def api(self):
        info = request.get_json()
        i = 0
        radio_metros = 100
        puntos = {'Coordenadas': []}
        mapa = folium.Map(location=(info.get('latitude'), info.get('longitude')), zoom_start=15)
        folium.Marker(location=(info.get('latitude'), info.get('longitude')), icon=folium.Icon(icon="cloud", color="red"), tooltip="Usted esta aquí").add_to(mapa)
        while i < info.get('cantCoord'):
            # Generamos ángulo y distancia aleatoria
            angulo = 0 + ((2 * math.pi) - 0) * self.generate_u()
            distancia = float(radio_metros) * math.sqrt(self.generate_u())
            # Calculamos el desplazamiento en metros
            off_x = distancia * math.cos(angulo)
            off_y = distancia * math.sin(angulo)
            # CONVERSIÓN DE METROS A GRADOS
            # 1 grado aprox 111.320 metros
            delta_lat = off_y / 111320
            # La longitud depende de qué tan lejos estés del ecuador
            delta_lon = off_x / (111320 * math.cos(math.radians(info.get('latitude'))))
            # Retornamos la coordenada final sumada al centro
            latitud = info.get('latitude') + delta_lat
            longitud = info.get('longitude') + delta_lon
            puntos['Coordenadas'].append({'Lat': latitud, 'Lon': longitud})
            folium.Marker(location=(latitud, longitud), tooltip="Ubicaciones aleatorias").add_to(mapa)
            i+=1
        mapa.save("app/static/mapa.html")
        return jsonify(puntos)

############################# --- API LUCIANO QUE FUNCIONA CONSULTANDO URL POR INTERNET --- #############################
    def apiUbicaciones(self):
        i = 0
        puntos = {'Coordenadas': []}
        lat_centro = float(request.args.get('lat'))
        lon_centro = float(request.args.get('lon'))
        radio_metros = 100
        while i < 4: # Puse 4 por requerimiento de Luciano
            # Generamos ángulo y distancia aleatoria
            angulo = 0 + ((2 * math.pi) - 0) * self.generate_u()
            distancia = float(radio_metros) * math.sqrt(self.generate_u())
            # Calculamos el desplazamiento en metros
            off_x = distancia * math.cos(angulo)
            off_y = distancia * math.sin(angulo)
            # CONVERSIÓN DE METROS A GRADOS
            # 1 grado aprox 111.320 metros
            delta_lat = off_y / 111320
            # La longitud depende de qué tan lejos estés del ecuador
            delta_lon = off_x / (111320 * math.cos(math.radians(lat_centro)))
            # Retornamos la coordenada final sumada al centro
            nueva_lat = lat_centro + delta_lat
            nueva_lon = lon_centro + delta_lon
            puntos['Coordenadas'].append({'Lat': nueva_lat, 'Lon': nueva_lon})
            i+=1
        return jsonify(puntos)

############################# --- Metodos para llevar aleatoriedad uniforme del [0,1) al [a,b] ---  #############################

    def uniforme(self, lim_inf, lim_sup):
        valor = lim_inf + (lim_sup - lim_inf) * self.generate_u()
        return valor
    
    def uniformPosGeograficas(self, lim_inf, lim_sup, lat_centro, lon_centro, radio_metros):
        # Generamos ángulo y distancia aleatoria
        angulo = self.uniforme(lim_inf, lim_sup)
        distancia = float(radio_metros) * math.sqrt(self.generate_u())
        # Calculamos el desplazamiento en metros
        off_x = distancia * math.cos(angulo)
        off_y = distancia * math.sin(angulo)
        # CONVERSIÓN DE METROS A GRADOS
        # 1 grado aprox 111.320 metros
        delta_lat = off_y / 111320
        # La longitud depende de qué tan lejos estés del ecuador
        delta_lon = off_x / (111320 * math.cos(math.radians(lat_centro)))
        # Retornamos la coordenada final sumada al centro
        nueva_lat = lat_centro + delta_lat
        nueva_lon = lon_centro + delta_lon
        return nueva_lat, nueva_lon

    def normal(self, mu, sigma):
        i = 1
        sumu = 0
        while i <= 12:
            u = self.generate_u()
            sumu = sumu + u
            i += 1
        valor = sigma * (sumu - 6) + mu
        return valor
    
    def transInvFunDiscSinProb(self):
        u = self.generate_u()
        if (u <= 0.25 ):
            x = 'Menos de 15 min'
        elif (u <= 0.5):
            x = 'Entre 15 y 30 min'
        elif (u <= 0.75):
            x = 'Entre 30 y 50 min'
        else:
            x = '1 hora o mas'
        return x
    
    def transInvFunDiscConProb(self, p1, p2, p3):
        u = self.generate_u()
        if (u <= p1):
            x = 'Menos de 15 min'
        elif (u <= p1 + p2):
            x = 'Entre 15 y 30 min'
        elif (u <= p1 + p2 + p3):
            x = 'Entre 30 y 50 min'
        else:
            x = '1 hora o mas'
        return x

############################# --- Metodo congruencial mixto para generar u o nro pseudoaleatorio ---  #############################
    def generate_u(self):
        a = 1103515245 #19
        c = 12345 #155
        mod = 2147483647 #Módulo grande: 2^31 - 1, para garantizar la generación de numeros que no se repitan
        if self.b == 0:
            self.seed = 4
            self.b = 1
        self.seed = (a * self.seed + c) % mod
        u = self.seed / mod
        return u

############################# --- GENERAR MAPA ---  #############################

    def generate_map(self, lat, lon, radio, places):
        mapa = folium.Map(location=(lat, lon), zoom_start=15)
        folium.Circle(location=(lat,lon), radius=radio, color="crimson", fill=True, fill_color="crimson").add_to(mapa)
        folium.Marker(location=(lat, lon), icon=folium.Icon(color='red', prefix='fa', icon='male'), tooltip="Ubicación central").add_to(mapa)
        for place in places:
            html = "<b>Nombre</b>"+"<br>"+place['nombre']+"<br><br>"
            iframe = folium.IFrame(html)
            popup = folium.Popup(iframe, min_width=200, max_width=200)
            folium.Marker(location=(place['lat'], place['lon']), popup=popup).add_to(mapa)
        mapa.save("app/static/mapa.html")

