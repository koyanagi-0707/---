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
        self.root.geometry("500x750")
        self.root.configure(bg="#f0f8ff")

        # 設定読み込み
        self.settings = self.load_settings()

        # ゲーム変数
        self.sequence = []
        self.user_index = 0
        self.round = 1
        self.miss_count = 0
        self.is_playing_sequence = False

        # 難易度（デフォルト：かんたん）
        self.difficulty = "easy"

        # 色設定（柔らかい色）
        self.colors = ["#ff6b6b", "#4d96ff", "#6bcf63", "#ffd93d"]
        self.light_colors = ["#ff9e9e", "#8ab8ff", "#a8f0a8", "#ffec8a"]

        self.create_title_screen()

    # ============================================================
    # 設定ファイル
    # ============================================================
    def load_settings(self):
        if not os.path.exists(SETTINGS_FILE):
            return {"high_score": 0}
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
                 font=("Arial Rounded MT Bold", 28), bg="#f0f8ff").pack(pady=30)

        tk.Button(self.root, text="スタート", font=("Arial", 20),
                  command=self.start_game).pack(pady=15)

        # ★ 設定画面へ
        tk.Button(self.root, text="設定", font=("Arial", 18),
                  command=self.create_settings_screen).pack(pady=10)

        # ★ ハイスコアリセット
        tk.Button(self.root, text="ハイスコアをリセット", font=("Arial", 16),
                  command=self.reset_high_score).pack(pady=10)

        tk.Label(self.root, text=f"最高記録：{self.settings['high_score']}",
                 font=("Arial", 18), bg="#f0f8ff").pack(pady=10)

    # ============================================================
    # 設定画面（難易度選択）
    # ============================================================
    def create_settings_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="設定", font=("Arial Rounded MT Bold", 26),
                 bg="#f0f8ff").pack(pady=20)

        tk.Label(self.root, text="難易度", font=("Arial", 20),
                 bg="#f0f8ff").pack(pady=10)

        # ★ 現在の難易度をマークで表示
        def mark(level):
            return "●" if self.difficulty == level else "○"

        tk.Button(self.root, text=f"{mark('easy')} かんたん", font=("Arial", 18),
                  command=lambda: self.set_difficulty_and_refresh("easy")).pack(pady=5)

        tk.Button(self.root, text=f"{mark('normal')} ふつう", font=("Arial", 18),
                  command=lambda: self.set_difficulty_and_refresh("normal")).pack(pady=5)

        tk.Button(self.root, text=f"{mark('hard')} むずかしい", font=("Arial", 18),
                  command=lambda: self.set_difficulty_and_refresh("hard")).pack(pady=5)

        tk.Button(self.root, text="戻る", font=("Arial", 18),
                  command=self.create_title_screen).pack(pady=30)

    def set_difficulty_and_refresh(self, level):
        self.difficulty = level
        self.create_settings_screen()

    def reset_high_score(self):
        self.settings["high_score"] = 0
        self.save_settings()
        self.create_title_screen()

    # ============================================================
    # ゲーム開始
    # ============================================================
    def start_game(self):
        self.round = 1
        self.miss_count = 0
        self.sequence = []  # ★ 初期化
        self.create_game_screen()
        self.next_round()

    # ============================================================
    # ゲーム画面
    # ============================================================
    def create_game_screen(self):
        self.clear_screen()

        self.round_label = tk.Label(self.root, text=f"ラウンド：{self.round}",
                                    font=("Arial Rounded MT Bold", 22), bg="#f0f8ff")
        self.round_label.pack(pady=10)

        self.feedback_label = tk.Label(self.root, text="", font=("Arial", 20),
                                       bg="#f0f8ff")
        self.feedback_label.pack(pady=5)

        self.progress_label = tk.Label(self.root, text="", font=("Arial", 26),
                                       bg="#f0f8ff")
        self.progress_label.pack(pady=5)

        self.canvas = tk.Canvas(self.root, width=400, height=400,
                                bg="#f0f8ff", highlightthickness=0)
        self.canvas.pack()

        size = 140
        positions = [(100, 100), (260, 100), (100, 260), (260, 260)]

        self.buttons = {}
        for i, pos in enumerate(positions):
            color = self.colors[i]
            x, y = pos

            oval = self.canvas.create_oval(
                x - size/2, y - size/2,
                x + size/2, y + size/2,
                fill=color, outline="", width=0
            )

            tag = f"btn{i}"
            self.canvas.itemconfig(oval, tags=tag)
            self.canvas.tag_bind(tag, "<Button-1>",
                                 lambda e, c=color: self.user_press(c))

            self.buttons[color] = oval

        tk.Button(self.root, text="やめる", font=("Arial", 18),
                  command=self.create_title_screen).pack(pady=20)

    # ============================================================
    # ラウンド進行（難易度ごとにステップ増加）
    # ============================================================
    def next_round(self):
        self.user_index = 0
        self.miss_count = 0

        # ★ 難易度ごとの増加ステップ数
        if self.difficulty == "easy":
            increase = 1
        elif self.difficulty == "normal":
            increase = 2
        else:  # hard
            increase = random.randint(1, 3)

        # ★ sequence を増やす
        if self.round == 1:
            self.sequence = [random.choice(self.colors)]
        else:
            for _ in range(increase):
                self.sequence.append(random.choice(self.colors))

        self.update_progress()
        self.round_label.config(text=f"ラウンド：{self.round}")

        threading.Thread(target=self.play_sequence).start()

    # ============================================================
    # シーケンス再生（難易度でスピード変更）
    # ============================================================
    def play_sequence(self):
        self.is_playing_sequence = True
        time.sleep(0.8)

        if self.difficulty == "easy":
            flash_speed = 0.45
        elif self.difficulty == "hard":
            flash_speed = 0.20
        else:
            flash_speed = 0.30

        for color in self.sequence:
            self.animate_flash(color)
            time.sleep(flash_speed)

        self.is_playing_sequence = False

    def animate_flash(self, color):
        oval = self.buttons[color]
        index = self.colors.index(color)
        light = self.light_colors[index]

        self.canvas.itemconfig(oval, fill=light)
        self.root.update()
        time.sleep(0.25)

        self.canvas.itemconfig(oval, fill=color)
        self.root.update()

    # ============================================================
    # 光った数の表示（●○）
    # ============================================================
    def update_progress(self):
        done = "●" * self.user_index
        remain = "○" * (len(self.sequence) - self.user_index)
        self.progress_label.config(text=done + remain)

    # ============================================================
    # ユーザー入力
    # ============================================================
    def user_press(self, color):
        if self.is_playing_sequence:
            return

        self.animate_press(color)

        if color == self.sequence[self.user_index]:
            self.user_index += 1
            self.update_progress()

            if self.user_index == len(self.sequence):
                self.feedback_label.config(text="✔ 正解！", fg="green")
                self.root.after(600, lambda: self.feedback_label.config(text=""))

                self.round += 1
                if self.round - 1 > self.settings["high_score"]:
                    self.settings["high_score"] = self.round - 1
                    self.save_settings()
                self.next_round()
            return

        # 不正解（1ミス許容）
        self.miss_count += 1
        self.feedback_label.config(text="✖ まちがい！", fg="red")
        self.root.after(600, lambda: self.feedback_label.config(text=""))

        if self.miss_count == 1:
            self.user_index = 0
            self.update_progress()
            threading.Thread(target=self.play_sequence).start()
            return

        self.game_over()

    # ============================================================
    # 押したときの凹みアニメーション
    # ============================================================
    def animate_press(self, color):
        oval = self.buttons[color]
        index = self.colors.index(color)
        light = self.light_colors[index]

        self.canvas.itemconfig(oval, fill=light)
        self.root.update()
        time.sleep(0.1)

        self.canvas.itemconfig(oval, fill=color)
        self.root.update()

    # ============================================================
    # ゲームオーバー
    # ============================================================
    def game_over(self):
        self.clear_screen()

        tk.Label(self.root, text="ゲームオーバー",
                 font=("Arial Rounded MT Bold", 28), bg="#f0f8ff").pack(pady=40)

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
