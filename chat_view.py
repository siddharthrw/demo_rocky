import tkinter as tk
from tkinter import scrolledtext
from ai_session import AISession
from rocky_commands import extract_and_execute_commands

BG        = "#0d1117"
FG_USER   = "#e6edf3"
FG_ROCKY  = "#7ecfb3"
FG_STATUS = "#58a6ff"
FG_ERROR  = "#ff7b72"
FG_WARN   = "#f0c060"
TITLE_BG  = "#161b22"
BTN_SEND  = "#238636"
BTN_STOP  = "#da3633"
BTN_FG    = "#ffffff"
FONT      = ("Courier New", 10)
FONT_BOLD = ("Courier New", 10, "bold")

PERMISSION_KEYWORDS = [
    "delete", "remove", "format", "install", "uninstall",
    "download", "write", "create file", "modify", "overwrite",
    "run", "execute", "open", "launch", "shutdown", "restart"
]

class ChatWindow:
    def __init__(self, parent, state, on_celebrate):
        self.state = state
        self.on_celebrate = on_celebrate
        self._open = True
        self._pending_message = None

        self.win = tk.Toplevel(parent)
        self.win.title("Rocky — Project Hail Mary")
        self.win.geometry("460x560")
        self.win.configure(bg=BG)
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.close)

        # ── title bar ──────────────────────────────────────────────────────────
        title_bar = tk.Frame(self.win, bg=TITLE_BG, height=32)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)

        tk.Label(
            title_bar,
            text="◉  Rocky  |  Project Hail Mary Edition",
            bg=TITLE_BG, fg=FG_ROCKY,
            font=FONT_BOLD, anchor="w", padx=10
        ).pack(side="left", fill="y")

        tk.Label(
            title_bar,
            text="Gemini 2.0 Flash · Free",
            bg=TITLE_BG, fg="#555555",
            font=("Courier New", 8), anchor="e", padx=10
        ).pack(side="right", fill="y")

        # ── chat log ───────────────────────────────────────────────────────────
        self.log = scrolledtext.ScrolledText(
            self.win, bg=BG, fg=FG_USER, font=FONT,
            wrap=tk.WORD, state="disabled", bd=0,
            padx=8, pady=6
        )
        self.log.pack(fill="both", expand=True, padx=4, pady=(4, 0))

        self.log.tag_config("user",   foreground=FG_USER)
        self.log.tag_config("rocky",  foreground=FG_ROCKY)
        self.log.tag_config("status", foreground=FG_STATUS)
        self.log.tag_config("error",  foreground=FG_ERROR)
        self.log.tag_config("warn",   foreground=FG_WARN)
        self.log.tag_config("label",  foreground="#555555",
                             font=("Courier New", 8))

        # ── permission banner (hidden until needed) ────────────────────────────
        self.perm_frame = tk.Frame(self.win, bg="#2d1b00", pady=6)

        self.perm_label = tk.Label(
            self.perm_frame,
            text="", bg="#2d1b00", fg=FG_WARN,
            font=("Courier New", 9), wraplength=340, justify="left"
        )
        self.perm_label.pack(side="left", padx=10)

        perm_btn_frame = tk.Frame(self.perm_frame, bg="#2d1b00")
        perm_btn_frame.pack(side="right", padx=6)

        tk.Button(
            perm_btn_frame, text="Allow", bg=BTN_SEND, fg=BTN_FG,
            font=FONT_BOLD, relief="flat", width=6,
            command=self._allow
        ).pack(side="left", padx=2)

        tk.Button(
            perm_btn_frame, text="Deny", bg=BTN_STOP, fg=BTN_FG,
            font=FONT_BOLD, relief="flat", width=6,
            command=self._deny
        ).pack(side="left", padx=2)

        # ── input row ─────────────────────────────────────────────────────────
        input_frame = tk.Frame(self.win, bg=TITLE_BG)
        input_frame.pack(fill="x", padx=4, pady=4)

        self.entry = tk.Entry(
            input_frame, bg="#21262d", fg=FG_USER,
            font=FONT, insertbackground=FG_ROCKY,
            bd=0, relief="flat"
        )
        self.entry.pack(side="left", fill="x", expand=True,
                        padx=(6, 4), ipady=5)
        self.entry.bind("<Return>", self._on_enter)

        self.stop_btn = tk.Button(
            input_frame, text="■ Stop", bg=BTN_STOP, fg=BTN_FG,
            font=FONT_BOLD, relief="flat", width=6,
            command=self._stop, state="disabled"
        )
        self.stop_btn.pack(side="right", padx=(0, 2), pady=2)

        self.send_btn = tk.Button(
            input_frame, text="▶ Send", bg=BTN_SEND, fg=BTN_FG,
            font=FONT_BOLD, relief="flat", width=6,
            command=self._send
        )
        self.send_btn.pack(side="right", padx=(0, 2), pady=2)

        # ── session ───────────────────────────────────────────────────────────
        self.session = AISession(
            on_text=self._on_text,
            on_done=self._on_done,
            on_error=self._on_error
        )
        self.current_response = ""  # Buffer for current response

        self._append("status", "rocky online. all eyes on you.\n")
        self.entry.focus()

    # ── helpers ───────────────────────────────────────────────────────────────

    def _append(self, tag, text):
        self.log.configure(state="normal")
        self.log.insert("end", text, tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _needs_permission(self, msg: str) -> bool:
        lower = msg.lower()
        return any(kw in lower for kw in PERMISSION_KEYWORDS)

    # ── permission banner ─────────────────────────────────────────────────────

    def _show_permission_banner(self, msg: str):
        preview = msg[:80] + ("..." if len(msg) > 80 else "")
        self.perm_label.config(
            text=f"Rocky wants to act on: \"{preview}\"\nAllow this action?"
        )
        self.perm_frame.pack(fill="x", padx=4, pady=(0, 2))
        self.perm_frame.lift()
        self.send_btn.config(state="disabled")
        self.entry.config(state="disabled")

    def _hide_permission_banner(self):
        self.perm_frame.pack_forget()
        self.entry.config(state="normal")

    def _allow(self):
        self._hide_permission_banner()
        msg = self._pending_message
        self._pending_message = None
        self._append("warn", "[permission granted]\n")
        self._dispatch(msg)

    def _deny(self):
        self._hide_permission_banner()
        self._pending_message = None
        self._append("error", "[permission denied — rocky will not proceed]\n")
        self.send_btn.config(state="normal")
        self.state.busy = False
        self.state.mood = "walk"

    # ── send flow ─────────────────────────────────────────────────────────────

    def _on_enter(self, _=None):
        self._send()

    def _send(self):
        msg = self.entry.get().strip()
        if not msg or self.state.busy:
            return
        self.entry.delete(0, "end")
        self._append("label", "\nyou  ")
        self._append("user", f"{msg}\n")

        if self._needs_permission(msg):
            self._pending_message = msg
            self.state.busy = True
            self._show_permission_banner(msg)
        else:
            self._dispatch(msg)

    def _dispatch(self, msg: str):
        self.state.busy = True
        self.state.mood = "type"
        self.state.speech = "rocky thinking..."
        self.state.speech_timer = 9999
        self.send_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self._append("label", "\nrocky  ")
        self.session.send(msg)

    # ── stop ──────────────────────────────────────────────────────────────────

    def _stop(self):
        self.session.stop()
        self._append("warn", "\n[stopped by user]\n")
        self._reset_ui()

    # ── AI callbacks ──────────────────────────────────────────────────────────

    def _on_text(self, text):
        self.current_response += text
        self.win.after(0, lambda: self._append("rocky", text))

    def _on_done(self, stopped=False):
        def finish():
            # Process any commands in the response
            extract_and_execute_commands(self.current_response)
            self.current_response = ""
            
            self._append("rocky", "\n")
            if not stopped:
                self.state.mood = "celebrate"
                self.state.speech = "rocky done! *clicks happily*"
                self.state.speech_timer = 120
                self.on_celebrate()
            self._reset_ui()
        self.win.after(0, finish)

    def _on_error(self, msg: str):
        self.win.after(0, lambda: [
            self._append("error", f"\n[error] {msg}\n"),
            self._reset_ui()
        ])

    def _reset_ui(self):
        self.state.busy = False
        if self.state.mood != "celebrate":
            self.state.mood = "walk"
        self.state.speech_timer = 0
        self.send_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.entry.focus()

    # ── close ─────────────────────────────────────────────────────────────────

    def close(self):
        if self.state.busy:
            self.session.stop()
        self._open = False
        self.state.chat_visible = False
        self.state.mood = "walk"
        self.win.destroy()

    def is_open(self):
        return self._open