'''Здесь описываю всю работу приложения для просмотра гитар.

Решил не заморачиваться с размерами окна впоследствии, но сначала даже получилось реализовать
изменение размера главного логотипа вместе с основным окном. А потом я узнал, что можно вовсе
запретить изменять размер окна и это идеальное для меня решение.'''

import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from pathlib import Path
from contextlib import redirect_stdout
import os
from threading import Thread
import webbrowser

import main as parsing
import config
import folder



# Класс, позволяющий переводить поток вывода консоли в наш объект tk.Text
class TextWrapper:
    def __init__(self, text_filed):
        self.text_field = text_filed
    def write(self, text):
        self.text_field.insert(tk.END, text)
    def flush(self):
        self.text_field.update()
    


# Кнопка "Выход"
def button_quit():
    root.destroy()

# Переключение с меню на парсинг
def menu_to_parsing():
    disable_frame()
    enable_parsing()

# Переключение с меню на настройки
def menu_to_config():
    disable_frame()
    enable_config()

# Переключение с меню на галерею
def menu_to_gallery():
    # Получаем все гитары в кортеже, состоящем из 6 списков
    # 5 для каждого отдельного магазина, а 6 состоит из всех остальных
    guitars = manager.getGuitarsInList()
    global currentguitar
    currentguitar = [0, 'komissionchick']

    disable_frame()
    enable_gallery(guitars)

# Переключение с фрейма на меню
def oldframe_to_menu():
    disable_frame()
    enable_menu()

# Выключение любого фрейма в главном окне
def disable_frame():
    for frame in mainframe.winfo_children():
        frame.destroy()

def button_click(e):
    e.widget['background'] = 'red'

# Изменение магазина из выпадающего списка
def change_market(e, widgets, guitars):
    global currentguitar

    mainframe.focus()
    market = e.widget.get().lower()
    
    match(market):
        case "комиссиончик": currentguitar = [0, 'komissionchick']
        case "музторг": currentguitar = [0, 'muztorg']
        case "авито": currentguitar = [0, 'avito']
        case "ловец нот": currentguitar = [0, 'lovecnot']
        case "джаз шоп": currentguitar = [0, 'jazzshop']
    
    first_guitar = getGuitar(guitars)
    if first_guitar != None: showGuitar(first_guitar, widgets)



# Парсинг
def check_parsing(text_field):
    thread_function = Thread(target=mr_parsing, args=[text_field])
    thread_function.start()
def mr_parsing(text_field):
    with redirect_stdout(TextWrapper(text_field)):
        if komi_var.get() == 1: parsing.komi()
        if muztorg_var.get() == 1: parsing.muz()
        if avito_var.get() == 1: parsing.avito()
        if lovec_var.get() == 1: parsing.lovec()
        if jazz_var.get() == 1: parsing.jazz()

# Изменение предельной цены
def change_prices(*args):
    new_prices = []

    # Последовательно получаем весь список новых цен
    for entry in args:
        # Проверка на правильность ввода
        try:
            price = int(entry.get())
            new_prices.append(price)
        except:
            new_prices.append('DEFAULT')
        entry.delete(0, tk.END)

    # Меняем значения
    config.set_value(*new_prices)

# Обновление mr_console каждые 1000 млс
def update_console(console_frame, mr_console):
    mr_console.see('end')
    console_frame.after(200, update_console, console_frame, mr_console)

# Открытие папки с магазинами
def open_marketpath(): os.startfile(marketdir)



# Изменение значение currentguitar[0] в зависимости от переменной next
def nextFunc(g_number, g_len, next):
    '''Функция возвращает существующий номер гитары. Если же мы на 24 гитаре из 24, то
    она вернёт 24, и мы получим снова ту же гитару. В больших программах на этом этапе нужно
    было бы делать кнопку неактивной, но так как програмка небольшая, я решил оставить так.'''
    if next:
        # Берём следующую гитару
        if g_number + 1 > g_len: return g_number
        return g_number + 1
    else: 
        # Берём предыдущую
        if g_number - 1 <= 0: return g_number
        return g_number - 1

