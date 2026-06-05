import json
from cryptography.fernet import Fernet

class VaultManager:
    def __init__(self, vault_path="Python/vault.json"):
        self.vault_path = vault_path
        self.key_path = "Python/master.key"
        self._ensure_key()

    def _ensure_key(self):
        if not os.path.exists(self.key_path):
            key = Fernet.generate_key()
            with open(self.key_path, "wb") as key_file:
                key_file.write(key)

    def _get_fernet(self):
        with open(self.key_path, "rb") as key_file:
            key = key_file.read()
        return Fernet(key)

    def store_secret(self, key, value):
        f = self._get_fernet()
        encrypted = f.encrypt(value.encode()).decode()

        data = {}
        if os.path.exists(self.vault_path):
            with open(self.vault_path, "r") as f_in:
                data = json.load(f_in)

        data[key] = encrypted
        with open(self.vault_path, "w") as f_out:
            json.dump(data, f_out)

    def get_secret(self, key):
        if not os.path.exists(self.vault_path): return None
        with open(self.vault_path, "r") as f_in:
            data = json.load(f_in)

        if key not in data: return None
        f = self._get_fernet()
        return f.decrypt(data[key].encode()).decode()

import os
