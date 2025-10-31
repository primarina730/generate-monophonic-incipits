import os
import random
import re
from music21 import stream, note, meter, clef, key, tempo, duration
import verovio
import cairosvg

output_dir = "output_mei_png_varied"
os.makedirs(output_dir, exist_ok=True)

# time signature options
TIME_SIGNATURE_OPTIONS = ['3/4', '4/4']

# note duration options (quarter note = 1.0)
DURATION_OPTIONS = [
    ('whole', 4.0),
    ('half', 2.0),
    ('quarter', 1.0),
    ('eighth', 0.5),
    ('16th', 0.25)
]

# pitch range
PITCH_POOL = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4',
              'C5', 'D5', 'E5', 'F5', 'G5', 'A5', 'B5', 'C6']


def create_random_measure(beats_per_measure: float):
    """generate a measure with random notes/rests summing to beats_per_measure"""
    m = stream.Measure()
    remaining = beats_per_measure

    while remaining > 0:
        dur_name, dur_len = random.choice(DURATION_OPTIONS)
        # adjust if duration exceeds remaining beats
        if dur_len > remaining:
            dur_name, dur_len = ('quarter', remaining)  # round off

        # 20% chance of rest
        if random.random() < 0.2:
            n = note.Rest()
        else:
            n = note.Note(random.choice(PITCH_POOL))

        n.duration = duration.Duration(dur_len)
        m.append(n)
        remaining -= dur_len

    return m


def create_random_score():
    """generate a monophonic score with 3 measures (time signature aligned, varied rhythm)"""
    s = stream.Score()
    p = stream.Part()

    # basic settings
    p.append(clef.TrebleClef())
    ks = key.KeySignature(random.choice(range(-2, 3)))
    ts_str = random.choice(TIME_SIGNATURE_OPTIONS)
    ts = meter.TimeSignature(ts_str)
    p.append(ks)
    p.append(ts)
    p.append(tempo.MetronomeMark(number=random.randint(80, 140)))

    beats_per_measure = ts.barDuration.quarterLength

    for _ in range(3):  # 3measures
        m = create_random_measure(beats_per_measure)
        p.append(m)

    s.append(p)
    return s


def clean_mei_and_svg(mei_str: str, svg_str: str):
    """remove <title> tags and format SVG"""
    mei_str = re.sub(r"<title>.*?</title>", "", mei_str, flags=re.DOTALL)
    svg_str = re.sub(r"<title>.*?</title>", "", svg_str, flags=re.DOTALL)
    return mei_str.strip(), svg_str.strip()


def export_via_musicxml(score, index):
    """export score to MusicXML, then convert to MEI, SVG, and PNG"""
    base = f"score_{index:04d}"
    xml_path = os.path.join(output_dir, base + ".musicxml")
    mei_path = os.path.join(output_dir, base + ".mei")
    svg_path = os.path.join(output_dir, base + ".svg")
    png_path = os.path.join(output_dir, base + ".png")

    # save MusicXML
    score.write('musicxml', fp=xml_path)

    # convert MusicXML to MEI and SVG using Verovio
    tk = verovio.toolkit()
    tk.setOptions({
        "adjustPageHeight": True,
        "adjustPageWidth": True,
        "scale": 40,
        "footer": "none",
        "header": "none",
        "noHeader": True,
        "noFooter": True
    })
    tk.loadFile(xml_path)

    mei_data = tk.getMEI()
    svg_data = tk.renderToSVG(1)
    mei_data, svg_data = clean_mei_and_svg(mei_data, svg_data)

    # save MEI
    with open(mei_path, "w", encoding="utf-8") as f:
        f.write(mei_data)

    # save SVG
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_data)
        # PNG conversion (white background)
    cairosvg.svg2png(
        bytestring=svg_data.encode('utf-8'),
        write_to=png_path,
        background_color='white'
    )
    print(f"Exported {base}.png (time signature aligned, varied rhythm)")


if __name__ == "__main__":
    for i in range(10):
        s = create_random_score()
        export_via_musicxml(s, i + 1)
