import tkinter as tk
import chess

# Unicode chess pieces
PIECES = {
    "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚", "p": "♟",
    "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔", "P": "♙"
}

SQUARE_SIZE = 60
BOARD_SIZE = 8

LIGHT_COLOR = "#f0d9b5"
DARK_COLOR = "#b58863"


class ChessGUI:
    def __init__(self, root, fen):
        self.root = root
        self.board = chess.Board(fen)

        self.canvas = tk.Canvas(
            root,
            width=SQUARE_SIZE * BOARD_SIZE,
            height=SQUARE_SIZE * BOARD_SIZE
        )
        self.canvas.pack()

        self.draw_board()
        self.draw_pieces()

    def draw_board(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                color = LIGHT_COLOR if (r + c) % 2 == 0 else DARK_COLOR

                x1 = c * SQUARE_SIZE
                y1 = r * SQUARE_SIZE
                x2 = x1 + SQUARE_SIZE
                y2 = y1 + SQUARE_SIZE

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def draw_pieces(self):
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                file = chess.square_file(square)
                rank = 7 - chess.square_rank(square)

                x = file * SQUARE_SIZE + SQUARE_SIZE // 2
                y = rank * SQUARE_SIZE + SQUARE_SIZE // 2

                symbol = PIECES[piece.symbol()]

                self.canvas.create_text(
                    x, y,
                    text=symbol,
                    font=("Arial", 32)
                )


if __name__ == "__main__":
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    root = tk.Tk()
    root.title("FEN Chess Board")

    app = ChessGUI(root, fen)

    root.mainloop()