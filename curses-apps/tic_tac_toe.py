#!/usr/bin/env python3
"""
Tic-Tac-Toe curses game.
Keys:
  arrows / h j k l - move cursor
  Enter / Space - place mark
  n - new game
  m - toggle vs CPU (CPU uses 'O' by default)
  u - undo
  q - quit
"""
import curses
import copy
import random

EMPTY = " "
PLAYER_X = "X"
PLAYER_O = "O"

def check_winner(board):
    # board is 3x3 list of lists
    lines = []
    lines += [board[r] for r in range(3)]  # rows
    lines += [[board[r][c] for r in range(3)] for c in range(3)]  # cols
    lines += [[board[i][i] for i in range(3)], [board[i][2-i] for i in range(3)]]  # diags
    for ln in lines:
        if ln[0] != EMPTY and ln[0] == ln[1] == ln[2]:
            return ln[0]
    # draw?
    if all(board[r][c] != EMPTY for r in range(3) for c in range(3)):
        return "D"  # draw
    return None

def available_moves(board):
    return [(r,c) for r in range(3) for c in range(3) if board[r][c] == EMPTY]

# simple minimax for CPU (O)
def minimax(board, player):
    winner = check_winner(board)
    if winner == PLAYER_O:
        return 1, None
    if winner == PLAYER_X:
        return -1, None
    if winner == "D":
        return 0, None

    moves = available_moves(board)
    best = None
    if player == PLAYER_O:
        best_val = -999
        for mv in moves:
            r,c = mv
            board[r][c] = PLAYER_O
            val, _ = minimax(board, PLAYER_X)
            board[r][c] = EMPTY
            if val > best_val:
                best_val = val
                best = mv
        return best_val, best
    else:
        best_val = 999
        for mv in moves:
            r,c = mv
            board[r][c] = PLAYER_X
            val, _ = minimax(board, PLAYER_O)
            board[r][c] = EMPTY
            if val < best_val:
                best_val = val
                best = mv
        return best_val, best

class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [[EMPTY]*3 for _ in range(3)]
        self.turn = PLAYER_X
        self.cursor = (1,1)
        self.history = []
        self.vs_cpu = False
        self.msg = "X to play"

    def move_cursor(self, dr, dc):
        r,c = self.cursor
        r = min(2, max(0, r+dr))
        c = min(2, max(0, c+dc))
        self.cursor = (r,c)

    def place(self):
        r,c = self.cursor
        if self.board[r][c] != EMPTY:
            self.msg = "Cell occupied!"
            return
        self.history.append((r,c,self.turn))
        self.board[r][c] = self.turn
        winner = check_winner(self.board)
        if winner:
            if winner == "D":
                self.msg = "Draw! press n to restart."
            else:
                self.msg = f"{winner} wins! press n to restart."
            return
        # swap turn
        self.turn = PLAYER_O if self.turn == PLAYER_X else PLAYER_X
        self.msg = f"{self.turn} to play"

    def undo(self):
        if not self.history:
            self.msg = "Nothing to undo"
            return
        r,c,player = self.history.pop()
        self.board[r][c] = EMPTY
        self.turn = player
        self.msg = f"Undo, {self.turn} to play"

    def cpu_move(self):
        # CPU plays O
        if self.vs_cpu and self.turn == PLAYER_O:
            _, mv = minimax(self.board, PLAYER_O)
            if mv is None:
                mv = random.choice(available_moves(self.board)) if available_moves(self.board) else None
            if mv:
                r,c = mv
                self.cursor = (r,c)
                self.place()

def draw_board(stdscr, game):
    h,w = stdscr.getmaxyx()
    stdscr.clear()
    start_y = max(1, (h - 9)//2)
    start_x = max(2, (w - 25)//2)
    # Title
    stdscr.addstr(0, 0, "Tic-Tac-Toe (curses) - n: new  m: toggle CPU  u:undo  q:quit")
    # draw a 3x3 grid
    for r in range(3):
        for c in range(3):
            cell_y = start_y + r*3
            cell_x = start_x + c*8
            ch = game.board[r][c]
            # highlight cursor
            if (r,c) == game.cursor:
                attr = curses.A_REVERSE | curses.A_BOLD
            else:
                attr = curses.A_BOLD
            # draw box
            try:
                stdscr.addstr(cell_y, cell_x, "+-----+")
                stdscr.addstr(cell_y+1, cell_x, f"|  {ch}  |", attr)
                stdscr.addstr(cell_y+2, cell_x, "+-----+")
            except curses.error:
                pass
    # message
    stdscr.addstr(start_y + 10, start_x, f"{game.msg}")
    stdscr.refresh()

def main(stdscr):
    curses.curs_set(0)
    g = Game()
    draw_board(stdscr, g)
    while True:
        # if vs cpu and it's cpu turn, let CPU play
        if g.vs_cpu and g.turn == PLAYER_O:
            g.cpu_move()
            draw_board(stdscr, g)
            # check winner or continue
            if check_winner(g.board):
                # wait for key
                key = stdscr.getch()
                continue

        ch = stdscr.getch()
        if ch == -1:
            continue
        if ch in (ord('q'), 27):
            break
        elif ch in (ord('n'),):
            g.reset()
        elif ch in (ord('m'),):
            g.vs_cpu = not g.vs_cpu
            g.msg = "CPU ON" if g.vs_cpu else "CPU OFF"
        elif ch in (ord('u'),):
            g.undo()
        elif ch in (curses.KEY_UP, ord('k')):
            g.move_cursor(-1,0)
        elif ch in (curses.KEY_DOWN, ord('j')):
            g.move_cursor(1,0)
        elif ch in (curses.KEY_LEFT, ord('h')):
            g.move_cursor(0,-1)
        elif ch in (curses.KEY_RIGHT, ord('l')):
            g.move_cursor(0,1)
        elif ch in (10, 13, ord(' ')):  # Enter or Space
            g.place()
        draw_board(stdscr, g)

if __name__ == "__main__":
    import curses
    curses.wrapper(main)

