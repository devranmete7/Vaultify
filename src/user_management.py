# src/user_management.py
import os
import json
import hashlib
import datetime
import shutil
import PySimpleGUI as sg

USER_FILE = 'kullanicilar.json'

def login_window(show_warning=True):
    if show_warning:
        layout = [
            [sg.Text('Uyarı: Şifrelerinizi bir yere not almazsanız dosyalara erişiminiz olmayacaktır!', font=('Helvetica', 12))],
            [sg.Button('OK', size=(10, 1), bind_return_key=True)]
        ]
        window_warning = sg.Window('Önemli Bilgi', layout, finalize=True)
        while True:
            event, values = window_warning.read()
            if event in (sg.WIN_CLOSED, 'OK'):
                window_warning.close()
                break

    if not os.path.exists(USER_FILE):
        layout = [
            [sg.Text('Uygulamaya Şifre Oluşturun', font=('Helvetica', 14))],
            [sg.Text('Kullanıcı Adı:', size=(12, 1)), sg.Input(key='-USER-', size=(20, 1))],
            [sg.Text('Şifre:', size=(12, 1)), sg.Input(key='-PASS-', password_char='*', size=(20, 1), enable_events=True)],
            [sg.Checkbox('Şifreyi Göster', key='-SHOW_PASS-', enable_events=True)],
            [sg.Button('Kaydet', size=(10, 1), bind_return_key=True), sg.Button('Çıkış', size=(10, 1))]
        ]
        window = sg.Window('Kayıt', layout, finalize=True)
        while True:
            event, values = window.read()
            if event in (sg.WIN_CLOSED, 'Çıkış'):
                window.close()
                return None, None
            if event == '-SHOW_PASS-':
                window['-PASS-'].update(password_char='' if values['-SHOW_PASS-'] else '*')
            if event in ('Kaydet', '\r') and values['-USER-'] and values['-PASS-']:
                users_data = {
                    'users': {
                        values['-USER-']: {
                            'password': hashlib.sha256(values['-PASS-'].encode()).hexdigest(),
                            'folders': [],
                            'registration_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'last_login': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'recent_actions': [],
                            'folder_access_counts': {}
                        }
                    }
                }
                with open(USER_FILE, 'w') as f:
                    json.dump(users_data, f)
                window.close()
                return values['-USER-'], values['-PASS-']
    else:
        try:
            with open(USER_FILE, 'r') as f:
                content = f.read().strip()
                if not content:
                    users_data = {'users': {}}
                    with open(USER_FILE, 'w') as f_write:
                        json.dump(users_data, f_write)
                else:
                    f.seek(0)
                    users_data = json.load(f)
        except json.JSONDecodeError:
            sg.popup_error('Kullanıcı bilgileri dosyası bozuk! Varsayılan değerlerle sıfırlanıyor.', auto_close=True, auto_close_duration=2)
            users_data = {'users': {}}
            with open(USER_FILE, 'w') as f:
                json.dump(users_data, f)
        except IOError:
            sg.popup_error('Kullanıcı bilgileri dosyasına erişilemedi!', auto_close=True, auto_close_duration=2)
            return None, None

        layout = [
            [sg.Text('Giriş Yapın', font=('Helvetica', 14))],
            [sg.Text('Kullanıcı Adı:', size=(12, 1)), sg.Input(key='-USER-', size=(20, 1))],
            [sg.Text('Şifre:', size=(12, 1)), sg.Input(key='-PASS-', password_char='*', size=(20, 1), enable_events=True)],
            [sg.Checkbox('Şifreyi Göster', key='-SHOW_PASS-', enable_events=True)],
            [sg.Button('Giriş', size=(10, 1), bind_return_key=True), sg.Button('Çıkış', size=(10, 1))]
        ]
        window = sg.Window('Giriş', layout, finalize=True)
        while True:
            event, values = window.read()
            if event in (sg.WIN_CLOSED, 'Çıkış'):
                window.close()
                return None, None
            if event == '-SHOW_PASS-':
                window['-PASS-'].update(password_char='' if values['-SHOW_PASS-'] else '*')
            if event in ('Giriş', '\r'):
                username = values['-USER-']
                if username in users_data['users']:
                    user_data = users_data['users'][username]
                    if hashlib.sha256(values['-PASS-'].encode()).hexdigest() == user_data['password']:
                        user_data['last_login'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        with open(USER_FILE, 'w') as f:
                            json.dump(users_data, f)
                        window.close()
                        return username, values['-PASS-']
                    else:
                        sg.popup_error('Kullanıcı adı veya şifre yanlış!', auto_close=True, auto_close_duration=2)
                else:
                    sg.popup_error('Kullanıcı adı bulunamadı!', auto_close=True, auto_close_duration=2)

def change_password_window(username):
    with open(USER_FILE, 'r') as f:
        users_data = json.load(f)
    user_data = users_data['users'][username]
    layout = [
        [sg.Text('Şifreyi Değiştir', font=('Helvetica', 14))],
        [sg.Text('Kullanıcı Adı:', size=(12, 1)), sg.Input(username, key='-USER-', size=(20, 1), disabled=True)],
        [sg.Text('Mevcut Şifre:', size=(12, 1)), sg.Input(key='-OLD_PASS-', password_char='*', size=(20, 1))],
        [sg.Text('Yeni Şifre:', size=(12, 1)), sg.Input(key='-NEW_PASS-', password_char='*', size=(20, 1), enable_events=True)],
        [sg.Checkbox('Şifreyi Göster', key='-SHOW_PASS-', enable_events=True)],
        [sg.Button('Değiştir', size=(10, 1), bind_return_key=True), sg.Button('Geri', size=(10, 1))]
    ]
    window = sg.Window('Şifre Değiştir', layout, finalize=True)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Geri'):
            window.close()
            return False
        if event == '-SHOW_PASS-':
            window['-OLD_PASS-'].update(password_char='' if values['-SHOW_PASS-'] else '*')
            window['-NEW_PASS-'].update(password_char='' if values['-SHOW_PASS-'] else '*')
        if event in ('Değiştir', '\r'):
            if (values['-USER-'] == username and 
                hashlib.sha256(values['-OLD_PASS-'].encode()).hexdigest() == user_data['password']):
                user_data['password'] = hashlib.sha256(values['-NEW_PASS-'].encode()).hexdigest()
                user_data['recent_actions'].append(f"Şifre değiştirildi ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
                with open(USER_FILE, 'w') as f:
                    json.dump(users_data, f)
                sg.popup('Şifre başarıyla değiştirildi!', title='Başarılı', auto_close=True, auto_close_duration=2)
                window.close()
                return True
            else:
                sg.popup_error('Mevcut kullanıcı adı veya şifre yanlış!', auto_close=True, auto_close_duration=2)

def add_new_user():
    layout = [
        [sg.Text('Yeni Kullanıcı Oluşturun', font=('Helvetica', 14))],
        [sg.Text('Kullanıcı Adı:', size=(12, 1)), sg.Input(key='-USER-', size=(20, 1))],
        [sg.Text('Şifre:', size=(12, 1)), sg.Input(key='-PASS-', password_char='*', size=(20, 1), enable_events=True)],
        [sg.Checkbox('Şifreyi Göster', key='-SHOW_PASS-', enable_events=True)],
        [sg.Button('Kaydet', size=(10, 1), bind_return_key=True), sg.Button('Geri', size=(10, 1))]
    ]
    window = sg.Window('Yeni Kullanıcı', layout, finalize=True)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Geri'):
            window.close()
            return None, None
        if event == '-SHOW_PASS-':
            window['-PASS-'].update(password_char='' if values['-SHOW_PASS-'] else '*')
        if event in ('Kaydet', '\r') and values['-USER-'] and values['-PASS-']:
            with open(USER_FILE, 'r') as f:
                users_data = json.load(f)
            if values['-USER-'] in users_data['users']:
                sg.popup_error('Bu kullanıcı adı zaten mevcut!', auto_close=True, auto_close_duration=2)
                continue
            users_data['users'][values['-USER-']] = {
                'password': hashlib.sha256(values['-PASS-'].encode()).hexdigest(),
                'folders': [],
                'registration_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'last_login': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'recent_actions': [],
                'folder_access_counts': {}
            }
            with open(USER_FILE, 'w') as f:
                json.dump(users_data, f)
            sg.popup('Yeni kullanıcı oluşturuldu! Lütfen giriş yapın.', auto_close=True, auto_close_duration=2)
            window.close()
            return values['-USER-'], values['-PASS-']

def profile_window(username):
    with open(USER_FILE, 'r') as f:
        users_data = json.load(f)
    user_data = users_data['users'][username]

    total_folders = len(user_data.get('folders', []))
    total_files = 0
    for folder in user_data.get('folders', []):
        folder_path = os.path.join(os.getcwd(), folder)
        meta_file = os.path.join(folder_path, 'kasa_dosyalar.json')
        if os.path.exists(meta_file):
            with open(meta_file, 'r') as f:
                meta_data = json.load(f)
            total_files += len(meta_data['files'])
            for subfolder in meta_data['subfolders'].values():
                sub_meta_file = os.path.join(subfolder, 'kasa_dosyalar.json')
                if os.path.exists(sub_meta_file):
                    with open(sub_meta_file, 'r') as f:
                        sub_meta_data = json.load(f)
                    total_files += len(sub_meta_data['files'])

    recent_actions = user_data.get('recent_actions', [])[-5:]
    folder_access_counts = user_data.get('folder_access_counts', {})
    sorted_folders = sorted(folder_access_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    frequent_folders = [f"{folder} ({count} erişim)" for folder, count in sorted_folders]

    layout = [
        [sg.Text('Kullanıcı Profili', font=('Helvetica', 16))],
        [sg.Text('Kullanıcı Adı:', size=(15, 1)), sg.Input(username, key='-USERNAME-', size=(20, 1), disabled=True)],
        [sg.Text('Kayıt Tarihi:', size=(15, 1)), sg.Text(user_data['registration_date'])],
        [sg.Text('Son Giriş Zamanı:', size=(15, 1)), sg.Text(user_data['last_login'])],
        [sg.Text('Toplam Klasör Sayısı:', size=(15, 1)), sg.Text(str(total_folders))],
        [sg.Text('Toplam Dosya Sayısı:', size=(15, 1)), sg.Text(str(total_files))],
        [sg.Text('Son İşlemler:', font=('Helvetica', 12))],
        [sg.Listbox(values=recent_actions, size=(40, 5), key='-RECENT_ACTIONS-')],
        [sg.Text('En Sık Kullanılan Klasörler:', font=('Helvetica', 12))],
        [sg.Listbox(values=frequent_folders, size=(40, 3), key='-FREQUENT_FOLDERS-')],
        [sg.Button('Şifreyi Değiştir', size=(20, 1)), sg.Button('Hesaptan Çık', size=(20, 1))],
        [sg.Button('Yeni Hesap Ekle', size=(20, 1)), sg.Button('Uygulamayı Sıfırla', size=(20, 1))],
        [sg.Button('Kapat', size=(20, 1))]
    ]
    window = sg.Window('Profil', layout, finalize=True)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Kapat'):
            window.close()
            return None
        if event == 'Şifreyi Değiştir':
            window.close()
            return 'change_password'
        if event == 'Hesaptan Çık':
            sg.popup('Hesaptan çıkılıyor...', auto_close=True, auto_close_duration=1)
            window.close()
            return 'logout'
        if event == 'Yeni Hesap Ekle':
            window.close()
            return 'add_user'
        if event == 'Uygulamayı Sıfırla':
            confirm = sg.popup_yes_no('Tüm kullanıcılar, klasörler ve dosyalar silinecek. Bu işlem geri alınamaz! Devam etmek istiyor musunuz?', title='Uyarı')
            if confirm == 'Yes':
                for folder in os.listdir(os.getcwd()):
                    folder_path = os.path.join(os.getcwd(), folder)
                    if os.path.isdir(folder_path) and folder != 'src':
                        shutil.rmtree(folder_path)
                with open(USER_FILE, 'w') as f:
                    json.dump({'users': {}}, f)
                sg.popup('Uygulama sıfırlandı! Lütfen tekrar giriş yapın.', auto_close=True, auto_close_duration=2)
                window.close()
                return 'logout'