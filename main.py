import webview
import threading
import os

def start_django():
    os.system("python manage.py runserver")

if __name__ == '__main__':
    threading.Thread(target=start_django, daemon=True).start()
    webview.create_window('GestSchool', 'http://127.0.0.1:8000')
    webview.start()
