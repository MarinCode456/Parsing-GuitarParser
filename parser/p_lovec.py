'''
Модуль lovec для скачивания гитар с ловца нот.
Полностью готов к использованию, главная функция - getGuitars

Скачивает все гитары со всех страниц в асинхронном режиме.
Что плохо, в ловце нот половина гитар не в наличии, но их вроде как можно взять на заказ.
Поэтому я не стал делать проверку на наличие, но в будущем, возможно, стоит заняться и этим.

Работает как модуль с музторгом, асинхронно.

"p" в начале имени файла означает "parser"
'''

# Импорты
from bs4 import BeautifulSoup as bs
import asyncio
import aiohttp
import requests

import utils
import folder
import config

# Полезные переменные
m = folder.manager()
lovecdir = utils.lovecdir



# Получаем все ссылки на все гитары с ловца нот
def getUrls():
    print("    [GuitarParser] Начинаю парсинг товаров")
    urls = []
    
    # Начало ссылки для того, чтобы мы могли последовательно перебирать страницы
    upper_value = config.getLovecValue()
    print(f"    [GuitarParser] Предельная стоимость гитары: {upper_value}")
    if upper_value == 'DEFAULT': domain = "https://lovec-not.ru/categories/elektrogitary?page="
    else: domain = f"https://lovec-not.ru/categories/elektrogitary?priceto={upper_value}&page="
    url = f"{domain}1"

    rtext = requests.get(url).text
    aitems = bs(rtext, 'lxml').find_all('a', class_="products-view-picture-link")

    # Пока мы находим на странице какие-то элементы, продолжаем перебирать
    counter = 2
    while aitems:
        # Добавляем все ссылки
        for aitem in aitems:
            url = aitem['href']
            urls.append(url)

        print(f"    [GuitarParser] Уже загружено: {len(urls)} ссылок")

        # Формируем новую ссылку и ищём гитары уже на ней
        url = f"{domain}{counter}"
        counter += 1
        rtext = requests.get(url).text
        aitems = bs(rtext, 'lxml').find_all('a', class_="products-view-picture-link")
        
    return urls

# Получаем название, описание и фотку для одной ссылки с ловца нот
# А также записываем в новый файл
async def getOneGuitar(session, url, file_name):
    try:
        # Получаем всю информацию со страницы
        rtext = await utils.fetch_content(session, url)

        # Если мы не нашли на странице название гитары, то записываем DEFAULT
        name = bs(rtext, 'lxml').find('div', class_="details-title page-title").find('h1')
        if not name is None: name = name.text
        else:
            name = "DEFAULT"
            print(f"        [GuitarParser] Не найдено имени для гитары [{url}]")

        # Если мы не нашли на странице описание гитары, то записываем DEFAULT
        lore = bs(rtext, 'lxml').find('div', class_="tabs-content").find('p')
        if not lore is None: lore = lore.text.lstrip().replace("\n", "")
        else: 
            lore = "DEFAULT"
            print(f"        [GuitarParser] Не найдено описания для гитары [{url}]")

        # Если мы не нашли на странице цену гитары, то записываем NO_PRICE
        price = bs(rtext, 'lxml').find('div', class_="price-number")
        if not price is None: price = price.text
        else: 
            price = "NO_PRICE"
            print(f"        [GuitarParser] Не найдено цены для гитары [{url}]")

        # Если мы не нашли на странице картинку гитары, то не добавляем гитару
        img_url = bs(rtext, 'lxml').find('img', class_="gallery-picture-obj")
        if not img_url is None: 
            img_url = img_url['src']
            await utils.download_image(session, img_url, lovecdir / f"{file_name}.jpg")
        else: 
            print(f"        *[GuitarParser] Я не нашёл изображение для {file_name}-{url}")
            print(f"        *[GuitarParser] Скорее всего, гитара удалена")
            return

        # Мы здесь, значит информация найдена и мы записываем её в файлы
        strings = f"{name}\n{lore}\n{price}\n\n{url}\n\n{img_url}"
        m.writeTo(lovecdir / f"{file_name}.txt", strings)

        print(f"    [GuitarParser] В папку добавлена гитара [{file_name}] - {name}")
    except Exception as e:
        print(f"    *[GuitarParser] Произошла ошибка при работе с ссылкой {file_name}-{url}")
        print(f"    {e}")
        return

# Записываем в папку ловца нот всю информацию обо всех гитарах
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

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())