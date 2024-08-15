import tkinter as tk
from checker_game import CheckerGame
from tkinter import messagebox

class SetupWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Checkers Game Setup")
        self.geometry("400x300")

        # Initialize configuration variables with default values
        self.color_var = tk.StringVar(self, value="red")
        self.difficulty_var = tk.StringVar(self, value="beginner")

        frame = tk.Frame(self)
        frame.pack(pady=10)

        tk.Label(frame, text="Choose your color:").pack()
        color_menu = tk.OptionMenu(frame, self.color_var, "red", "green")
        color_menu.pack(fill="x", padx=5, pady=5)

        tk.Label(frame, text="Select AI difficulty:").pack()
        difficulty_menu = tk.OptionMenu(frame, self.difficulty_var, "beginner", "intermediate", "master")
        difficulty_menu.pack(fill="x", padx=5, pady=5)

        start_button = tk.Button(frame, text="Start Game", command=self.start_game)
        start_button.pack(pady=10)

        # Adding the instructions button
        help_button = tk.Button(frame, text="Show Instructions", command=self.show_instructions)
        help_button.pack(pady=10)

        rules_button = tk.Button(frame, text="Show Rules", command=self.show_rules)
        rules_button.pack(pady=5)

    def start_game(self):
        game_window = GameWindow(self.color_var.get(), self.difficulty_var.get())
        game_window.mainloop()
        self.destroy()

    def show_instructions(self):
        # Here you define what happens when the "Show Instructions" button is clicked.
        instructions = """
        Welcome to the Checkers Game!

        Instructions:
        - Choose your color to be either red or green.
        - Select the difficulty level of the AI you want to play against.
        - Click 'Start Game' to begin playing.
        - Once in the game, click on a piece to select it, and then click a highlighted square to move it.
        - Capture all of the opponent's pieces to win.

        Enjoy the game!
        """
        tk.messagebox.showinfo("Game Instructions", instructions)

    def show_rules(self):
        rules_window = tk.Toplevel(self)
        rules_window.title("Game Rules")
        rules_window.geometry("500x400")  # Adjust size as needed

        # Adding a Text widget to display rules
        rules_text = tk.Text(rules_window, wrap="word")
        rules_text.pack(expand=True, fill="both", padx=10, pady=10)
        rules_content = """
        Checkers Game Rules:

        1. Movement: Players take turns moving their pieces diagonally forward.
        2. Jumping: If a player's piece, the "jumper", can land on a square over an opponent's piece (the "jumped"), 
           and the square immediately beyond it is vacant, the jumper must jump the jumped, and the jumped is captured.
        3. Kinging: When a piece reaches the far edge of the board, it becomes a king. Kings can move and jump diagonally forward and backward.
        4. Winning: The game is won by capturing all of the opponent's pieces or by blocking the remaining pieces so they cannot move.

        Players alternate their turn. Try to capture all of your opponent's pieces or block them so they cannot move.
        """
        rules_text.insert("1.0", rules_content)
        rules_text.config(state="disabled")  # Make the text widget read-only

        # Optionally, you can add a close button
        close_button = tk.Button(rules_window, text="Close", command=rules_window.destroy)
        close_button.pack(pady=10)

class GameWindow(tk.Tk):
    def __init__(self, player_color, ai_difficulty):
        super().__init__()
        self.title("Checkers")
        self.game = CheckerGame(self, player_color, ai_difficulty)

if __name__ == "__main__":
    setup_window = SetupWindow()
    setup_window.mainloop()
