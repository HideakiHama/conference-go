import requests
from events.keys import PEXELS_API_KEY, OPEN_WEATHER_API_KEY
import json


def get_weather(state):
    r = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={state}&appid={OPEN_WEATHER_API_KEY}").json()
    # print(r)

    lat = r[0]["lat"]  #inside the list index 0 get the value of key "lat"
    lon = r[0]["lon"]
    # print(lat)
    # print(lon)

    w = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPEN_WEATHER_API_KEY}").json()
    # print(w)

    temperature = w['main']['temp']
    # print(temperature) # in Kelvin
    temperature = int(1.8 * (temperature - 273) + 32)
    # print(temperature) # in Fahrenheit
    description = w['weather'][0]['description']
    # print(description)
    return {"weather": {temperature, description}}


#https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API key}

def get_photo(city, state):
    headers = {"Authorization": PEXELS_API_KEY}

    params = { "per_page": 1, "query": f"{city} {state}"}

    url = "https://api.pexels.com/v1/search"

    response = requests.get(url, params=params, headers=headers)

    if response.status_code >= 300:
        return None

    content = json.loads(response.content)
    # print(content)
    return {"picture_url": content["photos"][0]["url"]}
