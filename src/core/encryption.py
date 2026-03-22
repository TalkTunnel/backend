from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import os
from typing import Tuple, Dict

class EncryptionService:
    """Базовый сервис шифрования (будет расширяться)"""
    
    @staticmethod
    def generate_key_pair() -> Tuple[str, str]:
        """Генерация пары ключей X25519"""
        private_key = x25519.X25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        return (
            base64.b64encode(private_bytes).decode(),
            base64.b64encode(public_bytes).decode()
        )
    
    @staticmethod
    def derive_shared_secret(private_key_b64: str, public_key_b64: str) -> bytes:
        """Вычисление общего секрета"""
        private_bytes = base64.b64decode(private_key_b64)
        public_bytes = base64.b64decode(public_key_b64)
        
        private_key = x25519.X25519PrivateKey.from_private_bytes(private_bytes)
        public_key = x25519.X25519PublicKey.from_public_bytes(public_bytes)
        
        shared_secret = private_key.exchange(public_key)
        
        # HKDF для получения ключа шифрования
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'messenger-chat',
        ).derive(shared_secret)
        
        return derived_key
    
    @staticmethod
    def encrypt_message(message: str, key: bytes) -> Dict[str, str]:
        """Шифрование сообщения AES-256-GCM"""
        nonce = os.urandom(12)
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(message.encode()) + encryptor.finalize()
        
        return {
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "nonce": base64.b64encode(nonce).decode(),
            "tag": base64.b64encode(encryptor.tag).decode()
        }
    
    @staticmethod
    def decrypt_message(encrypted_data: Dict[str, str], key: bytes) -> str:
        """Расшифровка сообщения"""
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        nonce = base64.b64decode(encrypted_data["nonce"])
        tag = base64.b64decode(encrypted_data["tag"])
        
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag))
        decryptor = cipher.decryptor()
        
        decrypted = decryptor.update(ciphertext) + decryptor.finalize()
        return decrypted.decode()