from .misc import ImageAsset, PublicKey, Tags, Attachment

class Actor:

    def __init__(self, domain, username, public_key) -> None:
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

    def add_property_value(self, name, value):
        self.attachment.add_property_value(name, value)

    def add_emoji(self, name, url):
        self.tag.add_emoji(name, url)

    def run(self) -> dict:
        required_document = {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                "https://w3id.org/security/v1",
            ],
            "id": self.id,
            "type": self.type,
            "inbox": self.inbox,
            "outbox": self.outbox,
            "following": self.following,
            "followers": self.followers,
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

        return { **required_document, **extra_values }
