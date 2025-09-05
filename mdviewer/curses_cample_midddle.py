import curses

def main(stdscr):
    stdscr.clear()
    curses.curs_set(0)
    max_y, max_x = stdscr.getmaxyx()
    msg1 = "Hello from curses!"
    msg2 = "\nPress any key to exit."
    msg1_x = int((max_x/2)) - int(len(msg1)/2)
    stdscr.addstr(int(max_y/2), int(max_x/2), msg1)
    stdscr.addstr(msg2)
    stdscr.refresh()
    stdscr.getch()

curses.wrapper(main)
