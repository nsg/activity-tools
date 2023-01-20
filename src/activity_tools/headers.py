
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
