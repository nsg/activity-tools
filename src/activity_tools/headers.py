import re
import base64
from typing import Tuple

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa

from cryptography.exceptions import InvalidSignature

from .objects import Actor

class ContentTypes:

    @classmethod
    @property
    def activity(cls) -> dict:
        return {
            'Content-Type': "application/activity+json"
        }

    @classmethod
    @property
    def jrd(cls) -> dict:
        return {
            'Content-Type': "application/jrd+json"
        }

class SignatureHeader:

    key_id: str
    algorithm: str
    headers: list
    signature: str

    def __init__(self, header) -> None:
        for sh in header.split(","):
            m = re.match(r'^"?([^"]+)"?="?([^"]+)"?$', sh)
            key = m.group(1)
            value = m.group(2)

            if key.lower() == "keyid":
                self.key_id = value
            elif key.lower() == "algorithm":
                self.algorithm = value
            elif key.lower() == "headers":
                self.headers = value.split(" ")
            elif key.lower() == "signature":
                self.signature = value
            else:
                raise Exception("Unsupported SignatureHeader key")

class Header:
    """
    Representation of a HTTP Header. This class has a bit magic that
    splits and parses headers like the signature header for easy use.
    """

    name: str
    """ The headers name """

    raw_value: str
    """ The unaltered header value """

    _parsed_value: list

    def __init__(self, header) -> None:
        self.name = header[0]
        self.raw_value = header[1]
        self._parsed_value = []

        if self.is_signature():
            self._parsed_value = SignatureHeader(self.raw_value)
        else:
            self._parsed_value = self.raw_value

    @property
    def value(self):
        """ 
        Parsed header value. Most headers are just strings, but
        special headers like the signature header will return a
        SignatureHeader object.
        """
        return self._parsed_value

    def is_signature(self) -> bool:
        """
        Returns true of this is the signature header
        """
        return self.name.lower() == "signature"

class Headers:

    headers: list[Header]

    def __init__(self, headers) -> None:
        self.headers = []

        for header in headers:
            self.headers.append(Header(header))

    def get(self, name):
        for header in self.headers:
            if header.name.lower() == name:
                return header

def verify_signature(
        object: dict,
        headers: list[Tuple[str, str]],
        inbox_path: str
    ) -> bool:
        """
        This function verifies the signature on the specified request. This function
        requires both the incoming object and HTTP headers with the path of the
        receiving inbox. The function will return a boolean value.

        arguments:
        - object     - A dict representing the object we like to verify
        - headers    - A list of tuples of strings representing our HTTP headers
        - inbox_path - The path to our inbox, eg. /users/foo/inbox
        """

        # Analyze headers
        headers_obj = Headers(headers)

        # The extract the value of the signature header
        signature_header: SignatureHeader = headers_obj.get('signature').value

        # Extract the signature, confusually another header with the same name
        # inside the signature header. Decode the signature.
        signature = base64.b64decode(signature_header.signature)

        # Fetch the remote actors, actor
        actor = Actor.fetch(actor_url=object['actor'])

        message = []
        for h in signature_header.headers:
            if h == '(request-target)':
                message.append(f"(request-target): post {inbox_path}")
            else:
                message.append(f"{h}: {headers_obj.get(h).raw_value}")

        message = "\n".join(message).encode("utf-8")

        try:
            actor.get_public_key().verify(
                signature, message, padding.PKCS1v15(), hashes.SHA256()
            )
        except InvalidSignature:
            return False

        return True
