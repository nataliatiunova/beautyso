
"""
Выполнить скрейпинг данных в веб-сайта http://books.toscrape.com/ 
и извлечь информацию о всех книгах на сайте во всех категориях: 
название, цену, количество товара в наличии (In stock (19 available)) 
в формате integer, описание.
Затем сохранить эту информацию в JSON-файле
"""
import warnings
from urllib3.exceptions import NotOpenSSLWarning
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

import requests
from bs4 import BeautifulSoup
import json
import os
import time
from urllib.parse import urljoin

#Функция для получения HTML-контента страницы
def get_page_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.HTTPError as http_err:
        print(f"Страница не найдена или другая ошибка HTTP: {http_err}")
        return None
    except Exception as err:
        print(f"Произошла ошибка: {err}")
        return None

# Функция для извлечения ссылок на все категории книг
def get_category_links(base_url):
    soup = get_page_content(base_url)
    if not soup:
        print("Не удалось загрузить базовый URL для категорий.")
        return []
    
    category_links = []
    
    # Ищем блок с категориями
    category_section = soup.select_one('div.side_categories > ul.nav.nav-list > li > ul')
    if not category_section:
        print("Раздел категорий не найден!")
        return category_links
    
    # Проходим по всем категориям
    for category in category_section.find_all('a', href=True):
        relative_link = category['href']  # Получаем относительную ссылку
        absolute_link = urljoin(base_url, relative_link)  # Преобразуем в абсолютную
        category_links.append(absolute_link)
    
    print(f"Найдено {len(category_links)} категорий: {category_links}")
    return category_links


# Функция для извлечения ссылок на все страницы в категории
def get_all_pages_in_category(category_url):
    page_links = [category_url]
    while True:
        soup = get_page_content(page_links[-1])
        next_button = soup.find('li', class_='next')
        if next_button:
            next_page_url = next_button.find('a').get('href')
            # Преобразование относительного URL в абсолютный
            next_page_full_url = '/'.join(page_links[-1].split('/')[:-1]) + '/' + next_page_url
            if next_page_full_url not in page_links:  # Проверка на дублирование
                page_links.append(next_page_full_url)
            else:
                break
        else:
            break
    print(f"Page links in category: {page_links}")
    return page_links

# Функция для извлечения ссылок на все книги на странице категории:

def get_book_links(page_url):
    soup = get_page_content(page_url)
    book_links = []
    for h3 in soup.find_all('h3'):
        link = h3.find('a').get('href')
        if link:
            book_links.append(urljoin(page_url, link))  # Используем urljoin для преобразования в абсолютный путь
    print(f"Book links on page: {book_links}")
    return book_links

# Функция для извлечения информации о книге
def get_book_info(book_url):
    soup = get_page_content(book_url)
    title = soup.find('h1').text.strip()
    price = soup.find('p', class_='price_color').text.strip().replace('Â£', '').strip()
    availability = soup.find('p', class_='instock availability').text.strip()
    availability_number = int(''.join(filter(str.isdigit, availability))) if any(char.isdigit() for char in availability) else 0
    description_tag = soup.find('meta', {'name': 'description'})
    description = description_tag['content'].strip() if description_tag else 'No description available'
   
    # Формируем словарь с информацией о книге
    book_info = {
        'title': title,
        'price': float(price),
        'availability': availability_number,
        'description': description
    }
    print(f"Book info: {book_info}")
    return book_info

# основная программа
def main():
    base_url = 'http://books.toscrape.com/'
    soup = get_page_content(base_url)
    if not soup:
        print("Не удалось загрузить базовый URL")
        return
    
    print(soup.prettify())  # Проверка структуры страницы
    all_books = []
    broken_links = []  # Для хранения битых ссылок

    try:
        category_links = get_category_links(base_url)
        print(f"Categories found: {len(category_links)}")  # Проверка категорий
    except Exception as e:
        print(f"Ошибка при получении категорий: {e}")
        return

    for category_link in category_links:
        try:
            page_links = get_all_pages_in_category(category_link)
            print(f"Pages in category: {len(page_links)}")  # Проверка страниц
        except Exception as e:
            print(f"Ошибка при получении страниц категории {category_link}: {e}")
            broken_links.append(category_link)
            continue
        
        for page_link in page_links:
            try:
                print(f"Scraping page: {page_link}")
                book_links = get_book_links(page_link)
                print(f"Books found on page: {len(book_links)}")  # Проверка книг
            except Exception as e:
                print(f"Ошибка при получении ссылок на книги с {page_link}: {e}")
                broken_links.append(page_link)
                continue
            
            for book_link in book_links:
                try:
                    print(f"Scraping book: {book_link}")
                    book_info = get_book_info(book_link)
                    if book_info:
                        print(f"Book info: {book_info}")  # Проверка информации о книге
                        all_books.append(book_info)
                    else:
                        print(f"Нет информации по книге: {book_link}")
                        broken_links.append(book_link)
                except Exception as e:
                    print(f"Ошибка при обработке книги {book_link}: {e}")
                    broken_links.append(book_link)
    
    print(f"Total books scraped: {len(all_books)}")
    print(f"Total broken links: {len(broken_links)}")
    
    # Сохранение данных о книгах
    try:
        with open('/Users/nataliatiunova/Desktop/Pyth_/Beautysoup/books_data.json', 'w', encoding='utf-8') as f:
            json.dump(all_books, f, ensure_ascii=False, indent=4)
        print("Data saved to books_data.json")
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")

    # Сохранение битых ссылок
    try:
        with open('/Users/nataliatiunova/Desktop/Pyth_/Beautysoup/broken_links.txt', 'w') as f:
            for link in broken_links:
                f.write(f"{link}\n")
        print("Broken links saved to broken_links.txt")
    except Exception as e:
        print(f"Ошибка при сохранении битых ссылок: {e}")

#content = get_page_content('http://books.toscrape.com')
#print(content[:1000])  # Вывод первых 500 символов HTML-кода страницы

if __name__ == '__main__':
    main()


