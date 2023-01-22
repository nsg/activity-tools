import requests
import re
import uuid
from urllib.parse import urlparse

from cryptography.hazmat.primitives.serialization import load_pem_public_key

from .misc import ImageAsset, PublicKey, Tags, Attachment

class Actor:
    """
    Generic actor object. Use `create(...)` to create an actor of your own,
    and `fetch(...)` to fetch an external actor.
    """

    username: str
    """ The actors username"""

    def __init__(self) -> None:
        """
        This creates an empty actor object
        """
        self.snake_pattern = re.compile(r'(?<!^)(?=[A-Z])')

    def add_property_value(self, name, value) -> None:
        """
        Add a PropertyValue to the list of attachments. In Mastodon this
        is used for the links in the profile.
        """
        self.attachment.add_property_value(name, value)

    def add_emoji(self, name, url) -> None:
        """
        Add a custom emoji to the tag list. If you for example like to
        map `:foo:` to `/images/foo.png`, this is the function for you!
        """
        self.tag.add_emoji(name, url)

    def create(self, domain: str, username: str, public_key_bytes: bytes) -> None:
        """
        Populate the actor object with data. This is a useful to create the
        actor for a user. All fields can be overriden.
        """
        self.domain = domain
        self.username = username
        self.public_key = None
        self.public_key_pem = public_key_bytes.decode()

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

    @classmethod
    def fetch(cls, actor_url):
        actor = Actor()
        actor._fetch(actor_url)
        return actor

    def _fetch(self, actor_url):
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
    
        self.public_key_pem = self.public_key['publicKeyPem']

    def get_public_key(self):
        return load_pem_public_key(self.public_key_pem.encode())

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
            "publicKey": PublicKey(
                self.domain,
                self.username,
                self.public_key_pem
            ).run(),
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

    raw: dict
    """
    The raw data representing this object
    """

    def __init__(self, data) -> None:
        self.raw = data
        self.id = data['id']
        self.type = data['type'].lower()
        self._actor = data['actor']
        self._object = data['object']

    @property
    def actor(self) -> Actor:
        return Actor.fetch(actor_url=self._actor)

    @property
    def object(self) -> Actor:
        return Actor.fetch(actor_url=self._object)

    def run(self) -> dict:
        """
        Return the raw JSON data
        """
        return self.raw

class Follow(InboxObject):

    def __init__(self, data) -> None:
        super().__init__(data)

class Undo(InboxObject):

    def __init__(self, data) -> None:
        super().__init__(data)

class ActivityPubObject:
    
    id: str
    """
    The objects ID, this should be a unique identifier
    """

    actor: Actor
    """
    The actor that created the message (the sender)
    """

    actor_url: str
    """
    A url to the actor that created the message (the sender)
    """

    object: object
    """
    A generic object representing the message/data. This may also
    point to a target actor.
    """

    raw: dict
    """
    Object in raw unaltered form represented as a dict. This may be the
    unaltered JSON document, but not always.
    """

class Accept(ActivityPubObject):

    object: Follow
    """ Object representing the Follow request """

    def __init__(self, object: InboxObject) -> None:
        self.id = f"{object.object.id}/accept/{str(uuid.uuid4())}"
        self.object = object
        self.raw = object.run()
        self.actor = object.object

    def run(self):
        return {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": self.id,
            "type": "Accept",
            "actor": self.object.object.id,
            "object": self.object.run()
        }
