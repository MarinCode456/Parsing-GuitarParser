'''
Модуль utils для общих функций всех парсеров.
Содержит всю доп. информацию, которяа нужна в ходе парсинга:
    - пути
    - функции для получения информации
    - функции для записи в файл
'''

# Импорты
import asyncio
import requests
from selenium import webdriver
from selenium_stealth import stealth
from pathlib import Path

# Пути ко всем папкам
filepath = Path(__file__)
gendir = filepath.parent.parent

marketdir = gendir / "markets"
komidir = marketdir / "komissionchick"
muzdir = marketdir / "muztorg"
avitodir = marketdir / "avito"
lovecdir = marketdir / "lovecnot"
jazzdir = marketdir / "jazzshop"

# Настройки для selenium-stealth
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_argument("--headless")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
# Отключает все сообщения селениума
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_experimental_option('useAutomationExtension', False)



# Функция для получения кода элемента страницы
async def fetch_content(session, url):
    async with session.get(url) as r:
        return await asyncio.wait_for(r.text(), 5)
    
# Функция для скачивания изображения
async def download_image(session, url, path):
    if not url:
        # Это значит, что ссылка не была получена
        return
    
    async with session.get(url) as data:
        image_data = await data.read()
        with open(path, 'wb') as file:
            file.write(image_data)

# Синхронная функция для скачивания изображения
def download_image_nota(url, path):
    rdata = requests.get(url).content
    with open(path, 'wb') as file:
        file.write(rdata)

# Получаем скрытый драйвер селениум
def getdriver():
    driver = webdriver.Chrome(options=options)

    # Благодаря этой функции наш парсинг становится более незаметным
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
    
    return driver