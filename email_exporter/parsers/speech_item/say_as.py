from .speech_item_abc import SpeechItemABC


class SayAs(SpeechItemABC):
    cardinal = "cardinal"
    ordinal = "ordinal"
    characters = "characters"
    fraction = "fraction"
    expletive = "expletive"
    unit = "unit"
    verbatim = "verbatim"
    spell_out = "spell-out"
    telephone = "telephone"

    def __init__(self, text, interpret_as):
        self._text = text
        assert interpret_as in [
            SayAs.cardinal,
            SayAs.ordinal,
            SayAs.characters,
            SayAs.fraction,
            SayAs.expletive,
            SayAs.unit,
            SayAs.verbatim,
            SayAs.spell_out,
            SayAs.telephone,
        ], f"Invalid interpret_as {interpret_as}"
        self._interpret_as = interpret_as

    def add_to_speech(self, speech):
        speech.say_as(value=self._text, interpret_as=self._interpret_as)
        return super().add_to_speech(speech)
