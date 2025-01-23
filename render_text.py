from typing import Tuple, List

import skia


def render_text(text: str,
                font_size: float,
                canvas_sz: Tuple[int, int],
                margins: Tuple[int, int, int, int],
                fonts: List[skia.Font]):

    # Create a Skia surface and canvas
    surface = skia.Surface(canvas_sz[0], canvas_sz[1])
    canvas = surface.getCanvas()

    # Set background color
    canvas.clear(skia.ColorWHITE)

    # Create a text blob builder
    builder = skia.TextBlobBuilder()

    # Split text into same-font runs
    runs: List[Tuple[str, skia.Font]] = []
    for char in text:
        # Default to the first font
        curr_font = fonts[0]
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

    # Print each run
    x_offset = margins[0]
    # TODO: better offset
    y_offset = margins[1] + runs[0][1].getSpacing() / 2
    for run_text, font in runs:
        builder.allocRun(run_text, font, x_offset, y_offset)
        x_offset += font.measureText(run_text)

    # Draw the built text blob
    text_blob = builder.make()

    paint = skia.Paint(AntiAlias=True, Color=skia.ColorBLACK)
    canvas.drawTextBlob(text_blob, 0, 0, paint)

    # Save output to PNG
    image = surface.makeImageSnapshot()
    image.save("output.png", skia.kPNG)
    print("Rendered text saved as 'output.png'")


if __name__ == "__main__":
    text = "Hello 😀. Let's celebrate🎉 !\n Hello 😀. Let's celebrate🎉 !\n"
    font_size = 30

    fonts = ['./HelveticaNeueLTCom-BdCn.ttf', './NotoColorEmoji-Regular.ttf']
    fonts = [skia.Font(skia.Typeface.MakeFromFile(f, 0), font_size) for f in fonts]

    render_text(text, font_size, (500, 200), (50, 50, 50, 50), fonts)
