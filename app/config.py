class Config:
    # Parametros para buscar_combo_ciudad
    api_base_url_combo_city = 'https://api.geoapify.com/v1/geocode/search?text='
    api_key = '3ea460fd6ee1440ba1999a9c39c0cebe'
    api_type = '&type=city&format=json'
    # Parametros para datos del clima
    api_base_url_weather = 'https://api.weatherapi.com/v1/forecast.json?'
    api_key_weather = '2107a50a1eae425f89015728212704'
    api_type_weather = '&days=1&aqi=no&alerts=no'
