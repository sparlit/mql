import json
from cryptography.fernet import Fernet
import os

class VaultManager:
    def __init__(self, vault_path="Python/vault.json"):
        """
        Initialize the VaultManager with a vault file path and ensure a master encryption key exists.
        
        Parameters:
            vault_path (str): Filesystem path to the JSON vault file (default: "Python/vault.json").
        """
        self.vault_path = vault_path
        self.key_path = "Python/master.key"
        self._ensure_key()

    def _ensure_key(self):
        """
        Ensure a Fernet master key file exists at self.key_path, creating it if missing.
        
        If the key file is absent, generate a new random Fernet key and write it to self.key_path in binary form.
        """
        if not os.path.exists(self.key_path):
            key = Fernet.generate_key()
            with open(self.key_path, "wb") as key_file:
                key_file.write(key)

    def _get_fernet(self):
        """
        Create a Fernet cipher initialized from the stored master key.
        
        Returns:
            Fernet: A `Fernet` instance initialized with the key read from the manager's key file.
        """
        with open(self.key_path, "rb") as key_file:
            key = key_file.read()
        return Fernet(key)

    def store_secret(self, key, value):
        """
        Encrypts a plaintext value and stores it under the given key in the persistent vault.
        
        If the vault file is missing or cannot be read/parsed, a new vault is created. The entry for `key` is added or replaced, the vault is written to disk at the instance's `vault_path`, and a filesystem sync is performed to flush changes.
        
        Parameters:
            key (str): The identifier under which to store the secret.
            value (str): The plaintext secret to encrypt and persist.
        """
        f = self._get_fernet()
        encrypted = f.encrypt(value.encode()).decode()

        data = {}
        if os.path.exists(self.vault_path):
            try:
                with open(self.vault_path, "r") as f_in:
                    content = f_in.read()
                    if content:
                        data = json.loads(content)
            except Exception:
                data = {}

        data[key] = encrypted
        with open(self.vault_path, "w") as f_out:
            json.dump(data, f_out)
        # Force flush to disk
        os.sync()

    def get_secret(self, key):
        """
        Retrieve and decrypt a stored secret by key from the vault file.
        
        Parameters:
            key (str): The name of the secret to retrieve from the vault.
        
        Returns:
            str: The decrypted plaintext secret if found.
            None: If the vault file is missing, unreadable, empty, contains invalid JSON, or the specified key is not present.
        """
        if not os.path.exists(self.vault_path): return None
        try:
            with open(self.vault_path, "r") as f_in:
                content = f_in.read()
                if not content: return None
                data = json.loads(content)
        except Exception:
            return None

        if key not in data: return None
        f = self._get_fernet()
        return f.decrypt(data[key].encode()).decode()
