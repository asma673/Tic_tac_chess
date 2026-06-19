"""
main.py -- Tic Tac Toe and Chess GUI in Python (tkinter)
Requires: python-chess (pip install python-chess)
Run: python main.py
"""

import tkinter as tk
from tkinter import messagebox
import random
import sys

# Try to import python-chess for the Chess game
try:
    import chess
except Exception as e:
    chess = None

# --------------------------
# Tic Tac Toe implementation
# --------------------------
class TicTacToe:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Tic Tac Toe")
        self.current_player = "X"
        self.board = [None] * 9
        self.buttons = []
        self.scores = {"X": 0, "O": 0, "Draws": 0}
        self.vs_ai = tk.BooleanVar(value=False)
        self.create_ui()
        self.update_status()

    def create_ui(self):
        top = tk.Frame(self.window)
        top.pack(padx=10, pady=5)
        frame = tk.Frame(self.window)
        frame.pack(padx=10, pady=5)
        for i in range(9):
            b = tk.Button(frame, text="", width=6, height=3, font=("Helvetica", 20),
                          command=lambda i=i: self.on_click(i))
            b.grid(row=i//3, column=i%3)
            self.buttons.append(b)

        ctrl = tk.Frame(self.window)
        ctrl.pack(padx=10, pady=5)
        tk.Checkbutton(ctrl, text="Play vs simple AI (random legal moves)", variable=self.vs_ai).pack(anchor="w")
        tk.Button(ctrl, text="Restart Game", command=self.restart).pack(side="left", padx=5)
        tk.Button(ctrl, text="Reset Scores", command=self.reset_scores).pack(side="left", padx=5)

        self.status_label = tk.Label(self.window, text="", font=("Helvetica", 12))
        self.status_label.pack(pady=5)
        self.score_label = tk.Label(self.window, text=self.score_text(), font=("Helvetica", 10))
        self.score_label.pack(pady=5)

    def score_text(self):
        return f"X: {self.scores['X']}   O: {self.scores['O']}   Draws: {self.scores['Draws']}"

    def update_status(self, extra=""):
        self.status_label.config(text=f"Turn: {self.current_player} {extra}")
        self.score_label.config(text=self.score_text())

    def on_click(self, idx):
        if self.board[idx] is not None:
            return
        if self.vs_ai.get() and self.current_player == "O":
            # If AI is O, ignore clicks on its turn
            return
        self.make_move(idx, self.current_player)
        winner = self.check_winner()
        if winner or all(self.board):
            self.end_round(winner)
            return
        self.switch_player()
        if self.vs_ai.get() and self.current_player == "O":
            self.window.after(200, self.ai_move)

    def ai_move(self):
        # Simple random legal move for AI
        empty = [i for i, v in enumerate(self.board) if v is None]
        if not empty:
            return
        idx = random.choice(empty)
        self.make_move(idx, "O")
        winner = self.check_winner()
        if winner or all(self.board):
            self.end_round(winner)
            return
        self.switch_player()

    def make_move(self, idx, player):
        self.board[idx] = player
        self.buttons[idx].config(text=player, state="disabled")
        self.update_status()

    def switch_player(self):
        self.current_player = "O" if self.current_player == "X" else "X"
        self.update_status()

    def check_winner(self):
        lines = [
            (0,1,2),(3,4,5),(6,7,8),  # rows
            (0,3,6),(1,4,7),(2,5,8),  # cols
            (0,4,8),(2,4,6)           # diags
        ]
        for a,b,c in lines:
            if self.board[a] and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a]
        return None

    def end_round(self, winner):
        if winner:
            messagebox.showinfo("Game Over", f"{winner} wins!")
            self.scores[winner] += 1
        else:
            messagebox.showinfo("Game Over", "It's a draw!")
            self.scores["Draws"] += 1
        # disable all buttons
        for b in self.buttons:
            b.config(state="disabled")
        self.update_status()
    
    def restart(self):
        self.board = [None] * 9
        for b in self.buttons:
            b.config(text="", state="normal")
        self.current_player = "X"
        self.update_status()
        # If AI plays first as O, no immediate move; X starts.

    def reset_scores(self):
        self.scores = {"X": 0, "O": 0, "Draws": 0}
        self.score_label.config(text=self.score_text())


