'''
Модуль jazz для скачивания гитар с джаз шопа.
Полностью готов к использованию, главная функция - getGuitars

Скачивает все гитары со всех страниц в асинхронном режиме.
Не знаю особо, что за магазин, но для красивого числа 5, решил взять ещё один магазин.

Здесь есть важный момент в пролистывании страниц.
Так как если вбить 1000 страницу, которой нет на сайте, выведется самая последняя.
Поэтому я запоминаю первую ссылку с предыдщуей страницы.
И если они совпадают, то прекращаю цикл поиска ссылок.

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
jazzdir = utils.jazzdir



# Получаем все ссылки на все гитары с ловца нот
def getUrls():
    print("    [GuitarParser] Начинаю парсинг товаров")
    urls = []
    
    # Начало ссылки для того, чтобы мы могли последовательно перебирать страницы
    upper_value = config.getJazzValue()
    print(f"    [GuitarParser] Предельная стоимость гитары: {upper_value}")
    if upper_value == 'DEFAULT': domain = "https://jazz-shop.ru/chelyabinsk/catalog/elektrogitary?page="
    else: domain = f"https://jazz-shop.ru/chelyabinsk/catalog/elektrogitary?price_to={upper_value}&page="
    url = f"{domain}1"

    rtext = requests.get(url).text
    items_container = bs(rtext, 'lxml').find('div', class_="catalog-products")
    aitems = items_container.find_all('a', itemprop="url")

    # Пока мы находим на странице какие-то элементы, продолжаем перебирать
    # При этом первые ссылки с каждой страницы не должны совпадать, иначе страницы повторяются.
    counter = 2
    old_url, now_url = '1', '2'
    while aitems and not (old_url == now_url):
        # Запоминаем первую ссылку на гитару со страницы
        old_url = aitems[0]['href']

        # Добавляем все ссылки
        for aitem in aitems:
            url = aitem['href']
            urls.append(url)

        print(f"    [GuitarParser] Уже загружено: {len(urls)} ссылок")

        # Формируем новую ссылку и ищём гитары уже на ней
        url = f"{domain}{counter}"
        counter += 1

        # Загружаем уже новую информацию
        rtext = requests.get(url).text
        items_container = bs(rtext, 'lxml').find('div', class_="catalog-products")
        aitems = items_container.find_all('a', itemprop="url")

        # Если aitems не пуст, берем первую ссылку на гитару для сравнения
        if aitems:
            now_url = aitems[0]['href']
        
    return urls

# Получаем название, описание и фотку для одной ссылки с ловца нот
# А также записываем в новый файл
async def getOneGuitar(session, url, file_name):
    try:
        # Получаем всю информацию со страницы
        rtext = await utils.fetch_content(session, url)

        # Если мы не нашли на странице название гитары, то записываем DEFAULT
        name = bs(rtext, 'lxml').find('h1', itemprop="name")
        if not name is None: name = name.text
        else:
            name = "DEFAULT"
            print(f"        [GuitarParser] Не найдено имени для гитары [{url}]")

        # Если мы не нашли на странице описание гитары, то записываем DEFAULT
        lore = bs(rtext, 'lxml').find('div', class_="tabbed-content").find('p')
        if not lore is None: lore = lore.text.lstrip().replace("\n", "")
        else: 
            lore = "DEFAULT"
            print(f"        [GuitarParser] Не найдено описания для гитары [{url}]")

        # Если мы не нашли на странице цену гитары, то записываем NO_PRICE
        price = bs(rtext, 'lxml').find('price', class_="price")
        if not price is None: price = price.text.replace("₽", "").replace("  ", "")
        else: 
            price = "NO_PRICE"
            print(f"        [GuitarParser] Не найдено цены для гитары [{url}]")

        # Если мы не нашли на странице картинку гитары, то не добавляем гитару
        img_url = bs(rtext, 'lxml').find('img', itemprop="contentUrl")
        if not img_url is None: 
            img_url = img_url['src']
            await utils.download_image(session, img_url, jazzdir / f"{file_name}.jpg")
        else: 
            print(f"        *[GuitarParser] Я не нашёл изображение для {file_name}-{url}")
            print(f"        *[GuitarParser] Скорее всего, гитара удалена")
            return

        # Мы здесь, значит информация найдена и мы записываем её в файлы
        strings = f"{name}\n{lore}\n{price}\n\n{url}\n\n{img_url}"
        m.writeTo(jazzdir / f"{file_name}.txt", strings)

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