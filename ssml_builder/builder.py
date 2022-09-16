from .tags import *


class SpeechBuilder:

    def __init__(self):
        self._content: list[SsmlTagABC] = []

    @property
    def content(self):
        return list(self._content)

    def speak(self):
        """
        <speak>
        :return:
        """
        return SpeakTag(self._content).to_string()

    def add_text(self, value: str):
        """
        add text
        :return:
        """
        self._content.append(RawText(value))
        return self

    def say_as(self, value, interpret_as):
        """
        <say_as>
        :param value:
        :param interpret_as:
        :return:
        """

        self._content.append(SayAsTag(RawText(value), interpret_as))
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

        self._content.append(ProsodyTag(RawText(value), rate, pitch, volume))

        return self

    def sub(self, value, alias):
        """
        <sub>
        :param value:
        :param alias:
        :return:
        """

        self._content.append(SubTag(RawText(value), alias=alias))
        return self

    def lang(self, value, lang):
        """
        <lang>
        :param value:
        :param lang:
        :return:
        """

        self._content.append(LangTag(RawText(value), lang=lang))
        return self

    def voice(self, value, name):
        """
        <voice>
        :param value:
        :param name:
        :return:
        """

        self._content.append(VoiceTag(RawText(value), name=name))
        return self

    def pause(self, time):
        """
        <break>
        :param time:
        :return:
        """

        self._content.append(BreakTag(time=time))

        ssml = '<break time="{}"/>'.format(time)

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

        self._content.append(AudioTag(src))
        return self

    def emphasis(self, value, level):
        self._content.append(EmphasisTag(RawText(value), level=level))
        return self

    def p(self, value):
        """
        :param value:
        :return:
        """
        self._content.append(PTag(RawText(value)))
        return self

    def s(self, value):
        """
        :param value:
        :return:
        """
        self._content.append(STag(RawText(value)))
        return self

    def add_tag(self, tag: SsmlTagABC):
        self._content.append(tag)
        return self
