import os
import subprocess
from cryptography.fernet import Fernet
from pyperclip import copy
from zipfile import ZipFile
from shutil import rmtree


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
            print('something went wrong')
    return x


the_hidden_file_name = ':encrypted'
location = os.getcwd()
the_test = b'this is a test to test if the file is encrypted or decrypted'


def show_important_file():
    os.system(f'attrib -h -s {location}\\Private\\dont_delete')


def hide_important_file():
    os.system(f'attrib +h +s {location}\\Private\\dont_delete')


def dec(key, path):
    if os.path.isdir(path):
        if os.listdir(path):
            for f in os.listdir(path):
                dec(key, f'{path}\\{f}')
            return
        else:
            return
    show_important_file()
    data = with_open(path, 'rb')
    with_open(path, 'wb', Fernet(key).decrypt(data))
    hide_important_file()


def enc(key, path):
    if os.path.isdir(path):
        if os.listdir(path):
            for f in os.listdir(path):
                enc(key, f'{path}\\{f}')
            return
        else:
            return
    show_important_file()
    data = with_open(path, 'rb')
    encrypted = Fernet(key).encrypt(data)
    with_open(path, 'wb', encrypted)
    hide_important_file()


def verify_pass(key):
    if key:
        data = with_open('Private\\dont_delete', 'rb')
        try:
            if Fernet(key).decrypt(data) == the_test:
                return True
            else:
                return False
        except Exception as e:
            print(f"an error was accord: {e}")
            return False


def new():
    password = Fernet.generate_key()

    os.mkdir('Private')

    with_open('Private\\password(dont_delete).txt', 'wb', password)

    os.system(f'attrib +r {location}\\Private\\password(dont_delete).txt')

    with_open('Private\\dont_delete', 'wb', the_test)

    enc(password, 'Private\\dont_delete')

    hide_important_file()

    copy(password.decode())

    print('password copied to clipboard keep it somewhere safe')

    password = input('verify the password\n>')

    while not verify_pass(password):
        password = input('verify the password\n>')
        print('try again')

    dec(password, 'Private\\dont_delete')


def check_if_secret_file_exist():
    return subprocess.getoutput(f'dir /r {location}').find(the_hidden_file_name) > 0


def write_zip(path, zip_file):
    if os.path.isdir(path):
        for f in os.listdir(path):
            write_zip(f'{path}\\{f}', zip_file)
        return
    zip_file.write(path)


def make_zip_n_encrypt():
    file = "Private.zip"
    password = with_open('Private\\password(dont_delete).txt', 'r').encode()
    with ZipFile(file, 'w') as Zip:
        for x in os.listdir('Private'):
            enc(password, 'Private\\' + x)
            write_zip('Private\\' + x, Zip)
    rmtree('Private')


def delete_n_hide():
    output = input('are you sure you want to lock your files?\n[Y,N]\n>')
    if output == 'y' or output == 'Y':
        make_zip_n_encrypt()
        os.system(f'type {location}\\{"Private.zip"} > {location}{the_hidden_file_name}')
        os.remove('Private.zip')


def export_zip():
    with ZipFile('Private.zip', 'r') as Zip:
        for x in Zip.filelist:
            Zip.extract(Zip.getinfo(x.filename))


def dec_files(key):
    password = key.encode()
    for file in os.listdir('Private'):
        dec(password, 'Private\\' + file)


def export():
    a = with_open(the_hidden_file_name, 'rb')
    os.remove(the_hidden_file_name)
    with_open('Private.zip', 'wb', a)
    export_zip()
    os.remove('Private.zip')
    check_n_dec()
    hide_important_file()


def check_n_dec():
    password = ''
    while not verify_pass(password):
        password = input('enter the password:\n>')
        print('try again')
    dec_files(password)


if check_if_secret_file_exist():
    export()
elif os.path.exists('Private'):
    if with_open('Private\\dont_delete', 'rb') == the_test:
        delete_n_hide()
    else:
        check_n_dec()
else:
    new()
