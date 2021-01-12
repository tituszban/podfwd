from google.cloud import texttospeech
from functools import reduce
from google.cloud import storage
import io


class TextToSpeech:
    def __init__(self, config):
        json = config.get("SA_FILE")
        if json:
            self.client = texttospeech.TextToSpeechClient.from_service_account_json(
                json)
        else:
            self.client = texttospeech.TextToSpeechClient()

    def t2s(self, text, voice="en-US-Wavenet-A"):
        synthesis_input = texttospeech.SynthesisInput(ssml=text)
        voice = texttospeech.VoiceSelectionParams(
            name=voice, language_code="en-US"
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        return response.audio_content

    def f2s(self, path):
        with open(path, encoding="utf-8") as f:
            return self.t2s(f.read())

    def lines_to_speech(self, lines):
        snippets = [self.t2s(l) for l in lines]
        return reduce(lambda a, b: a + b, snippets)
