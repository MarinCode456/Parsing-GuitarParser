import folder
import config
import p_komi
import p_muztorg
import p_avito 
import p_lovec
import p_jazz
import time

# Создаём папки для каждого магазина
try:
    m = folder.manager()
    m.createFolders()
except Exception as e:
    print("    *[GuitarParser] Произошла ошибка при подключении модуля папок")
    print(e)

# Создаём конфиг
try:
    config.createConfigFile()
    print("[GuitarParser] Файл конфига успешно создан\n")
except:
    print("    *[GuitarParser] Произошла ошибка при создании файла конфига")
    print(e)

# Функция, которая выводит затраченное время
def printRunTime(start, end):
    difference = end - start
    minutes = int(difference//60)
    seconds = int(difference - minutes*60)
    if seconds < 10: seconds = f"0{seconds}"
    print(f"    [GuitarParser] Скрипт выполнился за {minutes}:{seconds}\n")

# Все функции ниже собирают гитары с магазинов
def komi():
    print("\n[GuitarParser] Начинаю скачивать гитары с коммисиончика")

    start = time.time()
    p_komi.getGuitars()
    end = time.time()
    printRunTime(start, end)

    print("    [GuitarParser] Гитары с комиссиончика уже в папке!\n\n")

def muz():
    print("\n[GuitarParser] Начинаю скачивать гитары с музторга")

    start = time.time()
    p_muztorg.getGuitars()
    end = time.time()
    printRunTime(start, end)

    print("    [GuitarParser] Гитары с музторга уже в папке!\n\n")

def avito():
    print("\n[GuitarParser] Начинаю скачивать гитары с авито")

    start = time.time()
    p_avito.getGuitars()
    end = time.time()
    printRunTime(start, end)

    print("    [GuitarParser] Гитары с авито уже в папке!\n\n")

def lovec():
    print("\n[GuitarParser] Начинаю скачивать гитары с ловца нот")

    start = time.time()
    p_lovec.getGuitars()
    end = time.time()
    printRunTime(start, end)

    print("    [GuitarParser] Гитары с ловца нот уже в папке!\n\n")

def jazz():
    print("\n[GuitarParser] Начинаю скачивать гитары с джаз шопа")

    start = time.time()
    p_jazz.getGuitars()
    end = time.time()
    printRunTime(start, end)

    print("    [GuitarParser] Гитары с джаз шопа уже в папке!\n\n")



# Место вызова функции main
def main():
    while True:
        print('''\nИтак, ты попал в программу для сбора всех гитар с 5-ти магазинов. Вот мои команды:
              
1. Получить все гитары с 5-и магазинов
2. Получить гитары с Комиссиончика
3. Получить гитары с Музторга
4. Получить гитары с Авито
5. Получить гитары с Ловца Нот
6. Получить гитары с Джаз Шопа
7. Изменить настройки поиска
''')
        choice = input("Введи номер команды: ")
        
        # Не позволяем ввести что-то кроме 1-7
        try:
            choice = int(choice)
            if not (1 <= choice <= 7):
                print("Я тебя не понял\n")
                continue
        except:
            print("Я тебя не понял\n")
            continue

        # Если мы здесь, номер команды верный
        match choice:
            case 1: komi(); muz(); avito(); lovec(); jazz()
            case 2: komi()
            case 3: muz()
            case 4: avito()
            case 5: lovec()
            case 6: jazz()
            case 7:
                while True:
                    print('''\nВыберите какому магазину изменить предельную стоимость:
                          
1. Комиссиончик
2. Музторг
3. Авито
4. Ловец Нот
5. Джаз Шоп
6. Выйти из меню настроек
''')
                    config_choice = input("Введите номер: ")

                    # Проверка правильности ввода
                    try:
                        config_choice = int(config_choice)
                        if not (1 <= config_choice <= 6):
                            print("Я тебя не понял")
                            continue
                    except:
                        print("Я тебя не понял")
                        continue

                    # Если мы здесь, номер команды верный
                    match config_choice:
                        case 1: 
                            komi_upper_value = input("Введите предельную стоимость гитар с комиссиончика: ")
                            
                            # Проверка является ли ввод числом
                            try: 
                                komi_upper_value = int(komi_upper_value)
                                config.set_value(komi=f"{komi_upper_value}")
                                print("Успешно!")
                            except:
                                print("Я тебя не понял")
                                continue
                        case 2: 
                            muztorg_upper_value = input("Введите предельную стоимость гитар с музторга: ")
                            
                            # Проверка является ли ввод числом
                            try: 
                                muztorg_upper_value = int(muztorg_upper_value)
                                config.set_value(muztorg=f"{muztorg_upper_value}")
                                print("Успешно!")
                            except:
                                print("Я тебя не понял")
                                continue
                        case 3: 
                            avito_upper_value = input("Введите предельную стоимость гитар с авито: ")
                            
                            # Проверка является ли ввод числом
                            try: 
                                avito_upper_value = int(avito_upper_value)
                                config.set_value(avito=f"{avito_upper_value}")
                                print("Успешно!")
                            except:
                                print("Я тебя не понял")
                                continue
                        case 4: 
                            lovec_upper_value = input("Введите предельную стоимость гитар с ловца нот: ")
                            
                            # Проверка является ли ввод числом
                            try: 
                                lovec_upper_value = int(lovec_upper_value)
                                config.set_value(lovec=f"{lovec_upper_value}")
                                print("Успешно!")
                            except:
                                print("Я тебя не понял")
                                continue
                        case 5: 
                            jazz_upper_value = input("Введите предельную стоимость гитар с джаз шопа: ")
                            
                            # Проверка является ли ввод числом
                            try: 
                                jazz_upper_value = int(jazz_upper_value)
                                config.set_value(jazz=f"{jazz_upper_value}")
                                print("Успешно!")
                            except:
                                print("Я тебя не понял")
                                continue
                        case 6: break

''' Эта проверка позволяет запускать скрипт только если его запустили напрямую
Например, если импортировать этот скрипт, то ничего не произойдет, так как
Только при открытии напрямую в переменную __name__ передается строка "__main__"'''
if __name__ == "__main__":
    main()