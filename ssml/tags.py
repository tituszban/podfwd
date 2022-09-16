from abc import ABC, abstractmethod
import re
from typing import NewType, Optional

SsmlStr = NewType("SsmlStr", str)


# Full support for: https://cloud.google.com/text-to-speech/docs/ssml
# Partial support for: https://docs.aws.amazon.com/polly/latest/dg/supportedtags.html

class SsmlTagABC(ABC):
    @abstractmethod
    def to_string(self) -> SsmlStr:
        raise NotImplementedError()


class RawText(SsmlTagABC):
    def __init__(self, text: str) -> None:
        self._text = text

    def _santise(self, text: str) -> SsmlStr:
        return SsmlStr(text)     # TODO: sanitise user text

    def to_string(self) -> SsmlStr:
        return self._santise(self._text)


class SsmlTag(SsmlTagABC):
    def __init__(self, content: list[SsmlTagABC], tag_name: str, tag_args: dict[str, Optional[str]]):
        self._content = content
        self._tag_name = tag_name
        self._tag_args = tag_args

    def to_string(self) -> SsmlStr:
        if len(self._content) > 0:
            return SsmlStr("<{tag} {args}>{content}</{tag}".format(
                tag=self._tag_name,
                args=' '.join(f'{key}="{value}"' for key, value in self._tag_args.items() if value),
                content='\n'.join(map(lambda c: c.to_string(), self._content))
            ))

        return SsmlStr("<{tag} {args} />".format(
            tag=self._tag_name,
            args=' '.join(f'{key}="{value}"' for key, value in self._tag_args.items() if value),
        ))


class Speak(SsmlTag):
    def __init__(self, content: list[SsmlTagABC]):
        super().__init__(content, "speak", {})


class Empty(SsmlTag):
    def __init__(self, tag_name: str, tag_args: dict[str, Optional[str]]):
        super().__init__([], tag_name, tag_args)


class Break(Empty):
    def __init__(self, time: Optional[str] = None, strength: Optional[str] = None):
        assert time or strength, "Either time or strength must be set"
        super().__init__("break", {
            "time": time,
            "strength": strength
        })


class SayAs(SsmlTag):
    VALID_INTERPRET_AS = (
        "currency",
        "telephone",
        "verbatim",
        "spell-out",
        "date",
        "characters",
        "cardinal",
        "ordinal",
        "fraction",
        "expletive",
        "beep",
        "unit",
        "time"
    )

    def __init__(self, content: list[SsmlTagABC], interpret_as: str, addtional_args: dict[str, Optional[str]] = {}):
        assert interpret_as in self.VALID_INTERPRET_AS, "Invalid interpret_as"
        super().__init__(content, "say-as", {"interpret-as": interpret_as, **addtional_args})


class SayAsCurrency(SayAs):
    def __init__(self, content: list[SsmlTagABC], language: str):
        super().__init__(content, "currency", {"language": language})


class SayAsTelephone(SayAs):
    def __init__(self, content: list[SsmlTagABC], format: Optional[str] = None, style: Optional[str] = None):
        super().__init__(content, "telephone", {
            "format": format,
            "google:style": style,
        })


class SayAsVerbatim(SayAs):
    def __init__(self, content: list[SsmlTagABC]):
        super().__init__(content, "verbatim")


class SayAsDate(SayAs):
    def __init__(self, content: list[SsmlTagABC], format: str, detail: str):
        super().__init__(content, "date", {"format": format, "detail": detail})


class SayAsCharacters(SayAs):
    def __init__(self, content: list[SsmlTagABC]):
        super().__init__(content, "characters")


class SayAsCardinal(SayAs):
    def __init__(self, content: list[SsmlTagABC]):
        super().__init__(content, "cardinal")


class SayAsOrdinal(SayAs):
    def __init__(self, content: list[SsmlTagABC]):
        super().__init__(content, "ordinal")


class SayAsFraction(SayAs):
    def __init__(self, content: list[SsmlTagABC]):
        super().__init__(content, "fraction")


class SayAsExpletive(SayAs):
    def __init__(self, content: list[SsmlTagABC]):
        super().__init__(content, "expletive")


class SayAsUnit(SayAs):
    def __init__(self, content: list[SsmlTagABC]):
        super().__init__(content, "unit")


class SayAsTime(SayAs):
    def __init__(self, content: list[SsmlTagABC], format: str):
        super().__init__(content, "time", {"format": format})


class Audio(SsmlTag):
    def __init__(self,
                 src: str,
                 description: Optional[str] = None,
                 alt: Optional[str] = None,
                 clip_begin: Optional[str] = None,
                 clip_end: Optional[str] = None,
                 speed: Optional[str] = None,
                 repeat_count: Optional[str] = None,
                 repeat_dur: Optional[str] = None,
                 sound_level: Optional[str] = None):
        super().__init__(
            [
                *([SsmlTag([RawText(description)], "desc", {})] if description else []),
                *([RawText(alt)] if alt else [])
            ],
            "audio",
            {
                "src": src,
                "clipBegin": clip_begin,
                "clipEnd": clip_end,
                "speed": speed,
                "repeatCount": repeat_count,
                "repeatDur": repeat_dur,
                "soundLevel": sound_level
            }
        )


