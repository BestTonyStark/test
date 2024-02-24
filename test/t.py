from pprint import pprint
import requests
token = '07507bc3c8207608f132daf5dd0b76dc'
def fetch_weather():
    city = input('Введите город:  ')
    try:
        r = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={token}'
        )
        data = r.json()
        temp = data['main']['temp']
        return temp
    except:
        return 'Ошибка...'
