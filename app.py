import webview
import os
import sys
import json
import base64
import hashlib
import time
from cryptography.fernet import Fernet


def password_to_key(password):
    """Convert a password to a Fernet key using SHA-256"""
    digest = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def get_absolute_path(filename):
    """Get the absolute path for a file, handling both packaged and development modes"""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.abspath(filename)


class VaultixAPI:
    """API for the Vaultix password manager frontend"""

    def __init__(self):
        """Initialize the Vaultix API"""
        self.unlocked = False
        self.fernet = None
        self.data = []
        self.data_path = get_absolute_path("data.enc")
        self.settings = {
            'tray_enabled': False,
            'autostart_enabled': False,
            'autolock_enabled': True,
            'dark_mode': True,
            'last_login': 0
        }
        self.settings_path = get_absolute_path("settings.json")
        self._load_settings()

    def _load_settings(self):
        """Load application settings if available"""
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
        except Exception as e:
            print(f"Error loading settings: {e}")

    def _save_settings(self):
        """Save application settings"""
        try:
            with open(self.settings_path, 'w') as f:
                json.dump(self.settings, f)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

    def check_password(self, password):
        """Verify the master password and decrypt the data"""
        try:
            key = password_to_key(password)
            self.fernet = Fernet(key)

            if os.path.exists(self.data_path):
                decrypted = self.fernet.decrypt(
                    open(self.data_path, 'rb').read())
                self.data = json.loads(decrypted.decode())
            else:
                # First time setup - create empty encrypted file
                self.data = []
                self._save_data()

            self.unlocked = True
            self.settings['last_login'] = int(time.time())
            self._save_settings()
            return True
        except Exception as e:
            print(f"Password check failed: {e}")
            return False

    def load_main(self):
        """Load the main application interface"""
        if self.unlocked:
            html_path = get_absolute_path("index.html")
            webview.windows[0].load_url(f"file://{html_path}")
            webview.windows[0].set_title("Vaultix")
            webview.windows[0].resize(1000, 700)  # Larger window for better UX
            # The window's resizable property is set at creation time, not afterwards
        else:
            webview.windows[0].destroy()

    def get_data(self):
        """Get the decrypted password data"""
        return self.data

    def set_data(self, new_data):
        """Update the password data"""
        self.data = new_data
        return True

    def _save_data(self):
        """Internal method to save encrypted data"""
        try:
            encrypted_data = self.fernet.encrypt(
                json.dumps(self.data).encode())
            with open(self.data_path, 'wb') as f:
                f.write(encrypted_data)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False

    def save_data(self):
        """Save the password data to the encrypted file"""
        return self._save_data()

    def import_data(self, json_str):
        """Import data from a JSON string"""
        try:
            imported = json.loads(json_str)
            if isinstance(imported, list):
                # Add IDs if they don't exist
                for item in imported:
                    if 'id' not in item:
                        item['id'] = f"imported_{int(time.time())}_{len(self.data)}"
                self.data.extend(imported)
                return True
            return False
        except Exception as e:
            print(f"Import error: {e}")
            return False

    def export_data(self, include_passwords=False):
        """Export data as JSON, optionally removing sensitive fields"""
        try:
            if not include_passwords:
                export_data = []
                for item in self.data:
                    export_item = item.copy()
                    if 'password' in export_item:
                        # Redact passwords
                        export_item['password'] = '********'
                    export_data.append(export_item)
                return json.dumps(export_data)
            return json.dumps(self.data)
        except Exception as e:
            print(f"Export error: {e}")
            return None

    def open_settings(self):
        """Open the settings page"""
        html_path = get_absolute_path("settings.html")
        webview.windows[0].load_url(f"file://{html_path}")

    def change_password(self, new_password):
        """Change the master password"""
        try:
            new_key = password_to_key(new_password)
            new_fernet = Fernet(new_key)
            encrypted_data = new_fernet.encrypt(json.dumps(self.data).encode())
            with open(self.data_path, 'wb') as f:
                f.write(encrypted_data)
            self.fernet = new_fernet
            return True
        except Exception as e:
            print(f"Password change error: {e}")
            return False

    def set_tray(self, enabled):
        """Enable or disable tray icon"""
        self.settings['tray_enabled'] = enabled
        return self._save_settings()

    def set_autostart(self, enabled):
        """Enable or disable application autostart"""
        self.settings['autostart_enabled'] = enabled
        return self._save_settings()

    def set_autolock(self, enabled):
        """Enable or disable auto-lock feature"""
        self.settings['autolock_enabled'] = enabled
        return self._save_settings()

    def set_dark_mode(self, enabled):
        """Enable or disable dark mode"""
        self.settings['dark_mode'] = enabled
        return self._save_settings()

    def get_settings(self):
        """Get all application settings"""
        return self.settings

    def generate_password(self, length=16, include_uppercase=True,
                          include_numbers=True, include_symbols=True):
        """Generate a secure random password"""
        import string
        import random

        char_set = string.ascii_lowercase
        if include_uppercase:
            char_set += string.ascii_uppercase
        if include_numbers:
            char_set += string.digits
        if include_symbols:
            char_set += "!@#$%^&*()-_=+[]{}|;:,.<>?"

        # Ensure we have at least one of each required character type
        password = []
        if include_uppercase:
            password.append(random.choice(string.ascii_uppercase))
        if include_numbers:
            password.append(random.choice(string.digits))
        if include_symbols:
            password.append(random.choice("!@#$%^&*()-_=+[]{}|;:,.<>?"))

        # Fill the rest with random characters
        remaining_length = length - len(password)
        password.extend(random.choice(char_set)
                        for _ in range(remaining_length))

        # Shuffle the password characters
        random.shuffle(password)
        return ''.join(password)

    def create_backup(self):
        """Create an encrypted backup of the database"""
        try:
            import time
            import shutil

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_filename = f"vaultix_backup_{timestamp}.enc"

            # Get user's documents folder for the backup
            if sys.platform == 'win32':
                documents_dir = os.path.join(
                    os.path.expanduser('~'), 'Documents')
            else:
                documents_dir = os.path.join(
                    os.path.expanduser('~'), 'Documents')

            if not os.path.exists(documents_dir):
                os.makedirs(documents_dir)

            backup_path = os.path.join(documents_dir, backup_filename)

            # Copy the encrypted file
            shutil.copy2(self.data_path, backup_path)

            return {
                'success': True,
                'path': backup_path,
                'filename': backup_filename
            }
        except Exception as e:
            print(f"Backup error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def restore_backup(self, backup_path):
        """Restore from a backup file"""
        try:
            if not os.path.exists(backup_path):
                return False

            # Verify this is a valid backup file
            with open(backup_path, 'rb') as f:
                backup_data = f.read()

            # Try to decrypt with current key
            try:
                self.fernet.decrypt(backup_data)
            except Exception:
                return False  # Can't decrypt, invalid backup or wrong master password

            # Replace current database with backup
            with open(self.data_path, 'wb') as f:
                f.write(backup_data)

            # Reload data
            decrypted = self.fernet.decrypt(backup_data)
            self.data = json.loads(decrypted.decode())

            return True
        except Exception as e:
            print(f"Restore error: {e}")
            return False


def start_app():
    """Initialize and start the Vaultix application"""
    api = VaultixAPI()

    html_path = get_absolute_path("login.html")

    # Create a stylish window with proper icon and size
    window = webview.create_window(
        title="Vaultix Password Manager",
        url=f"file://{html_path}",
        width=600,
        height=650,
        resizable=True,  # Allow window to be resized
        js_api=api,
        min_size=(400, 500)
    )

    # Start the application with the best available GUI renderer
    webview.start(gui="edgechromium", debug=False, http_server=False)


if __name__ == "__main__":
    start_app()
