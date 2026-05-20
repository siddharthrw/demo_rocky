import tkinter as tk
from PIL import Image, ImageTk
import random
import os
from dotenv import load_dotenv
from rocky_state import RockyState
from chat_view import ChatWindow

load_dotenv()

SPRITE_DIR = "sprites"
ROCKY_W, ROCKY_H = 64, 64
FPS = 60
SPRITE_FPS = 8

SPRITES = {
    "walk":      ["walkleft1.png", "walkleft2.png"],
    "stand":     ["stand.png"],
    "type":      ["jazz1.png", "jazz2.png"],
    "celebrate": ["jazz1.png", "jazz2.png", "jazz3.png"],
}

QUIPS = [
    "*clicks excitedly*",
    "rocky ready!",
    "all eyes on you",
    "what task, friend?",
    "rocky do big science",
    "amaze!",
    "*wiggles legs*",
    "rocky is watching... nicely",
]


class RockyApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", "black")
        self.root.configure(bg="black")

        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        self.y_pos = self.screen_h - ROCKY_H - 52

        self.root.geometry(f"{ROCKY_W}x{ROCKY_H}+100+{self.y_pos}")

        self.canvas = tk.Canvas(
            self.root, width=ROCKY_W, height=ROCKY_H,
            bg="black", highlightthickness=0
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Button-3>", self._on_right_click)
        self.canvas.bind(
            "<Enter>",
            lambda e: self._show_tooltip("left-click to chat  •  right-click to quit")
        )
        self.canvas.bind("<Leave>", lambda e: self._hide_tooltip())

        self.state = RockyState()
        self.chat_win = None
        self._flipped_frame = None

        self._load_frames()

        self.frame_idx = 0
        self.sprite_tick = 0
        self.celebrate_timer = 0
        self.quip_timer = random.randint(900, 2700)

        self.bubble = tk.Label(
            self.root, text="", bg="#fffde7", fg="#1a1a2e",
            font=("Courier New", 8), relief="solid", bd=1,
            padx=4, pady=2, wraplength=160
        )

        self._img_item = self.canvas.create_image(0, 0, anchor="nw")
        self.root.after(0, self._loop)

    # ── sprite loading ────────────────────────────────────────────────────────

    def _load_frames(self):
        self.frames = {}
        missing = []
        for mood, files in SPRITES.items():
            self.frames[mood] = []
            for f in files:
                path = os.path.join(SPRITE_DIR, f)
                if not os.path.exists(path):
                    if path not in missing:
                        missing.append(path)
                else:
                    img = Image.open(path).resize(
                        (ROCKY_W, ROCKY_H), Image.NEAREST
                    )
                    self.frames[mood].append(ImageTk.PhotoImage(img))

        if missing:
            print("\n⚠  Missing sprite files:")
            for m in set(missing):
                print(f"   {m}")
            print("Add them to the sprites\\ folder and restart.\n")

    def _get_frame(self, mood, idx):
        frames = self.frames.get(mood) or self.frames.get("stand") or []
        if not frames:
            return None
        return frames[idx % len(frames)]

    # ── interactions ──────────────────────────────────────────────────────────

    def _on_click(self, _):
        if self.chat_win is None or not self.chat_win.is_open():
            self.chat_win = ChatWindow(
                self.root, self.state, self._on_celebrate
            )
        self.state.chat_visible = True
        self.state.mood = "stand"

    def _on_right_click(self, _):
        self.root.destroy()

    def _on_celebrate(self):
        self.celebrate_timer = 90

    def _show_tooltip(self, text):
        self.state.speech = text
        self.state.speech_timer = 9999

    def _hide_tooltip(self):
        if self.state.speech_timer == 9999:
            self.state.speech_timer = 0

    # ── main loop ─────────────────────────────────────────────────────────────

    def _loop(self):
        s = self.state

        # movement
        if s.mood == "walk":
            speed = 1.2
            s.x += speed if s.direction == "right" else -speed
            if s.x >= self.screen_w - ROCKY_W:
                s.direction = "left"
            elif s.x <= 0:
                s.direction = "right"

        # celebration countdown
        if self.celebrate_timer > 0:
            self.celebrate_timer -= 1
            s.mood = "celebrate"
            if self.celebrate_timer == 0:
                s.mood = "walk" if not s.busy else "type"

        # random idle quip
        self.quip_timer -= 1
        if self.quip_timer <= 0 and not s.busy:
            s.speech = random.choice(QUIPS)
            s.speech_timer = 150
            self.quip_timer = random.randint(900, 2700)

        # speech bubble
        if s.speech_timer > 0 and s.speech:
            s.speech_timer -= 1
            self.bubble.config(text=s.speech)
            self.bubble.place(x=0, y=-34)
            self.bubble.lift()
        else:
            self.bubble.place_forget()

        # sprite animation tick
        self.sprite_tick += 1
        if self.sprite_tick >= FPS // SPRITE_FPS:
            self.sprite_tick = 0
            mood_frames = self.frames.get(s.mood) or self.frames.get("stand", [])
            if mood_frames:
                self.frame_idx = (self.frame_idx + 1) % len(mood_frames)

        # get frame — flip horizontally when walking left
        frame = self._get_frame(s.mood, self.frame_idx)

        if s.direction == "left" and s.mood == "walk":
            file_list = SPRITES.get(s.mood, ["stand.png"])
            fname = file_list[self.frame_idx % len(file_list)]
            path = os.path.join(SPRITE_DIR, fname)
            if os.path.exists(path):
                pil_img = (
                    Image.open(path)
                    .resize((ROCKY_W, ROCKY_H), Image.NEAREST)
                    .transpose(Image.FLIP_LEFT_RIGHT)
                )
                frame = ImageTk.PhotoImage(pil_img)
                self._flipped_frame = frame  # keep reference alive

        if frame:
            self.canvas.itemconfig(self._img_item, image=frame)

        self.root.geometry(
            f"{ROCKY_W}x{ROCKY_H}+{int(s.x)}+{self.y_pos}"
        )
        self.root.after(1000 // FPS, self._loop)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    RockyApp().run()