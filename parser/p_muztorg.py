'''
Модуль muztorg для скачивания гитар с музторга.
Полностью готов к использованию, главная функция - getGuitars

Скачивает вообще все электрогитары с музторга. Его не остановить.
Сначала последовательно проходится по всем страницам и записывает себе все ссылки на гитары.
Потом уже в асинхронном режиме скачивает по 30 гитар за раз, пока не скачает все.

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
muzdir = utils.muzdir



# Получаем все ссылки на все гитары с музторга
def getUrls():
    # Получаем верхнее значение стоимости
    upper_value = config.getMuztorgValue()
    print(f"    [GuitarParser] Предельная стоимость гитары: {upper_value}")
    if upper_value == 'DEFAULT': url = 'https://www.muztorg.ru/category/elektrogitary?page='
    else: url = f'https://www.muztorg.ru/category/elektrogitary?end_price={upper_value}&page='

    u_list = []
    rtext = requests.get(url + "1").text
    soup = bs(rtext, 'lxml').find('div', class_='thumbnail-list grid-3')

    counter = 2
    while soup != None:
        for i in soup.find_all('a', href=True, itemprop='image'):
            u_list.append("https://www.muztorg.ru" + i['href'])

        print(f"    [GuitarParser] Уже загружено: {len(u_list)} ссылок")

        rtext = requests.get(url + str(counter)).text
        soup = bs(rtext, 'lxml').find('div', class_='thumbnail-list grid-3')
        counter += 1

    return u_list

# Получаем название, описание и фотку для одной ссылки с музторга
# А также записываем в новый файл
async def getOneGuitar(session, url, file_name):
    try:
        # Получаем всю информацию со страницы
        rtext = await utils.fetch_content(session, url)

        # Если мы не нашли на странице название гитары, то записываем DEFAULT
        name = bs(rtext, 'lxml').find('h1', class_="product-title")
        if not name is None: name = name.text
        else:
            name = "DEFAULT"
            print(f"        [GuitarParser] Не найдено имени для гитары [{url}]")

        # Если мы не нашли на странице описание гитары, то записываем DEFAULT
        lore = bs(rtext, 'lxml').find('div', class_="product-info__i _description")
        if not lore is None: lore = lore.text.lstrip().replace("\n", "")
        else: 
            lore = "DEFAULT"
            print(f"        [GuitarParser] Не найдено описания для гитары [{url}]")

        # Если мы не нашли на странице цену гитары, то записываем NO_PRICE
        price = bs(rtext, 'lxml').find('p', class_="price-value-gtm origin hidden")
        if not price is None: price = price.text
        else: 
            price = "NO_PRICE"
            print(f"        [GuitarParser] Не найдено цены для гитары [{url}]")

        # Если мы не нашли на странице картинку гитары, то не добавляем гитару
        img_url = bs(rtext, 'lxml').find('img', id='slide1')
        if not img_url is None: 
            img_url = img_url['data-src']
            await utils.download_image(session, img_url, muzdir / f"{file_name}.jpg")
        else: 
            print(f"        *[GuitarParser] Я не нашёл изображение для {file_name}-{url}")
            print(f"        *[GuitarParser] Скорее всего, гитара удалена")
            return

        # Мы здесь, значит информация найдена и мы записываем её в файлы
        strings = f"{name}\n{lore}\n{price}\n\n{url}\n\n{img_url}"
        m.writeTo(muzdir / f"{file_name}.txt", strings)

        print(f"    [GuitarParser] В папку добавлена гитара [{file_name}] - {name}")
    except Exception as e:
        print(f"    *[GuitarParser] Произошла ошибка при работе с ссылкой {file_name}-{url}")
        print(f"    {e}")
        return

# Записываем в папку музторга всю информацию обо всех гитарах
def getGuitars():
    urls = getUrls()

    # Вложенная функция для поддержки асинхронности
    async def main():
        async with aiohttp.ClientSession() as session:
            tasks = []
            counter = 1

            # Создаём столько задач, сколько у нас гитар
            for url in urls:
                tasks.append(getOneGuitar(session, url, counter))
                counter += 1

            # Последовательно запускаем по 30 задач
            packet_size = 30
            total_tasks = len(tasks)
            for packet_start in range(0, total_tasks, packet_size):
                # Выбираем меньшее (для ситуации, когда обрабатываем последние задачи)
                packet_end = min(packet_start + packet_size, total_tasks)
                packet = tasks[packet_start:packet_end]
                
                await asyncio.gather(*packet)
                print(f"    [GuitarParser] Загружено {packet_end} из {total_tasks} гитар")

    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())