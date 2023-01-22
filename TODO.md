```
def outbox_index(domain, username, data):
    return {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": f"https://{domain}/users/{username}/outbox",
        "type": "OrderedCollection",
        "totalItems": data.size(username),
        "first": f"https://{domain}/users/{username}/outbox/page/0",
        "last": f"https://{domain}/users/{username}/outbox/page/0"
    }

def outbox_page(domain, username, page, data):
    return {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            {
                "ostatus": "http://ostatus.org#",
                "atomUri": "ostatus:atomUri",
                "inReplyToAtomUri": "ostatus:inReplyToAtomUri",
                "conversation": "ostatus:conversation",
                "sensitive": "as:sensitive",
                "toot": "http://joinmastodon.org/ns#",
                "votersCount": "toot:votersCount",
                "blurhash": "toot:blurhash",
                "focalPoint": {
                    "@container": "@list",
                    "@id": "toot:focalPoint"
                },
                "Hashtag": "as:Hashtag"
            }
        ],
        "id": f"https://{domain}/users/{username}/outbox/page/{page}",
        "type": "OrderedCollectionPage",
        #"next": f"https://{domain}/users/{username}/outbox/page/N",
        #"prev": f"https://{domain}/users/{username}/outbox/page/N",
        "partOf": f"https://{domain}/users/{username}/outbox",
        "orderedItems": data.all(username)
    }

return {
    "id": f"https://{domain}/users/{username}/{str(uuid.uuid4())}",
    "type": "Note",
    "published": published_date,
    "attributedTo": f"https://{domain}/users/{username}",
    "inReplyTo": reply_to,
    "content": content,
    "to": [send_to],
}

content = {
    #"@context": "https://www.w3.org/ns/activitystreams",
    "id": f"https://{domain}/users/{username}/{str(uuid.uuid4())}",
    "type": "Create",
    "actor": f"https://{domain}/users/{username}",
    "published": published_date,
    "to": ["https://www.w3.org/ns/activitystreams#Public"],
    #cc": [f"https://{domain}/users/{username}/followers"],
    "object": note(domain, username, reply_to, content, published_date, public),
}
```
