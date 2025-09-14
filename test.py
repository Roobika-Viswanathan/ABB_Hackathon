import streamlit as st
from streamlit.components.v1 import html

st.title("Browser Speech-to-Text with Copy-Paste Workaround")

st.markdown("### Click 'Start Recording' and speak.")

speech_to_text_html = """
<button id="start-btn">Start Recording</button>
<div id="output" style="margin-top:10px; font-size:1.2em; color:#333; border:1px solid #ddd; padding:5px;"></div>
<textarea id="recognized-text" style="width: 100%; height: 100px; margin-top: 10px;" placeholder="Recognized text will appear here..."></textarea>

<script>
const btn = document.getElementById('start-btn');
const output = document.getElementById('output');
const textarea = document.getElementById('recognized-text');

let recognizing = false;
let recognition;

if (!('webkitSpeechRecognition' in window)) {
  output.textContent = 'Web Speech API not supported in this browser.';
} else {
  recognition = new webkitSpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.lang = 'en-US';

  recognition.onstart = () => {
    recognizing = true;
    btn.textContent = 'Listening... Click to Stop';
  };

  recognition.onerror = (event) => {
    output.textContent = 'Error: ' + event.error;
  };

  recognition.onend = () => {
    recognizing = false;
    btn.textContent = 'Start Recording';
  };

  recognition.onresult = (event) => {
    let finalTranscript = '';
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        finalTranscript += event.results[i][0].transcript;
      }
    }
    textarea.value = finalTranscript;
    output.textContent = finalTranscript;
  };
}

btn.onclick = () => {
  if (recognizing) recognition.stop();
  else recognition.start();
};
</script>
"""

html(speech_to_text_html, height=250)

recognized_text = st.text_area("Use or edit recognised text below:")

if st.button("Use Recognized Text"):
    st.success(f"Text received: {recognized_text}")
    # Use recognized_text further in your app logic here
