import re
from typing import Tuple, List, Literal

import skia


def render_text(text: str,
                canvas_sz: Tuple[int, int],
                margins: Tuple[int, int, int, int],
                fonts: List[skia.Font],
                align: Literal['left', 'center', 'right'] = 'left') -> Tuple[bytes, float]:

    # Split text into same-font runs
    runs: List[Tuple[str, skia.Font]] = []
    default_font = fonts[0]
    for char in text:
        # Default to first font
        curr_font = default_font
        for font in fonts:
            if font.unicharToGlyph(ord(char)) != 0:
                curr_font = font
                break
        prev_run = runs[-1] if runs else None
        if not prev_run or prev_run[1] != curr_font or prev_run[0][-1] == '\n':
            # New run
            runs.append((char, curr_font))
        else:
            # Append to prev run
            runs[-1] = runs[-1][0] + char, runs[-1][1]

    # Compute bbox
    line_height = fonts[0].getSpacing()
    x_start = margins[0]
    # TODO: better offset?
    y_start = margins[1] + line_height
    max_width = canvas_sz[0] - x_start - margins[2]
    max_height = canvas_sz[1] - y_start - margins[3]

    # Split text into lines
    lines: List[List[Tuple[str, skia.Font]]] = [[]]
    curr_line_width = 0
    for run_text, font in runs:
        # Regular expression to split and keep the separator attached to the previous word
        words = re.split(r'(\s|\n)', run_text)
        # Combine words with their separators
        words = ["".join(words[i:i + 2]) for i in range(0, len(words), 2) if words[i].strip()]
        for word in words:
            new_line_after = False
            if word.endswith('\n'):
                new_line_after = True
                word = word[:-1]
            new_line_before = False
            if word.startswith('\n'):
                new_line_before = True
                word = word[1:]

            curr_line = lines[-1]
            word_width = font.measureText(word.rstrip())
            if not new_line_before and (len(curr_line) == 0 or word_width + curr_line_width <= max_width):
                # Continue prev line
                curr_line.append((word, font))
                curr_line_width += font.measureText(word)
            else:
                # Start new line
                lines.append([(word, font)])
                curr_line_width = font.measureText(word)
            if new_line_after:
                lines.append([])
                curr_line_width = 0

    # Create a Skia surface and canvas
    surface = skia.Surface(canvas_sz[0], canvas_sz[1])
    canvas = surface.getCanvas()
    canvas.clear(skia.ColorWHITE)
    builder = skia.TextBlobBuilder()

    # remove trailing empty line
    if len(lines) > 0 and len(lines[-1]) == 0:
        lines = lines[:-1]

    # Print each line
    y_offset = y_start
    for i, line in enumerate(lines):
        print(f"Line {i}", "".join([w for w, f in line]))
        line_width = sum([f.measureText(t) for t, f in line])
        if align == 'left':
            x_offset = x_start
        elif align == 'center':
            x_offset = x_start + (max_width - line_width) / 2
        else:
            x_offset = max_width - line_width
        for run_text, font in line:
            builder.allocRun(run_text, font, x_offset, y_offset)
            x_offset += font.measureText(run_text)
        y_offset += line_height

    # Draw the built text blob
    text_blob = builder.make()

    paint = skia.Paint(AntiAlias=True, Color=skia.ColorBLACK)
    canvas.drawTextBlob(text_blob, 0, 0, paint)

    # Debug
    rect = skia.Rect.MakeXYWH(margins[0], margins[1], max_width, max_height)
    paint = skia.Paint()
    paint.setStyle(skia.Paint.kStroke_Style)
    paint.setColor(skia.ColorRED)
    canvas.drawRect(rect, paint)

    # Save output to PNG
    image = surface.makeImageSnapshot()
    print("Rendered text saved as 'output.png'")
    return bytes(image.encodeToData(skia.kPNG, 100)), y_offset + margins[3]


if __name__ == "__main__":
    long_word = "really_looooooooooooooooooooooooooooooooooong_word_long_word"
    text = f"Hello 😀. Let's celebrate🎉!\nHello 😀. Let's celebrate🎉!\n\na\nb\nc\n{long_word}"
    font_size = 30

    fonts = ['./HelveticaNeueLTCom-BdCn.ttf', './NotoColorEmoji-Regular.ttf']
    fonts = [skia.Font(skia.Typeface.MakeFromFile(f, 0), font_size) for f in fonts]

    canvas_sz = (600, 400)
    margins = (10, 50, 10, 50)

    image_bytes, _ = render_text(text, canvas_sz, margins, fonts)
    with open('output.png', 'wb') as f:
        f.write(image_bytes)

    image_bytes, _ = render_text(text, canvas_sz, margins, fonts, align='center')
    with open('output-center.png', 'wb') as f:
        f.write(image_bytes)

    image_bytes, _ = render_text(text, canvas_sz, margins, fonts, align='right')
    with open('output-right.png', 'wb') as f:
        f.write(image_bytes)
