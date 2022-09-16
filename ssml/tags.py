from abc import ABC, abstractmethod
import re
from typing import Callable, Generator, NewType, Optional, Union

SsmlStr = NewType("SsmlStr", str)


# Full support for: https://cloud.google.com/text-to-speech/docs/ssml
# Partial support for: https://docs.aws.amazon.com/polly/latest/dg/supportedtags.html

class SsmlTagABC(ABC):
    @abstractmethod
    def to_string(self) -> SsmlStr:
        raise NotImplementedError()

    @abstractmethod
    def replace_text(self, text: str, replacer: Callable[[str], "SsmlTagABC"], *, ignore_case: bool = False) -> "SsmlTagABC":
        raise NotImplementedError()

    @abstractmethod
    def is_tag(self, tag_name: str):
        raise NotImplementedError()


class TagArray(SsmlTagABC):
    def __init__(self, content: list[SsmlTagABC]) -> None:
        self._content = content

    @property
    def content(self):
        return self._content

    def to_string(self) -> SsmlStr:
        return SsmlStr(''.join(map(lambda c: c.to_string(), self._content)))

    @classmethod
    def from_array_or_list(cls, tag_array_or_list: "TagArrayOrList") -> Optional["TagArray"]:
        if tag_array_or_list is None:
            return None
        if isinstance(tag_array_or_list, TagArray):
            return tag_array_or_list
        if isinstance(tag_array_or_list, SsmlTagABC):
            return TagArray([tag_array_or_list])
        if isinstance(tag_array_or_list, list):
            return TagArray(tag_array_or_list)
        raise TypeError(f"Invalid type for tag, array or list: {type(tag_array_or_list)}")

    def replace_text(self, text: str, replacer: Callable[[str], "SsmlTagABC"], *, ignore_case: bool = False) -> "SsmlTagABC":
        return [
            tag.replace_text(text, replacer, ignore_case=ignore_case)
            for tag in self._content
        ]

    def is_tag(self, tag_name: str):
        return False


TagArrayOrList = Union[Optional[SsmlTagABC], Optional[TagArray], list[SsmlTagABC]]


class RawText(SsmlTagABC):
    def __init__(self, text: str) -> None:
        self._text = text

    def _santise(self, text: str) -> SsmlStr:
        return SsmlStr(text)     # TODO: sanitise user text

    def to_string(self) -> SsmlStr:
        return self._santise(self._text)

    def replace_text(self, text: str, replacer: Callable[[str], "SsmlTagABC"], *, ignore_case: bool = False) -> "SsmlTagABC":
        # TODO: support replace_re
        def _split(spliter: str, original_text: str) -> Generator[tuple[str, bool], None, None]:
            spliter = spliter.lower() if ignore_case else spliter
            search_text = original_text.lower() if ignore_case else original_text

            while (i := search_text.find(spliter)) != -1:
                if i == 0:
                    yield (original_text[:len(spliter)], True)
                    original_text = original_text[len(spliter):]
                    search_text = search_text[len(spliter):]
                else:
                    yield (original_text[:i], False)
                    original_text = original_text[i:]
                    search_text = search_text[i:]
            yield (search_text, False)

        if (splt := list(_split(text, self._text))) == 0:
            return self

        replaced_content: list[SsmlTagABC] = []
        for text, is_match in splt:
            if not is_match:
                replaced_content.append(RawText(text))
            else:
                replaced_content.append(replacer(text))
        return TagArray(replaced_content)

    def is_tag(self, tag_name: str):
        return False


class SsmlTag(SsmlTagABC):
    def __init__(self, content: TagArrayOrList, tag_name: str, tag_args: dict[str, Optional[str]]):
        self._content = TagArray.from_array_or_list(content)
        self._tag_name = tag_name
        self._tag_args = tag_args

    def to_string(self) -> SsmlStr:
        args_to_str = ' '.join(["", *[f'{key}="{value}"' for key, value in self._tag_args.items() if value]])

        if self._content:
            return SsmlStr("<{tag}{args}>{content}</{tag}>".format(
                tag=self._tag_name,
                args=args_to_str,
                content=self._content.to_string()
            ))

        return SsmlStr("<{tag}{args} />".format(
            tag=self._tag_name,
            args=args_to_str,
        ))

    def replace_text(self, text: str, replacer: Callable[[str], "SsmlTagABC"], *, ignore_case: bool = False) -> "SsmlTagABC":
        if not self._content:
            return self

        return SsmlTag(
            self._content.replace_text(text, replacer, ignore_case=ignore_case),
            self._tag_name,
            self._tag_args
        )

    def is_tag(self, tag_name: str):
        return self._tag_name == tag_name


class Speak(SsmlTag):
    def __init__(self, content: TagArrayOrList):
        super().__init__(content, "speak", {})


