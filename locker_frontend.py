from tkinter import Tk, ttk, Toplevel, TclError

title_style = ('bold', 20)

icon = __file__[:__file__.rfind('\\')] + '\\lock.ico'


class main_window:
    def __init__(self):
        self.root = Tk()
        self.all_variables = {}

    def create(self):
        self.root.resizable(False, False)
        self.root.eval('tk::PlaceWindow . center')
        self.root.iconbitmap(icon)
        self.root.title('locker')
        return self.root

    def add_button(self, x: int or float, y: int or float, func, text: str, anchor='center', variables: tuple = ()):

        b = ttk.Button(self.root, text=text, command=lambda: [func(*variables), func][variables == ()])

        b.place(relx=x/10, rely=y/10, anchor=anchor)

    def add_text(self, x: int or float, y: int or float,  text: str, anchor: str='center'):
        ttk.Label(self.root, text=text, font='Mont_Blanc 11 bold').place(relx=x/10, rely=y/10, anchor=anchor)

    def mainloop(self):
        self.root.mainloop()


class LoadingScreen:
    def __init__(self, main: Tk):
        self.main = main
        self.title = None
        self.progressbar = None
        self.text = None
        self.maximum = None
        self.other = None
        self.action = None
        self.root = Toplevel(main)

    def new(self, maximum: int, title: str, other: str):
        # define window

        self.root.iconbitmap(icon)

        self.root.geometry('200x150')

        self.root.resizable(False, False)

        self.root.title(f'{title}...')

        self.title = title
        self.other = other

        self.progressbar = ttk.Progressbar(self.root, maximum=maximum)
        self.progressbar.place(relx=0.5, rely=0.5, anchor='center', height=35, width=150)

        ttk.Label(self.root, text=f'{title}...', font=title_style).place(relx=0.5, rely=0, anchor='n')

        self.text = ttk.Label(self.root, text=f'{other}: [0/{maximum}]')
        self.text.place(relx=0.5, rely=1, anchor='s')

        self.action = ttk.Label(self.root, text='', background='#07d62d')
        self.action.place(relx=0.5, rely=0.5, anchor='center')

    def mainloop(self):
        self.root.mainloop()

    def update(self, add: list[str, float], action: str = ''):
        try:
            maximum = self.progressbar['maximum']

            self.text['text'] = f'{self.other}: {add[0]} \n [{(self.progressbar["value"])}/{float(maximum)}]'

            self.progressbar['value'] += add[1]
            if action:
                self.action['text'] = 'action: ' + action

            self.root.update()
        except TclError:
            try:
                self.root.destroy()
                self.main.update()
            except TclError:
                exit()


def ask_password(title: str, win: Tk or main_window):

    win.iconbitmap(icon)

    if type(win) == main_window:
        # define window
        root = Toplevel(win.root)
    else:
        root = win
    root.title(title)
    root.geometry('200x200')
    root.resizable(False, False)

    entry = ttk.Entry(root)
    ttk.Label(root, text=title).place(relx=0.5, rely=0.4, anchor='center')
    entry.place(relx=0.5, rely=0.5, anchor='center')

    def des():
        root.quit()

    ttk.Button(root, text='ok', command=des).place(relx=0.5, rely=0.65, anchor='center')
    root.mainloop()
    a = entry.get()
    root.destroy()
    return a