# Получение первой возможной гитары со списка с гитарами
def getGuitar(guitars, findInOther = True, next = True):
    # Если findInOther = True, то при безуспешном поиске гитары в комиссиончике, 
    # мы попытаемся найти гитару в другом магазине
    global currentguitar

    shop = currentguitar[1]
    if shop == 'komissionchick': currentguitar[0] = nextFunc(currentguitar[0], guitars[0], next)
    elif shop == 'muztorg': currentguitar[0] = nextFunc(currentguitar[0], guitars[1], next)
    elif shop == 'avito': currentguitar[0] = nextFunc(currentguitar[0], guitars[2], next)
    elif shop == 'lovecnot': currentguitar[0] = nextFunc(currentguitar[0], guitars[3], next)
    elif shop == 'jazzshop': currentguitar[0] = nextFunc(currentguitar[0], guitars[4], next)
    elif shop == 'allshops':
        # Если мы просматриваем все гитары, делаем отдельные действия
        pass

    # Если таких гитар вообще нет, просто возвращаем
    if currentguitar[0] == 0: return
    return manager.getInfo(currentguitar)

# Открывает ссылку на гитару в браузере
def callback(url): webbrowser.open_new(url)

# Проверяет, помещается ли слово в строку
def isFree47(string, word):
    return (len(string) + len(word)) < 47

# Разбивает одну большую строчку описания на более мелкие до 47 символов,
# при этом не разбивая одно и то же слово на разные строки
def get47Strings(lore):
    strings = []
    words = lore.split(" ")
    
    line = ""
    for word in words:
        if isFree47(line, word): 
            line += f"{word} "
        else: 
            strings.append(line)
            line = f"{word} "
    strings.append(line)

    return strings

# Отображение гитары на полученные виджеты
def showGuitar(guitarInfo, widgets, guitars=None, next = True):
    # Если нужно - получаем следующую гитару
    if guitars: guitarInfo = getGuitar(guitars, findInOther=True, next=next)
    if not guitarInfo: return

    # Получаем виджеты
    wid_name = widgets[0]
    wid_lores = widgets[1]
    wid_price = widgets[2]
    wid_link = widgets[3]
    wid_picture = widgets[4]

    # Выводим название, стоимость, задаём ссылку гитаре
    wid_name.config(text=f'◌ {guitarInfo[0]} ◌')
    wid_price.config(text=f'Стоимость: {guitarInfo[2]} р.')
    wid_link.config(text=f'Перейти на страницу товара')
    wid_link.bind('<Button-1>', lambda e: callback(guitarInfo[3]))

    # Выводим описание товара
    lore = guitarInfo[1]
    lore_strings = get47Strings(lore)

    # Очищаем все строчки от старой информации
    for label in wid_lores: label.config(text="")
    # Записываем лор по 47 символов в строку
    for i in range(0, len(wid_lores)):
        try:
            wid_lores[i].config(text=lore_strings[i])
        except:
            break
        
    # Выводим картинку
    pic = Image.open(guitarInfo[4])
    w, h = pic.size[0], pic.size[1]
    k = w/400
    new_w, new_h = int(w/k), int(h/k)

    pic = ImageTk.PhotoImage(pic.resize((new_w, new_h)))
    wid_picture.configure(image=pic)
    wid_picture.image = pic





# Включение меню с кнопками
def enable_menu():
    # Фрейм для логотипа и кнопок
    menu_frame = tk.Frame(master = mainframe, bg="#22272d")
    menu_frame.pack()
    menu_frame_options = tk.Frame(master = mainframe, bg="#22272d")
    menu_frame_options.pack()

    # Загружаем логотип
    logo = Image.open(logodir / "megalogo.jpg")
    logoimg = ImageTk.PhotoImage(logo)
    img_panel = tk.Label(master=menu_frame, image=logoimg, borderwidth=0)
    img_panel.image = logoimg
    img_panel.pack()

    # Создаём кнопки
    button1 = tk.Button(menu_frame, text='Парсинг', font='Intro', width=49, height=2, command=menu_to_parsing)
    button2 = tk.Button(menu_frame, text='Галерея', font='Intro', width=49, height=2, command=menu_to_gallery)
    button3 = tk.Button(menu_frame_options, text='Настройки', font='Intro', width=49, height=2, command=menu_to_config)
    button4 = tk.Button(menu_frame_options, text='Выход', font='Intro', width=49, height=2, command=button_quit)
    button1.pack(side='left', pady=(100, 0), padx=(0, 25))
    button2.pack(side='left', pady=(100, 0))
    button3.pack(side='left', pady=(20, 0), padx=(0, 25))
    button4.pack(side='left', pady=(20, 0))

