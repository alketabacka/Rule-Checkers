import tkinter
import tkinter as tk
import random
from tkinter import messagebox

class CheckerGame:
    def __init__(self, master, player_color, ai_difficulty):
        self.master = master
        self.pieces = {}  # Tracks pieces by their (row, col) position
        self.selected_piece = None  # Stores the currently selected piece as (row, col)
        self.board = [[None for _ in range(8)] for _ in range(8)]  # 8x8 board
        self.create_board()
        self.red_eliminated = 0  # Initialize red_eliminated counter
        self.green_eliminated = 0  # Initialize green_eliminated counter
        self.create_controls()
        self.player_color = player_color
        self.ai_color = "green" if player_color == "red" else "red"
        self.ai_difficulty = ai_difficulty
        self.current_turn = player_color
        self.difficulty_depths = {'beginner': 2, 'intermediate': 4, 'master': 6}
        self.minimax_depth = self.difficulty_depths[ai_difficulty]

    def create_controls(self):
        hint_button = tk.Button(self.master, text="Show Hints", command=self.show_hints)
        hint_button.grid(row=9, column=0, columnspan=8, sticky="we")  # Adjust position as needed

        # Create and place the label for the number of eliminated red pieces
        self.red_eliminated_label = tk.Label(self.master, text=f"Red Eliminated: {self.red_eliminated}")
        self.red_eliminated_label.grid(row=10, column=0, columnspan=4, sticky="we")

        # Create and place the label for the number of eliminated green pieces
        self.green_eliminated_label = tk.Label(self.master, text=f"Green Eliminated: {self.green_eliminated}")
        self.green_eliminated_label.grid(row=10, column=4, columnspan=4, sticky="we")

    def update_eliminated_count(self, color):
        if color == "red":
            self.red_eliminated += 1
            self.red_eliminated_label.config(text=f"Red Eliminated: {self.red_eliminated}")
        elif color == "green":
            self.green_eliminated += 1
            self.green_eliminated_label.config(text=f"Green Eliminated: {self.green_eliminated}")

    def create_board(self):
        for i in range(8):
            for j in range(8):
                color = "white" if (i + j) % 2 == 0 else "black"
                self.board[i][j] = tk.Canvas(self.master, width=60, height=60, bg=color)
                self.board[i][j].grid(row=i, column=j)
                self.board[i][j].bind("<Button-1>", lambda event, row=i, col=j: self.on_square_clicked(row, col))
                if color == "black" and (i < 3 or i > 4):
                    piece_color = "red" if i < 3 else "green"
                    self.draw_piece(i, j, {"color": piece_color, "is_king": False})

    def draw_piece(self, row, col, piece_info):
        self.board[row][col].delete("all")
        color = "yellow" if piece_info["is_king"] else piece_info["color"]
        self.board[row][col].create_oval(10, 10, 50, 50, fill=color, tags=f"piece{row}{col}")
        self.pieces[(row, col)] = piece_info

    def on_square_clicked(self, row, col):
        if (row, col) in self.pieces:
            if self.pieces[(row, col)]["color"] == self.current_turn:
                self.selected_piece = (row, col)
                return
        if self.selected_piece:
            from_row, from_col = self.selected_piece
            if (row, col) != self.selected_piece:
                valid_move, message = self.is_valid_move(self.selected_piece, (row, col))
                if valid_move:
                    self.move_piece(from_row, from_col, row, col)
                    self.selected_piece = None
                    self.clear_highlights()
                else:
                    messagebox.showerror("Invalid Move", message)
                    self.selected_piece = None
                    self.clear_highlights()

    def is_valid_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        dx = to_row - from_row  # Change in row (direction and magnitude)
        dy = to_col - from_col  # Change in column (must be exactly 1 or 2 for valid moves)

        if (from_pos not in self.pieces) or (to_pos in self.pieces):
            return False, "Invalid move: No piece at source or destination not empty."

        piece_info = self.pieces[from_pos]

        # Check movement direction for non-king pieces:
        if not piece_info["is_king"]:
            if piece_info["color"] == "red" and dx < 0:  # Red pieces must move upward (decreasing row index)
                return False, "Red non-king pieces can only move forwards."
            if piece_info["color"] == "green" and dx > 0:  # Green pieces must move downward (increasing row index)
                return False, "Green non-king pieces can only move forwards."

        # Check if the move is a simple diagonal move
        if abs(dx) == 1 and abs(dy) == 1:
            return True, "Valid move"

        # Check if the move is a valid jump
        if abs(dx) == 2 and abs(dy) == 2:
            mid_row, mid_col = (from_row + to_row) // 2, (from_col + to_col) // 2
            if (mid_row, mid_col) in self.pieces and self.pieces[(mid_row, mid_col)]["color"] != piece_info["color"]:
                return True, "Valid jump"
            else:
                return False, "Invalid jump: No opponent piece to capture."

        return False, "Invalid move: Moves must be diagonal and within correct range."

    def move_piece(self, from_row, from_col, target_row, target_col):
        self.board[from_row][from_col].delete("all")
        piece_info = self.pieces.pop((from_row, from_col))

        # Check if the move is a jump and handle capture
        if abs(target_row - from_row) == 2:
            mid_row = (from_row + target_row) // 2
            mid_col = (from_col + target_col) // 2
            captured_piece_info = self.pieces.pop((mid_row, mid_col), None)
            self.board[mid_row][mid_col].delete("all")
            if captured_piece_info and captured_piece_info["is_king"]:
                # Crown the capturing piece if it captures a king and is not a king itself
                piece_info["is_king"] = True
                # Update eliminated count
                self.update_eliminated_count(captured_piece_info["color"])
            elif captured_piece_info:
                # Update eliminated count
                self.update_eliminated_count(captured_piece_info["color"])

        # Place the piece in the new location
        self.pieces[(target_row, target_col)] = piece_info
        self.draw_piece(target_row, target_col, piece_info)

        # Turn piece into a king if it reaches the opposite end (if not already handled by king capture)
        if not piece_info["is_king"] and ((piece_info["color"] == "red" and target_row == 7) or
                                          (piece_info["color"] == "green" and target_row == 0)):
            piece_info["is_king"] = True

        self.is_game_over()  # Check if the game is over
        self.switch_turns()  # Switch turns

    def must_continue_capturing(self):
        # Check if the selected piece has further capturing moves available
        if not self.selected_piece:
            return False
        _, possible_jumps = self.get_legal_moves_for_piece(self.selected_piece)
        return bool(possible_jumps)

    def ai_move(self):
        # Get all legal moves for the AI
        _, jump_moves = self.get_legal_moves(self.ai_color)
        if jump_moves:
            move = self.random_move(jump_moves)
            self.execute_move(move)
            # Continue capturing if possible
            self.continue_capturing(move)
        else:
            regular_moves, _ = self.get_legal_moves(self.ai_color)
            if regular_moves:
                # Use minimax to choose the best move based on the current difficulty level (depth)
                move = self.minimax_move(regular_moves, self.minimax_depth)
                self.execute_move(move)
        self.switch_turns()

    def execute_move(self, move):
        """Execute a move on the board."""
        from_pos, to_pos = move
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        # Check if the piece exists at the from position
        if from_pos not in self.pieces:
            return

        piece_info = self.pieces.pop(from_pos, None)

        # Handle jumps
        if abs(to_row - from_row) == 2:
            mid_row, mid_col = (from_row + to_row) // 2, (from_col + to_col) // 2
            if (mid_row, mid_col) in self.pieces:
                captured_piece_info = self.pieces.pop((mid_row, mid_col), None)
                self.board[mid_row][mid_col].delete("all")
                # Update eliminated count if a piece was captured
                if captured_piece_info and captured_piece_info["is_king"]:
                    # Crown the capturing piece if it captures a king and is not a king itself
                    piece_info["is_king"] = True
                    self.update_eliminated_count(captured_piece_info["color"])
                elif captured_piece_info:
                    # Update eliminated count
                    self.update_eliminated_count(captured_piece_info["color"])

        # Move piece to new position and check if the to position is valid
        if (to_row, to_col) not in self.pieces:
            self.pieces[to_pos] = piece_info
            self.board[from_row][from_col].delete("all")
            self.draw_piece(to_row, to_col, piece_info)
        else:
            self.pieces[from_pos] = piece_info  # Restore the piece back to its original position if move failed

        # Check for king promotion
        if ((piece_info["color"] == "red" and to_row == 7) or (piece_info["color"] == "green" and to_row == 0)) and not \
                piece_info["is_king"]:
            piece_info["is_king"] = True
            self.draw_piece(to_row, to_col, piece_info)
        # If the move was a multi-step move, pause before proceeding to the next step
        if abs(to_row - from_row) == 2:
            self.master.after(1000, lambda: self.continue_capturing(move))

    def switch_turns(self):
        self.current_turn = self.ai_color if self.current_turn == self.player_color else self.player_color
        if self.current_turn == self.ai_color:
            self.master.after(500, self.ai_move)
        else:
            # Check if the game is over
            winner = self.determine_winner()
            if winner:
                messagebox.showinfo("Game Over", f"{winner} wins the game!")
                self.master.quit()  # Quit the game after displaying the winner message
            
                # No winner yet, continue the game
                #self.show_hints()  # Show hints for the current player's turn

    def random_move(self, moves):
        return random.choice(moves)

    def minimax_move(self, moves, depth):
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        for move in moves:
            self.simulate_move(move)
            score = self.minimax(depth - 1, False, alpha, beta)
            self.undo_move()
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, score)  # Update alpha after each minimax call
        return best_move

    def minimax(self, depth, maximizingPlayer, alpha, beta):
        if depth == 0 or self.is_game_over():
            return self.evaluate_board()

        if maximizingPlayer:
            max_eval = float('-inf')
            for move in self.get_all_legal_moves(self.ai_color):
                self.simulate_move(move)
                eval = self.minimax(depth - 1, False, alpha, beta)
                self.undo_move()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)  # Update alpha
                if beta <= alpha:
                    break  # Beta cut-off
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.get_all_legal_moves(self.player_color):
                self.simulate_move(move)
                eval = self.minimax(depth - 1, True, alpha, beta)
                self.undo_move()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)  # Update beta
                if beta <= alpha:
                    break  # Alpha cut-off
            return min_eval

    def get_legal_moves(self, color):
        legal_moves = []
        jump_moves = []
        for (row, col), piece_info in self.pieces.items():
            if piece_info["color"] == color:
                moves, jumps = self.get_legal_moves_for_piece((row, col))
                legal_moves.extend(moves)
                jump_moves.extend(jumps)
        if jump_moves:
            return [], jump_moves  # Return only jump moves if available
        return legal_moves, []

    def get_all_legal_moves(self, color):
        moves = []
        for pos in self.pieces:
            if self.pieces[pos] == color:
                piece_moves = self.get_legal_moves_for_piece(pos)
                if piece_moves:  # This check is technically redundant now but adds clarity
                    moves.extend(piece_moves)
        return moves

    def simulate_move(self, move):
        """Simulate a move for minimax evaluation, storing state for undo."""
        from_pos, to_pos = move
        moved_piece = self.pieces.pop(from_pos)  # Move the piece
        captured_piece = self.pieces.pop(to_pos, None)  # Capture if applicable
        self.pieces[to_pos] = moved_piece  # Place at new location
        # Store state needed to undo this move
        self.last_simulated_move = (from_pos, to_pos, moved_piece, captured_piece)

    def undo_move(self):
        """Undo a move after simulation."""
        if not hasattr(self, 'last_simulated_move'):
            return  # No move to undo
        from_pos, to_pos, moved_piece, captured_piece = self.last_simulated_move
        # Move back the piece
        self.pieces[from_pos] = moved_piece
        # Restore captured piece if there was one
        if captured_piece is not None:
            self.pieces[to_pos] = captured_piece
        else:
            self.pieces.pop(to_pos, None)  # Ensure to_pos is cleared if no capture happened

        del self.last_simulated_move  # Clear the last simulated move

    def check_move(self, row, col, dx, dy):
        """Checks if a move is legal and returns the target position if it is."""
        target = (row + dx, col + dy)
        jump_target = (row + 2 * dx, col + 2 * dy)
        piece_info = self.pieces[(row, col)]

        # Allow kings to move backwards and forwards
        if not piece_info['is_king']:
            if (piece_info['color'] == "red" and dx < 0) or (piece_info['color'] == "green" and dx > 0):
                return None  # Prevent backward jumps and moves for non-kings

        if 0 <= target[0] < 8 and 0 <= target[1] < 8 and target not in self.pieces:
            return target  # Regular move
        elif 0 <= jump_target[0] < 8 and 0 <= jump_target[1] < 8 and jump_target not in self.pieces:
            mid_target = (row + dx, col + dy)
            if mid_target in self.pieces and self.pieces[mid_target]['color'] != piece_info['color']:
                return jump_target  # Jump move
        return None

    def evaluate_board(self):
        # Basic evaluation based on piece count
        ai_pieces = sum(1 for p in self.pieces.values() if p['color'] == self.ai_color)
        human_pieces = sum(1 for p in self.pieces.values() if p['color'] == self.player_color)
        return ai_pieces - human_pieces

    def is_game_over(self):
        if not self.pieces:  # if there are no pieces at all, it's a draw
            return True

        # Check for any legal moves for each player
        red_moves, red_jumps = self.get_legal_moves("red")
        green_moves, green_jumps = self.get_legal_moves("green")

        # Game is over if neither player has any moves
        red_can_move = red_moves or red_jumps
        green_can_move = green_moves or green_jumps

        return not red_can_move and not green_can_move

    def get_legal_moves_for_piece(self, pos):
        row, col = pos
        piece_info = self.pieces[pos]
        regular_moves = []
        jump_moves = []
        directions = [-1, 1] if piece_info['is_king'] else ([1] if piece_info['color'] == 'red' else [-1])

        for dx in directions:
            for dy in [-1, 1]:  # Check both diagonal directions
                new_row, new_col = row + dx, col + dy
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    if (new_row, new_col) not in self.pieces:
                        regular_moves.append(((row, col), (new_row, new_col)))
                    jump_row, jump_col = new_row + dx, new_col + dy
                    if 0 <= jump_row < 8 and 0 <= jump_col < 8 and (jump_row, jump_col) not in self.pieces:
                        mid_row, mid_col = new_row, new_col
                        if (mid_row, mid_col) in self.pieces and self.pieces[(mid_row, mid_col)]['color'] != piece_info[
                            'color']:
                            jump_moves.append(((row, col), (jump_row, jump_col)))

        return regular_moves, jump_moves

    def determine_winner(self):
        red_has_moves = any(self.get_legal_moves_for_piece(pos)
                            for pos, piece_info in self.pieces.items() if piece_info["color"] == "red")
        green_has_moves = any(self.get_legal_moves_for_piece(pos)
                              for pos, piece_info in self.pieces.items() if piece_info["color"] == "green")

        if not red_has_moves:
            return "Green"
        elif not green_has_moves:
            return "Red"
        return None  # No winner yet

    def highlight_moves(self, moves):
        # Resetting the color of all squares first
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 1:  # Only black squares
                    self.board[row][col].config(bg="black")

        # Highlighting the squares based on the provided moves list
        for from_pos, to_pos in moves:
            _, to_col = to_pos
            self.board[_][to_col].config(bg="lightgreen")  # Use light green for visibility

    def show_hints(self):
        # Clear any previous highlights
        self.clear_highlights()
        # Fetch the legal moves for the current player's turn
        _, possible_moves = self.get_legal_moves(self.current_turn)
        # Highlight these moves
        self.highlight_moves(possible_moves)

    def clear_highlights(self):
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 1:  # Only black squares need color reset
                    self.board[row][col].config(bg="black")

    def continue_capturing(self, move):
        from_pos, to_pos = move
        to_row, to_col = to_pos
        _, further_jumps = self.get_legal_moves_for_piece(to_pos)
        while further_jumps:
            move = self.random_move(further_jumps)
            self.execute_move(move)
            _, further_jumps = self.get_legal_moves_for_piece(to_pos) if to_pos in self.pieces else ([], [])

if __name__ == "__main__":
    root = tk.Tk()
    # Example test instantiation with dummy values for player_color and ai_difficulty
    game = CheckerGame(root, player_color="red", ai_difficulty="beginner")
    root.mainloop()
