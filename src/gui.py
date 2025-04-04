# src/gui.py
import os
import PySimpleGUI as sg

def folder_password_window(folder_path):
    layout = [
        [sg.Text(f'{os.path.basename(folder_path)} Şifresini Girin', font=('Helvetica', 14))],
        [sg.Text('Şifre:', size=(12, 1)), sg.Input(key='-FOLDER_PASS-', password_char='*', size=(20, 1), enable_events=True)],
        [sg.Button('Giriş', size=(10, 1), bind_return_key=True), sg.Button('Geri', size=(10, 1))]
    ]
    window = sg.Window('Klasör Giriş', layout, finalize=True)
    window['-FOLDER_PASS-'].set_focus()
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Geri'):
            window.close()
            return None
        if event in ('Giriş', '\r') and values['-FOLDER_PASS-']:
            folder_pass = values['-FOLDER_PASS-']
            window.close()
            return folder_pass