# Включение фрейма с парсингом
def enable_parsing():
    # Фрейм для вывода сообщений из консоли
    console_frame = tk.Frame(master = mainframe, width=1280, height=475, bg="#22272d")
    console_frame.pack_propagate(0)

    # Вывод текста из консоли будет производиться именно сюда
    mr_console = tk.Text(master = console_frame, width=157, height=150, bg='#F5F5DC')
    mr_console.see("end")
    mr_console.pack()

    # Также добавляем функцию для вызова каждые 1000 млс
    update_console(console_frame, mr_console)
    console_frame.pack()

    # Фрейм для кнопки
    button_frame = tk.Frame(master = mainframe, bg="#22272d")
    button_frame.pack()

    # Кнопка для парсинга
    parse_button = tk.Button(master = button_frame, text='Начать парсинг', font='Intro', width=49, height=2, command=lambda: check_parsing(mr_console), bg="#373f4d", fg='#03dbfb')
    parse_button.pack(pady=(35,25))

    # Нижний фрейм для чекбоксов
    bottom_frame = tk.Frame(master = mainframe, bg='#F5F5DC')
    bottom_frame.pack()

    # Чекбоксы для каждого магазина
    komi_check = tk.Checkbutton(master = bottom_frame, text='Комиссиончик', bg="#22272d", foreground='#03dbfb', font='Intro', variable=komi_var)
    muztorg_check = tk.Checkbutton(master = bottom_frame, text='Музторг', bg="#22272d", foreground='#03dbfb', font='Intro', variable=muztorg_var)
    avito_check = tk.Checkbutton(master = bottom_frame, text='Авито', bg="#22272d", foreground='#03dbfb', font='Intro', variable=avito_var)
    lovec_check = tk.Checkbutton(master = bottom_frame, text='Ловец нот', bg="#22272d", foreground='#03dbfb', font='Intro', variable=lovec_var)
    jazz_check = tk.Checkbutton(master = bottom_frame, text='Джаз Шоп', bg="#22272d", foreground='#03dbfb', font='Intro', variable=jazz_var)
    komi_check.pack(side='left')
    muztorg_check.pack(side='left')
    avito_check.pack(side='left')
    lovec_check.pack(side='left')
    jazz_check.pack(side='left')

    # Фрейм ещё ниже для кнопок 'обратно' и 'папка'
    somebuttons_frame = tk.Frame(master = mainframe, bg="#22272d")
    somebuttons_frame.pack()

    # Сами эти кнопки-картинки
    back_button = tk.Button(master = somebuttons_frame, image=back_button_image, width=60, height=60, bg="#22272d", highlightthickness = 0, borderwidth=0, command=oldframe_to_menu)
    folder_button = tk.Button(master = somebuttons_frame, image=folder_button_image, width=60, height=60, bg="#22272d", highlightthickness = 0, borderwidth=0, command=open_marketpath)

    folder_button.pack(side='left', pady=(20,0), padx=(0, 10))
    back_button.pack(side='left', pady=(20,0), padx=(10, 0))

