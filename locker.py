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


def with_open(path_of_file_or_dir: str, mode: str, write_to: any = None):
    """
    is opening a file so errors won't pop up
    :param path_of_file_or_dir: the path you want to enter
    :param mode: enter the mode you need for the file
    :param write_to: use only if you're using a mode to edit a file,
    enter the string or bytes to edit the file
    :return: if you entered r mode it will return what it read
    """
    x = b''
    with open(path_of_file_or_dir, mode) as file:
        if file.writable():
            file.write(write_to)
        elif file.readable():
            x = file.read()
        else:
            messagebox.showinfo('', 'something went wrong')
    return x


def check_if_secret_file_exist():
    return subprocess.getoutput(f'dir /r "{location}"').find(the_hidden_file_name) > 0


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
    os.system(f'attrib +h +s "{location}\\Private\\dont_delete"')
    os.system(f'attrib +h +s "{location}\\Private\\password(dont_delete)"')


def show_important_file():
    os.system(f'attrib -h -s "{location}\\Private\\dont_delete"')
    os.system(f'attrib -h -s "{location}\\Private\\password(dont_delete)"')


def change_password():
    current_pass = ask_password('enter current password')
    while not verify_pass(generate_password(current_pass)):
        current_pass = ask_password('enter current password')

    new_password = ask_password('set the new password')

    new_password = Fernet(generate_password(new_password)).encrypt(new_password.encode())

    show_important_file()
    with_open(location + '\\Private\\password(dont_delete)', 'wb', new_password)
    hide_important_file()


def dec(key, path_of_file_or_dir):
    if os.path.isdir(path_of_file_or_dir):
        if os.listdir(path_of_file_or_dir):
            for f in os.listdir(path_of_file_or_dir):
                dec(key, f'{path_of_file_or_dir}\\{f}')
            return
        else:
            return
    show_important_file()
    data = with_open(path_of_file_or_dir, 'rb')
    with_open(path_of_file_or_dir, 'wb', Fernet(key).decrypt(data))
    hide_important_file()


def enc(key, path_of_file_or_dir):
    if os.path.isdir(path_of_file_or_dir):
        if os.listdir(path_of_file_or_dir):
            for f in os.listdir(path_of_file_or_dir):
                enc(key, f'{path_of_file_or_dir}\\{f}')
            return
        else:
            return
    show_important_file()
    data = with_open(path_of_file_or_dir, 'rb')
    encrypted = Fernet(key).encrypt(data)
    with_open(path_of_file_or_dir, 'wb', encrypted)
    hide_important_file()


def verify_pass(key, is_inc: bool = False):
    if key != urlsafe_b64encode(b'-'*32):
        data = with_open(location + '\\Private\\password(dont_delete)', 'rb')
        try:
            decrypted = Fernet(key).decrypt(data)
            if is_inc:
                decrypted = Fernet(key).decrypt(decrypted)
            if generate_password(decrypted.decode()) == key:
                messagebox.showinfo('', 'password correct!!!')
                return True
            else:
                messagebox.showwarning('wrong password', f"wrong password\nplease try again")
                return False
        except fernet.InvalidToken:
            messagebox.showwarning('wrong password', f"wrong password\nplease try again")
            return False


def new():
    the_password = ask_password('set password')

    password = generate_password(the_password)

    os.mkdir(location + '/Private')

    with_open(location + '/Private/password(dont_delete)', 'wb', Fernet(password).encrypt(the_password.encode()))

    with_open(location + '/Private/dont_delete', 'wb', the_test)

    hide_important_file()

    password = generate_password(ask_password('verify the password'))

    while not verify_pass(password):
        password = generate_password(ask_password('verify the password'))


def write_zip(path_of_file_or_dir, zip_file: ZipFile, relative_path):

    if os.path.isdir(path_of_file_or_dir):

        for f in os.listdir(path_of_file_or_dir):

            write_zip(f'{path_of_file_or_dir}\\{f}', zip_file, f'{relative_path}\\{f}')

        return
    zip_file.write(path_of_file_or_dir, arcname=relative_path)


def make_zip_n_encrypt():
    file = location + "\\Private.zip"
    show_important_file()
    password = generate_password(ask_password('enter password to lock files'))
    while not verify_pass(password):
        password = generate_password(ask_password('enter password to lock files'))
    hide_important_file()
    with ZipFile(file, 'w') as Zip:
        for x in os.listdir(location + '\\Private'):
            enc(password, location + '\\Private\\' + x)
            write_zip(location + '\\Private\\' + x, Zip, x)
    rmtree(location + '\\Private')


def delete_n_hide(main_win: frontend.main_window):
    output = messagebox.askyesno('are you sure?', 'are you sure you want to lock your files?')
    if output:
        make_zip_n_encrypt()
        os.system(f'type "{location}\\Private.zip" > "{location}{the_hidden_file_name}"')
        os.remove(location + '\\Private.zip')
        messagebox.showinfo('', 'files where locked successfully')
        main_win.root.destroy()


def export_zip():
    with ZipFile(location + '\\Private.zip', 'r') as Zip:
        for x in Zip.filelist:
            Zip.extract(Zip.getinfo(x.filename), location + '\\Private')


def dec_files(key):
    password = key
    for file in os.listdir(location + '\\Private'):
        dec(password, location + '\\Private\\' + file)


def export():
    a = with_open(location + the_hidden_file_name, 'rb')
    os.remove(location + the_hidden_file_name)
    with_open(location + '\\Private.zip', 'wb', a)
    export_zip()
    os.remove(location + '\\Private.zip')
    check_n_dec()
    hide_important_file()


def check_n_dec():
    password = generate_password('')
    while not verify_pass(password, True):
        password = generate_password(ask_password('enter password'))
    dec_files(password)


def start_explorer():
    loc_for_cmd = location.replace("/", "\\")
    os.system(f'start explorer {loc_for_cmd}\\Private')


if check_if_secret_file_exist():
    export()
    start_explorer()
elif os.path.exists(location + '\\Private'):
    hide_important_file()
    if with_open(location + '\\Private\\dont_delete', 'rb') == the_test:
        show_important_file()
        main = frontend.main_window()
        main.create()
        main.add_text(5, 2, 'What do You want to do?', anchor='n')
        main.add_button(5, 4.5, delete_n_hide, 'lock files', variables=(main,))
        main.add_button(5, 6, change_password, 'change password')
        main.mainloop()
    else:
        show_important_file()
        check_n_dec()
        start_explorer()
else:
    new()
    start_explorer()
