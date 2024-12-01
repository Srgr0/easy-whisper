from flask import Flask, request, render_template, jsonify, Response, stream_with_context
import subprocess
import os
from werkzeug.utils import secure_filename
# from flask_basicauth import BasicAuth
import logging
import json

app = Flask(__name__)

# Basic認証の設定
# app.config['BASIC_AUTH_USERNAME'] = 'your_username'
# app.config['BASIC_AUTH_PASSWORD'] = 'your_password'
# basic_auth = BasicAuth(app)

# アップロードフォルダの設定
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/", methods=["GET", "POST"])
# @basic_auth.required
def index():
    if request.method == "POST":
        def process_audio():
            try:
                if "url" in request.form and request.form["url"]:
                    # URLが入力された場合
                    url = request.form["url"]
                    filename = secure_filename("downloaded_audio.mp3")
                    filepath = os.path.join(UPLOAD_FOLDER, filename)

                    yield "Downloading from URL...<br>"
                    subprocess.run(["yt-dlp", "-x", "--audio-format", "mp3", "-o", filepath, url], check=True)
                elif "file" in request.files:
                    # ファイルがアップロードされた場合
                    file = request.files["file"]
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    yield "File uploaded successfully.<br>"
                else:
                    yield "No input provided. Please provide a URL or upload a file.<br>"
                    return

                # ffmpegでOGGに変換
                ogg_filepath = os.path.splitext(filepath)[0] + ".ogg"
                yield "Converting to OGG...<br>"
                subprocess.run([
                    "ffmpeg", "-i", filepath, "-vn", "-map_metadata", "-1",
                    "-ac", "1", "-c:a", "libopus", "-b:a", "12k", "-application", "voip", ogg_filepath
                ], check=True)

                # Whisper APIを呼び出す
                yield "Calling Whisper API...<br>"
                whisper_response = subprocess.run([
                    "curl", "https://api.openai.com/v1/audio/transcriptions",
                    "-H", f"Authorization: Bearer {API_KEY}",
                    "-H", "Content-Type: multipart/form-data",
                    "-F", f"file=@{ogg_filepath}",
                    "-F", "model=whisper-1",
                    "-F", "response_format=verbose_json"
                ], capture_output=True, text=True)

                response_json = whisper_response.stdout
                yield f"Whisper API Response:<br><pre>{json.dumps(json.loads(response_json), indent=2)}</pre>"
            except subprocess.CalledProcessError as e:
                yield f"Error occurred: {e}<br>"

        return Response(stream_with_context(process_audio()))

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