# Включение фрейма с настройками
def enable_config():
    # Фрейм со описанием настроек
    title_frame = tk.Frame(master=mainframe, bg="#22272d")
    title_frame.pack()

    # Фрейм со всеми названиями магазинов
    names_frame = tk.Frame(master=mainframe, bg="#22272d")
    names_frame.pack()

    # Фрейм со всеми окошками для ввода
    entrys_frame = tk.Frame(master=mainframe, bg="#22272d")
    entrys_frame.pack(pady=(0, 300))

    # Фрейм с кнопкой 'Изменить' и выходом
    base_frame = tk.Frame(master=mainframe, bg="#22272d")
    base_frame.pack()

    title = tk.Label(master = title_frame, font='Intro 15', bg="#22272d", fg='white', text='Здесь вы можете изменить максимальную стоимость гитары для каждого магазина\nДля этого введите в окошко магазина желаемую стоимость и нажмите «Изменить»')
    title.pack(pady=(50,125))

    komi_title = tk.Label(master=names_frame, font='Intro 15', bg="#22272d", fg='white', text='Коммисиончик', width=15)
    muz_title = tk.Label(master=names_frame, font='Intro 15', bg="#22272d", fg='white', text='Музторг', width=15)
    avito_title = tk.Label(master=names_frame, font='Intro 15', bg="#22272d", fg='white', text='Авито', width=15)
    lovec_title = tk.Label(master=names_frame, font='Intro 15', bg="#22272d", fg='white', text='Ловец нот', width=15)
    jazz_title = tk.Label(master=names_frame, font='Intro 15', bg="#22272d", fg='white', text='Джаз шоп', width=15)
    komi_title.pack(side='left')
    muz_title.pack(side='left')
    avito_title.pack(side='left')
    lovec_title.pack(side='left')
    jazz_title.pack(side='left')

    komi_entry = tk.Entry(master=entrys_frame, width=10, font='Intro')
    muz_entry = tk.Entry(master=entrys_frame, width=10, font='Intro')
    avito_entry = tk.Entry(master=entrys_frame, width=10, font='Intro')
    lovec_entry = tk.Entry(master=entrys_frame, width=10, font='Intro')
    jazz_entry = tk.Entry(master=entrys_frame, width=10, font='Intro')
    komi_entry.pack(side='left', padx=(0, 52))
    muz_entry.pack(side='left', padx=(52,50))
    avito_entry.pack(side='left', padx=(52,45))
    lovec_entry.pack(side='left', padx=52)
    jazz_entry.pack(side='left', padx=(52,0))

    change_button = tk.Button(master=base_frame, font='Intro', text='Изменить', bg="#373f4d", fg='#03dbfb', width=20, height=2, command=(lambda: change_prices(komi_entry, muz_entry, avito_entry, lovec_entry, jazz_entry)))
    back_button = tk.Button(master=base_frame, bg="#373f4d", fg='#03dbfb', image=back_button_image, width=45, height=45, command=oldframe_to_menu)
    change_button.pack(side='left', padx=(0, 35))
    back_button.pack(side='left')

