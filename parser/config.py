from pathlib import Path

current_file = Path(__file__)
gendir = current_file.parent
configdir = gendir / "config.txt"

# Значения по умолчанию
default = "DEFAULT"
default_strings = [f"komi_upper_value: {default}\n",
f"muztorg_upper_value: {default}\n"
f"avito_upper_value: {default}\n"
f"lovec_upper_value: {default}\n"
f"jazz_upper_value: {default}"]

# Перезаписываем конфиг на дефолтный
def reload_config():
    with open(configdir, 'w') as file: file.write(''.join(default_strings))
    print("[GuitarParser] Строчки конфига были перезаписаны, так как не удовлетворяют условию программы")

# Меняем значения в конфиге
def set_value(komi="DEFAULT", muztorg="DEFAULT", avito="DEFAULT", lovec="DEFAULT", jazz="DEFAULT"):
    # Получаем старые строчки конфига
    with open(configdir, 'r') as file: strings = file.readlines()

    # Если по умолчанию в переменной содержится Default, то мы ничего не меняем в строчке
    # Но если передано какое-то другое значение, то меняем
    if komi != "DEFAULT": strings[0] = f"komi_upper_value: {komi}\n"
    if muztorg != "DEFAULT": strings[1] = f"muztorg_upper_value: {muztorg}\n"
    if avito != "DEFAULT": strings[2] = f"avito_upper_value: {avito}\n"
    if lovec != "DEFAULT": strings[3] = f"lovec_upper_value: {lovec}\n"
    if jazz != "DEFAULT": strings[4] = f"jazz_upper_value: {jazz}"

    with open(configdir, 'w') as file: file.write(''.join(strings))

# Создание файла конфига
def createConfigFile():
    ''' Вызывается перед каждым открытием файла main.py
    Если конфиг не создан, либо какие-то его поля имеют неверное значение, то он перезаписывается.'''

    if not configdir.exists():
        # Если файла нет, создаём его
        with open(configdir, 'w') as file:
            file.write(''.join(default_strings))

    else:
        # config.txt существует, проверим его на верность значений
        with open(configdir, 'r') as file: strings = [line.rstrip() for line in file.readlines()]
        names = ['komi_upper_value:', 'muztorg_upper_value:', 'avito_upper_value:', 'lovec_upper_value:', 'jazz_upper_value:']

        # Собираем значения из конфига
        config_names, config_values = [], []
        for s in strings:
            name_value = s.split(' ')
            config_names.append(name_value[0])
            config_values.append(name_value[1])

            # Если значений у этой переменной больше, то мы перезаписываем конфиг, так как это неверно
            if len(name_value) > 2: 
                reload_config()
                return

        # Проверка значений
        if names != config_names: 
            reload_config()
            return

        # Проверка численных значений
        for value in config_values:
            # Если значение не дефолтное и не является числом, мы перезаписываем конфиг
            if (value != 'DEFAULT') and not (value.isdigit()): 
                reload_config()
                return

# Получаем все строчки конфига
def getConfigLines():
    with open(configdir, 'r') as file: lines = [line.rstrip() for line in file.readlines()]
    return lines

# Функции для получения значения для каждого магазина
def getKomiValue(): return getConfigLines()[0].split(' ')[1]
def getMuztorgValue(): return getConfigLines()[1].split(' ')[1]
def getAvitoValue(): return getConfigLines()[2].split(' ')[1]
def getLovecValue(): return getConfigLines()[3].split(' ')[1]
def getJazzValue(): return getConfigLines()[4].split(' ')[1]