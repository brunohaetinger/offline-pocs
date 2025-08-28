#!/usr/bin/env python3
import curses, curses.textpad
import sys, os, re, textwrap, time

HELP = "↑/k ↓/j: scroll  PgUp/PgDn  g/G: top/end  /:search  n/N: next/prev  r:reload  q:quit"

# ---------- Markdown -> styled line tuples ----------
# Each rendered item is (text, style) where style in:
# 'normal','h1','h2','h3','h4','h5','h6','list','quote','code','hr'

heading_re = re.compile(r'^(#{1,6})\s+(.*)$')
ulist_re   = re.compile(r'^\s*[-*+]\s+(.*)$')
olist_re   = re.compile(r'^\s*\d+[.)]\s+(.*)$')
hr_re      = re.compile(r'^\s*([-*_])(?:\s*\1){2,}\s*$')
link_re    = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

def strip_inline(md: str) -> str:
    # Convert [text](url) -> "text <url>"
    def repl(m):
        return f"{m.group(1)} <{m.group(2)}>"
    s = link_re.sub(repl, md)
    # Remove emphasis markers **, __, *, _ around words (simple)
    s = re.sub(r'(\*\*|__)(.*?)\1', r'\2', s)
    s = re.sub(r'(\*|_)(.*?)\1', r'\2', s)
    # Inline code: `x` -> x
    s = re.sub(r'`([^`]+)`', r'\1', s)
    return s

def render_markdown(lines, width):
    rendered = []
    in_code = False
    for raw in lines:
        line = raw.rstrip("\n")

        # Code fences
        if line.strip().startswith("```"):
            in_code = not in_code
            if in_code:
                rendered.append(("─" * max(1, width-2), "hr"))
            else:
                rendered.append(("─" * max(1, width-2), "hr"))
            continue

        if in_code:
            # Keep indentation; wrap but preserve code feel
            if not line:
                rendered.append(("", "code"))
                continue
            wrapped = textwrap.wrap(line, width=width-2, replace_whitespace=False,
                                    drop_whitespace=False, subsequent_indent="")
            if not wrapped:
                rendered.append(("", "code"))
            for w in wrapped or [""]:
                rendered.append((w, "code"))
            continue

        # Horizontal rule
        if hr_re.match(line):
            rendered.append(("─" * max(1, width-2), "hr"))
            continue

        # Headings
        m = heading_re.match(line)
        if m:
            level = len(m.group(1))
            text  = strip_inline(m.group(2)).strip()
            style = f"h{level}"
            # Slight visual pop: add underline for h1/h2
            if level <= 2:
                text = text.upper()
            wrapped = textwrap.wrap(text, width=width-2) or [""]
            for w in wrapped:
                rendered.append((w, style))
            if level <= 2:
                rendered.append(("─" * min(len(text), width-2), "hr"))
            continue

        # Lists
        m = ulist_re.match(line)
        if m:
            content = strip_inline(m.group(1))
            bullet = "• "
            wrapped = textwrap.wrap(content, width=width-4,
                                    subsequent_indent="  ")
            if not wrapped:
                rendered.append((f"{bullet}", "list"))
            else:
                rendered.append((bullet + wrapped[0], "list"))
                for w in wrapped[1:]:
                    rendered.append(("  " + w, "list"))
            continue

        m = olist_re.match(line)
        if m:
            # Keep original number if possible
            num = line.strip().split()[0]
            content = strip_inline(line[line.find(num)+len(num):].lstrip(". )"))
            prefix = f"{num} "
            wrapw = max(1, width - (len(prefix)+2))
            wrapped = textwrap.wrap(content, width=wrapw,
                                    subsequent_indent=" " * len(prefix))
            if not wrapped:
                rendered.append((prefix, "list"))
            else:
                rendered.append((prefix + wrapped[0], "list"))
                for w in wrapped[1:]:
                    rendered.append((w, "list"))
            continue

        # Blockquote
        if line.lstrip().startswith(">"):
            text = strip_inline(line.lstrip()[1:].lstrip())
            wrapped = textwrap.wrap(text, width=width-4, subsequent_indent="  ")
            bar = "│ "
            if not wrapped:
                rendered.append((bar, "quote"))
            else:
                rendered.append((bar + wrapped[0], "quote"))
                for w in wrapped[1:]:
                    rendered.append(("  " + w, "quote"))
            continue

        # Paragraph / blank
        text = strip_inline(line)
        if not text.strip():
            rendered.append(("", "normal"))
            continue
        wrapped = textwrap.wrap(text, width=width-2) or [""]
        for w in wrapped:
            rendered.append((w, "normal"))
    return rendered

