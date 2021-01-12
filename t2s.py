from google.cloud import texttospeech
from functools import reduce
from google.cloud import storage
import io


class TextToSpeech:
    def __init__(self, bucket_name, json=None):
        if json:
            self.client = texttospeech.TextToSpeechClient.from_service_account_json(json)
            self.storage_client = storage.Client.from_service_account_json(json)
        else:
            self.client = texttospeech.TextToSpeechClient()
            self.storage_client = storage.Client()

        self.bucket = self.storage_client.get_bucket(bucket_name)

    def t2s(self, text):
        synthesis_input = texttospeech.SynthesisInput(ssml=text)
        voice = texttospeech.VoiceSelectionParams(
            name="en-US-Wavenet-A", language_code="en-US"
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

    def upload_bytes(self, blob_name, content):
        blob = self.bucket.blob(blob_name)
        blob.upload_from_file(io.BytesIO(content))
        return blob.public_url

    def upload_xml(self, blob_name, content):
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(content, content_type='text/xml')
        return blob.public_url

    def download_xml(self, blob_name):
        blob = self.bucket.blob(blob_name)
        return blob.download_as_string().decode("utf-8")

    def delete_blob(self, blob_name):
        blob = self.bucket.blob(blob_name)
        blob.delete()

    def upload_lines(self, lines, blob_name):
        content = self.lines_to_speech(lines)
        return self.upload_bytes(blob_name, content)


if __name__ == "__main__":
    path = "ssml/The TechCrunch Exchange - Bootstrapping to $80M ARR.txt"
    with open(path) as f:
        lines = f.readlines()
    t2s = TextToSpeech("autopodcast")
    t2s.upload_lines(lines, "test_pod.mp3")
