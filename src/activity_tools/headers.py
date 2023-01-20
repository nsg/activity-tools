import re
import base64

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

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

class Signature():

    def __init__(self, actor_url, headers, inbox_path) -> None:
        self.actor_url = actor_url
        self.headers = headers
        self.signature_headers = {}
        self.inbox_path = inbox_path

        if not "Signature" in headers:
            raise Exception("Signature is missing from headers")

        for sh in headers['Signature'].split(","):
            m = re.match(r"^(\w+)=(.+)$", sh)
            key = m.group(1)
            value = m.group(2)
            self.signature_headers[key] = value.replace('"', '')

    def validate(self):

        actor = Actor()
        actor.fetch(actor_url=self.actor_url)

        signature = base64.b64decode(self.signature_headers['signature'])

        message = []
        for h in self.signature_headers["headers"].split(" "):
            print(h)
            if h == '(request-target)':
                message.append(f"(request-target): post {self.inbox_path}")
            else:
                message.append(f"{h}: {self.headers[h.upper()]}")

        message = "\n".join(message).encode("utf-8")

        try:
            actor.get_public_key().verify(
                signature, message, padding.PKCS1v15(), hashes.SHA256()
            )
        except InvalidSignature:
            return False

        return True
