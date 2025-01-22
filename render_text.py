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

    primary_font =  skia.Font(skia.Typeface.MakeFromFile('./HelveticaNeueLTCom-BdCn.ttf', 0), font_size)
    emoji_font = skia.Font(skia.Typeface.MakeFromFile('NotoColorEmoji-Regular.ttf', 0), font_size)

    # Define font and paint
    paint = skia.Paint(AntiAlias=True, Color=skia.ColorBLACK)

    # Draw text using helvetica
    canvas.drawTextBlob(skia.TextBlob.MakeFromString(text, primary_font), 20, 50, paint)
    
    # Draw text using emoji font
    canvas.drawTextBlob(skia.TextBlob.MakeFromString(text, emoji_font), 20, 150, paint)

    # Save output to PNG
    image = surface.makeImageSnapshot()
    image.save("output.png", skia.kPNG)
    print("Rendered text saved as 'output.png'. Check for missing emojis (rendered as '?').")

if __name__ == "__main__":
    render_text()
