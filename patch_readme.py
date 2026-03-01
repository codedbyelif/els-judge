with open("README.md", "r") as f:
    text = f.read()

# Make sure we don't duplicate English instructions
if "### Terminal Dashboard (CLI)" not in text:
    pass # we know it's there from the read
else:
    # Let's cleanly replace the English instructions section so they match
    english_tui = """### Terminal Dashboard (CLI)

If you prefer the terminal, you can use our beautifully styled TUI (Terminal User Interface):

1. Make sure your `FastAPI` backend is running (`bash start.sh` or `uvicorn main:app`).
2. Open a new terminal window/tab and run the CLI tool:
   ```bash
   python cli.py
   ```
3. Paste your code into the left panel and press `Enter`.
4. Provide your instructions in the prompt input at the bottom.
5. Press `CTRL+R` or click the button to see the AI analyze your code directly in the terminal!"""

    import re
    text = re.sub(r"### Terminal Dashboard \(CLI\)[\s\S]*?---\n\n## Architecture", english_tui + "\n\n---\n\n## Architecture", text)

with open("README.md", "w") as f:
    f.write(text)
