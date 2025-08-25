import curses

def main(stdscr):
    stdscr.clear()
    stdscr.addstr(0, 0, "Hello from curses! Press any key to exit.")
    stdscr.refresh()
    stdscr.getch()

curses.wrapper(main)
