# Модуль, отвечающий за работу с папками и файлами

from pathlib import Path
import shutil

# Вспомогательные переменные
currentfile = Path(__file__)
generaldir = currentfile.parent.parent
marketdir = generaldir / "markets"
markets = [marketdir, marketdir / "komissionchick", marketdir / "muztorg", marketdir / "avito", marketdir / "lovecnot", marketdir / "jazzshop"]

class manager:
    # Функция создания каждой папки для каждого магазина, если их нет
    def createFolders(self):
        # Удаляем папку markets
        if marketdir.exists():
            shutil.rmtree(marketdir)
            print(f"[GuitarParser] Папка markets успешно очищена ")

        # Создаём папки
        for fol in markets:
            if not fol.exists():
                fol.mkdir()
                print(f"[GuitarParser] Папка {fol.name} успешно создана ")

    # Записывает в файл path строчки strings
    def writeTo(self, path, strings):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(strings)

    # Получаем все файлы всех гитар
    def getGuitarsInList(self):
        '''Так как мы номируем каждую гитару в каждой папке с номера 1 и так далее,
        То мы просто можем посчитать количество файлов в папке и разделить число на 2,
        Так как в папке хранится 1.jpg и 1.txt'''
        listOfGuitarNumbers = [None, None, None, None, None]
        for dir in marketdir.iterdir():
            # Для каждого пути получаем все файлы
            k = len(list(dir.iterdir())) // 2
            n = dir.name

            # В зависимости от имени папки мы присваиваем количество элементов,
            # Чтобы всё было по порядку
            if n == 'komissionchick': listOfGuitarNumbers[0] = k
            elif n == 'muztorg': listOfGuitarNumbers[1] = k
            elif n == 'avito': listOfGuitarNumbers[2] = k
            elif n == 'lovecnot': listOfGuitarNumbers[3] = k
            elif n == 'jazzshop': listOfGuitarNumbers[4] = k

        return listOfGuitarNumbers
    
    # Получаем информацию о гитаре
    def getInfo(self, guitartag):
        # guitartag[0] - номер файла, guitartag[1] - название папки
        file, shop = str(guitartag[0]) + ".txt", guitartag[1]
        dir = ''
        if shop == 'komissionchick':  dir = markets[1]
        elif shop == 'muztorg':  dir = markets[2]
        elif shop == 'avito':  dir = markets[3]
        elif shop == 'lovecnot':  dir = markets[4]
        elif shop == 'jazzshop':  dir = markets[5]

        # Получаем информацию
        with open(dir / file, encoding='utf-8') as f:
            l = [line.rstrip() for line in f.readlines()]
            return [l[0], l[1], l[2], l[4], marketdir / f"{guitartag[1]}" / f"{str(guitartag[0])}.jpg"]