from google.cloud import speech

class GoogleSpeechToText():
    def __init__(self) -> None:
        self.client = speech.SpeechClient()

    def transcribe(self, audio_file):
        """Transcribe the given audio file.
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
        )
        # The method returns a long-running operation, so we use async/await.
        operation = self.client.long_running_recognize(config=config, audio=audio)
        response = operation.result()
        for result in response.results:
            print(f"Transcript: {result.alternatives[0].transcript}")
        return response.results[0].alternatives[0].transcript
    """
        audio = speech.RecognitionAudio(content=audio_file.content)
        config=speech.RecognitionConfig()

        response = self.client.recognize(config=config, audio=audio)
        return response
