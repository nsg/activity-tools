

class ImageAsset:

    def __init__(self, url, media_type=None) -> None:
        if not media_type:
            ext = url.split(".")[-1]

            if ext == "jpg" or ext == "jpeg":
                media_type = "image/jpeg"
            elif ext == "png":
                media_type = "image/png"
            else:
                raise Exception(f"Unknown extension {ext}, specify media_type")

        self.media_type = media_type
        self.url = url

    def run(self) -> dict:
        return {
            "type": "Image",
            "mediaType": self.media_type,
            "url": self.url
        }

class Attachment:

    def __init__(self) -> None:
        self.attachments = []

    def add_property_value(self, name, value):
        self.attachments.append({
            "type": "PropertyValue",
            "name": name,
            "value": value
        })

    def run(self) -> dict:
        return self.attachments

class Link:

    def __init__(self, url, text) -> None:
        self.url = url
        self.text = text

    def run(self) -> dict:
        return f'<a href="{self.url}" target="_blank" rel="nofollow noopener noreferrer">{self.text}</a>'


class Tags:

    def __init__(self, domain) -> None:
        self.domain = domain
        self.tags = []

    def add_emoji(self, name, url) -> None:
        self.tags.append({
            "id": f"https://{self.domain}/emoji/{name}",
            "type": "Emoji",
            "name": ":{name}:",
            "icon": ImageAsset(url).run()
        })

    def run(self) -> dict:
        return self.tags

class PublicKey:

    def __init__(self, domain, username, public_key) -> None:
        self.id = f"https://{domain}/users/{username}/key"
        self.owner = f"https://{domain}/users/{username}"
        self.public_key = public_key

    def run(self) -> dict:
        return {
            "id": self.id,
            "owner": self.owner,
            "publicKeyPem": self.public_key,
        }
