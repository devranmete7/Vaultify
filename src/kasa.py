# src/kasa.py
import os
import json
import shutil
import hashlib
import PySimpleGUI as sg
from .encryption import encrypt_file, decrypt_file

def kasa_window(storage_folder, cipher, user_password):
    meta_file = os.path.join(storage_folder, 'kasa_dosyalar.json')
    if not os.path.exists(meta_file):
        with open(meta_file, 'w') as f:
            json.dump({'files': [], 'file_passwords': {}, 'subfolders': {}, 'subfolder_passwords': {}}, f)
    
    with open(meta_file, 'r') as f:
        meta_data = json.load(f)
    if 'file_passwords' not in meta_data:
        meta_data['file_passwords'] = {}
    if 'subfolders' not in meta_data:
        meta_data['subfolders'] = {}
    if 'subfolder_passwords' not in meta_data:
        meta_data['subfolder_passwords'] = {}
    with open(meta_file, 'w') as f:
        json.dump(meta_data, f)
    file_list = meta_data['files']
    subfolder_list = list(meta_data['subfolders'].keys())
    
    layout = [
        [sg.Text(f'{os.path.basename(storage_folder)} Kasası', font=('Helvetica', 16))],
        [sg.Text('Dosya Ekle:', size=(12, 1)), sg.Input(key='-FILE-', size=(30, 1)), sg.FileBrowse('Dosya Seç', size=(10, 1))],
        [sg.Button('Dosyayı Kasaya Taşı', size=(15, 1), bind_return_key=True), sg.Button('Dosyaları Listele', size=(15, 1)), sg.Button('Çıkış', size=(15, 1))],
        [sg.Text('Kasa İçeriği:', font=('Helvetica', 12))],
        [sg.Listbox(values=file_list + subfolder_list, size=(50, 10), key='-FILE_LIST-', enable_events=True)],
        [sg.Button('Seçilen Öğeyi Aç', size=(15, 1)), sg.Button('Seçilen Öğeyi Sil', size=(15, 1)), sg.Button('Yeni Klasör Oluştur', size=(15, 1))],
        [sg.Button('Şifre Ekle', size=(15, 1)), sg.Button('Şifre Değiştir', size=(15, 1)), sg.Button('Şifre Kaldır', size=(15, 1))]
    ]
    window = sg.Window('Klasör Kasası', layout, finalize=True)
    
    def update_file_list():
        with open(meta_file, 'r') as f:
            meta_data = json.load(f)
        file_list = meta_data['files']
        subfolder_list = list(meta_data['subfolders'].keys())
        window['-FILE_LIST-'].update(values=file_list + subfolder_list)

    def set_password(item_name, is_folder=False):
        layout = [
            [sg.Text(f'{item_name} için Şifre Belirle', font=('Helvetica', 14))],
            [sg.Text('Şifre:', size=(12, 1)), sg.Input(key='-PASS-', password_char='*', size=(20, 1), enable_events=True)],
            [sg.Button('Onayla', size=(10, 1), bind_return_key=True), sg.Button('İptal', size=(10, 1))]
        ]
        window_pass = sg.Window('Şifre Belirle', layout, finalize=True)
        window_pass['-PASS-'].set_focus()
        while True:
            event_pass, values_pass = window_pass.read()
            if event_pass in (sg.WIN_CLOSED, 'İptal'):
                window_pass.close()
                return None
            if event_pass in ('Onayla', '\r') and values_pass['-PASS-']:
                window_pass.close()
                return hashlib.sha256(values_pass['-PASS-'].encode()).hexdigest()

    def change_password(item_name, is_folder=False):
        layout = [
            [sg.Text(f'{item_name} Şifresini Değiştir', font=('Helvetica', 14))],
            [sg.Text('Yeni Şifre:', size=(12, 1)), sg.Input(key='-NEW_PASS-', password_char='*', size=(20, 1), enable_events=True)],
            [sg.Button('Değiştir', size=(10, 1), bind_return_key=True), sg.Button('İptal', size=(10, 1))]
        ]
        window_pass = sg.Window('Şifre Değiştir', layout, finalize=True)
        window_pass['-NEW_PASS-'].set_focus()
        while True:
            event_pass, values_pass = window_pass.read()
            if event_pass in (sg.WIN_CLOSED, 'İptal'):
                window_pass.close()
                return None
            if event_pass in ('Değiştir', '\r') and values_pass['-NEW_PASS-']:
                window_pass.close()
                return hashlib.sha256(values_pass['-NEW_PASS-'].encode()).hexdigest()

    def verify_password(item_name, is_folder=False):
        with open(meta_file, 'r') as f:
            meta_data = json.load(f)
        password_key = 'subfolder_passwords' if is_folder else 'file_passwords'
        if item_name in meta_data[password_key] and meta_data[password_key][item_name]:
            layout = [
                [sg.Text(f'{item_name} Şifresini Doğrula', font=('Helvetica', 14))],
                [sg.Text('Şifre:', size=(12, 1)), sg.Input(key='-PASS-', password_char='*', size=(20, 1), enable_events=True)],
                [sg.Button('Doğrula', size=(10, 1), bind_return_key=True), sg.Button('İptal', size=(10, 1))]
            ]
            window_pass = sg.Window('Şifre Doğrula', layout, finalize=True)
            window_pass['-PASS-'].set_focus()
            while True:
                event_pass, values_pass = window_pass.read()
                if event_pass in (sg.WIN_CLOSED, 'İptal'):
                    window_pass.close()
                    return False
                if event_pass in ('Doğrula', '\r') and values_pass['-PASS-']:
                    entered_pass = hashlib.sha256(values_pass['-PASS-'].encode()).hexdigest()
                    if entered_pass == meta_data[password_key][item_name]:
                        window_pass.close()
                        return True
                    else:
                        sg.popup_error('Yanlış şifre!', auto_close=True, auto_close_duration=2)
            window_pass.close()
        return True

    def check_password(item_name, is_folder=False):
        with open(meta_file, 'r') as f:
            meta_data = json.load(f)
        password_key = 'subfolder_passwords' if is_folder else 'file_passwords'
        if item_name in meta_data[password_key] and meta_data[password_key][item_name]:
            layout = [
                [sg.Text(f'{item_name} Şifresini Gir', font=('Helvetica', 14))],
                [sg.Text('Şifre:', size=(12, 1)), sg.Input(key='-PASS-', password_char='*', size=(20, 1), enable_events=True)],
                [sg.Button('Giriş', size=(10, 1), bind_return_key=True), sg.Button('İptal', size=(10, 1))]
            ]
            window_pass = sg.Window('Şifre Gir', layout, finalize=True)
            window_pass['-PASS-'].set_focus()
            while True:
                event_pass, values_pass = window_pass.read()
                if event_pass in (sg.WIN_CLOSED, 'İptal'):
                    window_pass.close()
                    return False
                if event_pass in ('Giriş', '\r') and values_pass['-PASS-']:
                    entered_pass = hashlib.sha256(values_pass['-PASS-'].encode()).hexdigest()
                    if entered_pass == meta_data[password_key][item_name]:
                        window_pass.close()
                        return True
                    else:
                        sg.popup_error('Yanlış şifre!', auto_close=True, auto_close_duration=2)
            window_pass.close()
        return True

    def create_subfolder():
        layout = [
            [sg.Text('Yeni Alt Klasör Oluşturun', font=('Helvetica', 14))],
            [sg.Text('Klasör Adı:', size=(12, 1)), sg.Input(key='-SUBFOLDER-', size=(20, 1))],
            [sg.Button('Oluştur', size=(10, 1), bind_return_key=True), sg.Button('İptal', size=(10, 1))]
        ]
        window_sub = sg.Window('Alt Klasör Oluştur', layout, finalize=True)
        while True:
            event_sub, values_sub = window_sub.read()
            if event_sub in (sg.WIN_CLOSED, 'İptal'):
                window_sub.close()
                return None
            if event_sub in ('Oluştur', '\r') and values_sub['-SUBFOLDER-']:
                subfolder_name = values_sub['-SUBFOLDER-']
                subfolder_path = os.path.join(storage_folder, subfolder_name)
                if not os.path.exists(subfolder_path):
                    os.makedirs(subfolder_path)
                    with open(meta_file, 'r') as f:
                        meta_data = json.load(f)
                    meta_data['subfolders'][subfolder_name] = subfolder_path
                    meta_data['subfolder_passwords'][subfolder_name] = ''
                    with open(meta_file, 'w') as f:
                        json.dump(meta_data, f)
                window_sub.close()
                return subfolder_path

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Çıkış'):
            break
        if event in ('Dosyayı Kasaya Taşı', '\r'):
            file_path = values['-FILE-']
            if file_path and os.path.exists(file_path):
                original_filename = os.path.basename(file_path)
                target_path = os.path.join(storage_folder, original_filename)
                backup_path = os.path.join('Kasa_Yedek', original_filename)
                if not os.path.exists('Kasa_Yedek'):
                    os.makedirs('Kasa_Yedek')
                # Dosyayı hedef konuma kopyala
                shutil.copy(file_path, target_path)
                # Hedef dosyayı şifrele
                encrypt_file(target_path, cipher)
                # Yedek kopya oluştur
                shutil.copy(target_path, backup_path)
                # Orijinal dosyayı sil
                os.remove(file_path)
                with open(meta_file, 'r') as f:
                    meta_data = json.load(f)
                if original_filename not in meta_data['files']:
                    meta_data['files'].append(original_filename)
                    meta_data['file_passwords'][original_filename] = ''
                    with open(meta_file, 'w') as f:
                        json.dump(meta_data, f)
                sg.popup('Dosya kasaya taşındı!', title='Başarılı', auto_close=True, auto_close_duration=2)
                update_file_list()
            else:
                sg.popup_error('Lütfen geçerli bir dosya seçin!', auto_close=True, auto_close_duration=2)
        if event == 'Dosyaları Listele':
            update_file_list()
        if event == 'Seçilen Öğeyi Aç' and values['-FILE_LIST-']:
            selected_item = values['-FILE_LIST-'][0]
            with open(meta_file, 'r') as f:
                meta_data = json.load(f)
            if selected_item in meta_data['files']:
                if check_password(selected_item, is_folder=False):
                    file_path = os.path.join(storage_folder, selected_item)
                    if os.path.exists(file_path):
                        # Dosyayı geçici olarak çöz
                        temp_path = os.path.join(storage_folder, 'gecici_' + selected_item)
                        with open(file_path, 'rb') as f:
                            encrypted_data = f.read()
                        try:
                            decrypted_data = cipher.decrypt(encrypted_data)
                            with open(temp_path, 'wb') as f:
                                f.write(decrypted_data)
                            os.startfile(temp_path)
                            sg.popup('Dosya açıldı!', title='Başarılı', auto_close=True, auto_close_duration=2)
                        except Exception as e:
                            sg.popup_error(f'Dosya açılamadı: {str(e)}', auto_close=True, auto_close_duration=2)
                    else:
                        sg.popup_error('Dosya kasada bulunamadı!', auto_close=True, auto_close_duration=2)
                else:
                    sg.popup_error('Dosya açılamadı: Şifre doğrulanamadı!', auto_close=True, auto_close_duration=2)
            elif selected_item in meta_data['subfolders']:
                if check_password(selected_item, is_folder=True):
                    subfolder_path = os.path.join(storage_folder, selected_item)
                    kasa_window(subfolder_path, cipher, user_password)
                else:
                    sg.popup_error('Alt klasöre girilemedi: Şifre doğrulanamadı!', auto_close=True, auto_close_duration=2)
            else:
                sg.popup_error('Geçersiz öğe!', auto_close=True, auto_close_duration=2)
        if event == 'Seçilen Öğeyi Sil' and values['-FILE_LIST-']:
            selected_item = values['-FILE_LIST-'][0]
            with open(meta_file, 'r') as f:
                meta_data = json.load(f)
            if selected_item in meta_data['files']:
                confirm = sg.popup_yes_no(f'{selected_item} dosyası silinecek. Silinsin mi?', title='Uyarı')
                if confirm == 'Yes':
                    file_path = os.path.join(storage_folder, selected_item)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        meta_data['files'].remove(selected_item)
                        if selected_item in meta_data['file_passwords']:
                            del meta_data['file_passwords'][selected_item]
                        with open(meta_file, 'w') as f:
                            json.dump(meta_data, f)
                        sg.popup(f'{selected_item} dosyası silindi!', title='Başarılı', auto_close=True, auto_close_duration=2)
                        update_file_list()
            elif selected_item in meta_data['subfolders']:
                confirm = sg.popup_yes_no(f'{selected_item} klasörü ve içeriği silinecek. Silinsin mi?', title='Uyarı')
                if confirm == 'Yes':
                    subfolder_path = os.path.join(storage_folder, selected_item)
                    if os.path.exists(subfolder_path):
                        shutil.rmtree(subfolder_path)
                        del meta_data['subfolders'][selected_item]
                        if selected_item in meta_data['subfolder_passwords']:
                            del meta_data['subfolder_passwords'][selected_item]
                        with open(meta_file, 'w') as f:
                            json.dump(meta_data, f)
                        sg.popup(f'{selected_item} klasörü silindi!', title='Başarılı', auto_close=True, auto_close_duration=2)
                        update_file_list()
            else:
                sg.popup_error('Geçersiz öğe!', auto_close=True, auto_close_duration=2)
        if event == 'Yeni Klasör Oluştur':
            subfolder_path = create_subfolder()
            if subfolder_path:
                sg.popup('Alt klasör oluşturuldu!', title='Başarılı', auto_close=True, auto_close_duration=2)
                update_file_list()
        if event == 'Şifre Ekle' and values['-FILE_LIST-']:
            selected_item = values['-FILE_LIST-'][0]
            with open(meta_file, 'r') as f:
                meta_data = json.load(f)
            is_folder = selected_item in meta_data['subfolders']
            new_password = set_password(selected_item, is_folder)
            if new_password:
                password_key = 'subfolder_passwords' if is_folder else 'file_passwords'
                meta_data[password_key][selected_item] = new_password
                with open(meta_file, 'w') as f:
                    json.dump(meta_data, f)
                sg.popup(f'{selected_item} için şifre eklendi!', title='Başarılı', auto_close=True, auto_close_duration=2)
        if event == 'Şifre Değiştir' and values['-FILE_LIST-']:
            selected_item = values['-FILE_LIST-'][0]
            with open(meta_file, 'r') as f:
                meta_data = json.load(f)
            is_folder = selected_item in meta_data['subfolders']
            if (is_folder and selected_item in meta_data['subfolder_passwords'] and meta_data['subfolder_passwords'][selected_item]) or \
               (not is_folder and selected_item in meta_data['file_passwords'] and meta_data['file_passwords'][selected_item]):
                if verify_password(selected_item, is_folder):
                    new_password = change_password(selected_item, is_folder)
                    if new_password:
                        password_key = 'subfolder_passwords' if is_folder else 'file_passwords'
                        meta_data[password_key][selected_item] = new_password
                        with open(meta_file, 'w') as f:
                            json.dump(meta_data, f)
                        sg.popup(f'{selected_item} şifresi değiştirildi!', title='Başarılı', auto_close=True, auto_close_duration=2)
                else:
                    sg.popup_error('Şifre doğrulanamadı!', auto_close=True, auto_close_duration=2)
            else:
                sg.popup_error(f'{selected_item} zaten şifresiz!', auto_close=True, auto_close_duration=2)
        if event == 'Şifre Kaldır' and values['-FILE_LIST-']:
            selected_item = values['-FILE_LIST-'][0]
            with open(meta_file, 'r') as f:
                meta_data = json.load(f)
            is_folder = selected_item in meta_data['subfolders']
            password_key = 'subfolder_passwords' if is_folder else 'file_passwords'
            if selected_item in meta_data[password_key] and meta_data[password_key][selected_item]:
                if verify_password(selected_item, is_folder):
                    meta_data[password_key][selected_item] = ''
                    with open(meta_file, 'w') as f:
                        json.dump(meta_data, f)
                    sg.popup(f'{selected_item} şifresi kaldırıldı!', title='Başarılı', auto_close=True, auto_close_duration=2)
                else:
                    sg.popup_error('Şifre doğrulanamadı!', auto_close=True, auto_close_duration=2)
            else:
                sg.popup_error(f'{selected_item} zaten şifresiz!', auto_close=True, auto_close_duration=2)
    window.close()