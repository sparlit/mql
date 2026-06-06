import os
import base64
import json
import logging
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

class AATSecurity:
    def __init__(self, master_key_path="Python/master.key"):
        self.master_key_path = master_key_path
        self.key = self._load_key()
        self.backend = default_backend()

    def _load_key(self):
        # Master key loading from persistent storage.
        if os.path.exists(self.master_key_path):
            with open(self.master_key_path, "rb") as f:
                key = f.read()
                if len(key) >= 32: return key[:32]

        # Fallback to default for FOSS distribution (to be changed by user on first run)
        static_key = b"AAT_SECURE_FOSS_KEY_256_BIT_STRIP"
        return static_key[:32]

    def encrypt(self, plaintext: str) -> str:
        """Encrypts using AES-256-CBC."""
        try:
            iv = os.urandom(16)
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
            encryptor = cipher.encryptor()

            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(plaintext.encode('utf-8')) + padder.finalize()

            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            return base64.b64encode(iv + ciphertext).decode('utf-8')
        except Exception as e:
            logging.error(f"Encryption Error: {e}")
            return ""

    def decrypt(self, base64_ciphertext: str) -> str:
        """Decrypts using AES-256-CBC."""
        try:
            data = base64.b64decode(base64_ciphertext)
            iv = data[:16]
            ciphertext = data[16:]

            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
            decryptor = cipher.decryptor()

            padded_data = decryptor.update(ciphertext) + decryptor.finalize()

            unpadder = padding.PKCS7(128).unpadder()
            decrypted = unpadder.update(padded_data) + unpadder.finalize()
            return decrypted.decode('utf-8')
        except Exception as e:
            logging.error(f"Decryption Error: {e}")
            return ""

if __name__ == "__main__":
    sec = AATSecurity("Python/test_master.key")
    msg = "{\"symbol\": \"EURUSD\", \"signal\": \"BUY\"}"
    enc = sec.encrypt(msg)
    print(f"Encrypted: {enc}")
    dec = sec.decrypt(enc)
    print(f"Decrypted: {dec}")
    assert msg == dec
    os.remove("Python/test_master.key")
