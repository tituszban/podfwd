
class StringItem:
    def __init__(self, text):
        self.component = None
        self.name = "string"
        self.text = text
        self.is_only_link = False
        self.links = []