# --------------------------
# Chess GUI using python-chess
# --------------------------
class ChessGUI:
    SQUARE_SIZE = 64
    LIGHT_COLOR = "#F0D9B5"
    DARK_COLOR = "#B58863"
    HIGHLIGHT_COLOR = "#AAA23F"

    unicode_pieces = {
        'P': '\u2659', 'N': '\u2658', 'B': '\u2657', 'R': '\u2656', 'Q': '\u2655', 'K': '\u2654',
        'p': '\u265F', 'n': '\u265E', 'b': '\u265D', 'r': '\u265C', 'q': '\u265B', 'k': '\u265A',
    }

    def __init__(self, parent):
        if chess is None:
            messagebox.showerror("Missing dependency", "python-chess is required for the Chess game.\nInstall with: pip install python-chess")
            return
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Chess")
        self.board = chess.Board()
        self.selected = None  # square name like 'e2'
        self.squares = {}  # (row,col) -> canvas item ids
        self.show_ai = tk.BooleanVar(value=False)
        self.create_ui()
        self.draw_board()

    def create_ui(self):
        top = tk.Frame(self.window)
        top.pack(side="left", padx=10, pady=10)
        self.canvas = tk.Canvas(top, width=8*self.SQUARE_SIZE, height=8*self.SQUARE_SIZE)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        right = tk.Frame(self.window)
        right.pack(side="right", fill="y", padx=10, pady=10)
        tk.Button(right, text="Restart", command=self.restart).pack(pady=5)
        tk.Checkbutton(right, text="Enable simple AI (random legal moves)", variable=self.show_ai).pack(anchor="w")
        self.status_label = tk.Label(right, text="", font=("Helvetica", 12))
        self.status_label.pack(pady=5)
        self.update_status()

    def draw_board(self):
        self.canvas.delete("all")
        for row in range(8):
            for col in range(8):
                x1 = col * self.SQUARE_SIZE
                y1 = row * self.SQUARE_SIZE
                x2 = x1 + self.SQUARE_SIZE
                y2 = y1 + self.SQUARE_SIZE
                is_light = (row + col) % 2 == 0
                color = self.LIGHT_COLOR if is_light else self.DARK_COLOR
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags="square")
                square_name = f"{chr(ord('a')+col)}{8-row}"
                piece = self.board.piece_at(chess.parse_square(square_name))
                text_id = None
                if piece:
                    symbol = piece.symbol()
                    uni = self.unicode_pieces.get(symbol, symbol)
                    text_id = self.canvas.create_text(x1 + self.SQUARE_SIZE//2, y1 + self.SQUARE_SIZE//2,
                                                      text=uni, font=("Arial", 32))
                self.squares[(row, col)] = (rect, text_id)
        self.update_status()

    def on_click(self, event):
        col = event.x // self.SQUARE_SIZE
        row = event.y // self.SQUARE_SIZE
        if not (0 <= col < 8 and 0 <= row < 8):
            return
        name = f"{chr(ord('a')+col)}{8-row}"
        if self.selected is None:
            # select a square if it has a piece of the side to move
            piece = self.board.piece_at(chess.parse_square(name))
            if piece and piece.color == self.board.turn:
                self.selected = name
                self.highlight_legal_moves(name)
        else:
            # attempt move
            from_sq = self.selected
            to_sq = name
            move_uci = from_sq + to_sq
            # handle promotions (default to queen)
            move = None
            try:
                move = chess.Move.from_uci(move_uci)
            except:
                # maybe promotion needed
                move = None
            if move and move in self.board.legal_moves:
                # normal move
                self.board.push(move)
            else:
                # handle promotion if pawn reaches last rank
                possible = None
                for m in self.board.legal_moves:
                    if m.uci().startswith(move_uci) and m.promotion:
                        possible = m
                        break
                if possible:
                    self.board.push(possible)
                else:
                    # invalid move, clear selection or reselect
                    piece = self.board.piece_at(chess.parse_square(to_sq))
                    if piece and piece.color == self.board.turn:
                        self.selected = to_sq
                        self.highlight_legal_moves(to_sq)
                        return
                    else:
                        self.selected = None
                        self.draw_board()
                        return
            self.selected = None
            self.draw_board()
            # after move, check for game end
            self.check_game_end()
            if self.show_ai.get() and not self.board.is_game_over() and self.board.turn == chess.BLACK:
                self.window.after(200, self.ai_move)

    def highlight_legal_moves(self, from_sq_name):
        # redraw board colors and highlight legal moves from selected square
        self.draw_board()
        from_sq = chess.parse_square(from_sq_name)
        for move in self.board.legal_moves:
            if move.from_square == from_sq:
                to_name = chess.square_name(move.to_square)
                col = ord(to_name[0]) - ord('a')
                row = 8 - int(to_name[1])
                rect, text_id = self.squares[(row, col)]
                self.canvas.itemconfig(rect, fill=self.HIGHLIGHT_COLOR)

    def ai_move(self):
        # simple random legal move for AI (Black)
        legal = list(self.board.legal_moves)
        if not legal:
            return
        mv = random.choice(legal)
        self.board.push(mv)
        self.draw_board()
        self.check_game_end()

    def check_game_end(self):
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            messagebox.showinfo("Checkmate", f"{winner} wins by checkmate!")
        elif self.board.is_stalemate():
            messagebox.showinfo("Draw", "Stalemate!")
        elif self.board.is_insufficient_material():
            messagebox.showinfo("Draw", "Draw by insufficient material.")
        elif self.board.can_claim_fifty_moves():
            messagebox.showinfo("Draw", "Draw by fifty-move rule (claimable).")
        # update status label
        self.update_status()

    def update_status(self):
        if chess is None:
            self.status_label.config(text="python-chess missing")
            return
        turn = "White" if self.board.turn == chess.WHITE else "Black"
        s = f"Turn: {turn}"
        if self.board.is_check():
            s += "  (Check)"
        if self.board.is_game_over():
            if self.board.is_checkmate():
                s += "  (Checkmate)"
            else:
                s += "  (Game over)"
        self.status_label.config(text=s)

    def restart(self):
        self.board = chess.Board()
        self.selected = None
        self.draw_board()

