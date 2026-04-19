import tkinter as tk
from tkinter import messagebox, ttk
import random
import sqlite3
import os

# ---------- SOUND SETUP ----------
try:
    import pygame
    pygame.mixer.init()
    SOUND = True
except:
    SOUND = False

def start_music():
    if SOUND and os.path.exists("bg_music.mp3"):
        try:
            pygame.mixer.music.load("bg_music.mp3")
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
        except:
            pass

def stop_music():
    if SOUND:
        pygame.mixer.music.stop()

def play_sound(file):
    if SOUND and os.path.exists(file):
        try:
            sound = pygame.mixer.Sound(file)
            sound.play()
        except:
            pass

# ---------- DATABASE ----------
conn = sqlite3.connect("leaderboard.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS leaderboard (
    name TEXT,
    score INTEGER
)
""")
conn.commit()

# ---------- GAME CLASS ----------
class GuessGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Number Guessing Game")
        self.root.geometry("380x450")
        self.root.configure(bg="#1e1e2f")

        self.frame = tk.Frame(root, bg="#1e1e2f")
        self.frame.pack(pady=20)

        self.name = tk.StringVar()
        self.guess = tk.IntVar()
        self.game_active = False

        self.create_start_screen()

    # ---------- START SCREEN ----------
    def create_start_screen(self):
        self.game_active = False
        self.clear_frame()

        tk.Label(self.frame, text="Number Guessing Game", fg="white", bg="#1e1e2f",
                 font=("Arial", 16, "bold")).pack(pady=10)

        tk.Label(self.frame, text="Enter Your Name", fg="white", bg="#1e1e2f").pack()
        tk.Entry(self.frame, textvariable=self.name, font=("Arial", 12), justify="center").pack(pady=5)

        tk.Label(self.frame, text="Select Difficulty", fg="white", bg="#1e1e2f").pack(pady=5)

        self.make_button("Easy", "#4CAF50", lambda: self.start_game("easy"))
        self.make_button("Medium", "#FF9800", lambda: self.start_game("medium"))
        self.make_button("Hard", "#f44336", lambda: self.start_game("hard"))

        self.make_button("Leaderboard", "#2196F3", self.show_leaderboard)

    # ---------- BUTTON STYLE ----------
    def make_button(self, text, color, cmd):
        tk.Button(
            self.frame,
            text=text,
            bg=color,
            fg="white",
            font=("Arial", 10, "bold"),
            width=18,
            command=cmd
        ).pack(pady=4)

    # ---------- START GAME ----------
    def start_game(self, level):
        self.clear_frame()

        settings = {
            "easy": (1, 50, 10, 30),
            "medium": (1, 100, 7, 25),
            "hard": (1, 200, 5, 20)
        }

        self.low, self.high, self.attempts, self.time_left = settings[level]
        self.number = random.randint(self.low, self.high)
        self.score = 100
        self.previous_guesses = []
        self.game_active = True

        tk.Label(self.frame, text=f"Guess between {self.low}-{self.high}",
                 fg="white", bg="#1e1e2f", font=("Arial", 12, "bold")).pack()

        self.timer_label = tk.Label(self.frame, text=f"Time: {self.time_left}",
                                    fg="white", bg="#1e1e2f")
        self.timer_label.pack()

        # Progress Bar
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TProgressbar", thickness=20,
                        troughcolor="#2e2e3e", background="#4CAF50")

        self.progress = ttk.Progressbar(self.frame, length=250,
                                        maximum=self.time_left)
        self.progress.pack(pady=5)
        self.progress['value'] = self.time_left

        self.attempt_label = tk.Label(self.frame,
                                     text=f"Attempts: {self.attempts}",
                                     fg="white", bg="#1e1e2f")
        self.attempt_label.pack()

        tk.Entry(self.frame, textvariable=self.guess,
                 font=("Arial", 12), justify="center").pack(pady=5)

        self.make_button("Submit", "#9C27B0", self.check_guess)

        self.hint_label = tk.Label(self.frame, text="",
                                   fg="white", bg="#1e1e2f")
        self.hint_label.pack(pady=5)

        self.run_timer()

    # ---------- TIMER ----------
    def run_timer(self):
        if self.time_left > 0 and self.game_active:
            self.time_left -= 1
            self.timer_label.config(text=f"Time: {self.time_left}")
            self.progress['value'] = self.time_left
            self.root.after(1000, self.run_timer)

        elif self.time_left == 0 and self.game_active:
            self.game_active = False
            stop_music()
            messagebox.showinfo("Game Over", "Time's up!")
            start_music()
            self.create_start_screen()

    # ---------- CHECK GUESS ----------
    def check_guess(self):
        if not self.game_active:
            return

        try:
            g = self.guess.get()
        except:
            messagebox.showerror("Error", "Enter valid number")
            return

        self.previous_guesses.append(g)
        self.attempts -= 1
        self.score -= 10

        self.attempt_label.config(text=f"Attempts: {self.attempts}")

        if g == self.number:
            self.game_active = False
            play_sound("correct.mp3")
            stop_music()
            self.save_score()
            messagebox.showinfo("Win", f"Correct! Score: {self.score}")
            start_music()
            self.create_start_screen()

        else:
            play_sound("wrong.mp3")
            self.hint_label.config(text=self.smart_hint(g))

            if self.attempts == 0:
                self.game_active = False
                stop_music()
                messagebox.showinfo("Game Over", f"Number was {self.number}")
                start_music()
                self.create_start_screen()

    # ---------- SMART HINT ----------
    def smart_hint(self, guess):
        diff = abs(self.number - guess)

        if diff <= 5:
            hint = "🔥 Very Close!"
        elif diff <= 15:
            hint = "🙂 Close"
        else:
            hint = "❄️ Far away"

        if guess < self.number:
            hint += " (Higher)"
        else:
            hint += " (Lower)"

        if len(self.previous_guesses) >= 2:
            if abs(self.previous_guesses[-1] - self.number) < abs(self.previous_guesses[-2] - self.number):
                hint += " 📈 Warmer"
            else:
                hint += " 📉 Colder"

        return hint

    # ---------- SAVE SCORE ----------
    def save_score(self):
        cursor.execute("INSERT INTO leaderboard VALUES (?, ?)",
                       (self.name.get(), self.score))
        conn.commit()

    # ---------- LEADERBOARD ----------
    def show_leaderboard(self):
        self.clear_frame()

        tk.Label(self.frame, text="Leaderboard",
                 fg="white", bg="#1e1e2f",
                 font=("Arial", 14, "bold")).pack()

        cursor.execute("SELECT * FROM leaderboard ORDER BY score DESC LIMIT 5")
        for row in cursor.fetchall():
            tk.Label(self.frame, text=f"{row[0]} - {row[1]}",
                     fg="white", bg="#1e1e2f").pack()

        self.make_button("Back", "#607D8B", self.create_start_screen)

    # ---------- UTIL ----------
    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

# ---------- RUN ----------
root = tk.Tk()
start_music()
app = GuessGame(root)
root.mainloop()