from __future__ import print_function
import os
import sys
import operator
from tkinter import scrolledtext, filedialog


def null_decorator(ob):
    return ob

if sys.version_info >= (3,2,0):
    import functools
    my_cache_decorator = functools.lru_cache(maxsize=4096)
else:
    my_cache_decorator = null_decorator

@my_cache_decorator
def get_dir_size(start_path = '.'):
    total_size = 0
    if 'scandir' in dir(os):
        # using fast 'os.scandir' method (new in version 3.5)
        for entry in os.scandir(start_path):
            if entry.is_dir(follow_symlinks = False):
                try:
                    total_size += get_dir_size(entry.path)
                except:
                    pass
            elif entry.is_file(follow_symlinks = False):
                total_size += entry.stat().st_size
    else:
        # using slow, but compatible 'os.listdir' method
        for entry in os.listdir(start_path):
            full_path = os.path.abspath(os.path.join(start_path, entry))
            if os.path.isdir(full_path):
                total_size += get_dir_size(full_path)
            elif os.path.isfile(full_path):
                total_size += os.path.getsize(full_path)
    return total_size

def get_dir_size_walk(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def bytes2human(n, format='%(value).0f%(symbol)s', symbols='customary'):
    SYMBOLS = {
        'customary'     : ('B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'),
        'customary_ext' : ('byte', 'kilo', 'mega', 'giga', 'tera', 'peta', 'exa',
                           'zetta', 'iotta'),
        'iec'           : ('Bi', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi'),
        'iec_ext'       : ('byte', 'kibi', 'mebi', 'gibi', 'tebi', 'pebi', 'exbi',
                           'zebi', 'yobi'),
    }
    n = int(n)
    if n < 0:
        raise ValueError("n < 0")
    symbols = SYMBOLS[symbols]
    prefix = {}
    for i, s in enumerate(symbols[1:]):
        prefix[s] = 1 << (i+1)*10
    for symbol in reversed(symbols[1:]):
        if n >= prefix[symbol]:
            value = float(n) / prefix[symbol]
            return format % locals()
    return format % dict(symbol=symbols[0], value=n)


if __name__ == '__main__':


    from tkinter import *


    def clicked():
        folder = txt.get()
        start_dir = os.path.normpath(os.path.abspath(sys.argv[1])) if len(sys.argv) > 1 else folder
        dir_tree = {}
        get_size = get_dir_size

        for root, dirs, files in os.walk(start_dir):
            for d in dirs:
                dir_path = os.path.join(root, d)
                if os.path.isdir(dir_path):
                    try:
                        dir_tree[dir_path] = get_size(dir_path)
                    except:
                        pass

        prev = []
        global lbl
        lbl.destroy()
        lbl = scrolledtext.ScrolledText(window, width=60, height=30, font=("Consolas", 12, "bold"))  # Поле с файлами
        lbl.grid(column=0, row=1)  # Расположение списка файлов
        diag_max_name = []
        diag_max_size = []
        all_size = 0
        for d, size in sorted(dir_tree.items(), key=operator.itemgetter(0)):
            tire = ''
            new_d = d.replace(start_dir + '\\', '')
            rp = False
            for i in reversed(prev):
                if i + '\\' in d:
                    tire += '|'
                    if not rp:
                        new_d = d.replace(i + '\\', '')
                        rp = True
            lbl.insert(INSERT, '%s\t%s%s' % (bytes2human(size, format='%(value).2f%(symbol)s'), tire, new_d) + "\n", size)
            if size in (range(0, 1000)):
                colors = "cyan3"
            elif size in (range(1001, 10000)):
                colors = "SeaGreen3",
            elif size in (range(10001, 100000)):
                colors = "PaleGreen3"
            elif size in (range(100001, 1000000)):
                colors = "chartreuse3"
            elif size in (range(1000001, 10000000)):
                colors = "DarkOliveGreen3"
            elif size in (range(10000001, 100000000)):
                colors = "goldenrod3"
            elif size in (range(100000001, 1000000000)):
                colors = "chocolate3"
            elif size in (range(1000000001, 10000000000)):
                colors = "firebrick3"
            else:
                colors = 'red'
            lbl.tag_config(size, background=colors)
            output = ''
            prev.append(d)

        for d, size in sorted(dir_tree.items(), key=operator.itemgetter(1), reverse=True):
            addd = True
            for x in diag_max_name:
                if x in d:
                    addd = False
            if addd:
                diag_max_name.append(d)
                diag_max_size.append(size)
                all_size += size
            if len(diag_max_name) == 10:
                break
        for i in range(len(diag_max_size)):
            diag_max_size[i] = diag_max_size[i] / all_size

        lst = window.grid_slaves()
        for i in lst:
            if i.winfo_name() == 'entry':
                i.destroy()
        fig2 = Figure()  # Создаем объект фигуры для диаграммы
        ax2 = fig2.add_subplot()  # Добавляем координатную плоскость
        ax2.pie(diag_max_size, radius=1, labels=diag_max_name, autopct='%0.2f%%',
               shadow=True)  # Создание круговой диаграммы
        chart2 = FigureCanvasTkAgg(fig2, window)  # Добавление круговой диаграммы на окно
        chart2.get_tk_widget().grid(column=1, row=1)  # Расположение круговой диаграммы


    window = Tk()
    window.title("Программа построения графической карты разделов диска")

    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure

    stockListExp = ['AMZN', 'AAPL', 'JETS', 'CCL', 'NCLH']  # Указываем название областей диаграммы
    stockSplitExp = [15, 25, 40, 10, 10]  # Указывает процентное соотношение в диаграмме

    fig = Figure()  # Создаем объект фигуры для диаграммы
    ax = fig.add_subplot()  # Добавляем координатную плоскость

    ax.pie(stockSplitExp, radius=1, labels=stockListExp, autopct='%0.2f%%', shadow=True)  # Создание круговой диаграммы

    chart1 = FigureCanvasTkAgg(fig, window)  # Добавление круговой диаграммы на окно

    def browse_button():
        filename = filedialog.askdirectory()
        txt.config(text=filename)

    txt = Entry(window, width=50)  # Поле ввода пути к папке
    txt.grid(column=0, row=0)  # Расположение указателя пути
    lbl = scrolledtext.ScrolledText(window, width=60, height=30, font=("Consolas", 12, "bold"))  # Поле с файлами
    lbl.grid(column=0, row=1)  # Расположение списка файлов
    btn = Button(window, text="Вычислить!", command=clicked)  # Кнопка сканирования
    button2 = Button(text="Выбрать папку", command=browse_button).grid(row=0, column=3) # Кнопка выбора пути к папке
    btn.grid(column=2, row=0)  # Расположение кнопки сканирования
    chart1.get_tk_widget().grid(column=1, row=1)  # Расположение круговой диаграммы

    window.mainloop()



