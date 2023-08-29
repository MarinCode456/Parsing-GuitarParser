'''
Модуль avito для скачивания гитар с авито.
Полностью готов к использованию, главная функция - getGuitars

Работает лишь на одну страницу, так как у нас в городе гитары не заполняют даже двух страниц.
Все они помещаются на первой, поэтому совершенно не вижу смысла проходится по следующим, однако
возможно реализую в будущем, если понадобится.

Что интересно, единственный парсер из 5, который использует тихий селениум.
Всё из-за того, что авито подгружает страницы динамически, а кроме того имеет хорошую
защиту от парсеров, из-за чего если поставить задержку больше 10 секунд между скачиванием гитар,
банит айпи, что печально.

"p" в начале имени файла означает "parser"
'''

# Импорты
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
import time

import utils
import folder
import config

# Полезные переменные
m = folder.manager()
avitodir = utils.avitodir



# Получаем все ссылки на все гитары с авито
def getUrls():
    print("    [GuitarParser] Начинаю парсинг товаров")
    driver = utils.getdriver()
    
    # Начало ссылки для того, чтобы мы могли последовательно перебирать страницы
    upper_value = config.getAvitoValue()
    print(f"    [GuitarParser] Предельная стоимость гитары: {upper_value}")
    if upper_value == 'DEFAULT': domain = "https://www.avito.ru/chelyabinsk/muzykalnye_instrumenty?cd=1&q=электрогитара&user=1&p="
    else: domain = f"https://www.avito.ru/chelyabinsk/muzykalnye_instrumenty?cd=1&pmax={upper_value}&q=электрогитара&user=1&p="
    url = f"{domain}1"

    '''Здесь можно реализовать также проход по страницам.
    Для этого нужно будет каждый раз искать тег div с data-marker catalog-serp и если его не будет
    то нам эта страница не нужна. Я решил этого не делать, так как у нас в Челябинске (именно для этого города создаётся парсер)
    никогда количество гитар не переваливает за одну страницу. Но в последствии можно это доделать.'''

    # Извлекаем все ссылки со страницы
    driver.get(url)
    catalog = driver.find_element(By.CSS_SELECTOR, '[data-marker="catalog-serp"]')

    # Берем только нечетные элементы списка, так как в одном товаре есть сразу 2 тега a, у которых одинаковые ссылки
    hrefs = catalog.find_elements(By.CSS_SELECTOR, '[itemprop="url"]')[::2]
    urls = []
    for href in hrefs:
        urls.append(href.get_attribute("href"))

    print(f"    [GuitarParser] Ссылок товаров получено: {len(urls)}")

    # Задержка перед закрытием
    time.sleep(5)
    driver.quit()

    return urls

# Записываем данные всех ссылок в файлы
def getGuitarsInfo(urls):
    print("    [GuitarParser] Начинаю сбор информации о гитарах")

    # Получаем драйвер для чтения каждой ссылки
    driver = utils.getdriver()

    # Название для сохраняемых файлов, которое инкрементируется с каждой успешной загрузкой
    file_name = 1

    for url in urls:
        try:
            # Получаем информацию со страницы
            driver.get(url)

            # Если мы не нашли на странице название гитары, то записываем DEFAULT
            name = driver.find_element(By.CLASS_NAME, 'title-info-title-text')
            if not name is None: name = name.text
            else:
                name = "DEFAULT"
                print(f"        [GuitarParser] Не найдено имени для гитары [{url}]")

            # Если мы не нашли на странице описание гитары, то записываем DEFAULT
            lore = driver.find_element(By.CSS_SELECTOR, '[itemprop="description"]')
            if not lore is None: lore = lore.text.lstrip().replace("\n", " ")
            else: 
                lore = "DEFAULT"
                print(f"        [GuitarParser] Не найдено описания для гитары [{url}]")

            # Если мы не нашли на странице цену гитары, то записываем NO_PRICE
            price = driver.find_element(By.CSS_SELECTOR, '[itemprop="price"]')
            if not price is None: price = price.get_attribute("content")
            else: 
                lore = "NO_PRICE"
                print(f"        [GuitarParser] Не найдено цены для гитары [{url}]")

            # Если мы не нашли на странице картинку гитары, то не добавляем гитару
            img_url = driver.find_element(By.CSS_SELECTOR, '[data-image-id="0"]')
            if not img_url is None: 
                img_url = img_url.get_attribute("data-url")
                utils.download_image_nota(img_url, avitodir / f"{file_name}.jpg")
            else: 
                print(f"        *[GuitarParser] Я не нашёл изображение для [{url}]")
                print(f"        *[GuitarParser] Скорее всего, гитара удалена")
                return

            # Мы здесь, значит информация найдена и мы записываем её в файлы
            strings = f"{name}\n{lore}\n{price}\n\n{url}\n\n{img_url}"
            m.writeTo(avitodir / f"{file_name}.txt", strings)

            print(f"    [GuitarParser] В папку добавлена гитара [{file_name}] - {name}")
            file_name += 1

            # После каждой ссылки мы ждём 10 секунд, чтобы наш айпи не блокнули
            time.sleep(10)
        except Exception as e:
            print(f"    *[GuitarParser] Произошла ошибка при работе с ссылкой {file_name}-{url}")
            print(f"    {e}")
            return

# Записываем в папку авито всю информацию обо всех гитарах
def getGuitars():
    urls = getUrls()
    getGuitarsInfo(urls)