import aiohttp
from config import API_KEY_WEATHER, UNITS, API_KEY_ACTIVITY


# Асинхронная функция для получения данных из API о погоде
# о текущей температуре в городе
async def current_temperature(city: str) -> float:
    """
    city: city name

    return current temperature in city using openweathermap data
    """
    # Получим url для широты и долготы
    geo_info_url = \
        f'https://api.openweathermap.org/geo/1.0/direct?q={city}&appid={API_KEY_WEATHER}'

    async with aiohttp.ClientSession() as session:
        async with session.get(geo_info_url) as geo_response:
            geo_info = await geo_response.json()
            lat = geo_info[0]['lat']
            lon = geo_info[0]['lon']

        # Получим url для текущих данных о погоде
        weather_url = \
            f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units={UNITS}&appid={API_KEY_WEATHER}'

        async with session.get(weather_url) as weather_response:
            cur_weather = await weather_response.json()

    # Вернём текущую температуру
    cur_temp = cur_weather['main']['temp']

    return cur_temp


async def get_food_info(product_name: str):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product_name}&json=true"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as food_info_response:
            if food_info_response.status == 200:
                food_info = await food_info_response.json()
                products = food_info.get('products', [])
                if products:  # Проверяем, есть ли найденные продукты
                    first_product = products[0]
                    return {
                        'name': first_product.get('product_name', 'Неизвестно'),
                        'calories': first_product.get('nutriments', {}).get('energy-kcal_100g', 0)
                    }
                return None
            print(f"Ошибка: {food_info_response.status}")
            return None


async def activity_info(activity: str, weight: int) -> [float, None]:
    url = 'https://api.api-ninjas.com/v1/caloriesburned?'
    request_params = {
        'activity': activity,
        'weight': weight
    }
    headers = {
        'X-Api-Key': API_KEY_ACTIVITY
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers, params=request_params) as response:
            if response.status == 200:
                calories_per_hour = await response.json()
                calories_per_hour = float(calories_per_hour[0]['calories_per_hour'])
                return calories_per_hour

            print(f"Ошибка: {response.status}")

            return None
