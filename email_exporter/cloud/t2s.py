from google.cloud import texttospeech
from functools import reduce
# from google.cloud import storage
# import io


class TextToSpeech:
    # https://cloud.google.com/text-to-speech/docs/voices
    # The ones that are missing I don't like
    supported_languages = [
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

    def __init__(self, config, logger):
        json = config.get("SA_FILE")
        if json:
            self.client = texttospeech.TextToSpeechClient.from_service_account_json(
                json)
        else:
            self.client = texttospeech.TextToSpeechClient()
        self._logger = logger

    def t2s(self, text, voice=None):
        if voice not in self.supported_languages:
            voice = "en-US-Wavenet-A"

        self._logger.info(f"Converting {len(text)} characters of text to speech, using voice: {voice}")

        language_code = '-'.join(voice.split("-")[:2])
        synthesis_input = texttospeech.SynthesisInput(ssml=text)
        voice = texttospeech.VoiceSelectionParams(
            name=voice, language_code=language_code
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        audio_content = response.audio_content

        self._logger.info(f"Received {len(audio_content)} bytes of audio content")

        return audio_content

    def f2s(self, path):
        self._logger.info(f"Converting file {path} to speech")
        with open(path, encoding="utf-8") as f:
            return self.t2s(f.read())

    def lines_to_speech(self, lines, voice=None):
        self._logger.info(f"Converting {len(lines)} blocks of text to speech")
        snippets = [self.t2s(line, voice) for line in lines]
        return reduce(lambda a, b: a + b, snippets)