class P(SsmlTag):
    def __init__(self, content: list[SsmlTagABC]):
        super().__init__(content, "p", {})


class S(SsmlTag):
    def __init__(self, content: list[SsmlTagABC]):
        super().__init__(content, "s", {})


class Sub(SsmlTag):
    def __init__(self, content: list[SsmlTagABC], alias: str):
        super().__init__(content, "sub", {"alias": alias})


class Mark(Empty):
    def __init__(self, name: str):
        super().__init__("mark", {"name": name})


class Prosody(SsmlTag):
    VALID_PROSODY_ATTRIBUTES = {
        'rate': ('x-slow', 'slow', 'medium', 'fast', 'x-fast'),
        'pitch': ('x-low', 'low', 'medium', 'high', 'x-high'),
        'volume': ('silent', 'x-soft', 'soft', 'medium', 'loud', 'x-loud')
    }

    def __init__(self, content: list[SsmlTagABC], rate: Optional[str] = None, volume: Optional[str] = None, pitch: Optional[str] = None):
        if rate and rate not in self.VALID_PROSODY_ATTRIBUTES['rate']:
            if re.match(r'^\d+%$', rate) is None:
                raise ValueError('The rate provided to prosody is not valid')

        if pitch and pitch not in self.VALID_PROSODY_ATTRIBUTES['pitch']:
            if re.match(r'^(\+|\-)+\d+(\.\d+)*%$', pitch) is None:
                raise ValueError('The pitch provided to prosody is not valid')

        if volume and volume not in self.VALID_PROSODY_ATTRIBUTES['volume']:
            if re.match(r'^(\+|\-)+\d+(\.\d)?dB$', volume) is None:
                raise ValueError('The volume provided to prosody is not valid')

        super().__init__(content, "prosody", {
            "rate": rate,
            "volume": volume,
            "pitch": pitch
        })


class Emphasis(SsmlTag):
    VALID_EMPHASIS_ATTRIBUTES = [
        "strong", "moderate", "none", "reduced"
    ]

    def __init__(self, content: list[SsmlTagABC], level: str):
        if level not in self.VALID_EMPHASIS_ATTRIBUTES:
            raise ValueError("Invalid emphasis level")

        super().__init__(content, "emphasis", {"level": level})


class Par(SsmlTag):
    def __init__(self, content: list[SsmlTagABC]):
        super().__init__(content, "par", {})


class Seq(SsmlTag):
    def __init__(self, content: list[SsmlTagABC]):
        super().__init__(content, "seq", {})


class Media(SsmlTag):
    def __init__(self,
                 media_content: SsmlTagABC,
                 xml_id: Optional[str] = None,
                 begin: Optional[str] = None,
                 end: Optional[str] = None,
                 repeat_count: Optional[str] = None,
                 repeat_dur: Optional[str] = None,
                 sound_level: Optional[str] = None,
                 fade_in_dur: Optional[str] = None,
                 fade_out_dur: Optional[str] = None):
        assert isinstance(media_content, Audio) or isinstance(
            media_content, Speak), "Only audio and speak tags are allowed in media"
        super().__init__([media_content], "media", {
            "xml:id": xml_id,
            "begin": begin,
            "end": end,
            "repeatCount": repeat_count,
            "repeatDur": repeat_dur,
            "soundLevel": sound_level,
            "fadeInDur": fade_in_dur,
            "fadeOutDur": fade_out_dur
        })


class Phoneme(SsmlTag):
    SUPPORTED_PHONETIC_ALPHABETS = ["ipa", "x-sampa"]

    def __init__(self, content: list[SsmlTagABC], alphabet: str, ph: str):
        assert alphabet in self.SUPPORTED_PHONETIC_ALPHABETS, "Unsupported phonetic alphabet"
        super().__init__(content, "phoneme", {
            "alphabet": alphabet,
            "ph": ph
        })


class Voice(SsmlTag):
    def __init__(self,
                 content: list[SsmlTagABC],
                 name: Optional[str] = None,
                 language: Optional[str] = None,
                 gender: Optional[str] = None,
                 variant: Optional[str] = None):
        if name:
            assert not language and not gender and not variant, "can't specify other tags if name is specified"
            assert name in self.get_supported_names(), "name is not in the list of supported names"
        else:
            assert language or gender or variant, "At least one voice tag must be specified"

        super().__init__(content, "voice", {
            "name": name,
            "language": language,
            "gender": gender,
            "variant": variant,
        })

    @abstractmethod
    def get_supported_names(self):
        return []       # TODO: add supported names for various cloud providers


class Lang(SsmlTag):
    def __init__(self, content: list[SsmlTagABC], lang: str):
        # TODO: assert lang is BCP-47 lang
        super().__init__(content, "lang", {
            "xml:lang": lang
        })


class PS(P):
    def __init__(self, content: list[SsmlTagABC]):
        super().__init__([S(content)])
