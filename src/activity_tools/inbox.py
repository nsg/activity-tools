from .objects import Follow, Undo
from .headers import Signature

class Inbox:

    def __init__(self, data, headers, inbox_path) -> None:
        self.data = data

        for key in ["@context", "object", "type"]:
            if not key in data:
                raise Exception(f"Missing {key} in inbox message")

        self.signature = Signature(data['actor'], headers, inbox_path)

    def validate(self):
        return self.signature.validate()

    def parse(self):
        func_name = f"type_{self.data['type'].lower()}"

        if not hasattr(self, func_name):
            raise Exception(f"Inbox message type {self.data['type']} is not implemented")

        return getattr(self, func_name)()

    def type_follow(self):
        return Follow(self.data, self.signature)

    def type_undo(self):
        return Undo(self.data, self.signature)
