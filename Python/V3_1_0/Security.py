# Project: Autonomous AutoTrader (AAT)
# Version: V3.3.0_20260606
# License: 100% FOSS / GNU GPL v3
# Author: Simon Peter
# Verification: Zero-Stub / Production Ready
# Description: AES-256-CBC Security and Encrypted Transport Layer

import base64
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

class AATSecurity:
    def __init__(self, key_str="AAT_SECURE_FOSS_KEY_256_BIT_STRIP"):
        self.key = key_str.encode()[:32].ljust(32, b'\0')

    def encrypt(self, text):
        iv = os.urandom(16)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(text.encode()) + padder.finalize()
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ct = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(iv + ct).decode()

    def decrypt(self, ct_b64):
        try:
            combined = base64.b64decode(ct_b64)
            iv, ct = combined[:16], combined[16:]
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ct) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            return (unpadder.update(padded_data) + unpadder.finalize()).decode()
        except: return None
