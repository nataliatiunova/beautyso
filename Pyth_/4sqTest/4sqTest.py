#1. log in as developer and get api-key
import requests

API_KEY = "fsq35AOCHuq3qIWEjOR0CB1kM0pzTk5E+rBUuTEVxfxXmj4="
BASE_URL = "https://api.foursquare.com/v3/places/search"

#функция поиска мест по параметрам query/near/limit
def find_place (category, location = 'San Francisco, CA', limit = 10):
    headers = {
        "accept": "application/json",
        "Authorization": API_KEY
    }
    params = {
        "query": category,
        "near": location,
        "limit": limit
    }
    response = requests.get(BASE_URL, headers = headers, params = params)

    # проверка API статус-кода
    if response.status_code == 200:
        return response.json()["results"]
    else:
        print("Ошибка при запросе API:", response.status_code, response.text)
        return []

def main():
    category = input ("введите категорию места для поиска: ")
    location = input ("введите город и штат для поиска (например, New York, NY): ")
    #вызываем функцию поиска заведений
    places = find_place(category, location)
    if not places:
        print("Заведения не найдены. Попробуйте другую категорию или местоположение.")
        return
    print(f"Найдено {len(places)} мест")
    for place in places:
        name = place.get ("name","Название не доступно")
        adress = place["location"]["formatted_address"] if "location" in place and "formatted_address" in place["location"] else "Адрес недоступен"
        rating = place.get("rating", "Рейтинг недоступен")
        print(f"\nНазвание: {name}")
        print(f"Адрес: {adress}")
        print(f"Рейтинг: {rating}")

if __name__ == "__main__":
    main()
 


