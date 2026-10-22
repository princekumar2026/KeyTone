# KeyTone

Type a few sentences and a Flask backend reads your keystroke rhythm, then tells you which developer archetype you type like (Debugger, Sprinter, Metronome, Architect, Marathoner).

- **Frontend:** vanilla JS captures keystroke timings, draws a live waveform on canvas, renders a radar chart in SVG.
- **Backend:** Flask + stdlib `statistics` compute WPM, rhythm consistency (coefficient of variation), pauses and correction rate.
- **Storage:** SQLite stores anonymous runs to give you a speed percentile.
- **Privacy:** only timings and a Backspace flag are sent. The actual characters never leave the browser.

## Run
    pip install -r requirements.txt
    python app.py   # http://127.0.0.1:5000

## Ideas to extend
Add auth + personal history, compare two people live with WebSockets, or train a small model on the stored runs.
