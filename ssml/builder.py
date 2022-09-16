from . import tags


class SpeechBuilder:

    def __init__(self):
        self._content: list[tags.SsmlTagABC] = []

    @property
    def content(self):
        return list(self._content)

    def speak(self):
        """
        <speak>
        :return:
        """
        return tags.Speak(self._content)

    def add_text(self, value: str):
        """
        add text
        :return:
        """
        self._content.append(tags.RawText(value))
        return self

    def say_as(self, value, interpret_as):
        """
        <say_as>
        :param value:
        :param interpret_as:
        :return:
        """

        self._content.append(tags.SayAs(tags.RawText(value), interpret_as))
        return self

    def prosody(self, value, rate='medium', pitch='medium', volume='medium'):
        """
        <prosody>
        :param value:
        :param rate:
        :param pitch:
        :param volume:
        :return:
        """

        self._content.append(tags.Prosody(tags.RawText(value), rate, pitch, volume))

        return self

    def sub(self, value, alias):
        """
        <sub>
        :param value:
        :param alias:
        :return:
        """

        self._content.append(tags.Sub(tags.RawText(value), alias=alias))
        return self

    def lang(self, value, lang):
        """
        <lang>
        :param value:
        :param lang:
        :return:
        """

        self._content.append(tags.Lang(tags.RawText(value), lang=lang))
        return self

    def voice(self, value, name):
        """
        <voice>
        :param value:
        :param name:
        :return:
        """

        self._content.append(tags.Voice(tags.RawText(value), name=name))
        return self

    def pause(self, time):
        """
        <break>
        :param time:
        :return:
        """

        self._content.append(tags.Break(time=time))

        return self

    def whisper(self, value):
        """
        :param value:
        :return:
        """
        # TODO: Support amazon effect tags: '<amazon:effect name="whispered">{}</amazon:effect>'
        raise Exception("Whisper is not supported")

    def audio(self, src):
        """
        :param src:
        :return:
        """

        self._content.append(tags.Audio(src))
        return self

    def emphasis(self, value, level):
        self._content.append(tags.Emphasis(tags.RawText(value), level=level))
        return self

    def p(self, value):
        """
        :param value:
        :return:
        """
        self._content.append(tags.P(tags.RawText(value)))
        return self

    def s(self, value):
        """
        :param value:
        :return:
        """
        self._content.append(tags.S(tags.RawText(value)))
        return self

    def add_tag(self, tag: tags.SsmlTagABC):
        self._content.append(tag)
        return self
