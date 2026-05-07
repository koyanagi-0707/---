import tkinter as tk
import random
import json
import threading
import time
import os

SETTINGS_FILE = "settings.json"


class SimonGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Memory Trainer")
        self.root.geometry("500x650")
        self.root.configure(bg="#f0f8ff")

        # -------------------------
        # 設定読み込み
        # -------------------------
        self.settings = self.load_settings()

        # ゲーム変数
        self.sequence = []
        self.user_index = 0
        self.round = 1
        self.miss_count = 0  # ← 1ミス許容
        self.is_playing_sequence = False

        # 色設定
        self.colors = ["red", "blue", "green", "yellow"]
        self.light_colors = {
            "red": "#ff8080",
            "blue": "#8080ff",
            "green": "#80ff80",
            "yellow": "#ffff80"
        }

        # 色弱モード用模様
        self.patterns = {
            "red": "●",
            "blue": "▲",
            "green": "■",
            "yellow": "★"
        }

        self.create_title_screen()

    # ============================================================
    # 設定ファイル読み込み
    # ============================================================
    def load_settings(self):
        if not os.path.exists(SETTINGS_FILE):
            return {
                "high_score": 0,
                "volume": 1.0,
                "color_mode": "normal",
                "button_size": "large"
            }
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)

    def save_settings(self):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f, indent=4)

    # ============================================================
    # タイトル画面
    # ============================================================
    def create_title_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Color Memory Trainer",
                 font=("Arial", 28, "bold"), bg="#f0f8ff").pack(pady=40)

        tk.Button(self.root, text="スタート", font=("Arial", 20),
                  command=self.start_game).pack(pady=20)

        tk.Button(self.root, text="設定", font=("Arial", 18),
                  command=self.create_settings_screen).pack(pady=10)

        tk.Label(self.root, text=f"最高記録：{self.settings['high_score']}",
                 font=("Arial", 16), bg="#f0f8ff").pack(pady=20)

    # ============================================================
    # 設定画面
    # ============================================================
    def create_settings_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="設定", font=("Arial", 26, "bold"),
                 bg="#f0f8ff").pack(pady=20)

        # 色弱モード
        tk.Label(self.root, text="色弱モード", font=("Arial", 18),
                 bg="#f0f8ff").pack()
        tk.Button(self.root, text="通常モード",
                  command=lambda: self.change_color_mode("normal")).pack(pady=5)
        tk.Button(self.root, text="色弱モード",
                  command=lambda: self.change_color_mode("pattern")).pack(pady=5)

        # ボタンサイズ
        tk.Label(self.root, text="ボタンサイズ", font=("Arial", 18),
                 bg="#f0f8ff").pack(pady=10)
        tk.Button(self.root, text="大", command=lambda: self.change_button_size("large")).pack()
        tk.Button(self.root, text="中", command=lambda: self.change_button_size("medium")).pack()
        tk.Button(self.root, text="小", command=lambda: self.change_button_size("small")).pack()

        tk.Button(self.root, text="戻る", font=("Arial", 18),
                  command=self.create_title_screen).pack(pady=30)

    def change_color_mode(self, mode):
        self.settings["color_mode"] = mode
        self.save_settings()

    def change_button_size(self, size):
        self.settings["button_size"] = size
        self.save_settings()

    # ============================================================
    # ゲーム開始
    # ============================================================
    def start_game(self):
        self.sequence = []
        self.round = 1
        self.miss_count = 0
        self.create_game_screen()
        self.next_round()

    # ============================================================
    # ゲーム画面
    # ============================================================
    def create_game_screen(self):
        self.clear_screen()

        tk.Label(self.root, text=f"ラウンド：{self.round}",
                 font=("Arial", 22), bg="#f0f8ff").pack(pady=10)

        self.canvas = tk.Canvas(self.root, width=400, height=400, bg="#f0f8ff", highlightthickness=0)
        self.canvas.pack()

        size = {"large": 150, "medium": 120, "small": 90}[self.settings["button_size"]]

        self.buttons = {}
        positions = [(50, 50), (200, 50), (50, 200), (200, 200)]

        for color, pos in zip(self.colors, positions):
            x, y = pos
            btn = tk.Button(self.root, bg=color, width=8, height=4,
                            command=lambda c=color: self.user_press(c))
            btn.place(x=x + 60, y=y + 200, width=size, height=size)
            self.buttons[color] = btn

        tk.Button(self.root, text="やめる", font=("Arial", 16),
                  command=self.create_title_screen).pack(pady=20)

    # ============================================================
    # ラウンド進行
    # ============================================================
    def next_round(self):
        self.user_index = 0
        self.miss_count = 0
        self.sequence.append(random.choice(self.colors))

        threading.Thread(target=self.play_sequence).start()

    # ============================================================
    # シーケンス再生
    # ============================================================
    def play_sequence(self):
        self.is_playing_sequence = True
        time.sleep(0.8)

        for color in self.sequence:
            self.flash_button(color)
            time.sleep(0.4)

        self.is_playing_sequence = False

    def flash_button(self, color):
        btn = self.buttons[color]
        original = btn["bg"]
        btn["bg"] = self.light_colors[color]
        self.root.update()
        time.sleep(0.25)
        btn["bg"] = original
        self.root.update()

    # ============================================================
    # ユーザー入力
    # ============================================================
    def user_press(self, color):
        if self.is_playing_sequence:
            return

        # 正解
        if color == self.sequence[self.user_index]:
            self.user_index += 1

            if self.user_index == len(self.sequence):
                self.round += 1
                if self.round - 1 > self.settings["high_score"]:
                    self.settings["high_score"] = self.round - 1
                    self.save_settings()
                self.next_round()
            return

        # -------------------------
        # 不正解（1ミス許容）
        # -------------------------
        self.miss_count += 1

        if self.miss_count == 1:
            self.user_index = 0
            threading.Thread(target=self.play_sequence).start()
            return

        # 2回目のミス → ゲームオーバー
        self.game_over()

    # ============================================================
    # ゲームオーバー
    # ============================================================
    def game_over(self):
        self.clear_screen()

        tk.Label(self.root, text="ゲームオーバー", font=("Arial", 28, "bold"),
                 bg="#f0f8ff").pack(pady=40)

        tk.Label(self.root, text=f"到達ラウンド：{self.round - 1}",
                 font=("Arial", 22), bg="#f0f8ff").pack(pady=10)

        tk.Label(self.root, text=f"最高記録：{self.settings['high_score']}",
                 font=("Arial", 20), bg="#f0f8ff").pack(pady=10)

        tk.Button(self.root, text="もう一度", font=("Arial", 20),
                  command=self.start_game).pack(pady=20)

        tk.Button(self.root, text="タイトルへ", font=("Arial", 18),
                  command=self.create_title_screen).pack(pady=10)

    # ============================================================
    # 画面クリア
    # ============================================================
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()


# ============================================================
# 実行
# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    SimonGame(root)
    root.mainloop()
