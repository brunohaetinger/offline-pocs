import curses
import sys
import markdown2

def render_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    # Convert markdown to HTML, then strip tags (quick demo)
    html = markdown2.markdown(text)
    # crude stripping for now
    clean = html.replace("<p>", "").replace("</p>", "\n")
    clean = clean.replace("<strong>", "").replace("</strong>", "")
    clean = clean.replace("<em>", "").replace("</em>", "")
    return clean

def main(stdscr, file_path):
    curses.curs_set(0)
    stdscr.clear()
    content = render_markdown(file_path).splitlines()
    h, w = stdscr.getmaxyx()
    pos = 0

    while True:
        stdscr.clear()
        for idx, line in enumerate(content[pos:pos + h - 1]):
            stdscr.addstr(idx, 0, line[:w-1])
        stdscr.refresh()

        key = stdscr.getch()
        if key == ord("q"):
            break
        elif key == curses.KEY_DOWN and pos < len(content) - h:
            pos += 1
        elif key == curses.KEY_UP and pos > 0:
            pos -= 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python md_previewer.py <file.md>")
        sys.exit(1)

    curses.wrapper(main, sys.argv[1])

