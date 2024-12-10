"""
Выполнить скрейпинг данных в веб-сайта http://books.toscrape.com/ 
и извлечь информацию о всех книгах на сайте во всех категориях: 
название, цену, количество товара в наличии (In stock (19 available)) 
в формате integer, описание.
Затем сохранить эту информацию в JSON-файле
"""

import requests
from bs4 import BeautifulSoup
import json
import time
#Функция для получения HTML-контента страницы
def get_page_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status() 
    return response.text

#Функция для извлечения ссылок на все категории книг
def get_category_links(base_url):
    content = get_page_content(base_url)
    soup = BeautifulSoup(content, 'html.parser')
    category_links = []
    category_section = soup.find('ul', class_='nav-list')
    for category in category_section.find_all('a'):
        link = category.get('href')
        if link:
            category_links.append(base_url + link)
    return category_links

# Функция для извлечения ссылок на все страницы в категории
def get_all_pages_in_category(category_url):
    page_links = [category_url]
    while True:
        content = get_page_content(page_links[-1])
        soup = BeautifulSoup(content, 'html.parser')
        next_button = soup.find('li', class_='next')
        if next_button:
            next_page_url = next_button.find('a').get('href')
            next_page_full_url = '/'.join(page_links[-1].split('/')[:-1]) + '/' + next_page_url
            page_links.append(next_page_full_url)
        else:
            break
    return page_links

# Функция для извлечения ссылок на все книги на странице категории:

def get_book_links(page_url):
    content = get_page_content(page_url)
    soup = BeautifulSoup(content, 'html.parser')
    book_links = []
    for h3 in soup.find_all('h3'):
        link = h3.find('a').get('href')
        if link:
            book_links.append('/'.join(page_url.split('/')[:-1]) + '/' + link)
    return book_links

# Функция для извлечения информации о книге

def get_book_info(book_url):
    content = get_page_content(book_url)
    soup = BeautifulSoup(content, 'html.parser')
    title = soup.find('h1').text.strip()
    price = soup.find('p', class_='price_color').text.strip()
    availability = soup.find('p', class_='instock availability').text.strip()
    availability_number = int(''.join(filter(str.isdigit, availability)))
    description_tag = soup.find('meta', {'name': 'description'})
    description = description_tag['content'].strip() if description_tag else 'No description available'
    return {
        'title': title,
        'price': price,
        'availability': availability_number,
        'description': description
    }

# основная программа
def main():
    base_url = 'http://books.toscrape.com/'
    all_books = []
    category_links = get_category_links(base_url)
    for category_link in category_links:
        page_links = get_all_pages_in_category(category_link)
        for page_link in page_links:
            book_links = get_book_links(page_link)
            for book_link in book_links:
                book_info = get_book_info(book_link)
                all_books.append(book_info)
                time.sleep(1)  # Пауза между запросами, чтобы не перегружать сервер
    with open('books_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_books, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()


