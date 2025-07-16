from abc import ABC, abstractmethod
from google.cloud import texttospeech
from functools import reduce
from email_exporter.config import Config
from logging import Logger
from typing import Union, List
from google import genai
from google.genai import types
import wave
import io


class T2SOutput(ABC):
    def __init__(self, extension: str):
        self.extension = extension

    @property
    @abstractmethod
    def audio_content(self) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def __add__(self, other: 'T2SOutput') -> 'T2SOutput':
        raise NotImplementedError


class Mp3T2SOutput(T2SOutput):
    def __init__(self, audio_content: bytes):
        super().__init__("mp3")
        self._audio_content = audio_content

    @property
    def audio_content(self) -> bytes:
        return self._audio_content

    def __add__(self, other: 'T2SOutput') -> 'T2SOutput':
        if not isinstance(other, Mp3T2SOutput):
            raise TypeError("Can only add Mp3T2SOutput instances")
        return Mp3T2SOutput(self._audio_content + other.audio_content)


class WaveT2SOutput(T2SOutput):
    def __init__(self, audio_content: bytes):
        super().__init__("wav")
        self._raw_audio = audio_content

    @property
    def audio_content(self) -> bytes:
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(self._raw_audio)
        return buffer.getvalue()

    def __add__(self, other: 'T2SOutput') -> 'T2SOutput':
        if not isinstance(other, WaveT2SOutput):
            raise TypeError("Can only add WaveT2SOutput instances")
        return WaveT2SOutput(self._raw_audio + other._raw_audio)


class TextToSpeech:
    # https://cloud.google.com/text-to-speech/docs/voices
    # The ones that are missing I don't like
    classic_voices = [
        "en-US-Wavenet-A",  # Male
        "en-US-Wavenet-B",  # Male
        "en-US-Wavenet-C",  # Female
        "en-US-Wavenet-D",  # Male
        "en-US-Wavenet-E",  # Female
        "en-US-Wavenet-F",  # Female
        "en-US-Wavenet-G",  # Female
        "en-US-Wavenet-H",  # Female
        "en-US-Wavenet-I",  # Male
        "en-US-Wavenet-J",  # Male
        "en-GB-Wavenet-A",  # Female
        "en-GB-Wavenet-B",  # Male
        "en-GB-Wavenet-F",  # Female
    ]
    # https://ai.google.dev/gemini-api/docs/speech-generation#voices
    gemini_voices = [
        "Zephyr",           # Male
        "Puck",             # Male
        "Charon",           # Male * - CO
        "Kore",             # Female
        "Fenrir",           # Male
        "Leda",             # Female
        "Orus",             # Male
        "Aoede",            # Female
        "Callirrhoe",       # Female
        "Autonoe",          # Female
        "Enceladus",        # Male * - Pragmatic Engineer
        "Iapetus",          # Male
        "Umbriel",          # Male
        "Algieba",          # Male * - Maybe BigTechnology
        "Despina",          # Female
        "Erinome",          # Female
        "Algenib",          # Male
        "Rasalgethi",       # Male
        "Laomedeia",        # Female * - Heated
        "Achernar",         # Female
        "Alnilam",          # Male *
        "Schedar",          # Male - bad
        "Gacrux",           # Female
        "Pulcherrima",      # Female *
        "Achird",           # Male
        "Zubenelgenubi",    # Male
        "Vindemiatrix",     # Female
        "Sadachbia",        # Male
        "Sadaltager",       # Male
        "Sulafat",          # Female *
    ]

    def __init__(self, config: Config, logger: Logger) -> None:
        json = config.get("SA_FILE")
        if json:
            self._t2s_client = texttospeech.TextToSpeechClient.from_service_account_json(json, *[])
        else:
            self._t2s_client = texttospeech.TextToSpeechClient()
        self._gemini_client = genai.Client(api_key=config.get("GEMINI_API_KEY"))
        self._logger = logger

    def t2s(self, text: str, voice: Union[str, None] = None) -> T2SOutput:
        if voice is None:
            voice = "en-US-Wavenet-A"

        if voice in self.classic_voices:
            return self._classical_t2s(text, voice)
        elif voice in self.gemini_voices:
            return self._gemini_t2s(text, voice)
        else:
            raise ValueError(
                f"Voice {voice} is not supported by TTS. Supported voices: {self.classic_voices + self.gemini_voices}")

    def _classical_t2s(self, text: str, voice: str) -> T2SOutput:
        assert voice in self.classic_voices, f"Voice {voice} is not supported by TTS"
        self._logger.info(f"Converting {len(text)} characters of text to speech, using voice: {voice}")

        language_code = '-'.join(voice.split("-")[:2])
        synthesis_input = texttospeech.SynthesisInput(ssml=text)
        voice = texttospeech.VoiceSelectionParams(
            name=voice, language_code=language_code
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = self._t2s_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        audio_content = response.audio_content

        self._logger.info(f"Received {len(audio_content)} bytes of audio content")

        return Mp3T2SOutput(audio_content)

    def _gemini_t2s(self, text: str, voice: str) -> T2SOutput:
        assert voice in self.gemini_voices, f"Voice {voice} is not supported by Gemini TTS"
        response = self._gemini_client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice,
                        )
                    )
                ),
            )
        )
        data = response.candidates[0].content.parts[0].inline_data.data

        return WaveT2SOutput(data)

    def f2s(self, path: str):
        self._logger.info(f"Converting file {path} to speech")
        with open(path, encoding="utf-8") as f:
            return self.t2s(f.read())

    def lines_to_speech(self, lines: List[str], voice: Union[str, None] = None) -> T2SOutput:
        self._logger.info(f"Converting {len(lines)} blocks of text to speech")
        # TODO: Gemini has different limits, so it may be possible to merge lines in text before syntesising
        snippets = [self.t2s(line, voice) for line in lines]
        return reduce(lambda a, b: a + b, snippets)
