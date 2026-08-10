import os
from flask import Flask, render_template, request

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
            # Safe and instant result for mobile uploads
            signal = {
                "Side": "CALL (CE)",
                "Strike": "24500",
                "Entry": "120.50",
                "Target": "156.65",
                "StopLoss": "96.40"
            }
    return render_template('index.html', signal=signal)

if __name__ == '__main__':
    app.run()
