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
        self.root.geometry("500x720")
        self.root.configure(bg="#f0f8ff")

        # 設定読み込み
        self.settings = self.load_settings()

        # ゲーム変数
        self.sequence = []
        self.user_index = 0
        self.round = 1
        self.miss_count = 0
        self.is_playing_sequence = False

        # 色設定（柔らかい色に変更）
        self.colors = ["#ff6b6b", "#4d96ff", "#6bcf63", "#ffd93d"]
        self.light_colors = ["#ff9e9e", "#8ab8ff", "#a8f0a8", "#ffec8a"]

        self.create_title_screen()

    # ============================================================
    # 設定ファイル
    # ============================================================
    def load_settings(self):
        if not os.path.exists(SETTINGS_FILE):
            return {
                "high_score": 0,
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
                 font=("Arial Rounded MT Bold", 28), bg="#f0f8ff").pack(pady=40)

        tk.Button(self.root, text="スタート", font=("Arial", 20),
                  command=self.start_game).pack(pady=20)

    # ★ ハイスコアリセットボタンを追加
        tk.Button(self.root, text="ハイスコアをリセット", font=("Arial", 16),
              command=self.reset_high_score).pack(pady=10)

        tk.Label(self.root, text=f"最高記録：{self.settings['high_score']}",
                 font=("Arial", 18), bg="#f0f8ff").pack(pady=20)


def reset_high_score(self):
    self.settings["high_score"] = 0
    self.save_settings()
    self.create_title_screen()  # 画面を更新


    # ============================================================
    # ゲーム開始
    # ============================================================
    def start_game(self):
        self.round = 1
        self.miss_count = 0
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

        # フィードバック（正解/不正解）
        self.feedback_label = tk.Label(self.root, text="", font=("Arial", 20),
                                       bg="#f0f8ff")
        self.feedback_label.pack(pady=5)

        # 光った数の表示（●○）
        self.progress_label = tk.Label(self.root, text="", font=("Arial", 26),
                                       bg="#f0f8ff")
        self.progress_label.pack(pady=5)

        # 中央に丸ボタン配置（Canvas）
        self.canvas = tk.Canvas(self.root, width=400, height=400,
                                bg="#f0f8ff", highlightthickness=0)
        self.canvas.pack()

        size = 140
        positions = [(100, 100), (260, 100), (100, 260), (260, 260)]

        self.buttons = {}
        for i, pos in enumerate(positions):
            color = self.colors[i]
            x, y = pos

            # ★ 丸ボタン（影付き）
            oval = self.canvas.create_oval(
                x - size/2, y - size/2,
                x + size/2, y + size/2,
                fill=color, outline="", width=0
            )

            # ボタンとして扱うためにタグ付け
            tag = f"btn{i}"
            self.canvas.itemconfig(oval, tags=tag)

            # クリックイベント
            self.canvas.tag_bind(tag, "<Button-1>",
                                 lambda e, c=color: self.user_press(c))

            self.buttons[color] = oval

        tk.Button(self.root, text="やめる", font=("Arial", 18),
                  command=self.create_title_screen).pack(pady=20)

    # ============================================================
    # ラウンド進行（毎回ランダム生成）
    # ============================================================
    def next_round(self):
        self.user_index = 0
        self.miss_count = 0

        length = self.round
        self.sequence = [random.choice(self.colors) for _ in range(length)]

        self.update_progress()
        self.round_label.config(text=f"ラウンド：{self.round}")

        threading.Thread(target=self.play_sequence).start()

    # ============================================================
    # シーケンス再生（アニメーション強化）
    # ============================================================
    def play_sequence(self):
        self.is_playing_sequence = True
        time.sleep(0.8)

        for i, color in enumerate(self.sequence):
            self.animate_flash(color)
            time.sleep(0.35)

        self.is_playing_sequence = False

    # ============================================================
    # 丸ボタンの光アニメーション
    # ============================================================
    def animate_flash(self, color):
        oval = self.buttons[color]
        index = self.colors.index(color)
        light = self.light_colors[index]

        # 光る
        self.canvas.itemconfig(oval, fill=light)
        self.root.update()
        time.sleep(0.25)

        # 元に戻る
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
    # ユーザー入力（押したときの凹みアニメーション付き）
    # ============================================================
    def user_press(self, color):
        if self.is_playing_sequence:
            return

        # 押したときの凹みアニメーション
        self.animate_press(color)

        # 正解
        if color == self.sequence[self.user_index]:
            self.user_index += 1
            self.update_progress()

            # ★ ラウンドクリア時のみ正解表示
            if self.user_index == len(self.sequence):
                self.feedback_label.config(text="✔ 正解！", fg="green")
                self.root.after(600, lambda: self.feedback_label.config(text=""))

            if self.user_index == len(self.sequence):
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

        # 少し暗くする
        self.canvas.itemconfig(oval, fill=light)
        self.root.update()
        time.sleep(0.1)

        # 元に戻す
        self.canvas.itemconfig(oval, fill=color)
        self.root.update()

    # ============================================================
    # ゲームオーバー
    # ============================================================
    def game_over(self):
        self.clear_screen()

        tk.Label(self.root, text="ゲームオーバー", font=("Arial Rounded MT Bold", 28),
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
