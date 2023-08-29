'''
Модуль komi для скачивания гитар с комиссиончика.
Полностью готов к использованию, главная функция - getGuitars

На момент написания парсера, на комиссиончике была всего лишь одна страница с гитарами
из-за чего я не знаю точно как работает переключение страниц. Поэтому в данной версии скрипт
может скачивать лишь одну страницу с комиссиончика

"p" в начале имени файла означает "parser"
'''

# Импорты
import requests
from bs4 import BeautifulSoup as bs
import asyncio
import aiohttp

import utils
import folder
import config

# Полезные переменные
m = folder.manager()
komidir = utils.komidir



# Получаем все ссылки на все гитары
def getUrls():
    # Получаем значение из конфига, если оно не дефолтное, то меняем ссылку
    upper_value = config.getKomiValue()
    print(f"    [GuitarParser] Предельная стоимость гитары: {upper_value}")
    if upper_value == 'DEFAULT': url = 'https://chel.komissionchik.ru/catalog/muzykalnye-instrumenty/guitars/?electro_music_tip[]=1898'
    else: url = f'https://chel.komissionchik.ru/catalog/muzykalnye-instrumenty/guitars/?&electro_music_tip[]=1898&price_max={upper_value}'

    rtext = requests.get(url).text
    soup = bs(rtext, 'lxml').find('div', class_='products products_col-5')
    u_list = []
    for i in soup.find_all('a', href=True):
        u_list.append("https://chel.komissionchik.ru" + i['href'])
    print(f"    [GuitarParser] Уже загружено: {len(u_list)} гитар")

    return u_list

# Получаем всю информацию для одной гитары, после чего записываем в файл
async def getOneGuitar(session, url, file_name):
    try:
        rtext = await utils.fetch_content(session, url)

        name = bs(rtext, 'lxml').find('h1', itemprop="name")
        if not name is None: name = name.text
        else:
            name = "DEFAULT"
            print(f"        [GuitarParser] Не найдено имени для гитары [{url}]")

        lore = bs(rtext, 'lxml').find('div', itemprop="description")
        if not lore is None: lore = lore.text.replace("\n", "")
        else:
            lore = "DEFAULT"
            print(f"        [GuitarParser] Не найдено описания для гитары [{url}]")

        price = bs(rtext, 'lxml').find('div', class_="price product__price")
        if not price is None: price = price["data-price"]
        else:
            price = "NO_PRICE"
            print(f"        [GuitarParser] Не найдено цены для гитары [{url}]")

        img_url = bs(rtext, 'lxml').find_all('a', class_="p-images__slider-item")
        if not img_url is None: 
            img_url = "https://chel.komissionchik.ru"+ img_url[0]["href"]
            await utils.download_image(session, img_url, komidir / f"{file_name}.jpg")
        else: 
            print(f"        *[GuitarParser] Я не нашёл изображение для [{url}]")
            print(f"        *[GuitarParser] Скорее всего, гитара удалена")
            return

        strings = f"{name}\n{lore}\n{price}\n\n{url}\n\n{img_url}"
        m.writeTo(komidir / f"{file_name}.txt", strings)

        print(f"    [GuitarParser] В папку добавлена гитара [{file_name}] - {name}")
    except Exception as e:
        print(f"    *[GuitarParser] Произошла ошибка при работе с ссылкой {url}")
        print(e)

# Записываем в папку комиссиончика всю информацию обо всех гитарах
def getGuitars():
    urls = getUrls()

    # Вложенная функция для поддержки асинхронности
    async def main():
        async with aiohttp.ClientSession() as session:
            tasks = []
            counter = 1

            for url in urls:
                tasks.append(getOneGuitar(session, url, counter))
                counter += 1
                
            await asyncio.gather(*tasks)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())