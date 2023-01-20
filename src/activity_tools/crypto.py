import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

class RSAKey():

    def __init__(self, path) -> None:
        self.private_key_path = path

        if os.path.exists(path):
            self.key = self.load_private_key(path)
        else:
            self.key = self.generate_private_key()
            self.save_private_key(path)
            print(f"Saved newly generated keys to {path}")

        self.private_key = self.key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption())

        self.public_key = self.key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def generate_private_key(self) -> rsa.RSAPrivateKey:
        return rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )

    def save_private_key(self, path: str) -> None:
        pem = self.key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        with open(path, 'wb') as pem_out:
            pem_out.write(pem)

    def load_private_key(self, path: str) -> rsa.RSAPrivateKey:
        with open(path, "rb") as key_file:
            key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
        )
        return key
