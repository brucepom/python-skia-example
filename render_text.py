from typing import Tuple, List

import skia


def render_text(text: str,
                canvas_sz: Tuple[int, int],
                margins: Tuple[int, int, int, int],
                fonts: List[skia.Font]):

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
        if len(runs) == 0 or runs[-1][1] != curr_font:
            # New run
            runs.append((char, curr_font))
        else:
            # Append to prev run
            runs[-1] = runs[-1][0] + char, runs[-1][1]

    # Compute bbox
    line_height = fonts[0].getSpacing()
    x_start = margins[0]
    # TODO: better offset?
    y_start = margins[1] + line_height / 2
    max_width = canvas_sz[0] - x_start - margins[2]

    # Split text into lines
    lines: List[List[Tuple[str, skia.Font]]] = [[]]
    curr_line_width = 0
    for run_text, font in runs:
        for word in run_text.split(' '):
            curr_line = lines[-1]
            word_width = font.measureText(word)
            if len(curr_line) == 0 or word_width + curr_line_width <= max_width:
                # Continue prev line
                curr_line.append((word, font))
                curr_line.append((" ", default_font))
                curr_line_width += word_width + default_font.measureText(" ")
            else:
                # Start new line
                lines.append([(word, font)])
                curr_line.append((" ", default_font))
                curr_line_width = word_width + default_font.measureText(" ")

    # Create a Skia surface and canvas
    surface = skia.Surface(canvas_sz[0], canvas_sz[1])
    canvas = surface.getCanvas()
    canvas.clear(skia.ColorWHITE)
    builder = skia.TextBlobBuilder()

    # Print each line
    y_offset = y_start
    for line in lines:
        print("".join([w for w, f in line]))
        x_offset = x_start
        for run_text, font in line:
            # print(run_text)
            builder.allocRun(run_text, font, x_offset, y_offset)
            x_offset += font.measureText(run_text)
        y_offset += line_height

    # Draw the built text blob
    text_blob = builder.make()

    paint = skia.Paint(AntiAlias=True, Color=skia.ColorBLACK)
    canvas.drawTextBlob(text_blob, 0, 0, paint)

    # Save output to PNG
    image = surface.makeImageSnapshot()
    image.save("output.png", skia.kPNG)
    print("Rendered text saved as 'output.png'")


if __name__ == "__main__":
    text = "Hello 😀. Let's celebrate🎉!\n Hello 😀. Let's celebrate🎉!\n"
    font_size = 30

    fonts = ['./HelveticaNeueLTCom-BdCn.ttf', './NotoColorEmoji-Regular.ttf']
    fonts = [skia.Font(skia.Typeface.MakeFromFile(f, 0), font_size) for f in fonts]

    render_text(text, (500, 200), (50, 50, 50, 50), fonts)
