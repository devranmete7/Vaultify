# src/folder_management.py
import os
import json
import shutil
import datetime
import hashlib
import PySimpleGUI as sg
from .user_management import profile_window

USER_FILE = 'kullanicilar.json'

def folder_window(username):
    layout = [
        [sg.Text('Yeni Klasör Oluşturun', font=('Helvetica', 14))],
        [sg.Text('Klasör Adı:', size=(12, 1)), sg.Input(key='-FOLDER-', size=(20, 1))],
        [sg.Text('Klasör Şifresi:', size=(12, 1)), sg.Input(key='-FOLDER_PASS-', password_char='*', size=(20, 1), enable_events=True)],
        [sg.Button('Oluştur', size=(10, 1), bind_return_key=True), sg.Button('Geri', size=(10, 1))]
    ]
    window = sg.Window('Klasör Oluştur', layout, finalize=True)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Geri'):
            window.close()
            return None, None
        if event in ('Oluştur', '\r') and values['-FOLDER-'] and values['-FOLDER_PASS-']:
            folder_name = values['-FOLDER-']
            folder_pass = values['-FOLDER_PASS-']
            folder_path = os.path.join(os.getcwd(), folder_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            with open(USER_FILE, 'r') as f:
                users_data = json.load(f)
            user_data = users_data['users'][username]
            if 'folders' not in user_data:
                user_data['folders'] = []
            if folder_name not in user_data['folders']:
                user_data['folders'].append(folder_name)
                user_data['recent_actions'].append(f"Yeni klasör oluşturuldu: {folder_name} ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
                with open(USER_FILE, 'w') as f:
                    json.dump(users_data, f)
            window.close()
            return folder_path, folder_pass

def main_menu(username):
    with open(USER_FILE, 'r') as f:
        users_data = json.load(f)
    user_data = users_data['users'][username]
    current_folders = [d for d in os.listdir(os.getcwd()) if os.path.isdir(d) and os.path.exists(os.path.join(d, 'folder_key.key'))]
    if 'folders' not in user_data:
        user_data['folders'] = []
    user_data['folders'] = [f for f in user_data['folders'] if f in current_folders]
    with open(USER_FILE, 'w') as f:
        json.dump(users_data, f)
    folder_list = user_data['folders']
    
    layout = [
        [sg.Text(f'Hoş Geldiniz, {username}', font=('Helvetica', 16))],
        [sg.Text('Oluşturulmuş Klasörler:', font=('Helvetica', 12))],
        [sg.Listbox(values=folder_list, size=(40, 5), key='-FOLDER_LIST-', enable_events=True)],
        [sg.Button('Klasörleri Göster', size=(15, 1)), sg.Button('Klasör Oluştur', size=(15, 1)), sg.Button('Klasöre Gir', size=(15, 1))],
        [sg.Button('Seçili Klasörü Sil', size=(15, 1)), sg.Button('Klasöre Şifre Ekle', size=(15, 1)), sg.Button('Profil', size=(15, 1))],
        [sg.Button('Çıkış', size=(15, 1))]
    ]
    window = sg.Window('Ana Menü', layout, finalize=True)

    def set_folder_password(folder_name):
        layout = [
            [sg.Text(f'{folder_name} için Şifre Belirle', font=('Helvetica', 14))],
            [sg.Text('Şifre:', size=(12, 1)), sg.Input(key='-PASS-', password_char='*', size=(20, 1), enable_events=True)],
            [sg.Checkbox('Şifreyi Göster', key='-SHOW_PASS-', enable_events=True)],
            [sg.Button('Onayla', size=(10, 1), bind_return_key=True), sg.Button('İptal', size=(10, 1))]
        ]
        window_pass = sg.Window('Şifre Belirle', layout, finalize=True)
        window_pass['-PASS-'].set_focus()
        while True:
            event_pass, values_pass = window_pass.read()
            if event_pass in (sg.WIN_CLOSED, 'İptal'):
                window_pass.close()
                return None
            if event_pass == '-SHOW_PASS-':
                window_pass['-PASS-'].update(password_char='' if values_pass['-SHOW_PASS-'] else '*')
            if event_pass in ('Onayla', '\r') and values_pass['-PASS-']:
                hashed_password = hashlib.sha256(values_pass['-PASS-'].encode()).hexdigest()
                window_pass.close()
                return hashed_password

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Çıkış'):
            window.close()
            return None
        if event == 'Klasörleri Göster':
            with open(USER_FILE, 'r') as f:
                users_data = json.load(f)
            user_data = users_data['users'][username]
            current_folders = [d for d in os.listdir(os.getcwd()) if os.path.isdir(d) and os.path.exists(os.path.join(d, 'folder_key.key'))]
            user_data['folders'] = [f for f in user_data['folders'] if f in current_folders]
            with open(USER_FILE, 'w') as f:
                json.dump(users_data, f)
            folder_list = user_data['folders']
            window['-FOLDER_LIST-'].update(values=folder_list)
        if event == 'Klasör Oluştur':
            window.close()
            return 'create_folder'
        if event == 'Klasöre Gir' and values['-FOLDER_LIST-']:
            folder_name = values['-FOLDER_LIST-'][0]
            with open(USER_FILE, 'r') as f:
                users_data = json.load(f)
            user_data = users_data['users'][username]
            user_data['folder_access_counts'][folder_name] = user_data['folder_access_counts'].get(folder_name, 0) + 1
            user_data['recent_actions'].append(f"Klasöre girildi: {folder_name} ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
            with open(USER_FILE, 'w') as f:
                json.dump(users_data, f)
            window.close()
            return folder_name
        if event == 'Seçili Klasörü Sil' and values['-FOLDER_LIST-']:
            folder_name = values['-FOLDER_LIST-'][0]
            confirm = sg.popup_yes_no(f'{folder_name} klasörü silinecek ve içindeki bilgiler yok olacak. Silinsin mi?', title='Uyarı')
            if confirm == 'Yes':
                folder_path = os.path.join(os.getcwd(), folder_name)
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)
                    with open(USER_FILE, 'r') as f:
                        users_data = json.load(f)
                    user_data = users_data['users'][username]
                    if folder_name in user_data['folders']:
                        user_data['folders'].remove(folder_name)
                        user_data['recent_actions'].append(f"Klasör silindi: {folder_name} ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
                        if folder_name in user_data['folder_access_counts']:
                            del user_data['folder_access_counts'][folder_name]
                        if 'folder_passwords' in user_data and folder_name in user_data['folder_passwords']:
                            del user_data['folder_passwords'][folder_name]
                        with open(USER_FILE, 'w') as f:
                            json.dump(users_data, f)
                    sg.popup(f'{folder_name} klasörü silindi!', title='Başarılı', auto_close=True, auto_close_duration=2)
                window['-FOLDER_LIST-'].update(values=user_data['folders'])
        if event == 'Klasöre Şifre Ekle' and values['-FOLDER_LIST-']:
            folder_name = values['-FOLDER_LIST-'][0]
            new_password = set_folder_password(folder_name)
            if new_password:
                with open(USER_FILE, 'r') as f:
                    users_data = json.load(f)
                user_data = users_data['users'][username]
                if 'folder_passwords' not in user_data:
                    user_data['folder_passwords'] = {}
                user_data['folder_passwords'][folder_name] = new_password
                user_data['recent_actions'].append(f"Klasöre şifre eklendi: {folder_name} ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
                with open(USER_FILE, 'w') as f:
                    json.dump(users_data, f)
                sg.popup(f'{folder_name} klasörüne şifre eklendi!', title='Başarılı', auto_close=True, auto_close_duration=2)
        if event == 'Profil':
            action = profile_window(username)
            if action:
                window.close()
                return action