class Empty(SsmlTag):
    def __init__(self, tag_name: str, tag_args: dict[str, Optional[str]]):
        super().__init__([], tag_name, tag_args)


class Break(Empty):
    def __init__(self, *, time: Optional[str] = None, strength: Optional[str] = None):
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

    def __init__(self, content: TagArrayOrList, interpret_as: str, addtional_args: dict[str, Optional[str]] = {}):
        assert interpret_as in self.VALID_INTERPRET_AS, "Invalid interpret_as"
        super().__init__(content, "say-as", {"interpret-as": interpret_as, **addtional_args})


class SayAsCurrency(SayAs):
    def __init__(self, content: TagArrayOrList, *, language: str):
        super().__init__(content, "currency", {"language": language})


class SayAsTelephone(SayAs):
    def __init__(self, content: TagArrayOrList, *, format: Optional[str] = None, style: Optional[str] = None):
        super().__init__(content, "telephone", {
            "format": format,
            "google:style": style,
        })


class SayAsVerbatim(SayAs):
    def __init__(self, content: TagArrayOrList):
        super().__init__(content, "verbatim")


class SayAsDate(SayAs):
    def __init__(self, content: TagArrayOrList, *, format: str, detail: str):
        super().__init__(content, "date", {"format": format, "detail": detail})


class SayAsCharacters(SayAs):
    def __init__(self, content: TagArrayOrList):
        super().__init__(content, "characters")


class SayAsCardinal(SayAs):
    def __init__(self, content: TagArrayOrList):
        super().__init__(content, "cardinal")


class SayAsOrdinal(SayAs):
    def __init__(self, content: TagArrayOrList):
        super().__init__(content, "ordinal")


class SayAsFraction(SayAs):
    def __init__(self, content: TagArrayOrList):
        super().__init__(content, "fraction")


class SayAsExpletive(SayAs):
    def __init__(self, content: TagArrayOrList):
        super().__init__(content, "expletive")


class SayAsUnit(SayAs):
    def __init__(self, content: TagArrayOrList):
        super().__init__(content, "unit")


class SayAsTime(SayAs):
    def __init__(self, content: TagArrayOrList, *, format: str):
        super().__init__(content, "time", {"format": format})


class Audio(SsmlTag):
    def __init__(self,
                 src: str,
                 *,
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
    def __init__(self, content: TagArrayOrList):
        super().__init__(content, "p", {})


class S(SsmlTag):
    def __init__(self, content: TagArrayOrList):
        super().__init__(content, "s", {})


class Sub(SsmlTag):
    def __init__(self, content: TagArrayOrList, *, alias: str):
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

    def __init__(self,
                 content: TagArrayOrList,
                 *,
                 rate: Optional[str] = None,
                 volume: Optional[str] = None,
                 pitch: Optional[str] = None):
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

    def __init__(self, content: TagArrayOrList, *, level: str):
        if level not in self.VALID_EMPHASIS_ATTRIBUTES:
            raise ValueError("Invalid emphasis level")

        super().__init__(content, "emphasis", {"level": level})


class Par(SsmlTag):
    def __init__(self, content: TagArrayOrList):
        super().__init__(content, "par", {})


class Seq(SsmlTag):
    def __init__(self, content: TagArrayOrList):
        super().__init__(content, "seq", {})


class Media(SsmlTag):
    def __init__(self,
                 media_content: SsmlTagABC,
                 *,
                 xml_id: Optional[str] = None,
                 begin: Optional[str] = None,
                 end: Optional[str] = None,
                 repeat_count: Optional[str] = None,
                 repeat_dur: Optional[str] = None,
                 sound_level: Optional[str] = None,
                 fade_in_dur: Optional[str] = None,
                 fade_out_dur: Optional[str] = None):
        assert media_content.is_tag("audio") or media_content.is_tag(
            "speak"), "Only audio and speak tags are allowed in media"

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

    def __init__(self, content: TagArrayOrList, *, alphabet: str, ph: str):
        assert alphabet in self.SUPPORTED_PHONETIC_ALPHABETS, "Unsupported phonetic alphabet"
        super().__init__(content, "phoneme", {
            "alphabet": alphabet,
            "ph": ph
        })


class Voice(SsmlTag):
    def __init__(self,
                 content: TagArrayOrList,
                 *,
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
    def __init__(self, content: TagArrayOrList, *, lang: str):
        # TODO: assert lang is BCP-47 lang
        super().__init__(content, "lang", {
            "xml:lang": lang
        })


class PS(P):
    def __init__(self, content: TagArrayOrList):
        super().__init__(S(content))


class PSText(PS):
    def __init__(self, content: str):
        super().__init__(RawText(content))


class PText(P):
    def __init__(self, content: str):
        super().__init__(RawText(content))


class SText(S):
    def __init__(self, content: str):
        super().__init__(RawText(content))
