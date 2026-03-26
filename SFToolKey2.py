import json
import os
import random
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import keyboard
import pydirectinput


# =========================
# CONFIG
# =========================
APP_TITLE = "SFToolKey"
SETTINGS_FILE = "sftoolkey_profiles.json"

pydirectinput.FAILSAFE = False
pydirectinput.PAUSE = 0.0


# =========================
# THEME
# =========================
BG = "#101010"
CARD = "#1a1a1a"
CARD_2 = "#202020"
ACCENT = "#ff8a1f"
ACCENT_HOVER = "#ff9b42"
TEXT = "#f3f3f3"
MUTED = "#bdbdbd"
BORDER = "#2b2b2b"
INPUT_BG = "#262626"
INPUT_ACTIVE = "#303030"
SUCCESS = "#5fd38d"
ERROR = "#ff6b6b"
WARN = "#ffcc66"
WAIT_BG = "#3a2a16"


# =========================
# HELPERS
# =========================
def now_str():
    return time.strftime("%H:%M:%S")


def parse_float(value, default=None):
    try:
        return float(str(value).strip().replace(",", "."))
    except Exception:
        return default


def parse_int(value, default=None):
    try:
        return int(float(str(value).strip().replace(",", ".")))
    except Exception:
        return default


def parse_keys_csv(text):
    parts = [x.strip().lower() for x in text.split(",")]
    return [x for x in parts if x]


def safe_is_pressed(key_name: str):
    if not key_name:
        return False
    try:
        return keyboard.is_pressed(key_name)
    except Exception:
        return False


def get_pointer_position(root):
    return root.winfo_pointerx(), root.winfo_pointery()


def clamp_positive(v, minimum=0.0):
    if v is None:
        return None
    return max(minimum, v)


