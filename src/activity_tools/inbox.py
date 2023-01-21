from .objects import Follow, Undo, InboxObject, Actor

class Inbox:

    def __init__(self, data) -> None:
        self.data = data

        for key in ["@context", "object", "type"]:
            if not key in data:
                raise Exception(f"Missing {key} in inbox message")

    def parse(self) -> InboxObject:
        func_name = f"type_{self.data['type'].lower()}"

        if not hasattr(self, func_name):
            raise Exception(f"Inbox message type {self.data['type']} is not implemented")

        return getattr(self, func_name)()

    def type_follow(self):
        return Follow(self.data)

    def type_undo(self):
        return Undo(self.data)