# --------------------------
# Main launcher
# --------------------------
class App:
    def __init__(self, root):
        self.root = root
        root.title("Games: Tic Tac Toe & Chess")
        tk.Label(root, text="Choose a game", font=("Helvetica", 14)).pack(pady=10)
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Tic Tac Toe", width=20, command=self.open_ttt).pack(pady=5)
        tk.Button(btn_frame, text="Chess", width=20, command=self.open_chess).pack(pady=5)
        tk.Button(root, text="About / Ethics", command=self.show_ethics).pack(pady=5)
        tk.Button(root, text="Quit", command=root.quit).pack(pady=6)

    def open_ttt(self):
        TicTacToe(self.root)

    def open_chess(self):
        ChessGUI(self.root)

    def show_ethics(self):
        text = (
            "Ethical & fair-play notes:\n\n"
            "- This application enforces standard game rules. For Chess it uses the python-chess library to validate moves.\n"
            "- No cheating or engine assistance is provided by default. If you enable the 'simple AI' option, it is a basic random move AI.\n"
            "- Use this program for friendly local play or learning; respect opponents and don't use this app to gain unfair advantage in rated events.\n"
            "- If sharing or modifying the code, follow software licensing and intellectual property rules for any third-party libraries used."
        )
        messagebox.showinfo("Ethics & Fair Play", text)

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()