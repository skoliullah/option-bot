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
    if file and file.filename.endswith('.csv'):
      file_path = os.path.join(UPLOAD_FOLDER, file.filename)
      file.save(file_path)

      cols = [
          'C_Dummy',
          'C_OI',
          'C_CHNG_IN_OI',
          'C_VOLUME',
          'C_IV',
          'C_LTP',
          'C_CHNG',
          'C_BID_QTY',
          'C_BID',
          'C_ASK',
          'C_ASK_QTY',
          'STRIKE',
          'P_BID_QTY',
          'P_BID',
          'P_ASK',
          'P_ASK_QTY',
          'P_CHNG',
          'P_LTP',
          'P_IV',
          'P_VOLUME',
          'P_CHNG_IN_OI',
          'P_OI',
          'P_Dummy',
      ]
      df = pd.read_csv(file_path, skiprows=2, header=None, names=cols)

      for col in df.columns:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(',', ''), errors='coerce'
        )

      total_c_vol = df['C_VOLUME'].sum()
      total_p_vol = df['P_VOLUME'].sum()

      if total_p_vol > total_c_vol:
        best_row = df.sort_values(by='P_VOLUME', ascending=False).iloc[0]
        side = 'PUT (PE)'
        strike = best_row['STRIKE']
        ltp = best_row['P_LTP']
      else:
        best_row = df.sort_values(by='C_VOLUME', ascending=False).iloc[0]
        side = 'CALL (CE)'
        strike = best_row['STRIKE']
        ltp = best_row['C_LTP']

      target = round(ltp * 1.30, 2)
      stop_loss = round(ltp * 0.80, 2)

      signal = {
          'Side': side,
          'Strike': strike,
          'Entry': ltp,
          'Target': target,
          'StopLoss': stop_loss,
      }

  return render_template('index.html', signal=signal)


if __name__ == '__main__':
  app.run(debug=True)
