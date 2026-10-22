import sqlite3
import statistics as st
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
DB = "keytone.db"

ARCHETYPES = {
    "Debugger":  "You type, doubt, delete, and refine. Your code survives because you question it.",
    "Sprinter":  "Fast bursts, wild tempo. You ship ideas before they cool down.",
    "Metronome": "Steady as a clock. Your commits are as predictable as they are clean.",
    "Architect": "Long pauses, deliberate strokes. You design in your head, then type once.",
    "Marathoner": "Balanced and durable. You can type for hours without losing the thread.",
}


def clamp(x, lo=0, hi=100):
    return max(lo, min(hi, x))


def analyze(events):
    times = [e["t"] for e in events if isinstance(e.get("t"), (int, float))]
    if len(times) < 15:
        return None
    gaps = [b - a for a, b in zip(times, times[1:]) if b > a]
    fast = [g for g in gaps if g < 600]
    pauses = [g for g in gaps if g >= 600]
    back = sum(1 for e in events if e.get("k") == "Backspace")
    minutes = (times[-1] - times[0]) / 60000 or 1e-6
    wpm = (len(times) - back) / 5 / minutes
    cv = st.pstdev(fast) / st.mean(fast) if len(fast) > 2 else 1

    axes = {
        "Speed": clamp(wpm / 90 * 100),
        "Rhythm": clamp(120 - cv * 100),
        "Accuracy": clamp(100 - back / len(times) * 600),
        "Flow": clamp(len(fast) / max(len(gaps), 1) * 100),
        "Thinking": clamp(len(pauses) / len(times) * 800),
    }
    if axes["Accuracy"] < 60:
        name = "Debugger"
    elif axes["Speed"] > 70 and axes["Rhythm"] < 55:
        name = "Sprinter"
    elif axes["Rhythm"] >= 70:
        name = "Metronome"
    elif axes["Thinking"] >= 45:
        name = "Architect"
    else:
        name = "Marathoner"
    return {"wpm": round(wpm, 1), "axes": {k: round(v) for k, v in axes.items()},
            "archetype": name, "about": ARCHETYPES[name]}


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/analyze")
def api_analyze():
    result = analyze((request.get_json(silent=True) or {}).get("events", []))
    if not result:
        return jsonify(error="Type at least 15 keys so there is a rhythm to read."), 400
    with sqlite3.connect(DB) as con:
        con.execute("create table if not exists runs(wpm real, archetype text)")
        total = con.execute("select count(*) from runs").fetchone()[0]
        slower = con.execute("select count(*) from runs where wpm < ?", (result["wpm"],)).fetchone()[0]
        con.execute("insert into runs values(?, ?)", (result["wpm"], result["archetype"]))
    result["percentile"] = round(slower / total * 100) if total else None
    result["runs"] = total + 1
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
