import re
from typing import Tuple, List, Literal, Generator, Iterable, T, Dict

import emoji
import skia


class GeneratorWrapper(Iterable[T]):
    def __init__(self, generator: Generator[T, None, None]):
        self.generator = generator
        self.cache: List[T] = []  # Cache to store already generated items

    def __iter__(self) -> Generator[T, None, None]:
        # Yield items from the cache first
        for item in self.cache:
            yield item

        # Continue generating new items and add them to the cache
        for item in self.generator:
            # print("Init " + str(item))
            self.cache.append(item)
            yield item


def render_text(text: str,
                canvas_sz: Tuple[int, int],
                margins: Tuple[int, int, int, int],
                fonts: Iterable[skia.Font],
                align: Literal['left', 'center', 'right'] = 'left') -> Tuple[bytes, float]:

    default_font = next(iter(fonts))
    # We need some emoji to compute the width
    always_present_emoji = "😀"

    # Detect multi-character emoji
    # and handle them separately
    emoji_start: Dict[int, int] = {}
    emoji_set = set()
    emoji_font = default_font
    for token in iter(emoji.analyze(text)):
        if len(token.chars) > 1:
            emoji_set.add(token.chars)
            emoji_start[token.value.start] = len(token.chars)
            # print(token.chars, len(token.chars), token.value.start)
    if len(emoji_set) > 0:
        for font in fonts:
            if font.unicharToGlyph(ord(always_present_emoji)) != 0:
                emoji_font = font
                break

    def measure_width(text: str, font: skia.Font) -> float:
        is_emoji = text in emoji_set
        w = font.measureText(always_present_emoji) if is_emoji else font.measureText(text)
        return w

    # Split text into same-font runs
    runs: List[Tuple[str, skia.Font]] = []
    text_len = len(text)
    i = 0
    while i < text_len:
        if i in emoji_start.keys():
            emoji_len = emoji_start[i]
            runs.append((text[i:i+emoji_len], emoji_font))
            i += emoji_len
        else:
            char = text[i]
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
            i += 1

    # Compute bbox
    x_start = margins[0]
    max_width = canvas_sz[0] - x_start - margins[2]

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
            word_width = measure_width(word.rstrip(), font)
            if not new_line_before and (len(curr_line) == 0 or word_width + curr_line_width <= max_width):
                # Continue prev line
                curr_line.append((word, font))
                curr_line_width += measure_width(word, font)
            else:
                # Start new line
                lines.append([(word, font)])
                curr_line_width = measure_width(word, font)
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

    # TODO: better offset?
    y_start = margins[1]
    max_height = canvas_sz[1] - y_start - margins[3]

    # Print each line
    paint = skia.Paint(AntiAlias=True, Color=skia.ColorBLACK)
    y_offset = y_start
    for i, line in enumerate(lines):
        line_width = sum([measure_width(t, f) for t, f in line])
        line_height = max([f.getSpacing() for _, f in line])
        y_offset += line_height

        print(f"Line {i}", "".join([w for w, f in line]), line_width)
        if align == 'left':
            x_offset = x_start
        elif align == 'center':
            x_offset = x_start + (max_width - line_width) / 2
        else:
            x_offset = max_width - line_width
        for run_text, font in line:
            is_emoji = run_text in emoji_set
            if is_emoji:
                blob = skia.TextBlob.MakeFromShapedText(run_text, font)
                descent = font.getMetrics().fDescent
                canvas.drawTextBlob(blob, x_offset, y_offset - line_height + descent, paint)
                x_offset += measure_width(run_text, font)
            else:
                builder.allocRun(run_text, font, x_offset, y_offset)
                x_offset += measure_width(run_text, font)

    # Draw the built text blob
    text_blob = builder.make()

    paint = skia.Paint(AntiAlias=True, Color=skia.ColorBLACK)
    canvas.drawTextBlob(text_blob, 0, 0, paint)

    # Debug
    # Bbox
    rect = skia.Rect.MakeXYWH(margins[0], margins[1], max_width, max_height)
    paint = skia.Paint()
    paint.setStyle(skia.Paint.kStroke_Style)
    paint.setColor(skia.ColorRED)
    canvas.drawRect(rect, paint)
    # Bottom line
    rect = skia.Rect.MakeXYWH(0, y_offset, canvas_sz[0], 1)
    paint.setColor(skia.ColorBLUE)
    canvas.drawRect(rect, paint)

    # Save output to PNG
    image = surface.makeImageSnapshot()

    # You may use y_bottom to detect vertical overflow
    y_bottom = y_offset + margins[3]
    return bytes(image.encodeToData(skia.kPNG, 100)), y_bottom


if __name__ == "__main__":
    long_word = "really_looooooooooooooooooooooooooooooooooong_word_long_word"
    painter = "👩🏼‍🎨"
    text = f"{painter}{painter}\nHello 😀. Let's celebrate🎉!\nHello 😀. Let's celebrate🎉!\n\na\nb\nc\n{long_word}"
    # text = "ABC" # default font only
    font_size = 30

    fonts = ['./HelveticaNeueLTCom-BdCn.ttf', './NotoColorEmoji-Regular.ttf']
    fonts = (skia.Font(skia.Typeface.MakeFromFile(f, 0), font_size) for f in fonts)
    fonts = GeneratorWrapper(fonts)

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