# ---------- UI ----------
class Viewer:
    def __init__(self, stdscr, path):
        self.stdscr = stdscr
        self.path = path
        self.lines = []
        self.styles = []
        self.view = []        # list[(text, style)]
        self.offset = 0
        self.h = 0
        self.w = 0
        self.search_q = None
        self.last_found = -1

    def load(self):
        with open(self.path, "r", encoding="utf-8", errors="replace") as f:
            self.lines = f.readlines()

    def rerender(self):
        self.h, self.w = self.stdscr.getmaxyx()
        width = max(20, self.w - 2)
        self.view = render_markdown(self.lines, width)
        self.offset = min(self.offset, max(0, len(self.view) - self.h + 1))

    def clamp_offset(self):
        maxoff = max(0, len(self.view) - (self.h - 1))
        self.offset = min(max(self.offset, 0), maxoff)

    def draw(self):
        self.stdscr.erase()
        # Body
        body_h = self.h - 1
        for i in range(body_h):
            idx = self.offset + i
            if idx >= len(self.view):
                break
            text, style = self.view[idx]
            try:
                self.stdscr.addstr(i, 0, truncate(text, self.w-1), style_attr(style))
            except curses.error:
                pass

        # Status bar
        status = f" {os.path.basename(self.path)}  {self.offset+1}/{len(self.view)}  {HELP}"
        status = truncate(status, self.w-1)
        try:
            self.stdscr.addstr(self.h-1, 0, status, curses.A_REVERSE)
        except curses.error:
            pass
        self.stdscr.refresh()

    def search(self, query, backwards=False):
        if not query:
            return
        start = self.last_found if self.last_found != -1 else self.offset
        rng = range(start-1, -1, -1) if backwards else range(start+1, len(self.view))
        q = query.lower()
        for idx in rng:
            if q in self.view[idx][0].lower():
                self.last_found = idx
                # place found line near top
                self.offset = max(0, idx - 1)
                return
        # wrap-around
        rng = range(len(self.view)-1, -1, -1) if backwards else range(0, len(self.view))
        for idx in rng:
            if q in self.view[idx][0].lower():
                self.last_found = idx
                self.offset = max(0, idx - 1)
                return

def truncate(s, width):
    return s if len(s) <= width else s[:max(0, width-1)] + "…"

# Colors / attributes
def style_attr(style):
    # Fallback if no color
    if not curses.has_colors():
        base = curses.A_NORMAL
        if style.startswith("h"): base |= curses.A_BOLD
        if style in ("hr",): base |= curses.A_DIM
        if style in ("code", "quote"): base |= curses.A_STANDOUT
        return base

    mapping = {
        "normal": curses.color_pair(0),
        "hr":     curses.color_pair(8)  | curses.A_DIM,
        "list":   curses.color_pair(5),
        "quote":  curses.color_pair(6),
        "code":   curses.color_pair(7),

        "h1": curses.color_pair(1) | curses.A_BOLD,
        "h2": curses.color_pair(2) | curses.A_BOLD,
        "h3": curses.color_pair(3) | curses.A_BOLD,
        "h4": curses.color_pair(4) | curses.A_BOLD,
        "h5": curses.color_pair(4),
        "h6": curses.color_pair(4) | curses.A_DIM,
    }
    return mapping.get(style, curses.color_pair(0))

def init_colors():
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        # pair(idx, fg, bg)
        curses.init_pair(1, curses.COLOR_CYAN,   -1)
        curses.init_pair(2, curses.COLOR_YELLOW, -1)
        curses.init_pair(3, curses.COLOR_MAGENTA,-1)
        curses.init_pair(4, curses.COLOR_WHITE,  -1)
        curses.init_pair(5, curses.COLOR_GREEN,  -1)   # list
        curses.init_pair(6, curses.COLOR_BLUE,   -1)   # quote
        curses.init_pair(7, curses.COLOR_BLACK,  curses.COLOR_WHITE)  # code
        curses.init_pair(8, curses.COLOR_WHITE,  -1)   # hr

def prompt(stdscr, msg):
    h, w = stdscr.getmaxyx()
    stdscr.addstr(h-1, 0, " " * (w-1), curses.A_REVERSE)
    stdscr.addstr(h-1, 0, msg, curses.A_REVERSE)
    curses.echo()
    curses.curs_set(1)
    stdscr.refresh()
    try:
        s = stdscr.getstr(h-1, len(msg)).decode("utf-8")
    except Exception:
        s = ""
    curses.noecho()
    curses.curs_set(0)
    return s

def main(stdscr, path):
    curses.curs_set(0)
    stdscr.keypad(True)
    init_colors()

    v = Viewer(stdscr, path)
    v.load()
    v.rerender()
    v.draw()

    while True:
        ch = stdscr.getch()
        if ch in (ord('q'), 27):  # q or Esc
            break
        elif ch in (curses.KEY_RESIZE,):
            v.rerender()
        elif ch in (curses.KEY_DOWN, ord('j')):
            v.offset += 1
        elif ch in (curses.KEY_UP, ord('k')):
            v.offset -= 1
        elif ch in (curses.KEY_NPAGE,):  # PgDn
            v.offset += (v.h - 2)
        elif ch in (curses.KEY_PPAGE,):  # PgUp
            v.offset -= (v.h - 2)
        elif ch in (ord('g'),):
            v.offset = 0
        elif ch in (ord('G'),):
            v.offset = max(0, len(v.view) - v.h + 1)
        elif ch in (ord('r'),):
            # reload
            try:
                v.load()
                v.rerender()
            except Exception:
                pass
        elif ch == ord('/'):
            q = prompt(stdscr, "/")
            v.search_q = q
            v.search(q, backwards=False)
        elif ch in (ord('n'),):
            if v.search_q:
                v.search(v.search_q, backwards=False)
        elif ch in (ord('N'),):
            if v.search_q:
                v.search(v.search_q, backwards=True)

        v.clamp_offset()
        v.draw()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: mdview.py <file.md>")
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.isfile(path):
        print(f"Not found: {path}")
        sys.exit(1)
    curses.wrapper(main, path)

