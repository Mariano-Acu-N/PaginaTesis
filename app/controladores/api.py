from flask import Blueprint, request, jsonify
from app.servicios.api_service import ApiService
from app.config import Config
import folium
import math
from shapely.geometry import Point, Polygon
from datetime import datetime
from timezonefinder import TimezoneFinder

class ApiController:
    def __init__(self):
        self.api_bp = Blueprint('api', __name__)
        self.b = 0
        self.seed = 0
        self.id_Simulacion = 0
        self.primera_sim = True
        self.mapa_Geo = 0
        self.register_routes()

    def register_routes(self):
        self.api_bp.route('/reiniciarSimulacion', methods=['POST'])(self.reiniciarSimulacion)
        self.api_bp.route('/reiniciarBanderaMapa', methods=['POST'])(self.reiniciarBanderaMapa)
        self.api_bp.route('/obtenerLatLon', methods=['POST'])(self.obtenerLatLon)
        self.api_bp.route('/simularContextoAmbienteManual', methods=['POST'])(self.simularContextoAmbienteManual)
        self.api_bp.route('/simularContextoAmbienteAPI', methods=['POST'])(self.simularContextoAmbienteAPI)
        self.api_bp.route('/simularContextoGeografico', methods=['POST'])(self.simularContextoGeografico)
        self.api_bp.route('/simularContextoTemporal', methods=['POST'])(self.simularContextoTemporal)
        # self.api_bp.route('/api', methods=['POST'])(self.api)
        self.api_bp.route('/apiUbicaciones', methods=['GET'])(self.apiUbicaciones)


    # Para reiniciar la variable primera_sim, sino queda en False porque el frontend usa la misma instancia del backend para todas las ejecuciones
    def reiniciarSimulacion(self):
        self.primera_sim = True
        return jsonify({'status': 'ok', 'mensaje': 'Flag de simulación reiniciado'}), 200

    def reiniciarBanderaMapa(self):
        self.mapa_Geo = 0

    def obtenerLatLon(self):
        data = {'lat': '', 'lng': ''}
        info = request.get_json()
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
        data['lat'] = lat
        data['lng'] = lon
        return data

