import curses

def main(stdscr):
    stdscr.clear()
    curses.curs_set(0)
    stdscr.addstr(0, 0, "Hello from curses!")
    stdscr.addstr("\nPress any key to exit.")
    stdscr.refresh()
    stdscr.getch()

curses.wrapper(main)
