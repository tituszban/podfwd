class ParsedItem:
    def __init__(self, ssml: list[str], description: list[str]=[]):
        self._ssml = ssml
        self._description = description

    @property
    def ssml(self):
        return self._ssml

    @property
    def combined_description(self):
        return '\n'.join(self._description)
