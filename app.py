
import webview
import os
import sys
import json
import base64
import hashlib
from cryptography.fernet import Fernet

def password_to_key(password):
    digest = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(digest)

class VaultixAPI:
    def __init__(self):
        self.unlocked = False
        self.fernet = None
        self.data = []
        self.data_path = get_absolute_path("data.enc")

    def check_password(self, password):
        try:
            key = password_to_key(password)
            self.fernet = Fernet(key)
            decrypted = self.fernet.decrypt(open(self.data_path, 'rb').read())
            self.data = json.loads(decrypted.decode())
            self.unlocked = True
            return True
        except:
            return False

    def load_main(self):
        if self.unlocked:
            html_path = get_absolute_path("index.html")
            webview.windows[0].load_url(f"file://{html_path}")
        else:
            webview.windows[0].destroy()

    def get_data(self):
        return self.data

    def set_data(self, new_data):
        self.data = new_data
        return True

    def save_data(self):
        try:
            encrypted_data = self.fernet.encrypt(json.dumps(self.data).encode())
            with open(self.data_path, 'wb') as f:
                f.write(encrypted_data)
            return True
        except:
            return False

    def import_data(self, json_str):
        try:
            imported = json.loads(json_str)
            self.data.extend(imported)
            return True
        except:
            return False

    def open_settings(self):
        html_path = get_absolute_path("settings.html")
        webview.windows[0].load_url(f"file://{html_path}")

    def change_password(self, new_password):
        try:
            new_key = password_to_key(new_password)
            new_fernet = Fernet(new_key)
            encrypted_data = new_fernet.encrypt(json.dumps(self.data).encode())
            with open(self.data_path, 'wb') as f:
                f.write(encrypted_data)
            return True
        except:
            return False

def get_absolute_path(filename):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.abspath(filename)

def start_app():
    api = VaultixAPI()
    html_path = get_absolute_path("login.html")
    webview.create_window("Vaultix Login", f"file://{html_path}",
                          width=600, height=400, resizable=False, js_api=api)
    webview.start(gui="edgechromium", debug=False, http_server=False)

if __name__ == "__main__":
    start_app()
