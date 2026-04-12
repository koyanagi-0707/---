import tkinter as tk
import random
import time
import threading

# 色と光ったときの色
COLORS = {
    "R": {"normal": "#802020", "light": "#ff6666"},
    "B": {"normal": "#202080", "light": "#6666ff"},
    "Y": {"normal": "#808020", "light": "#ffff66"},
    "G": {"normal": "#206020", "light": "#66ff66"},
}

class SimonGame:
    def __init__(self, root):
        self.root = root
        self.root.title("4色記憶ゲーム")
        self.root.geometry("700x800")

        # 中央寄せ
        for i in range(5):
            self.root.grid_rowconfigure(i, weight=1)
            self.root.grid_columnconfigure(i, weight=1)

        self.sequence = []
        self.user_index = 0

        # メッセージ表示
        self.message = tk.Label(root, text="", font=("Arial", 28))
        self.message.grid(row=0, column=1, columnspan=2, pady=10)

        # 丸ボタン用キャンバス
        self.canvas = tk.Canvas(root, width=500, height=500, bg="white", highlightthickness=0)
        self.canvas.grid(row=1, column=1, rowspan=2, columnspan=2)

        self.create_round_buttons()

        # スタートボタン
        self.start_button = tk.Button(root, text="スタート", font=("Arial", 26),
                                      command=self.start_game)
        self.start_button.grid(row=4, column=1, columnspan=2, pady=20)

    def create_round_buttons(self):
        self.buttons = {}
        r = 100  # 半径

        # 配置位置
        positions = {
            "R": (150, 150),
            "B": (350, 150),
            "Y": (150, 350),
            "G": (350, 350),
        }

        for key, (x, y) in positions.items():
            item = self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill=COLORS[key]["normal"],
                outline=""
            )
            self.buttons[key] = item

            # クリックイベント
            self.canvas.tag_bind(item, "<Button-1>", lambda e, k=key: self.user_press(k))

    def start_game(self):
        self.sequence = []
        self.user_index = 0
        self.message.config(text="")
        self.next_round()

    def next_round(self):
        self.user_index = 0

        # ★ ラウンド数＝光る数
        round_num = len(self.sequence) + 1

        # ★ ラウンドごとに完全に新しいランダム列を生成
        self.sequence = [
            random.choice(list(COLORS.keys()))
            for _ in range(round_num)
        ]

        threading.Thread(target=self.countdown_and_play).start()

    def countdown_and_play(self):
        # カウントダウン
        for i in ["3", "2", "1"]:
            self.message.config(text=f"よ～くみててね… {i}")
            time.sleep(1)

        self.message.config(text="ひかっているよ！…")
        time.sleep(0.5)

        # シーケンス再生
        for key in self.sequence:
            self.flash_button(key)
            time.sleep(0.4)

        self.message.config(text="ひかったじゅんばんにおしてね！")

    def flash_button(self, key):
        item = self.buttons[key]
        self.canvas.itemconfig(item, fill=COLORS[key]["light"])
        self.root.update()
        time.sleep(0.3)
        self.canvas.itemconfig(item, fill=COLORS[key]["normal"])
        self.root.update()

    # ユーザー押下時の光
    def flash_button_user(self, key):
        item = self.buttons[key]
        self.canvas.itemconfig(item, fill=COLORS[key]["light"])
        self.root.update()

        self.root.after(150, lambda: self.canvas.itemconfig(item, fill=COLORS[key]["normal"]))

    def user_press(self, key):
        # 押した瞬間に光る
        self.flash_button_user(key)

        if self.message.cget("text") != "ひかったじゅんばんにおしてね！":
            return

        if key == self.sequence[self.user_index]:
            self.user_index += 1

            # 全部正解
            if self.user_index == len(self.sequence):
                self.message.config(text="せいかい！すこしむずかしくなるよ！")
                self.root.after(1200, self.next_round)
        else:
            self.game_over()

    def game_over(self):
        self.message.config(text=f"ざんねん！ここまで！ スコア：{len(self.sequence)-1}")


root = tk.Tk()
game = SimonGame(root)
root.mainloop()