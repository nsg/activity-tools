import requests
import re
from urllib.parse import urlparse

from cryptography.hazmat.primitives.serialization import load_pem_public_key

from .misc import ImageAsset, PublicKey, Tags, Attachment

class Actor:

    def __init__(self) -> None:
        self.snake_pattern = re.compile(r'(?<!^)(?=[A-Z])')

    def add_property_value(self, name, value):
        self.attachment.add_property_value(name, value)

    def add_emoji(self, name, url):
        self.tag.add_emoji(name, url)

    def create(self, domain, username, public_key) -> None:
        self.domain = domain
        self.username = username
        self.public_key = public_key

        self.id = f"https://{self.domain}/users/{self.username}"
        self.type = "Person"

        self.inbox = f"https://{self.domain}/users/{self.username}/inbox"
        self.outbox = f"https://{self.domain}/users/{self.username}/outbox"

        self.following = f"https://{domain}/users/{username}/following"
        self.followers = f"https://{domain}/users/{username}/followers"

        self.discoverable = False
        self.summary = ""
        self.published = "1523-06-06T10:00:00Z"

        self.name = f"{self.username.capitalize()}"
        self.preferred_username = f"{self.username}"

        self.icon_url = None
        self.image_url = None
        self.manually_approves_followers = None
        self.attachment = Attachment()
        self.tag = Tags(self.domain)

    def fetch(self, actor_url):
        self.actor_raw = {}

        if not actor_url:
            raise Exception("Actor URL is not set")

        headers = {
            'Content-Type': "application/activity+json",
            'Accept': 'application/activity+json'
        }

        actor_resp = requests.get(actor_url, headers=headers)
        if actor_resp.status_code > 299:
            raise Exception(f"Actor {actor_url} responded with a {actor_resp.status_code}")

        self.actor_raw = actor_resp.json()
        urlid = urlparse(self.actor_raw['id'])

        self.domain = urlid.netloc

        keys = [
            "publicKey",
            "id",
            "type",
            "inbox",
            "outbox",
            "following",
            "followers",
            "discoverable",
            "summary",
            "published",
            "name",
            "preferredUsername",
            "icon",
            "image",
            "manuallyApprovesFollowers",
            "attachment",
            "tag"
        ]

        for key in keys:
            key_snake = self.snake_pattern.sub('_', key).lower()
            setattr(self, key_snake, self.actor_raw.get(key))
    
    def get_public_key(self):
        return load_pem_public_key(self.public_key['publicKeyPem'].encode("utf-8"))

    def run(self) -> dict:
        required_document = {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                "https://w3id.org/security/v1",
            ],
            "id": self.id,
            "type": self.type,
            "inbox": self.inbox,
            "discoverable": self.discoverable,
            "summary": self.summary,
            "published": self.published,
            "name": self.name,
            "preferredUsername": self.preferred_username,
            "attachment": self.attachment.run(),
            "tag": self.tag.run(),
            "publicKey": PublicKey(self.domain, self.username, "public key").run(),
        }

        extra_values = {}

        if self.icon_url:
            extra_values["icon"] = ImageAsset(self.icon_url)

        if self.icon_url:
            extra_values["image"] = ImageAsset(self.image_url)

        if self.manually_approves_followers:
            extra_values["manuallyApprovesFollowers"] = self.manually_approves_followers

        if self.followers:
            extra_values["followers"] = self.followers

        if self.following:
            extra_values["following"] = self.following

        if self.outbox:
            extra_values["outbox"] = self.outbox

        return { **required_document, **extra_values }


class WrapActivityStreamsObject:

    def __init__(self, object) -> None:
        self.object = object

    def run(self) -> dict:
        context = {
            "@context": "https://www.w3.org/ns/activitystreams"
        }

        return { **context, **self.object.run() }

class InboxObject:

    def __init__(self, data, signature) -> None:
        self.id = data['id']
        self.type = data['type'].lower()
        self._actor = data['actor']
        self._object = data['object']
        self.signature = signature

    @property
    def actor(self):
        return self._actor

    @property
    def object(self):
        return self._object

class Follow(InboxObject):

    def __init__(self, data, signature) -> None:
        super().__init__(data, signature)

class Undo(InboxObject):

    def __init__(self, data, signature) -> None:
        super().__init__(data, signature)