# Включаем галерею
def enable_gallery(guitars):
    # Создаём 2 фрейма: первый - полностью под картинки, второй - под описание товара и кнопки переключения
    picture_frame = tk.Frame(master=mainframe, bg="#22272d", width=400, height=640, highlightbackground='#03dbfb', highlightthickness=1)
    picture_frame.pack(side='left', padx=50)
    picture_frame.pack_propagate(0)
    card_frame = tk.Frame(master=mainframe, bg="#22272d", width=750, height=640)
    card_frame.pack(side='left')

    # Ещё 2 фрейма внутри фрейма под описание товара: первый - описание, второй - кнопки переключения
    itemdesc_frame = tk.Frame(master=card_frame, bg='#22272d', width=750, height=440, highlightbackground='#03dbfb', highlightthickness=1)
    itemdesc_frame.pack_propagate(0)
    itemdesc_frame.pack(pady=(0,50))
    lr_frame = tk.Frame(master=card_frame, bg='#22272d', width=750, height=150)
    lr_frame.pack_propagate(0)
    lr_frame.pack()

    # Картинка гитары
    g_picture = tk.Label(master=picture_frame, border=0, width=400, height=640, bg="#22272d")
    g_picture.pack()

    # Название гитары
    g_name = tk.Label(master=itemdesc_frame, font='Intro 18', bg="#22272d", fg='white')
    g_name.pack(pady=(15, 30))

    '''Максимальная длина строки - 65 символов
    
    Здесь создаётся 7 разных лейблов для каждой новой строчки.
    Звучит бредово, но я не нашёл другого выхода. Виджет Text нельзя заблокировать для ввода без костылей,
    А при переносе в одном и том же label с помощью \n, следующие строчки находятся в центре, а не слева.
    Из-за этого приходится работать с этим:'''
    g_desc1 = tk.Label(master=itemdesc_frame, font='Intro 14', anchor='nw', text='', bg="#22272d", fg='white', width=54, height=1)
    g_desc2 = tk.Label(master=itemdesc_frame, font='Intro 14', anchor='nw', text='', bg="#22272d", fg='white', width=54, height=1)
    g_desc3 = tk.Label(master=itemdesc_frame, font='Intro 14', anchor='nw', text='', bg="#22272d", fg='white', width=54, height=1)
    g_desc4 = tk.Label(master=itemdesc_frame, font='Intro 14', anchor='nw', text='', bg="#22272d", fg='white', width=54, height=1)
    g_desc5 = tk.Label(master=itemdesc_frame, font='Intro 14', anchor='nw', text='', bg="#22272d", fg='white', width=54, height=1)
    g_desc6 = tk.Label(master=itemdesc_frame, font='Intro 14', anchor='nw', text='', bg="#22272d", fg='white', width=54, height=1)
    g_desc7 = tk.Label(master=itemdesc_frame, font='Intro 14', anchor='nw', text='', bg="#22272d", fg='white', width=54, height=1)
    g_price = tk.Label(master=itemdesc_frame, font='Intro 14', anchor='nw', text='', bg="#22272d", fg='white', width=54, height=1)
    g_link = tk.Label(master=itemdesc_frame, font='Intro 14', anchor='nw', text='', bg="#22272d", fg='#03dbfb', width=54, height=1)
    g_desc1.pack(padx=(20,0))
    g_desc2.pack(padx=(20,0))
    g_desc3.pack(padx=(20,0))
    g_desc4.pack(padx=(20,0))
    g_desc5.pack(padx=(20,0))
    g_desc6.pack(padx=(20,0))
    g_desc7.pack(padx=(20,0))
    g_price.pack(padx=(20,0))
    g_link.pack(padx=(20,0))

    widgets = [g_name, [g_desc1, g_desc2, g_desc3, g_desc4, g_desc5, g_desc6, g_desc7], g_price, g_link, g_picture]

    # Выпадающий список для выбора магазина
    listbox_value = tk.StringVar()
    g_listbox = ttk.Combobox(master=itemdesc_frame, textvariable=listbox_value, background="#22272d", foreground='white', font='Intro 14', state='readonly', values=['Комиссиончик', 'Музторг', 'Авито', 'Ловец нот', 'Джаз шоп'], width=15, height=6)
    g_listbox.bind('<<ComboboxSelected>>', lambda e: change_market(e, widgets, guitars))
    g_listbox.pack(padx=(33,0), anchor='nw', pady=(25,0))

    # Кнопки влево-вправо и назад
    left_button = tk.Button(master=lr_frame, image=left_button_image, background="#22272d", width=100, height=100, border=0, command=lambda: showGuitar([], widgets, guitars, next=False))
    right_button = tk.Button(master=lr_frame, image=right_button_image, background="#22272d", width=100, height=100, border=0, command=lambda: showGuitar([], widgets, guitars))
    back_button = tk.Button(master=lr_frame, image=back_button_image, background="#22272d", border=0, width=60, height=60, command=oldframe_to_menu)
    left_button.pack(side='left', padx=(247,0))
    right_button.pack(side='left', padx=(60,150))
    back_button.pack(side='left')

    # Получаем первую гитару для показа
    # Формат: название, описание, цена, ссылка, имя файла картинки
    first_guitar = getGuitar(guitars)
    if first_guitar != None:
        # Если хоть одна гитара есть, мы показываем её
        showGuitar(first_guitar, widgets)
    g_picture.update()





# Получаем главный каталог
currentfile = Path(__file__)
logodir = currentfile.parent / 'icons'
marketdir = currentfile.parent.parent / 'markets'

# Создаём основу приложения
root = tk.Tk()
root.title("Guitar Parser v2")
root.geometry('1280x720')
root.resizable(width=False, height=False)
root.iconbitmap(logodir / 'main_icon.ico')

# Переменные для чекбоксов магазинов
komi_var = tk.IntVar()
muztorg_var = tk.IntVar()
avito_var = tk.IntVar()
lovec_var = tk.IntVar()
jazz_var = tk.IntVar()

# Главный фрейм
mainframe = tk.Frame(master = root, bg="#22272d")
mainframe.pack(expand=True, fill='both')

# Картинки для некоторых кнопок
back_button_image = Image.open(logodir / 'back_button.png')
back_button_image = ImageTk.PhotoImage(back_button_image, width=60, height=60)
folder_button_image = Image.open(logodir / 'folder_button.png')
folder_button_image = ImageTk.PhotoImage(folder_button_image, width=60, height=60)
left_button_image = Image.open(logodir / 'left.png').resize((100,100))
left_button_image = ImageTk.PhotoImage(left_button_image)
right_button_image = Image.open(logodir / 'right.png').resize((100,100))
right_button_image = ImageTk.PhotoImage(right_button_image)

# Переменная, хранящая текущую показываемую гитару
currentguitar = [0, 'komissionchick']

# folder-manager
manager = folder.manager()

# Включаем основное меню и запускаем цикл
enable_menu()
root.mainloop()