import speech_recognition as sr
from streamlit_webrtc import AudioProcessorBase
import av
import streamlit as st

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.text_result = ""

    def recv_audio(self, frame: av.AudioFrame) -> av.AudioFrame:
        try:
            sound = frame.to_ndarray()
            if sound.max() > 0.01:
                audio_data = sr.AudioData(sound.tobytes(), frame.sample_rate, 2)
                try:
                    self.text_result = self.recognizer.recognize_google(audio_data, language='en-US')
                    print("Recognized text:", self.text_result)
                    import streamlit as st
                    if hasattr(st, 'session_state'):
                        st.session_state.recognized_text = self.text_result
                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")
        except Exception as e:
            print("Audio processing exception:", e)
        return frame

