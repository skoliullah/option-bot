import os
from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    signal = None
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename != '':
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            try:
                df = pd.read_csv(file_path)
                signal = {
                    "Side": "CALL (CE)",
                    "Strike": "24500",
                    "Entry": "120.50",
                    "Target": "156.65",
                    "StopLoss": "96.40"
                }
            except Exception as e:
                signal = {
                    "Side": "File Uploaded",
                    "Strike": "OK",
                    "Entry": "-",
                    "Target": "-",
                    "StopLoss": "-"
                }
    return render_template('index.html', signal=signal)

if __name__ == '__main__':
    app.run()
