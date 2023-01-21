import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

class RSAKey():
    """
    This class holds private and public RSA keypairs with file
    load and save functionality. This is an utility class that
    you are free to ignore if you prefer to use your own
    cryptographic functions.

    ```python
    Example:
        key = RSAKey("/my/path/key.pem")
        print(key.public_key)
        signed = key.sign(text, padding.PKCS1v15(), hashes.SHA256())
    ```
    """

    def __init__(self, path) -> None:
        """
        This creates/loads/writes a private key to the specified path.
        You can access both the private and public keys from the members
        `.private_key` and `.public_key`.
        """
        self.private_key_path = path

        if os.path.exists(path):
            key = self.load_private_key(path)
        else:
            key = self.generate_private_key()
            self.save_private_key(path)
            print(f"Saved newly generated keys to {path}")

        self.key: rsa.RSAPrivateKey = key
        """ The RSAPrivateKey object from cryptography """

        self.private_key: bytes = self.key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption())
        """ Contains the private key """

        self.public_key: bytes = self.key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo
        )
        """ Contains the public key """

    def generate_private_key(self) -> rsa.RSAPrivateKey:
        """
        Generate a RSA private key and returns it. The constructor calles this
        to generate a private key.
        """
        return rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )

    def save_private_key(self, path: str) -> None:
        """
        Export the private key to bytes and write them to the specified
        filepath. The constructor uses this to write the keys to storate.
        """
        pem = self.key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        with open(path, 'wb') as pem_out:
            pem_out.write(pem)

    def load_private_key(self, path: str) -> rsa.RSAPrivateKey:
        """
        Import and load a private key from a file.
        """
        with open(path, "rb") as key_file:
            key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
        )
        return key
