# Модуль, отвечающий за работу с папками и файлами

from pathlib import Path
import shutil

# Вспомогательные переменные
currentfile = Path(__file__)
generaldir = currentfile.parent.parent
marketdir = generaldir / "markets"

class manager:
    # Функция создания каждой папки для каждого магазина, если их нет
    def createFolders(self):
        markets = [marketdir, marketdir / "komissionchick", marketdir / "muztorg", marketdir / "avito", marketdir / "lovecnot", marketdir / "jazzshop"]

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