from flask import Flask, render_template, request, send_file
import os
import tempfile
import pydub
from openai import OpenAI

app = Flask(__name__)

# Replace YOUR_API_KEY with your actual OpenAI API key
openai = OpenAI(api_key="")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    text = request.form['text']
    model = request.form['model']
    voice = request.form['voice']
    format = request.form['format']
    name = request.form['name']  # Retrieve the name from the form

    mp3_speech_path = text_to_speech(text, model, voice)

    if format != "mp3":
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format}") as tmpfile:
            convert_audio_format(mp3_speech_path, tmpfile.name, format)
            speech_path = tmpfile.name
        os.remove(mp3_speech_path)
    else:
        speech_path = mp3_speech_path

    if name:  # Check if a name is provided
        name = name.replace(" ", "_")  # Replace spaces with underscores in the name
        speech_path_with_name = f"{name}.{format}"  # Add the name to the file name
        os.rename(speech_path, speech_path_with_name)
        speech_path = speech_path_with_name

    return send_file(speech_path, as_attachment=True)

def text_to_speech(text, model, voice):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        speech_file_path = tmpfile.name
        response = openai.audio.speech.create(
            model=model,
            voice=voice,
            input=text
        )
        response.stream_to_file(speech_file_path)
        return speech_file_path

def convert_audio_format(input_path, output_path, format):
    audio = pydub.AudioSegment.from_mp3(input_path)
    audio.export(output_path, format=format)

if __name__ == '__main__':
    app.run(debug=True)