############################# --- CONTEXTO TEMPORAL --- #############################
    def simularContextoTemporal(self):
        #simuTiempo = {'id_Simulacion': self.id_Simulacion, 'fechaHora_Generacion': datetime.now(), 'tiempo': []}
        simuTiempo = {'id_Simulacion': self.id_Simulacion, 'tiempo': []}
        info = request.get_json()
        i = 0
        tf = TimezoneFinder()
        #Tiempo libre o disponible
        # menor a 15 min, entre 15 a 30 min, entre 30 a 50 min y mas de 1hr
        try:
            if (self.primera_sim):
                self.id_Simulacion += 1
                simuTiempo['id_Simulacion'] = self.id_Simulacion
                self.primera_sim = False
        except Exception as e:
            print(f"Error procesando formato de hora: {e}")
        while i < info.get('cantDatosT'):
            hrnueva, minnuevos = self.generar_hora(info)
            if info.get('b') == 0:
            #while i < info.get('cantDatosT'):
            #    hrnueva, minnuevos = self.generar_hora(info)
                tiempo_libre = self.laplace() #minutos
                #simuTiempo['tiempo'].append({'tiempo_libre': tiempo_libre, 'hr_del_dia': f"{hrnueva}:{minnuevos}"})
                #i+=1
            else:
            #while i < info.get('cantDatosT'):
            #    hrnueva, minnuevos = self.generar_hora(info)
                tiempo_libre = self.transInvFunDisc(info.get('p1'),info.get('p2'),info.get('p3')) #minutos
                #simuTiempo['tiempo'].append({'tiempo_libre': tiempo_libre, 'hr_del_dia': f"{hrnueva}:{minnuevos}"})
                #i+=1
            simuTiempo['tiempo'].append({'tiempo_libre': tiempo_libre, 'hr_del_dia': f"{hrnueva}:{minnuevos}"})
            i+=1
        zona_horaria = tf.timezone_at(lat=info.get('lat'), lng=info.get('lng'))
        simuTiempo['tiempo'].append({'unidad_medida_tiempo_libre': 'minutos / hora', 'unidad_medida_hr_del_dia': '24hr', 'zona_horaria': zona_horaria})
        if self.mapa_Geo != 1:
            self.generate_map(info.get('lat'), info.get('lng'), 0, 0)
        return jsonify(simuTiempo)

    def generar_hora(self, info):
        #Hora del día
        hrdesde, mdesde = self.procesar_hora(info.get('hrdesde'))
        hrhasta, mhasta = self.procesar_hora(info.get('hrhasta'))
        total_min_desde = hrdesde * 60 + mdesde
        total_min_hasta = hrhasta * 60 + mhasta

        # Si la hora de fin es menor a la de inicio, asume que cruzó la medianoche (día siguiente)
        if total_min_hasta < total_min_desde:
             total_min_hasta += 1440  # 24 horas * 60 minutos

        total_min_nuevo = self.uniforme(total_min_desde, total_min_hasta)

        hrnueva = int((total_min_nuevo // 60) % 24)
        minnuevos = int(total_min_nuevo % 60)

        # El :02d garantiza 2 dígitos agregando '0' si es de 1 solo dígito, :02d funciona con tipo de datos int
        hrformateada = f"{hrnueva:02d}"
        minformateado = f"{minnuevos:02d}"

        return hrformateada, minformateado

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

    def simularContextoAmbienteManual(self):
        #simuAmb = {'id_Simulacion': self.id_Simulacion, 'fechaHora_Generacion': datetime.now(), 'clima': []}
        simuAmb = {'id_Simulacion': self.id_Simulacion, 'clima': []}
        cont = 0
        info = request.get_json()
        while cont < int(info.get('cantAmb')):
            temp = self.uniforme(info.get('tempmin'), info.get('tempmax'))
            hum = self.normal(info.get('humDeseada'), info.get('humFluctuacion')) # No aplico la multiplicacion por 0.1 porque ya debería conocer la desviación estandar, diferente el caso de que cuando la obtengo de la API
            datosAmbGenerados = self.agregarDatosClima (temp, hum, simuAmb)
            cont+=1
        datosAmbGenerados['clima'].append({'unidad_medida_temp': 'grados', 'unidad_medida_hum': 'porcentaje'})
        if self.mapa_Geo != 1:
            self.generate_map(info.get('lat'), info.get('lng'), 0, 0)
        return jsonify(datosAmbGenerados)

    def simularContextoAmbienteAPI(self):
        #simuAmb = {'id_Simulacion': self.id_Simulacion, 'fechaHora_Generacion': datetime.now(), 'clima': []}
        simuAmb = {'id_Simulacion': self.id_Simulacion, 'clima': []}
        cont = 0
        apiser = ApiService(Config.api_base_url_combo_city, Config.api_key, Config.api_type,
                            Config.api_base_url_weather, Config.api_key_weather, Config.api_type_weather)
        info = request.get_json()
        latlon = str(info.get('lat')) + ", " + str(info.get('lng'))
        pronostico = apiser.clima(latlon)
        while cont < int(info.get('cantAmb')):
            temp = self.uniforme(pronostico['forecast']['forecastday'][0]['day']['mintemp_c'], pronostico['forecast']['forecastday'][0]['day']['maxtemp_c'])
            desviacion_estandar = pronostico['forecast']['forecastday'][0]['day']['avghumidity'] * 0.1 # se multiplica por 0.1 (10%) = 5% de desviacion propuesta por el fabricante + 5% para abarcar posibles ruidos provenientes del ambiente
            hum = self.normal(pronostico['forecast']['forecastday'][0]['day']['avghumidity'], desviacion_estandar)
            datosAmbGenerados = self.agregarDatosClima (temp, hum, simuAmb)
            cont+=1
        datosAmbGenerados['clima'].append({'unidad_medida_temp': 'grados', 'unidad_medida_hum': 'porcentaje'})
        if self.mapa_Geo != 1:
            self.generate_map(info.get('lat'), info.get('lng'), 0, 0)
        return jsonify(datosAmbGenerados)

    def agregarDatosClima (self, temp, hum, simuAmb):
        if hum > 100:
            hum = 100
        elif hum < 0:
            hum = 0
        if (self.primera_sim):
            self.id_Simulacion += 1
            # round(temp, 1) para que tome 1 decimal, el dato ya es del tipo float
            simuAmb['clima'].append({'temp': round(temp, 1), 'hum': int(hum)})
            self.primera_sim = False
        else:
            # round(temp, 1) para que tome 1 decimal, el dato ya es del tipo float
            simuAmb['clima'].append({'temp': round(temp, 1), 'hum': int(hum)})
        return simuAmb

############################# --- CONTEXTO GEOGRAFICO --- #############################

    def simularContextoGeografico(self):
        #simuGeo = {'id_Simulacion': self.id_Simulacion, 'fechaHora_Generacion': datetime.now().isoformat(), 'puntosGeograficos': []}
        simuGeo = {'id_Simulacion': self.id_Simulacion, 'puntosGeograficos': []}
        etiqueta_nombre = 1
        encontrados = 0
        lim_inf = 0
        lim_sup = 2 * math.pi
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
        info = request.get_json()
        if (self.primera_sim):
            self.id_Simulacion += 1
            simuGeo['id_Simulacion'] = self.id_Simulacion
            self.primera_sim = False
        lat = float(info.get('lat'))
        lon = float(info.get('lon'))
        radio = info.get('radio')
        while encontrados < int(info.get('cantPuntos')):
            posX, posY = self.uniformPosGeogr(lim_inf, lim_sup, lat, lon, radio)
            punto = Point(posY, posX)
            esta_dentro = poligono.contains(punto)
            if (esta_dentro):
                simuGeo['puntosGeograficos'].append({'nombre': f'Ubicacion {etiqueta_nombre}', 'categoria': info.get('category'), 'lat': posX, 'lon': posY, 'en_UNSE': 'Si'})
            else:
                simuGeo['puntosGeograficos'].append({'nombre': f'Ubicacion {etiqueta_nombre}', 'categoria': info.get('category'), 'lat': posX, 'lon': posY, 'en_UNSE': 'No'})
            etiqueta_nombre += 1
            encontrados += 1
        self.mapa_Geo = 1 # 1 es para indicar que mostrara el mapa con los puntos sin que se solape con el mapa del ambiente o los tiempos
        self.generate_map(lat, lon, radio, simuGeo['puntosGeograficos'])
        simuGeo['puntosGeograficos'].append({'unidad_medida_coordenadas_lat_lon': 'grados'})
        return jsonify(simuGeo)

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
    
    def uniformPosGeogr(self, lim_inf, lim_sup, lat_centro, lon_centro, radio_metros):
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
    
    def laplace(self):
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
    
    def transInvFunDisc(self, p1, p2, p3):
        u = self.generate_u()
        if u <= p1:
            x = 'Menos de 15 min'
        elif u <= (p1 + p2):
            x = 'Entre 15 y 30 min'
        elif u <= (p1 + p2 + p3):
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
        if self.mapa_Geo == 1:
            mapa = folium.Map(location=(lat, lon), zoom_start=15)
            folium.Circle(location=(lat,lon), radius=radio, color="crimson", fill=True, fill_color="crimson").add_to(mapa)
            folium.Marker(location=(lat, lon), icon=folium.Icon(color='red', prefix='fa', icon='male'), tooltip="Ubicación central").add_to(mapa)
            for place in places:
                html = "<b>Nombre</b>"+"<br>"+place['nombre']+"<br><br>"+"<b>Categoria</b>"+"<br>"+place['categoria']
                iframe = folium.IFrame(html)
                popup = folium.Popup(iframe, min_width=200, max_width=200)
                folium.Marker(location=(place['lat'], place['lon']), popup=popup).add_to(mapa)
        else:
            mapa = folium.Map(location=(lat, lon), zoom_start=15)
            folium.Marker(location=(lat, lon), icon=folium.Icon(color='red', prefix='fa', icon='male'), tooltip="Su ubicación").add_to(mapa)
        mapa.save("app/static/mapa.html")

############################# --- EXPORTAR ---  #############################

    def exportarJSON(self, data):

        return jsonify(data)
