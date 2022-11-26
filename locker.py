import os
import subprocess
from base64 import urlsafe_b64encode
from shutil import rmtree
from zipfile import ZipFile
from tkinter import messagebox, filedialog
from cryptography import fernet
from cryptography.fernet import Fernet
import locker_frontend as frontend
from sys import exit

def is_password_valid(password):
    def err(error: str):
        frontend.password = ''
        messagebox.showerror('', error)

    if password.isascii() and 32 >= len(password) >= 8:
        return True
    else:
        if len(password) == 0:
            exit()
        elif not password.isascii():
            err('the password must be with ascii characters only')
        elif not len(password) >= 8:
            err('the password must be equal or more then 8 letters')
        elif not 32 >= len(password):
            err('the password must be equal or less then 32 letters')

        return False


def ask_password(title: str, is_ret: bool = False):

    if not is_ret:
        messagebox.showinfo('note', f'''the password must be:
equal or more then 8 letters
equal or less then 32 letters
with ascii characters only''')
    main_win = frontend.Tk()
    main_win.attributes('-topmost', True)
    password = frontend.ask_password(title, main_win)
    if is_password_valid(password):
        return password
    else:
        return ask_password('try again', True)


def generate_password(password):
    password = password.encode()

    password = password + ((32 - len(password)) * b'-')

    password = urlsafe_b64encode(password)

    return password


def with_open(path: str, mode: str, write_to: any = None):
    """
    is opening a file so errors won't pop up
    :param path: the path you want to enter
    :param mode: enter the mode you need for the file
    :param write_to: use only if you're using a mode to edit a file,
    enter the string or bytes to edit the file
    :return: if you entered r mode it will return what it read
    """
    x = b''
    with open(path, mode) as file:
        if file.writable():
            file.write(write_to)
        elif file.readable():
            x = file.read()
        else:
            messagebox.showinfo('', 'something went wrong')
    return x

def check_if_secret_file_exist():
    return subprocess.getoutput(f'dir /r {location}').find(the_hidden_file_name) > 0


the_hidden_file_name = ':encrypted'
path = os.getcwd()
location = ''
if os.path.exists(path + '\\location'):
    location = with_open(path + '\\location', 'r')
else:
    messagebox.showinfo('', 'choose the directory you put the Private directory into')

    while location == '':
        location = filedialog.askdirectory()

    with_open(path + '\\location', 'w', location)
the_test = b'this is a test to test if the file is encrypted or decrypted'


def hide_important_file():
    os.system(f'attrib -h -s "{location}\\Private\\dont_delete"')
    os.system(f'attrib -h -s "{location}\\Private\\password(dont_delete)"')


def show_important_file():
    os.system(f'attrib +h +s "{location}\\Private\\dont_delete"')
    os.system(f'attrib +h +s "{location}\\Private\\password(dont_delete)"')


def change_password():
    password = ask_password('set the new password')
    hide_important_file()
    with_open(location + '\\Private\\password(dont_delete)', 'w', password)
    show_important_file()


def dec(key, path):
    if os.path.isdir(path):
        if os.listdir(path):
            for f in os.listdir(path):
                dec(key, f'{path}\\{f}')
            return
        else:
            return
    hide_important_file()
    data = with_open(path, 'rb')
    with_open(path, 'wb', Fernet(key).decrypt(data))
    show_important_file()


def enc(key, path):
    if os.path.isdir(path):
        if os.listdir(path):
            for f in os.listdir(path):
                enc(key, f'{path}\\{f}')
            return
        else:
            return
    hide_important_file()
    data = with_open(path, 'rb')
    encrypted = Fernet(key).encrypt(data)
    with_open(path, 'wb', encrypted)
    show_important_file()


def verify_pass(key):
    if key != urlsafe_b64encode(b'-'*32):
        data = with_open(location + '\\Private\\dont_delete', 'rb')
        try:
            decrypted = Fernet(key).decrypt(data)
            if decrypted == the_test:
                messagebox.showinfo('', 'password correct!!!')
                return True
            else:
                return False
        except fernet.InvalidToken:
            messagebox.showwarning('wrong password', f"wrong password\nplease try again")
            return False


def new():
    the_password = ask_password('set password')

    password = generate_password(the_password)

    os.mkdir(location + '\\Private')

    with_open(location + '\\Private\\password(dont_delete)', 'w', the_password)

    with_open(location + '\\Private\\dont_delete', 'wb', the_test)

    enc(password, location + '\\Private\\dont_delete')

    show_important_file()

    password = generate_password(ask_password('verify the password'))

    while not verify_pass(password):
        password = generate_password(ask_password('verify the password'))

    dec(password, location + '\\Private\\dont_delete')


def write_zip(path, zip_file):
    if os.path.isdir(path):
        for f in os.listdir(path):
            write_zip(f'{path}\\{f}', zip_file)
        return
    zip_file.write(path)


def make_zip_n_encrypt():
    file = location + "Private.zip"
    hide_important_file()
    password = generate_password(with_open(location + '\\Private\\password(dont_delete)', 'r'))
    show_important_file()
    with ZipFile(file, 'w') as Zip:
        for x in os.listdir(location + '\\Private'):
            enc(password, location + '\\Private\\' + x)
            write_zip(location + '\\Private\\' + x, Zip)
    rmtree(location + '\\Private')


def delete_n_hide(main_win: frontend.main_window):
    output = messagebox.askyesno('are you sure?', 'are you sure you want to lock your files?')
    if output:
        make_zip_n_encrypt()
        os.system(f'type "{location}\\Private.zip" > "{location}\\{the_hidden_file_name}"')
        os.remove(location + '\\Private.zip')
        messagebox.showinfo('', 'files where locked successfully')
        main_win.root.destroy()


def export_zip():
    with ZipFile(location + '\\Private.zip', 'r') as Zip:
        for x in Zip.filelist:
            Zip.extract(Zip.getinfo(x.filename))


def dec_files(key):
    password = key
    for file in os.listdir(location + '\\Private'):
        dec(password, location + '\\Private\\' + file)


def export():
    a = with_open(the_hidden_file_name, 'rb')
    os.remove(the_hidden_file_name)
    with_open(location + '\\Private.zip', 'wb', a)

    export_zip()
    os.remove(location + '\\Private.zip')
    check_n_dec()
    show_important_file()


def check_n_dec():
    password = generate_password('')
    while not verify_pass(password):
        password = generate_password(ask_password('enter password'))

    dec_files(password)


if check_if_secret_file_exist():
    export()
elif os.path.exists(location + '\\Private'):
    show_important_file()
    if with_open(location + '\\Private\\dont_delete', 'rb') == the_test:
        hide_important_file()
        main = frontend.main_window()
        main.create()
        main.add_text(5, 2, 'What do You want to do?', anchor='n')
        main.add_button(5, 4.5, delete_n_hide, 'lock files', variables=(main,))
        main.add_button(5, 6, change_password, 'change password')
        main.mainloop()
    else:
        hide_important_file()
        check_n_dec()
else:
    new()
