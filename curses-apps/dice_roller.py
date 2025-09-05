#!/usr/bin/env python3
import curses
import copy
import random


def main(stdscr):
    curses.curs_set(0)
    dice = -1
    stdscr.addstr(0, 0, "Type 'n' to roll the dice or 'q' to quit")
    while True:
        ch = stdscr.getch()
        if ch == -1:
            continue
        if ch in (ord('q'), 27):
            break
        elif ch in (ord('n'),):
            dice = random.choice([1,2,3,4,5,6])
        #elif ch in (10, 13, ord(' ')):  # Enter or Space
        # stdscr.clear()
        stdscr.addstr(1, 0, f"Dice number is: {str(dice)}")

if __name__ == "__main__":
    import curses
    curses.wrapper(main)

