# python skia example
Requires Python 3.x. I tested it with Python 3.13.1

Setup:
```
pip install -r requirements.txt
```

Run it:
```
python render_text.py
```

After running, check output.png. Note that the sample text contains emojis. Note that we can render the text with either font but that one font only supports the regular characters and displays emojis with "?".

We want to render the text using the first font (Helvetica) but fall back to the second font (Noto Color Emoji) for emoji characters.

Check out "desired_outcome.png" for an example of what we'd like to accomplish.