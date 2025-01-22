import skia

# Example text with emojis
text = "Hello 😀. Let's celebrate🎉 !"
font_size = 18
canvas_width, canvas_height = 500, 200

def render_text():
    # Create a Skia surface and canvas
    surface = skia.Surface(canvas_width, canvas_height)
    canvas = surface.getCanvas()

    # Set background color
    canvas.clear(skia.ColorWHITE)

    # Load primary and emoji fonts
    primary_font = skia.Font(skia.Typeface.MakeFromFile('./HelveticaNeueLTCom-BdCn.ttf', 0), font_size)
    emoji_font = skia.Font(skia.Typeface.MakeFromFile('NotoColorEmoji-Regular.ttf', 0), font_size)

    fallback_fonts = [
        primary_font,
        emoji_font,
    ]

    # Create a text blob builder
    builder = skia.TextBlobBuilder()
    paint = skia.Paint(AntiAlias=True, Color=skia.ColorBLACK)

    # Manually process each character for font fallback
    x_offset = 20  # Start position
    y_offset = 50  # Baseline position
    for char in text:
        for font in fallback_fonts:
            if font.unicharToGlyph(ord(char)) != 0:
                builder.allocRun(char, font, x_offset, y_offset)
                x_offset += font.measureText(char)
                break

    # Draw the built text blob
    text_blob = builder.make()
    canvas.drawTextBlob(text_blob, 0, 0, paint)

    # Save output to PNG
    image = surface.makeImageSnapshot()
    image.save("output.png", skia.kPNG)
    print("Rendered text saved as 'output.png'. Check for missing emojis (rendered as '?').")

if __name__ == "__main__":
    render_text()
