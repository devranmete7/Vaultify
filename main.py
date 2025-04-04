# main.py
import os
import sys
import PySimpleGUI as sg
from src.user_management import login_window, change_password_window, profile_window, add_new_user
from src.folder_management import main_menu, folder_window
from src.encryption import generate_key, create_cipher
from src.kasa import kasa_window
from src.gui import folder_password_window

# Arayüz temasını ayarla
sg.theme('DarkTeal9')

# Kullanıcı bilgileri dosyası
KEY_FILE = 'kasa_anahtar.key'

# Ana program akışı
username, password = login_window(show_warning=True)
if not username or not password:
    sys.exit()

while True:
    choice = main_menu(username)
    if not choice:  # Çıkış butonuna basıldığında
        sg.popup('Görüşürüz!', title='Hoşça Kal', auto_close=True, auto_close_duration=1)
        sys.exit()

    if choice == 'create_folder':
        folder_path, folder_pass = folder_window(username)
        if folder_path and folder_pass:
            key_file = os.path.join(folder_path, 'folder_key.key')
            if not os.path.exists(key_file):
                key, salt = generate_key(folder_pass)
                with open(key_file, 'wb') as f:
                    f.write(salt + key)
            else:
                with open(key_file, 'rb') as f:
                    data = f.read()
                    salt, stored_key = data[:16], data[16:]
                key, _ = generate_key(folder_pass, salt)
            cipher = create_cipher(key)
            kasa_window(folder_path, cipher, folder_pass)
    elif isinstance(choice, str) and os.path.exists(choice):
        folder_path = choice
        folder_pass = folder_password_window(folder_path)
        if folder_pass:
            key_file = os.path.join(folder_path, 'folder_key.key')
            with open(key_file, 'rb') as f:
                data = f.read()
                salt, stored_key = data[:16], data[16:]
            key, _ = generate_key(folder_pass, salt)
            if key == stored_key:
                cipher = create_cipher(key)
                kasa_window(folder_path, cipher, folder_pass)
            else:
                sg.popup_error('Yanlış klasör şifresi!', auto_close=True, auto_close_duration=2)
    elif choice == 'change_password':
        if change_password_window(username):
            sg.popup('Yeni şifre ile giriş yapmanız gerekiyor.', auto_close=True, auto_close_duration=2)
            username, password = login_window(show_warning=False)
            if not username or not password:
                sys.exit()
    elif choice == 'logout':
        username, password = login_window(show_warning=False)
        if not username or not password:
            sys.exit()
    elif choice == 'add_user':
        new_username, new_password = add_new_user()
        if new_username and new_password:
            username, password = login_window(show_warning=False)
            if not username or not password:
                sys.exit()