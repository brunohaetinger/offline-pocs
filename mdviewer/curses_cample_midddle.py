import curses

def main(stdscr):
    stdscr.clear()
    curses.curs_set(0)
    max_y, max_x = stdscr.getmaxyx()
    msg1 = "Hello from curses!"
    msg2 = "Press any key to exit."
    msg1_x = int((max_x/2)) - int(len(msg1)/2)
    msg2_x = int((max_x/2)) - int(len(msg2)/2)
    stdscr.addstr(int(max_y/2), msg1_x, msg1)
    stdscr.addstr(int(max_y/2)+1, msg2_x,msg2)
    stdscr.refresh()
    stdscr.getch()

curses.wrapper(main)