# =========================
# APP
# =========================
class SFToolKeyApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("980x860")
        self.root.minsize(900, 720)
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self.running_random = False
        self.running_clicker = False
        self.running_macro = False

        self.random_thread = None
        self.clicker_thread = None
        self.macro_thread = None
        self.hotkey_thread = None

        self.editing_hotkey = False
        self.hotkeys_blocked_until = 0.0
        self.hotkey_listener_started = False

        self.profiles = {}
        self.current_profile_name = tk.StringVar(value="default")

        self.build_vars()
        self.apply_ttk_style()
        self.build_gui()
        self.load_profiles_from_disk()
        self.start_hotkey_listener()

        self.log("Приложение запущено")

    # =========================
    # VARIABLES
    # =========================
    def build_vars(self):
        # Common
        self.status_global = tk.StringVar(value="Остановлено")
        self.profile_name_var = tk.StringVar(value="default")

        # Random tab
        self.random_use_keyboard = tk.BooleanVar(value=True)
        self.random_use_mouse = tk.BooleanVar(value=True)
        self.random_keys = tk.StringVar(value="w,a,s,d")
        self.random_key_hold = tk.StringVar(value="0.7")
        self.random_key_pause = tk.StringVar(value="0.2")
        self.random_mouse_interval_min = tk.StringVar(value="2.0")
        self.random_mouse_interval_max = tk.StringVar(value="5.0")
        self.random_mouse_move_min = tk.StringVar(value="20")
        self.random_mouse_move_max = tk.StringVar(value="120")
        self.random_start_hotkey = tk.StringVar(value="f8")
        self.random_stop_hotkey = tk.StringVar(value="f9")

        # Clicker tab
        self.clicker_status = tk.StringVar(value="Остановлено")
        self.clicker_mode = tk.StringVar(value="mouse")  # mouse / keyboard
        self.clicker_mouse_button = tk.StringVar(value="left")
        self.clicker_keyboard_key = tk.StringVar(value="space")

        self.clicker_interval_mode = tk.StringVar(value="fixed")  # fixed / random
        self.clicker_interval_value = tk.StringVar(value="50")
        self.clicker_interval_unit = tk.StringVar(value="ms")
        self.clicker_interval_min = tk.StringVar(value="30")
        self.clicker_interval_max = tk.StringVar(value="80")
        self.clicker_interval_random_unit = tk.StringVar(value="ms")

        self.clicker_action_type = tk.StringVar(value="single")  # single/double/triple/hold
        self.clicker_hold_time = tk.StringVar(value="0.3")

        self.clicker_repeat_mode = tk.StringVar(value="infinite")  # infinite / count
        self.clicker_repeat_count = tk.StringVar(value="100")

        self.clicker_target_mode = tk.StringVar(value="current")  # current / coords
        self.clicker_target_x = tk.StringVar(value="0")
        self.clicker_target_y = tk.StringVar(value="0")

        self.clicker_start_hotkey = tk.StringVar(value="f6")
        self.clicker_stop_hotkey = tk.StringVar(value="f7")

        self.clicker_count_done = tk.StringVar(value="0")

        # Macro tab
        self.macro_status = tk.StringVar(value="Остановлено")
        self.macro_repeat_mode = tk.StringVar(value="1")  # 1 / infinite / count
        self.macro_repeat_count = tk.StringVar(value="3")
        self.macro_start_hotkey = tk.StringVar(value="f10")
        self.macro_stop_hotkey = tk.StringVar(value="f11")

    # =========================
    # LOGGING
    # =========================
    def log(self, text):
        line = f"[{now_str()}] {text}"
        if hasattr(self, "log_box"):
            self.log_box.configure(state="normal")
            self.log_box.insert("end", line + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        print(line)

    def clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")
        self.log("Лог очищен")

    # =========================
    # STYLE
    # =========================
    def apply_ttk_style(self):
        style = ttk.Style()
        style.theme_use("default")

        style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=[8, 8, 8, 0])
        style.configure(
            "TNotebook.Tab",
            background=CARD_2,
            foreground=TEXT,
            padding=[16, 10],
            font=("Segoe UI", 10, "bold"),
            borderwidth=0
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", ACCENT), ("active", INPUT_ACTIVE)],
            foreground=[("selected", "black"), ("active", TEXT)]
        )

    # =========================
    # UI HELPERS
    # =========================
    def make_card(self, parent):
        return tk.Frame(parent, bg=CARD, highlightthickness=1, highlightbackground=BORDER)

    def make_title(self, parent, text):
        return tk.Label(parent, text=text, bg=CARD, fg=TEXT, font=("Segoe UI", 11, "bold"))

    def make_text(self, parent, text):
        return tk.Label(parent, text=text, bg=CARD, fg=MUTED, font=("Segoe UI", 10))

    def make_entry(self, parent, textvar=None, width=18):
        return tk.Entry(
            parent,
            textvariable=textvar,
            width=width,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            font=("Segoe UI", 10),
        )

    def make_button(self, parent, text, command, width=14, bg=ACCENT, fg="black"):
        return tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            bg=bg,
            fg=fg,
            activebackground=ACCENT_HOVER if bg == ACCENT else bg,
            activeforeground=fg,
            relief="flat",
            bd=0,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            padx=10,
            pady=8,
        )

    def make_check(self, parent, text, variable):
        return tk.Checkbutton(
            parent,
            text=text,
            variable=variable,
            bg=CARD,
            fg=TEXT,
            activebackground=CARD,
            activeforeground=TEXT,
            selectcolor=INPUT_BG,
            font=("Segoe UI", 10),
            cursor="hand2",
            bd=0,
            highlightthickness=0,
        )

    def make_radio(self, parent, text, variable, value, command=None):
        return tk.Radiobutton(
            parent,
            text=text,
            variable=variable,
            value=value,
            command=command,
            bg=CARD,
            fg=TEXT,
            activebackground=CARD,
            activeforeground=TEXT,
            selectcolor=INPUT_BG,
            font=("Segoe UI", 10),
            cursor="hand2",
            bd=0,
            highlightthickness=0,
        )

    def make_option(self, parent, variable, values, width=12):
        menu = tk.OptionMenu(parent, variable, *values)
        menu.config(
            bg=INPUT_BG,
            fg=TEXT,
            activebackground=INPUT_ACTIVE,
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER,
            font=("Segoe UI", 10),
            width=width,
        )
        menu["menu"].config(
            bg=INPUT_BG,
            fg=TEXT,
            activebackground=ACCENT,
            activeforeground="black",
            font=("Segoe UI", 10),
        )
        return menu

    # =========================
    # KEY BIND BOX
    # =========================
    class KeyBindBox(tk.Label):
        def __init__(self, app, parent, variable, width=16):
            super().__init__(
                parent,
                textvariable=variable,
                width=width,
                bg=INPUT_BG,
                fg=TEXT,
                relief="flat",
                bd=0,
                padx=12,
                pady=10,
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
                highlightthickness=1,
                highlightbackground=BORDER,
            )
            self.app = app
            self.variable = variable
            self.waiting = False

            self.bind("<Button-1>", self.start_capture)
            self.bind("<Enter>", lambda e: self.config(bg=INPUT_ACTIVE if not self.waiting else WAIT_BG))
            self.bind("<Leave>", lambda e: self.config(bg=INPUT_BG if not self.waiting else WAIT_BG))

        def start_capture(self, event=None):
            if self.waiting:
                return
            self.waiting = True
            self.app.editing_hotkey = True
            self.config(bg=WAIT_BG, highlightbackground=ACCENT)
            self.variable.set("Нажми клавишу...")
            threading.Thread(target=self.capture_thread, daemon=True).start()

        def capture_thread(self):
            try:
                while True:
                    ev = keyboard.read_event(suppress=False)
                    if ev.event_type == keyboard.KEY_DOWN:
                        name = (ev.name or "").lower()
                        if name:
                            self.app.root.after(0, lambda n=name: self.finish_capture(n))
                            return
            except Exception:
                self.app.root.after(0, lambda: self.finish_capture(""))

        def finish_capture(self, key_name):
            if key_name:
                self.variable.set(key_name)
                self.app.hotkeys_blocked_until = time.time() + 2.0
                self.app.log(f"Назначена клавиша: {key_name}")
            self.waiting = False
            self.app.editing_hotkey = False
            self.config(bg=INPUT_BG, highlightbackground=BORDER)

    # =========================
    # GUI
    # =========================
    def build_gui(self):
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0, bd=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.content = tk.Frame(canvas, bg=BG)
        self.canvas_window = canvas.create_window((0, 0), window=self.content, anchor="nw")

        self.content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(self.canvas_window, width=e.width))

        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        self.build_header()
        self.build_profile_bar()
        self.build_tabs()
        self.build_bottom_log()

    def build_header(self):
        header = tk.Frame(self.content, bg=BG)
        header.pack(fill="x", padx=14, pady=(14, 6))

        tk.Label(header, text=APP_TITLE, bg=BG, fg=TEXT, font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(
            header,
            text="Случайные клавиши, движение мыши, автокликер, макросы и профили",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(2, 0))

    def build_profile_bar(self):
        card = self.make_card(self.content)
        card.pack(fill="x", padx=14, pady=(0, 10))

        self.make_title(card, "Профили").grid(row=0, column=0, columnspan=8, sticky="w", padx=14, pady=(12, 6))

        self.make_text(card, "Имя профиля").grid(row=1, column=0, sticky="w", padx=(14, 8), pady=(0, 8))
        self.profile_entry = self.make_entry(card, self.profile_name_var, width=24)
        self.profile_entry.grid(row=1, column=1, sticky="w", pady=(0, 8))

        self.make_button(card, "Сохранить", self.save_current_profile, width=12).grid(row=1, column=2, padx=6, pady=(0, 8))
        self.make_button(card, "Загрузить", self.load_selected_profile, width=12).grid(row=1, column=3, padx=6, pady=(0, 8))
        self.make_button(card, "Удалить", self.delete_selected_profile, width=12, bg="#a33a2f", fg="white").grid(row=1, column=4, padx=6, pady=(0, 8))
        self.make_button(card, "Экспорт", self.export_profiles, width=12).grid(row=1, column=5, padx=6, pady=(0, 8))
        self.make_button(card, "Импорт", self.import_profiles, width=12).grid(row=1, column=6, padx=6, pady=(0, 8))
        self.make_button(card, "PANIC STOP", self.panic_stop, width=14, bg=ERROR, fg="black").grid(row=1, column=7, padx=(6, 14), pady=(0, 8))

        self.profile_listbox = tk.Listbox(
            card,
            height=4,
            bg=INPUT_BG,
            fg=TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            selectbackground=ACCENT,
            selectforeground="black",
            font=("Segoe UI", 10)
        )
        self.profile_listbox.grid(row=2, column=0, columnspan=8, sticky="ew", padx=14, pady=(0, 12))
        self.profile_listbox.bind("<<ListboxSelect>>", self.on_profile_selected)

        for i in range(8):
            card.columnconfigure(i, weight=1)

    def build_tabs(self):
        notebook = ttk.Notebook(self.content)
        notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.random_tab = tk.Frame(notebook, bg=BG)
        self.clicker_tab = tk.Frame(notebook, bg=BG)
        self.macro_tab = tk.Frame(notebook, bg=BG)

        notebook.add(self.random_tab, text="Основное")
        notebook.add(self.clicker_tab, text="Автокликер")
        notebook.add(self.macro_tab, text="Макросы")

        self.build_random_tab()
        self.build_clicker_tab()
        self.build_macro_tab()

    def build_bottom_log(self):
        card = self.make_card(self.content)
        card.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        top = tk.Frame(card, bg=CARD)
        top.pack(fill="x", padx=14, pady=(12, 8))

        self.make_title(top, "Лог").pack(side="left")
        self.make_button(top, "Очистить лог", self.clear_log, width=12).pack(side="right")

        self.log_box = tk.Text(
            card,
            height=10,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            font=("Consolas", 10),
            state="disabled"
        )
        self.log_box.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    # =========================
    # RANDOM TAB
    # =========================
    def build_random_tab(self):
        card = self.make_card(self.random_tab)
        card.pack(fill="both", expand=True, padx=14, pady=14)

        self.make_title(card, "Случайные клавиши и движение мыши").grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(14, 4))
        self.make_text(card, "Настрой случайные клавиши, интервалы мыши и горячие кнопки").grid(row=1, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 14))

        self.make_check(card, "Клавиатура", self.random_use_keyboard).grid(row=2, column=0, sticky="w", padx=14, pady=4)
        self.make_check(card, "Мышь", self.random_use_mouse).grid(row=2, column=1, sticky="w", padx=14, pady=4)

        self.make_text(card, "Клавиши через запятую").grid(row=3, column=0, sticky="w", padx=14, pady=(12, 4))
        self.make_entry(card, self.random_keys, 30).grid(row=4, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 10))

        self.make_text(card, "Удержание клавиши (сек)").grid(row=5, column=0, sticky="w", padx=14, pady=(6, 4))
        self.make_entry(card, self.random_key_hold).grid(row=6, column=0, sticky="ew", padx=14, pady=(0, 10))

        self.make_text(card, "Пауза между клавишами (сек)").grid(row=5, column=1, sticky="w", padx=14, pady=(6, 4))
        self.make_entry(card, self.random_key_pause).grid(row=6, column=1, sticky="ew", padx=14, pady=(0, 10))

        self.make_text(card, "Мин. интервал мыши (сек)").grid(row=7, column=0, sticky="w", padx=14, pady=(6, 4))
        self.make_entry(card, self.random_mouse_interval_min).grid(row=8, column=0, sticky="ew", padx=14, pady=(0, 10))

        self.make_text(card, "Макс. интервал мыши (сек)").grid(row=7, column=1, sticky="w", padx=14, pady=(6, 4))
        self.make_entry(card, self.random_mouse_interval_max).grid(row=8, column=1, sticky="ew", padx=14, pady=(0, 10))

        self.make_text(card, "Мин. движение мыши").grid(row=9, column=0, sticky="w", padx=14, pady=(6, 4))
        self.make_entry(card, self.random_mouse_move_min).grid(row=10, column=0, sticky="ew", padx=14, pady=(0, 10))

        self.make_text(card, "Макс. движение мыши").grid(row=9, column=1, sticky="w", padx=14, pady=(6, 4))
        self.make_entry(card, self.random_mouse_move_max).grid(row=10, column=1, sticky="ew", padx=14, pady=(0, 10))

        self.make_text(card, "Горячая клавиша старта").grid(row=11, column=0, sticky="w", padx=14, pady=(8, 4))
        self.KeyBindBox(self, card, self.random_start_hotkey, width=18).grid(row=12, column=0, sticky="w", padx=14, pady=(0, 10))

        self.make_text(card, "Горячая клавиша стопа").grid(row=11, column=1, sticky="w", padx=14, pady=(8, 4))
        self.KeyBindBox(self, card, self.random_stop_hotkey, width=18).grid(row=12, column=1, sticky="w", padx=14, pady=(0, 10))

        tk.Label(card, textvariable=self.status_global, bg=CARD, fg=ACCENT, font=("Segoe UI", 10, "bold")).grid(
            row=13, column=0, columnspan=2, sticky="w", padx=14, pady=(6, 10)
        )

        btns = tk.Frame(card, bg=CARD)
        btns.grid(row=14, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 14))
        self.make_button(btns, "Старт", self.start_random_module).pack(side="left", padx=(0, 8))
        self.make_button(btns, "Стоп", self.stop_random_module).pack(side="left")

        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)

    # =========================
    # CLICKER TAB
    # =========================
    def build_clicker_tab(self):
        card = self.make_card(self.clicker_tab)
        card.pack(fill="both", expand=True, padx=14, pady=14)

        self.make_title(card, "Автокликер").grid(row=0, column=0, columnspan=4, sticky="w", padx=14, pady=(14, 4))
        self.make_text(card, "Мышь, клавиатура, интервалы, повторы, удержание и координаты").grid(row=1, column=0, columnspan=4, sticky="w", padx=14, pady=(0, 14))

        # Mode
        self.make_text(card, "Режим нажатия").grid(row=2, column=0, sticky="w", padx=14, pady=(6, 4))
        mode_wrap = tk.Frame(card, bg=CARD)
        mode_wrap.grid(row=3, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 10))
        self.make_radio(mode_wrap, "Мышь", self.clicker_mode, "mouse", self.refresh_clicker_mode).pack(side="left", padx=(0, 10))
        self.make_radio(mode_wrap, "Клавиатура", self.clicker_mode, "keyboard", self.refresh_clicker_mode).pack(side="left")

        self.make_text(card, "Тип действия").grid(row=2, column=2, sticky="w", padx=14, pady=(6, 4))
        self.make_option(card, self.clicker_action_type, ["single", "double", "triple", "hold"], width=12).grid(
            row=3, column=2, sticky="w", padx=14, pady=(0, 10)
        )

        self.make_text(card, "Удержание (сек) для hold").grid(row=2, column=3, sticky="w", padx=14, pady=(6, 4))
        self.make_entry(card, self.clicker_hold_time).grid(row=3, column=3, sticky="ew", padx=14, pady=(0, 10))

        # Mouse / Keyboard choice
        self.clicker_mouse_frame = tk.Frame(card, bg=CARD)
        self.clicker_mouse_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 10))
        self.make_text(self.clicker_mouse_frame, "Кнопка мыши").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.make_option(self.clicker_mouse_frame, self.clicker_mouse_button, ["left", "middle", "right"], width=10).grid(row=1, column=0, sticky="w")

        self.clicker_key_frame = tk.Frame(card, bg=CARD)
        self.clicker_key_frame.grid(row=4, column=2, columnspan=2, sticky="ew", padx=14, pady=(0, 10))
        self.make_text(self.clicker_key_frame, "Клавиша клавиатуры").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.KeyBindBox(self, self.clicker_key_frame, self.clicker_keyboard_key, width=18).grid(row=1, column=0, sticky="w")

        # Interval section
        self.make_text(card, "Режим интервала").grid(row=5, column=0, sticky="w", padx=14, pady=(6, 4))
        interval_mode_wrap = tk.Frame(card, bg=CARD)
        interval_mode_wrap.grid(row=6, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 10))
        self.make_radio(interval_mode_wrap, "Фиксированный", self.clicker_interval_mode, "fixed", self.refresh_clicker_interval_mode).pack(side="left", padx=(0, 10))
        self.make_radio(interval_mode_wrap, "Случайный", self.clicker_interval_mode, "random", self.refresh_clicker_interval_mode).pack(side="left")

        self.fixed_interval_frame = tk.Frame(card, bg=CARD)
        self.fixed_interval_frame.grid(row=7, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 10))
        self.make_text(self.fixed_interval_frame, "Интервал").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.make_entry(self.fixed_interval_frame, self.clicker_interval_value, width=12).grid(row=1, column=0, sticky="w")
        self.make_option(self.fixed_interval_frame, self.clicker_interval_unit, ["ms", "sec"], width=6).grid(row=1, column=1, sticky="w", padx=8)

        self.random_interval_frame = tk.Frame(card, bg=CARD)
        self.random_interval_frame.grid(row=7, column=2, columnspan=2, sticky="w", padx=14, pady=(0, 10))
        self.make_text(self.random_interval_frame, "Интервал от / до").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 4))
        self.make_entry(self.random_interval_frame, self.clicker_interval_min, width=10).grid(row=1, column=0, sticky="w")
        self.make_entry(self.random_interval_frame, self.clicker_interval_max, width=10).grid(row=1, column=1, sticky="w", padx=8)
        self.make_option(self.random_interval_frame, self.clicker_interval_random_unit, ["ms", "sec"], width=6).grid(row=1, column=2, sticky="w")

        # Repeats
        self.make_text(card, "Повторы").grid(row=8, column=0, sticky="w", padx=14, pady=(6, 4))
        rep_wrap = tk.Frame(card, bg=CARD)
        rep_wrap.grid(row=9, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 10))
        self.make_radio(rep_wrap, "Бесконечно", self.clicker_repeat_mode, "infinite").pack(side="left", padx=(0, 10))
        self.make_radio(rep_wrap, "Количество", self.clicker_repeat_mode, "count").pack(side="left")

        self.make_text(card, "Сколько раз").grid(row=8, column=2, sticky="w", padx=14, pady=(6, 4))
        self.make_entry(card, self.clicker_repeat_count).grid(row=9, column=2, sticky="ew", padx=14, pady=(0, 10))

        # Target
        self.make_text(card, "Точка клика").grid(row=10, column=0, sticky="w", padx=14, pady=(6, 4))
        target_wrap = tk.Frame(card, bg=CARD)
        target_wrap.grid(row=11, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 10))
        self.make_radio(target_wrap, "Текущая позиция", self.clicker_target_mode, "current").pack(side="left", padx=(0, 10))
        self.make_radio(target_wrap, "Координаты", self.clicker_target_mode, "coords").pack(side="left")

        self.make_text(card, "X").grid(row=10, column=2, sticky="w", padx=14, pady=(6, 4))
        self.make_text(card, "Y").grid(row=10, column=3, sticky="w", padx=14, pady=(6, 4))
        self.make_entry(card, self.clicker_target_x).grid(row=11, column=2, sticky="ew", padx=14, pady=(0, 10))
        self.make_entry(card, self.clicker_target_y).grid(row=11, column=3, sticky="ew", padx=14, pady=(0, 10))

        target_btns = tk.Frame(card, bg=CARD)
        target_btns.grid(row=12, column=2, columnspan=2, sticky="w", padx=14, pady=(0, 10))
        self.make_button(target_btns, "Взять курсор", self.capture_current_cursor_position, width=12).pack(side="left")

        # Hotkeys
        self.make_text(card, "Горячая клавиша старта").grid(row=13, column=0, sticky="w", padx=14, pady=(6, 4))
        self.KeyBindBox(self, card, self.clicker_start_hotkey, width=18).grid(row=14, column=0, sticky="w", padx=14, pady=(0, 10))

        self.make_text(card, "Горячая клавиша стопа").grid(row=13, column=1, sticky="w", padx=14, pady=(6, 4))
        self.KeyBindBox(self, card, self.clicker_stop_hotkey, width=18).grid(row=14, column=1, sticky="w", padx=14, pady=(0, 10))

        self.make_text(card, "Сделано нажатий").grid(row=13, column=2, sticky="w", padx=14, pady=(6, 4))
        tk.Label(card, textvariable=self.clicker_count_done, bg=INPUT_BG, fg=SUCCESS, font=("Segoe UI", 11, "bold"),
                 padx=10, pady=8, highlightthickness=1, highlightbackground=BORDER).grid(
            row=14, column=2, sticky="w", padx=14, pady=(0, 10)
        )

        tk.Label(card, textvariable=self.clicker_status, bg=CARD, fg=ACCENT, font=("Segoe UI", 10, "bold")).grid(
            row=15, column=0, columnspan=4, sticky="w", padx=14, pady=(6, 10)
        )

        btns = tk.Frame(card, bg=CARD)
        btns.grid(row=16, column=0, columnspan=4, sticky="w", padx=14, pady=(0, 14))
        self.make_button(btns, "Старт", self.start_clicker).pack(side="left", padx=(0, 8))
        self.make_button(btns, "Стоп", self.stop_clicker).pack(side="left", padx=(0, 8))
        self.make_button(btns, "Сброс счётчика", self.reset_click_counter, width=14).pack(side="left")

        for i in range(4):
            card.columnconfigure(i, weight=1)

        self.refresh_clicker_mode()
        self.refresh_clicker_interval_mode()

    def refresh_clicker_mode(self):
        pass

    def refresh_clicker_interval_mode(self):
        pass

    def capture_current_cursor_position(self):
        x, y = get_pointer_position(self.root)
        self.clicker_target_x.set(str(x))
        self.clicker_target_y.set(str(y))
        self.log(f"Захвачены координаты: {x}, {y}")

    def reset_click_counter(self):
        self.clicker_count_done.set("0")
        self.log("Счётчик кликов сброшен")

    # =========================
    # MACRO TAB
    # =========================
    def build_macro_tab(self):
        card = self.make_card(self.macro_tab)
        card.pack(fill="both", expand=True, padx=14, pady=14)

        self.make_title(card, "Макросы").grid(row=0, column=0, columnspan=4, sticky="w", padx=14, pady=(14, 4))
        self.make_text(card, "Один шаг на строку. Примеры команд ниже.").grid(row=1, column=0, columnspan=4, sticky="w", padx=14, pady=(0, 12))

        help_text = (
            "Команды:\n"
            "WAIT 500\n"
            "KEY space\n"
            "TEXT hello world\n"
            "CLICK left\n"
            "DOUBLECLICK left\n"
            "MOVE 500 300\n"
            "HOLDKEY e 1.0\n"
            "HOLDMOUSE left 0.4"
        )

        help_box = tk.Text(
            card,
            height=7,
            bg=INPUT_BG,
            fg=MUTED,
            insertbackground=TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            font=("Consolas", 10)
        )
        help_box.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=14, pady=(0, 10))
        help_box.insert("1.0", help_text)
        help_box.configure(state="disabled")

        self.macro_editor = tk.Text(
            card,
            height=14,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            font=("Consolas", 10)
        )
        self.macro_editor.grid(row=2, column=2, columnspan=2, sticky="nsew", padx=14, pady=(0, 10))
        self.macro_editor.insert(
            "1.0",
            "WAIT 500\nKEY space\nWAIT 300\nCLICK left\nWAIT 300\nDOUBLECLICK left\n"
        )

        self.make_text(card, "Повтор").grid(row=3, column=0, sticky="w", padx=14, pady=(6, 4))
        rep_wrap = tk.Frame(card, bg=CARD)
        rep_wrap.grid(row=4, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 10))
        self.make_radio(rep_wrap, "1 раз", self.macro_repeat_mode, "1").pack(side="left", padx=(0, 10))
        self.make_radio(rep_wrap, "Бесконечно", self.macro_repeat_mode, "infinite").pack(side="left", padx=(0, 10))
        self.make_radio(rep_wrap, "Количество", self.macro_repeat_mode, "count").pack(side="left")

        self.make_text(card, "Сколько раз").grid(row=3, column=2, sticky="w", padx=14, pady=(6, 4))
        self.make_entry(card, self.macro_repeat_count).grid(row=4, column=2, sticky="ew", padx=14, pady=(0, 10))

        self.make_text(card, "Горячая клавиша старта").grid(row=5, column=0, sticky="w", padx=14, pady=(6, 4))
        self.KeyBindBox(self, card, self.macro_start_hotkey, width=18).grid(row=6, column=0, sticky="w", padx=14, pady=(0, 10))

        self.make_text(card, "Горячая клавиша стопа").grid(row=5, column=1, sticky="w", padx=14, pady=(6, 4))
        self.KeyBindBox(self, card, self.macro_stop_hotkey, width=18).grid(row=6, column=1, sticky="w", padx=14, pady=(0, 10))

        tk.Label(card, textvariable=self.macro_status, bg=CARD, fg=ACCENT, font=("Segoe UI", 10, "bold")).grid(
            row=7, column=0, columnspan=4, sticky="w", padx=14, pady=(6, 10)
        )

        btns = tk.Frame(card, bg=CARD)
        btns.grid(row=8, column=0, columnspan=4, sticky="w", padx=14, pady=(0, 14))
        self.make_button(btns, "Старт макроса", self.start_macro, width=14).pack(side="left", padx=(0, 8))
        self.make_button(btns, "Стоп макроса", self.stop_macro, width=14).pack(side="left", padx=(0, 8))
        self.make_button(btns, "Сохранить макрос в txt", self.export_macro_text, width=18).pack(side="left")

        for i in range(4):
            card.columnconfigure(i, weight=1)
        card.rowconfigure(2, weight=1)

    # =========================
    # RANDOM WORKER
    # =========================
    def random_keyboard_worker(self, keys_list, hold_time, pause_time):
        while self.running_random:
            key = random.choice(keys_list)
            try:
                pydirectinput.keyDown(key)
                self.log(f"Случайная клавиша: {key}")
                start = time.time()
                while self.running_random and time.time() - start < hold_time:
                    time.sleep(0.01)
                pydirectinput.keyUp(key)
            except Exception as e:
                self.log(f"Ошибка клавиши {key}: {e}")
                try:
                    pydirectinput.keyUp(key)
                except Exception:
                    pass

            pause_start = time.time()
            while self.running_random and time.time() - pause_start < pause_time:
                time.sleep(0.01)

    def random_mouse_worker(self, interval_min, interval_max, move_min, move_max):
        next_move = time.time() + random.uniform(interval_min, interval_max)
        while self.running_random:
            if time.time() >= next_move:
                dx = random.randint(move_min, move_max) * random.choice([-1, 1])
                dy = random.randint(move_min, move_max) * random.choice([-1, 1])
                try:
                    pydirectinput.moveRel(dx, dy, duration=0)
                    self.log(f"Движение мыши: dx={dx}, dy={dy}")
                except Exception as e:
                    self.log(f"Ошибка движения мыши: {e}")
                next_move = time.time() + random.uniform(interval_min, interval_max)
            time.sleep(0.01)

    def start_random_module(self):
        if self.running_random:
            self.status_global.set("Уже запущено")
            return

        use_keyboard = self.random_use_keyboard.get()
        use_mouse = self.random_use_mouse.get()

        if not use_keyboard and not use_mouse:
            self.status_global.set("Включи клавиатуру или мышь")
            return

        keys_list = parse_keys_csv(self.random_keys.get())
        if use_keyboard and not keys_list:
            self.status_global.set("Укажи клавиши")
            return

        hold_time = parse_float(self.random_key_hold.get())
        pause_time = parse_float(self.random_key_pause.get())
        interval_min = parse_float(self.random_mouse_interval_min.get())
        interval_max = parse_float(self.random_mouse_interval_max.get())
        move_min = parse_int(self.random_mouse_move_min.get())
        move_max = parse_int(self.random_mouse_move_max.get())

        if hold_time is None or pause_time is None or interval_min is None or interval_max is None:
            self.status_global.set("Проверь числовые значения")
            return
        if move_min is None or move_max is None:
            self.status_global.set("Проверь движение мыши")
            return
        if interval_min > interval_max:
            self.status_global.set("Мин. интервал больше макс.")
            return
        if move_min > move_max:
            self.status_global.set("Мин. движение больше макс.")
            return

        self.running_random = True
        self.status_global.set("Работает")
        self.log("Запущен модуль случайных клавиш/мыши")

        if use_keyboard:
            threading.Thread(
                target=self.random_keyboard_worker,
                args=(keys_list, hold_time, pause_time),
                daemon=True
            ).start()

        if use_mouse:
            threading.Thread(
                target=self.random_mouse_worker,
                args=(interval_min, interval_max, move_min, move_max),
                daemon=True
            ).start()

    def stop_random_module(self):
        if not self.running_random:
            self.status_global.set("Остановлено")
            return
        self.running_random = False
        self.status_global.set("Остановлено")
        self.release_all_inputs()
        self.log("Остановлен модуль случайных клавиш/мыши")

    # =========================
    # CLICKER LOGIC
    # =========================
    def get_clicker_interval_seconds(self):
        mode = self.clicker_interval_mode.get()

        if mode == "fixed":
            value = parse_float(self.clicker_interval_value.get())
            if value is None or value <= 0:
                return None
            unit = self.clicker_interval_unit.get()
            return value / 1000.0 if unit == "ms" else value

        vmin = parse_float(self.clicker_interval_min.get())
        vmax = parse_float(self.clicker_interval_max.get())
        if vmin is None or vmax is None or vmin <= 0 or vmax <= 0 or vmin > vmax:
            return None
        unit = self.clicker_interval_random_unit.get()
        factor = 1 / 1000.0 if unit == "ms" else 1.0
        return random.uniform(vmin * factor, vmax * factor)

    def get_click_target(self):
        mode = self.clicker_target_mode.get()
        if mode == "current":
            return None
        x = parse_int(self.clicker_target_x.get())
        y = parse_int(self.clicker_target_y.get())
        if x is None or y is None:
            return None
        return x, y

    def perform_clicker_action(self):
        mode = self.clicker_mode.get()
        action = self.clicker_action_type.get()
        hold_time = parse_float(self.clicker_hold_time.get(), 0.3)

        target = self.get_click_target()
        if self.clicker_target_mode.get() == "coords":
            if target is None:
                raise ValueError("Неверные координаты")
            pydirectinput.moveTo(target[0], target[1], duration=0)

        if mode == "mouse":
            btn = self.clicker_mouse_button.get()
            if action == "single":
                pydirectinput.click(button=btn)
            elif action == "double":
                pydirectinput.click(button=btn, clicks=2, interval=0.05)
            elif action == "triple":
                pydirectinput.click(button=btn, clicks=3, interval=0.05)
            elif action == "hold":
                pydirectinput.mouseDown(button=btn)
                time.sleep(max(0.01, hold_time))
                pydirectinput.mouseUp(button=btn)
        else:
            key = self.clicker_keyboard_key.get().strip().lower()
            if not key:
                raise ValueError("Не выбрана клавиша клавиатуры")
            if action == "single":
                pydirectinput.press(key)
            elif action == "double":
                pydirectinput.press(key)
                time.sleep(0.05)
                pydirectinput.press(key)
            elif action == "triple":
                pydirectinput.press(key)
                time.sleep(0.05)
                pydirectinput.press(key)
                time.sleep(0.05)
                pydirectinput.press(key)
            elif action == "hold":
                pydirectinput.keyDown(key)
                time.sleep(max(0.01, hold_time))
                pydirectinput.keyUp(key)

    def clicker_worker(self):
        self.clicker_status.set("Работает")
        count_done = 0

        limit = None
        if self.clicker_repeat_mode.get() == "count":
            limit = parse_int(self.clicker_repeat_count.get())
            if limit is None or limit <= 0:
                self.root.after(0, lambda: self.clicker_status.set("Неверное количество повторов"))
                self.running_clicker = False
                return

        self.log("Автокликер запущен")

        while self.running_clicker:
            if limit is not None and count_done >= limit:
                break

            try:
                self.perform_clicker_action()
                count_done += 1
                self.root.after(0, lambda c=count_done: self.clicker_count_done.set(str(c)))
                self.log(f"Автоклик: {count_done}")
            except Exception as e:
                self.log(f"Ошибка автокликера: {e}")
                break

            interval = self.get_clicker_interval_seconds()
            if interval is None or interval <= 0:
                self.log("Ошибка интервала автокликера")
                break

            slept = 0.0
            while self.running_clicker and slept < interval:
                step = min(0.01, interval - slept)
                time.sleep(max(0.001, step))
                slept += step

        self.running_clicker = False
        self.root.after(0, lambda: self.clicker_status.set("Остановлено"))
        self.log("Автокликер остановлен")

    def start_clicker(self):
        if self.running_clicker:
            self.clicker_status.set("Уже запущен")
            return

        if self.clicker_mode.get() == "keyboard" and not self.clicker_keyboard_key.get().strip():
            self.clicker_status.set("Выбери клавишу")
            return

        if self.clicker_target_mode.get() == "coords":
            if self.get_click_target() is None:
                self.clicker_status.set("Проверь координаты")
                return

        if self.get_clicker_interval_seconds() is None:
            self.clicker_status.set("Проверь интервал")
            return

        self.running_clicker = True
        self.clicker_status.set("Запуск...")
        self.clicker_thread = threading.Thread(target=self.clicker_worker, daemon=True)
        self.clicker_thread.start()

    def stop_clicker(self):
        if not self.running_clicker:
            self.clicker_status.set("Остановлено")
            return
        self.running_clicker = False
        self.clicker_status.set("Останавливается...")
        self.release_all_inputs()
        self.log("Остановка автокликера")

    # =========================
    # MACRO LOGIC
    # =========================
    def parse_macro_lines(self):
        text = self.macro_editor.get("1.0", "end").strip()
        lines = [line.strip() for line in text.splitlines()]
        return [line for line in lines if line and not line.startswith("#")]

    def execute_macro_line(self, line):
        parts = line.split()
        cmd = parts[0].upper()

        if cmd == "WAIT":
            if len(parts) < 2:
                raise ValueError("WAIT требует число")
            ms = parse_float(parts[1])
            if ms is None:
                raise ValueError("WAIT: неверное число")
            time.sleep(ms / 1000.0)
            return

        if cmd == "KEY":
            if len(parts) < 2:
                raise ValueError("KEY требует клавишу")
            pydirectinput.press(parts[1].lower())
            return

        if cmd == "TEXT":
            text_to_type = line[len("TEXT "):]
            pydirectinput.write(text_to_type, interval=0.02)
            return

        if cmd == "CLICK":
            if len(parts) < 2:
                raise ValueError("CLICK требует кнопку")
            pydirectinput.click(button=parts[1].lower())
            return

        if cmd == "DOUBLECLICK":
            if len(parts) < 2:
                raise ValueError("DOUBLECLICK требует кнопку")
            pydirectinput.click(button=parts[1].lower(), clicks=2, interval=0.05)
            return

        if cmd == "MOVE":
            if len(parts) < 3:
                raise ValueError("MOVE требует X Y")
            x = parse_int(parts[1])
            y = parse_int(parts[2])
            if x is None or y is None:
                raise ValueError("MOVE: неверные координаты")
            pydirectinput.moveTo(x, y, duration=0)
            return

        if cmd == "HOLDKEY":
            if len(parts) < 3:
                raise ValueError("HOLDKEY требует key time")
            key = parts[1].lower()
            sec = parse_float(parts[2])
            if sec is None:
                raise ValueError("HOLDKEY: неверное время")
            pydirectinput.keyDown(key)
            time.sleep(max(0.01, sec))
            pydirectinput.keyUp(key)
            return

        if cmd == "HOLDMOUSE":
            if len(parts) < 3:
                raise ValueError("HOLDMOUSE требует button time")
            btn = parts[1].lower()
            sec = parse_float(parts[2])
            if sec is None:
                raise ValueError("HOLDMOUSE: неверное время")
            pydirectinput.mouseDown(button=btn)
            time.sleep(max(0.01, sec))
            pydirectinput.mouseUp(button=btn)
            return

        raise ValueError(f"Неизвестная команда: {cmd}")

    def macro_worker(self):
        lines = self.parse_macro_lines()
        if not lines:
            self.root.after(0, lambda: self.macro_status.set("Макрос пуст"))
            self.running_macro = False
            return

        repeat_mode = self.macro_repeat_mode.get()
        repeat_count = 1

        if repeat_mode == "count":
            repeat_count = parse_int(self.macro_repeat_count.get())
            if repeat_count is None or repeat_count <= 0:
                self.root.after(0, lambda: self.macro_status.set("Неверное число повторов"))
                self.running_macro = False
                return
        elif repeat_mode == "infinite":
            repeat_count = None

        self.root.after(0, lambda: self.macro_status.set("Работает"))
        self.log("Макрос запущен")

        round_index = 0
        while self.running_macro:
            if repeat_count is not None and round_index >= repeat_count:
                break

            round_index += 1
            self.log(f"Макрос: цикл {round_index}")

            for line in lines:
                if not self.running_macro:
                    break
                try:
                    self.execute_macro_line(line)
                    self.log(f"Макрос: {line}")
                except Exception as e:
                    self.log(f"Ошибка макроса: {e}")
                    self.running_macro = False
                    break

        self.running_macro = False
        self.root.after(0, lambda: self.macro_status.set("Остановлено"))
        self.log("Макрос остановлен")

    def start_macro(self):
        if self.running_macro:
            self.macro_status.set("Уже запущен")
            return
        self.running_macro = True
        self.macro_status.set("Запуск...")
        self.macro_thread = threading.Thread(target=self.macro_worker, daemon=True)
        self.macro_thread.start()

    def stop_macro(self):
        if not self.running_macro:
            self.macro_status.set("Остановлено")
            return
        self.running_macro = False
        self.macro_status.set("Останавливается...")
        self.release_all_inputs()
        self.log("Остановка макроса")

    def export_macro_text(self):
        path = filedialog.asksaveasfilename(
            title="Сохранить макрос",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        text = self.macro_editor.get("1.0", "end")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        self.log(f"Макрос сохранён: {path}")

    # =========================
    # HOTKEYS
    # =========================
    def start_hotkey_listener(self):
        if self.hotkey_listener_started:
            return
        self.hotkey_listener_started = True
        self.hotkey_thread = threading.Thread(target=self.hotkey_listener, daemon=True)
        self.hotkey_thread.start()

    def hotkey_listener(self):
        last_pressed = {}

        while True:
            try:
                if self.editing_hotkey or time.time() < self.hotkeys_blocked_until:
                    time.sleep(0.05)
                    continue

                checks = [
                    (self.random_start_hotkey.get().strip().lower(), self.start_random_module),
                    (self.random_stop_hotkey.get().strip().lower(), self.stop_random_module),
                    (self.clicker_start_hotkey.get().strip().lower(), self.start_clicker),
                    (self.clicker_stop_hotkey.get().strip().lower(), self.stop_clicker),
                    (self.macro_start_hotkey.get().strip().lower(), self.start_macro),
                    (self.macro_stop_hotkey.get().strip().lower(), self.stop_macro),
                ]

                now = time.time()
                for key_name, action in checks:
                    if not key_name:
                        continue
                    if safe_is_pressed(key_name):
                        last = last_pressed.get(key_name, 0.0)
                        if now - last > 0.5:
                            self.root.after(0, action)
                            last_pressed[key_name] = now

            except Exception as e:
                self.log(f"Ошибка hotkey_listener: {e}")

            time.sleep(0.05)

    # =========================
    # PROFILE IO
    # =========================
    def collect_settings(self):
        return {
            "random_use_keyboard": self.random_use_keyboard.get(),
            "random_use_mouse": self.random_use_mouse.get(),
            "random_keys": self.random_keys.get(),
            "random_key_hold": self.random_key_hold.get(),
            "random_key_pause": self.random_key_pause.get(),
            "random_mouse_interval_min": self.random_mouse_interval_min.get(),
            "random_mouse_interval_max": self.random_mouse_interval_max.get(),
            "random_mouse_move_min": self.random_mouse_move_min.get(),
            "random_mouse_move_max": self.random_mouse_move_max.get(),
            "random_start_hotkey": self.random_start_hotkey.get(),
            "random_stop_hotkey": self.random_stop_hotkey.get(),

            "clicker_mode": self.clicker_mode.get(),
            "clicker_mouse_button": self.clicker_mouse_button.get(),
            "clicker_keyboard_key": self.clicker_keyboard_key.get(),
            "clicker_interval_mode": self.clicker_interval_mode.get(),
            "clicker_interval_value": self.clicker_interval_value.get(),
            "clicker_interval_unit": self.clicker_interval_unit.get(),
            "clicker_interval_min": self.clicker_interval_min.get(),
            "clicker_interval_max": self.clicker_interval_max.get(),
            "clicker_interval_random_unit": self.clicker_interval_random_unit.get(),
            "clicker_action_type": self.clicker_action_type.get(),
            "clicker_hold_time": self.clicker_hold_time.get(),
            "clicker_repeat_mode": self.clicker_repeat_mode.get(),
            "clicker_repeat_count": self.clicker_repeat_count.get(),
            "clicker_target_mode": self.clicker_target_mode.get(),
            "clicker_target_x": self.clicker_target_x.get(),
            "clicker_target_y": self.clicker_target_y.get(),
            "clicker_start_hotkey": self.clicker_start_hotkey.get(),
            "clicker_stop_hotkey": self.clicker_stop_hotkey.get(),

            "macro_text": self.macro_editor.get("1.0", "end"),
            "macro_repeat_mode": self.macro_repeat_mode.get(),
            "macro_repeat_count": self.macro_repeat_count.get(),
            "macro_start_hotkey": self.macro_start_hotkey.get(),
            "macro_stop_hotkey": self.macro_stop_hotkey.get(),
        }

    def apply_settings(self, data):
        self.random_use_keyboard.set(data.get("random_use_keyboard", True))
        self.random_use_mouse.set(data.get("random_use_mouse", True))
        self.random_keys.set(data.get("random_keys", "w,a,s,d"))
        self.random_key_hold.set(data.get("random_key_hold", "0.7"))
        self.random_key_pause.set(data.get("random_key_pause", "0.2"))
        self.random_mouse_interval_min.set(data.get("random_mouse_interval_min", "2.0"))
        self.random_mouse_interval_max.set(data.get("random_mouse_interval_max", "5.0"))
        self.random_mouse_move_min.set(data.get("random_mouse_move_min", "20"))
        self.random_mouse_move_max.set(data.get("random_mouse_move_max", "120"))
        self.random_start_hotkey.set(data.get("random_start_hotkey", "f8"))
        self.random_stop_hotkey.set(data.get("random_stop_hotkey", "f9"))

        self.clicker_mode.set(data.get("clicker_mode", "mouse"))
        self.clicker_mouse_button.set(data.get("clicker_mouse_button", "left"))
        self.clicker_keyboard_key.set(data.get("clicker_keyboard_key", "space"))
        self.clicker_interval_mode.set(data.get("clicker_interval_mode", "fixed"))
        self.clicker_interval_value.set(data.get("clicker_interval_value", "50"))
        self.clicker_interval_unit.set(data.get("clicker_interval_unit", "ms"))
        self.clicker_interval_min.set(data.get("clicker_interval_min", "30"))
        self.clicker_interval_max.set(data.get("clicker_interval_max", "80"))
        self.clicker_interval_random_unit.set(data.get("clicker_interval_random_unit", "ms"))
        self.clicker_action_type.set(data.get("clicker_action_type", "single"))
        self.clicker_hold_time.set(data.get("clicker_hold_time", "0.3"))
        self.clicker_repeat_mode.set(data.get("clicker_repeat_mode", "infinite"))
        self.clicker_repeat_count.set(data.get("clicker_repeat_count", "100"))
        self.clicker_target_mode.set(data.get("clicker_target_mode", "current"))
        self.clicker_target_x.set(data.get("clicker_target_x", "0"))
        self.clicker_target_y.set(data.get("clicker_target_y", "0"))
        self.clicker_start_hotkey.set(data.get("clicker_start_hotkey", "f6"))
        self.clicker_stop_hotkey.set(data.get("clicker_stop_hotkey", "f7"))

        self.macro_editor.delete("1.0", "end")
        self.macro_editor.insert("1.0", data.get("macro_text", "WAIT 500\nKEY space\n"))
        self.macro_repeat_mode.set(data.get("macro_repeat_mode", "1"))
        self.macro_repeat_count.set(data.get("macro_repeat_count", "3"))
        self.macro_start_hotkey.set(data.get("macro_start_hotkey", "f10"))
        self.macro_stop_hotkey.set(data.get("macro_stop_hotkey", "f11"))

    def save_profiles_to_disk(self):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.profiles, f, ensure_ascii=False, indent=2)

    def load_profiles_from_disk(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    self.profiles = json.load(f)
                self.log(f"Профили загружены из {SETTINGS_FILE}")
            except Exception as e:
                self.log(f"Ошибка загрузки профилей: {e}")
                self.profiles = {}
        else:
            self.profiles = {}

        if "default" not in self.profiles:
            self.profiles["default"] = self.collect_settings()
            self.save_profiles_to_disk()

        self.refresh_profile_list()
        self.profile_name_var.set("default")
        self.apply_settings(self.profiles["default"])

    def refresh_profile_list(self):
        self.profile_listbox.delete(0, "end")
        for name in sorted(self.profiles.keys()):
            self.profile_listbox.insert("end", name)

    def on_profile_selected(self, event=None):
        sel = self.profile_listbox.curselection()
        if not sel:
            return
        name = self.profile_listbox.get(sel[0])
        self.profile_name_var.set(name)

    def save_current_profile(self):
        name = self.profile_name_var.get().strip()
        if not name:
            messagebox.showwarning(APP_TITLE, "Укажи имя профиля")
            return
        self.profiles[name] = self.collect_settings()
        self.save_profiles_to_disk()
        self.refresh_profile_list()
        self.log(f"Профиль сохранён: {name}")

    def load_selected_profile(self):
        name = self.profile_name_var.get().strip()
        if not name:
            messagebox.showwarning(APP_TITLE, "Укажи имя профиля")
            return
        if name not in self.profiles:
            messagebox.showwarning(APP_TITLE, f"Профиль '{name}' не найден")
            return
        self.apply_settings(self.profiles[name])
        self.log(f"Профиль загружен: {name}")

    def delete_selected_profile(self):
        name = self.profile_name_var.get().strip()
        if not name:
            return
        if name == "default":
            messagebox.showwarning(APP_TITLE, "Профиль default удалять нельзя")
            return
        if name in self.profiles:
            del self.profiles[name]
            self.save_profiles_to_disk()
            self.refresh_profile_list()
            self.profile_name_var.set("default")
            self.log(f"Профиль удалён: {name}")

    def export_profiles(self):
        path = filedialog.asksaveasfilename(
            title="Экспорт профилей",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.profiles, f, ensure_ascii=False, indent=2)
        self.log(f"Профили экспортированы: {path}")

    def import_profiles(self):
        path = filedialog.askopenfilename(
            title="Импорт профилей",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                self.profiles.update(data)
                self.save_profiles_to_disk()
                self.refresh_profile_list()
                self.log(f"Профили импортированы: {path}")
            else:
                messagebox.showerror(APP_TITLE, "Файл не содержит словарь профилей")
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Ошибка импорта:\n{e}")

    # =========================
    # STOP ALL
    # =========================
    def release_all_inputs(self):
        keys_to_release = [
            "w", "a", "s", "d", "space", "shift", "ctrl", "alt", "tab",
            "enter", "q", "e", "r", "f", "1", "2", "3", "4", "5"
        ]
        for key in keys_to_release:
            try:
                pydirectinput.keyUp(key)
            except Exception:
                pass

        for btn in ["left", "middle", "right"]:
            try:
                pydirectinput.mouseUp(button=btn)
            except Exception:
                pass

    def panic_stop(self):
        self.running_random = False
        self.running_clicker = False
        self.running_macro = False
        self.status_global.set("Остановлено")
        self.clicker_status.set("Остановлено")
        self.macro_status.set("Остановлено")
        self.release_all_inputs()
        self.log("PANIC STOP: все модули остановлены")


# =========================
# START
# =========================
def main():
    root = tk.Tk()
    app = SFToolKeyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()