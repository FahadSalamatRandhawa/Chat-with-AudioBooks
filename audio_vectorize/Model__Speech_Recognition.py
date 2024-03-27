import speech_recognition as sr
import io
from pydub import AudioSegment
from pydub.silence import split_on_silence
from typing import List



class SpeechRecognitionModel():
    def __init__(self):
        self.r = sr.Recognizer()

    async def audioToText(self, audiofile):
        transcriptions:List[str]=[]
        wav_chunks:List[io.BytesIO]=[]
        # read file 
        format=audiofile.filename.split('.')[-1]
        print("File format", format)
        audio_data = io.BytesIO(await audiofile.read())
        print("file reading done : ",audio_data)
        audio:AudioSegment = AudioSegment.from_file(audio_data, format=format)
        print("audio segment done : ", audio)


        # split file in chunk
        audiochunks = split_on_silence(audio,
        min_silence_len = 1000,
        # adjust this per requirement
        silence_thresh = audio.dBFS-14,
        # keep the silence for 1 second, adjustable as well
        keep_silence=500,
        )


        # loop, convert chunks to wav and store in array
        for i, chunk in enumerate(audiochunks):
            wav_chunk=io.BytesIO()
            chunk.export(wav_chunk, format="wav")
            wav_chunk.seek(0)
            wav_chunks.append(wav_chunk)
        print("conversion to wav done, next step transcribing chunks ")

        
        for wav_data in wav_chunks:
            # recognize audio using Sphinx
            with sr.AudioFile(wav_data) as source:
                audio = self.r.record(source)
                text = self.r.recognize_google(audio)
                transcriptions.append(text)        

        return ' '.join(transcriptions)