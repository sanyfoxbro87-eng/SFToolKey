
import json
import os
import random
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import keyboard
import pydirectinput

APP_TITLE = "SFToolKey"
SETTINGS_FILE = "sftoolkey_profiles.json"

pydirectinput.FAILSAFE = False
pydirectinput.PAUSE = 0.0

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
ERROR = "#ff6b6b"
WAIT_BG = "#3a2a16"

I18N = {
    "ru": {
        "title": "SFToolKey",
        "subtitle": "Случайные клавиши, движение мыши, автокликер, макросы и профили",
        "profiles": "Профили",
        "profile_name": "Имя профиля",
        "save": "Сохранить",
        "load": "Загрузить",
        "delete": "Удалить",
        "export": "Экспорт",
        "import": "Импорт",
        "panic": "PANIC STOP",
        "main_tab": "Основное",
        "clicker_tab": "Автокликер",
        "macro_tab": "Макросы",
        "log": "Лог",
        "clear_log": "Очистить лог",
        "status_stopped": "Остановлено",
        "status_running": "Работает",
        "status_starting": "Запуск...",
        "status_stopping": "Останавливается...",
        "already_running": "Уже запущено",
        "enable_kb_mouse": "Включи клавиатуру или мышь",
        "check_numbers": "Проверь числовые значения",
        "keys_prompt": "Укажи клавиши",
        "random_title": "Случайные клавиши и движение мыши",
        "random_subtitle": "Настрой случайные клавиши, интервалы мыши и горячие кнопки",
        "keyboard": "Клавиатура",
        "mouse": "Мышь",
        "keys_csv": "Клавиши через запятую",
        "key_hold_sec": "Удержание клавиши (сек)",
        "key_pause_sec": "Пауза между клавишами (сек)",
        "mouse_interval_min_sec": "Мин. интервал мыши (сек)",
        "mouse_interval_max_sec": "Макс. интервал мыши (сек)",
        "mouse_move_min": "Мин. движение мыши",
        "mouse_move_max": "Макс. движение мыши",
        "hotkey_start": "Горячая клавиша старта",
        "hotkey_stop": "Горячая клавиша стопа",
        "start": "Старт",
        "stop": "Стоп",
        "press_key": "Нажми клавишу...",
        "clicker_title": "Автокликер",
        "clicker_subtitle": "Мышь, клавиатура, интервалы, повторы, удержание и координаты",
        "click_mode": "Режим нажатия",
        "action_type": "Тип действия",
        "hold_sec": "Удержание (сек) для hold",
        "mouse_button": "Кнопка мыши",
        "keyboard_key": "Клавиша клавиатуры",
        "interval_mode": "Режим интервала",
        "fixed": "Фиксированный",
        "random": "Случайный",
        "interval": "Интервал",
        "interval_from_to": "Интервал от / до",
        "repeats": "Повторы",
        "infinite": "Бесконечно",
        "count": "Количество",
        "count_label": "Сколько раз",
        "target_point": "Точка клика",
        "current_pos": "Текущая позиция",
        "coords": "Координаты",
        "capture_cursor": "Взять курсор",
        "done_clicks": "Сделано нажатий",
        "reset_counter": "Сброс счётчика",
        "choose_key": "Выбери клавишу",
        "check_interval": "Проверь интервал",
        "check_coords": "Проверь координаты",
        "macro_title": "Макросы",
        "macro_subtitle": "Один шаг на строку. Примеры команд ниже.",
        "repeat": "Повтор",
        "once": "1 раз",
        "start_macro": "Старт макроса",
        "stop_macro": "Стоп макроса",
        "save_macro_txt": "Сохранить макрос в txt",
        "lang": "Язык",
        "ru": "Русский",
        "en": "English",
    },
    "en": {
        "title": "SFToolKey",
        "subtitle": "Random keys, mouse movement, autoclicker, macros and profiles",
        "profiles": "Profiles",
        "profile_name": "Profile name",
        "save": "Save",
        "load": "Load",
        "delete": "Delete",
        "export": "Export",
        "import": "Import",
        "panic": "PANIC STOP",
        "main_tab": "Main",
        "clicker_tab": "Autoclicker",
        "macro_tab": "Macros",
        "log": "Log",
        "clear_log": "Clear log",
        "status_stopped": "Stopped",
        "status_running": "Running",
        "status_starting": "Starting...",
        "status_stopping": "Stopping...",
        "already_running": "Already running",
        "enable_kb_mouse": "Enable keyboard or mouse",
        "check_numbers": "Check numeric values",
        "keys_prompt": "Enter keys",
        "random_title": "Random keys and mouse movement",
        "random_subtitle": "Configure random keys, mouse intervals and hotkeys",
        "keyboard": "Keyboard",
        "mouse": "Mouse",
        "keys_csv": "Keys separated by commas",
        "key_hold_sec": "Key hold time (sec)",
        "key_pause_sec": "Pause between keys (sec)",
        "mouse_interval_min_sec": "Min mouse interval (sec)",
        "mouse_interval_max_sec": "Max mouse interval (sec)",
        "mouse_move_min": "Min mouse movement",
        "mouse_move_max": "Max mouse movement",
        "hotkey_start": "Start hotkey",
        "hotkey_stop": "Stop hotkey",
        "start": "Start",
        "stop": "Stop",
        "press_key": "Press a key...",
        "clicker_title": "Autoclicker",
        "clicker_subtitle": "Mouse, keyboard, intervals, repeats, hold and coordinates",
        "click_mode": "Input mode",
        "action_type": "Action type",
        "hold_sec": "Hold time (sec) for hold",
        "mouse_button": "Mouse button",
        "keyboard_key": "Keyboard key",
        "interval_mode": "Interval mode",
        "fixed": "Fixed",
        "random": "Random",
        "interval": "Interval",
        "interval_from_to": "Interval from / to",
        "repeats": "Repeats",
        "infinite": "Infinite",
        "count": "Count",
        "count_label": "How many times",
        "target_point": "Click target",
        "current_pos": "Current position",
        "coords": "Coordinates",
        "capture_cursor": "Capture cursor",
        "done_clicks": "Clicks done",
        "reset_counter": "Reset counter",
        "choose_key": "Choose a key",
        "check_interval": "Check interval",
        "check_coords": "Check coordinates",
        "macro_title": "Macros",
        "macro_subtitle": "One step per line. Examples below.",
        "repeat": "Repeat",
        "once": "1 time",
        "start_macro": "Start macro",
        "stop_macro": "Stop macro",
        "save_macro_txt": "Save macro to txt",
        "lang": "Language",
        "ru": "Русский",
        "en": "English",
    }
}


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


class SFToolKeyApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("980x860")
        self.root.minsize(900, 720)
        self.root.configure(bg=BG)

        self.running_random = False
        self.running_clicker = False
        self.running_macro = False
        self.editing_hotkey = False
        self.hotkeys_blocked_until = 0.0
        self.hotkey_listener_started = False
        self.profiles = {}

        self.lang = tk.StringVar(value="ru")
        self.profile_name_var = tk.StringVar(value="default")

        self.build_vars()
        self.apply_ttk_style()
        self.build_gui()
        self.load_profiles_from_disk()
        self.start_hotkey_listener()
        self.log("Started")

    def tr(self, key):
        lang = self.lang.get()
        return I18N.get(lang, I18N["ru"]).get(key, key)

    def build_vars(self):
        self.status_global = tk.StringVar(value="")
        self.clicker_status = tk.StringVar(value="")
        self.macro_status = tk.StringVar(value="")

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

        self.clicker_mode = tk.StringVar(value="mouse")
        self.clicker_mouse_button = tk.StringVar(value="left")
        self.clicker_keyboard_key = tk.StringVar(value="space")
        self.clicker_interval_mode = tk.StringVar(value="fixed")
        self.clicker_interval_value = tk.StringVar(value="50")
        self.clicker_interval_unit = tk.StringVar(value="ms")
        self.clicker_interval_min = tk.StringVar(value="30")
        self.clicker_interval_max = tk.StringVar(value="80")
        self.clicker_interval_random_unit = tk.StringVar(value="ms")
        self.clicker_action_type = tk.StringVar(value="single")
        self.clicker_hold_time = tk.StringVar(value="0.3")
        self.clicker_repeat_mode = tk.StringVar(value="infinite")
        self.clicker_repeat_count = tk.StringVar(value="100")
        self.clicker_target_mode = tk.StringVar(value="current")
        self.clicker_target_x = tk.StringVar(value="0")
        self.clicker_target_y = tk.StringVar(value="0")
        self.clicker_start_hotkey = tk.StringVar(value="f6")
        self.clicker_stop_hotkey = tk.StringVar(value="f7")
        self.clicker_count_done = tk.StringVar(value="0")

        self.macro_repeat_mode = tk.StringVar(value="1")
        self.macro_repeat_count = tk.StringVar(value="3")
        self.macro_start_hotkey = tk.StringVar(value="f10")
        self.macro_stop_hotkey = tk.StringVar(value="f11")

        self.set_stopped_statuses()

    def set_stopped_statuses(self):
        self.status_global.set(self.tr("status_stopped"))
        self.clicker_status.set(self.tr("status_stopped"))
        self.macro_status.set(self.tr("status_stopped"))

    def log(self, text):
        line = f"[{time.strftime('%H:%M:%S')}] {text}"
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

    def apply_ttk_style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=[8, 8, 8, 0])
        style.configure("TNotebook.Tab", background=CARD_2, foreground=TEXT, padding=[16, 10], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", ACCENT)], foreground=[("selected", "black")])

    def make_card(self, parent):
        return tk.Frame(parent, bg=CARD, highlightthickness=1, highlightbackground=BORDER)

    def make_title(self, parent, text):
        return tk.Label(parent, text=text, bg=CARD, fg=TEXT, font=("Segoe UI", 11, "bold"))

    def make_text(self, parent, text):
        return tk.Label(parent, text=text, bg=CARD, fg=MUTED, font=("Segoe UI", 10))

    def make_entry(self, parent, textvar=None, width=18):
        return tk.Entry(parent, textvariable=textvar, width=width, bg=INPUT_BG, fg=TEXT, insertbackground=TEXT,
                        relief="flat", highlightthickness=1, highlightbackground=BORDER, highlightcolor=ACCENT, font=("Segoe UI", 10))

    def make_button(self, parent, text, command, width=14, bg=ACCENT, fg="black"):
        return tk.Button(parent, text=text, command=command, width=width, bg=bg, fg=fg,
                         activebackground=ACCENT_HOVER if bg == ACCENT else bg, activeforeground=fg,
                         relief="flat", bd=0, font=("Segoe UI", 10, "bold"), cursor="hand2", padx=10, pady=8)

    def make_check(self, parent, text, variable):
        return tk.Checkbutton(parent, text=text, variable=variable, bg=CARD, fg=TEXT, activebackground=CARD,
                              activeforeground=TEXT, selectcolor=INPUT_BG, font=("Segoe UI", 10), cursor="hand2",
                              bd=0, highlightthickness=0)

    def make_radio(self, parent, text, variable, value):
        return tk.Radiobutton(parent, text=text, variable=variable, value=value, bg=CARD, fg=TEXT,
                              activebackground=CARD, activeforeground=TEXT, selectcolor=INPUT_BG,
                              font=("Segoe UI", 10), cursor="hand2", bd=0, highlightthickness=0)

    def make_option(self, parent, variable, values, width=12):
        menu = tk.OptionMenu(parent, variable, *values)
        menu.config(bg=INPUT_BG, fg=TEXT, activebackground=INPUT_ACTIVE, activeforeground=TEXT,
                    relief="flat", bd=0, highlightthickness=1, highlightbackground=BORDER, font=("Segoe UI", 10), width=width)
        menu["menu"].config(bg=INPUT_BG, fg=TEXT, activebackground=ACCENT, activeforeground="black", font=("Segoe UI", 10))
        return menu

    class KeyBindBox(tk.Label):
        def __init__(self, app, parent, variable, width=16):
            super().__init__(parent, textvariable=variable, width=width, bg=INPUT_BG, fg=TEXT, relief="flat", bd=0,
                             padx=12, pady=10, font=("Segoe UI", 10, "bold"), cursor="hand2",
                             highlightthickness=1, highlightbackground=BORDER)
            self.app = app
            self.variable = variable
            self.waiting = False
            self.bind("<Button-1>", self.start_capture)

        def start_capture(self, event=None):
            if self.waiting:
                return
            self.waiting = True
            self.app.editing_hotkey = True
            self.config(bg=WAIT_BG, highlightbackground=ACCENT)
            self.variable.set(self.app.tr("press_key"))
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
            self.waiting = False
            self.app.editing_hotkey = False
            self.config(bg=INPUT_BG, highlightbackground=BORDER)

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

        self.header = tk.Frame(self.content, bg=BG)
        self.header.pack(fill="x", padx=14, pady=(14, 6))
        self.title_label = tk.Label(self.header, bg=BG, fg=TEXT, font=("Segoe UI", 18, "bold"))
        self.title_label.pack(anchor="w")
        self.subtitle_label = tk.Label(self.header, bg=BG, fg=MUTED, font=("Segoe UI", 10))
        self.subtitle_label.pack(anchor="w", pady=(2, 0))

        langbar = tk.Frame(self.header, bg=BG)
        langbar.pack(anchor="e", pady=(4, 0))
        self.lang_label = tk.Label(langbar, bg=BG, fg=MUTED, font=("Segoe UI", 10))
        self.lang_label.pack(side="left", padx=(0, 8))
        self.lang_menu = self.make_option(langbar, self.lang, ["ru", "en"], width=8)
        self.lang_menu.pack(side="left")
        self.lang.trace_add("write", lambda *args: self.refresh_language())

        self.build_profile_bar()
        self.build_tabs()
        self.build_bottom_log()
        self.refresh_language()

    def build_profile_bar(self):
        self.profile_card = self.make_card(self.content)
        self.profile_card.pack(fill="x", padx=14, pady=(0, 10))

        self.profiles_title = self.make_title(self.profile_card, "")
        self.profiles_title.grid(row=0, column=0, columnspan=8, sticky="w", padx=14, pady=(12, 6))
        self.profile_name_label = self.make_text(self.profile_card, "")
        self.profile_name_label.grid(row=1, column=0, sticky="w", padx=(14, 8), pady=(0, 8))
        self.profile_entry = self.make_entry(self.profile_card, self.profile_name_var, width=24)
        self.profile_entry.grid(row=1, column=1, sticky="w", pady=(0, 8))
        self.save_profile_btn = self.make_button(self.profile_card, "", self.save_current_profile, width=12)
        self.save_profile_btn.grid(row=1, column=2, padx=6, pady=(0, 8))
        self.load_profile_btn = self.make_button(self.profile_card, "", self.load_selected_profile, width=12)
        self.load_profile_btn.grid(row=1, column=3, padx=6, pady=(0, 8))
        self.delete_profile_btn = self.make_button(self.profile_card, "", self.delete_selected_profile, width=12, bg="#a33a2f", fg="white")
        self.delete_profile_btn.grid(row=1, column=4, padx=6, pady=(0, 8))
        self.export_btn = self.make_button(self.profile_card, "", self.export_profiles, width=12)
        self.export_btn.grid(row=1, column=5, padx=6, pady=(0, 8))
        self.import_btn = self.make_button(self.profile_card, "", self.import_profiles, width=12)
        self.import_btn.grid(row=1, column=6, padx=6, pady=(0, 8))
        self.panic_btn = self.make_button(self.profile_card, "", self.panic_stop, width=14, bg=ERROR, fg="black")
        self.panic_btn.grid(row=1, column=7, padx=(6, 14), pady=(0, 8))

        self.profile_listbox = tk.Listbox(self.profile_card, height=4, bg=INPUT_BG, fg=TEXT, relief="flat",
                                          highlightthickness=1, highlightbackground=BORDER, selectbackground=ACCENT,
                                          selectforeground="black", font=("Segoe UI", 10))
        self.profile_listbox.grid(row=2, column=0, columnspan=8, sticky="ew", padx=14, pady=(0, 12))
        self.profile_listbox.bind("<<ListboxSelect>>", self.on_profile_selected)
        for i in range(8):
            self.profile_card.columnconfigure(i, weight=1)

    def build_tabs(self):
        self.notebook = ttk.Notebook(self.content)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.random_tab = tk.Frame(self.notebook, bg=BG)
        self.clicker_tab = tk.Frame(self.notebook, bg=BG)
        self.macro_tab = tk.Frame(self.notebook, bg=BG)

        self.notebook.add(self.random_tab, text="")
        self.notebook.add(self.clicker_tab, text="")
        self.notebook.add(self.macro_tab, text="")

        self.build_random_tab()
        self.build_clicker_tab()
        self.build_macro_tab()

    def build_bottom_log(self):
        self.log_card = self.make_card(self.content)
        self.log_card.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        top = tk.Frame(self.log_card, bg=CARD)
        top.pack(fill="x", padx=14, pady=(12, 8))
        self.log_title = self.make_title(top, "")
        self.log_title.pack(side="left")
        self.clear_log_btn = self.make_button(top, "", self.clear_log, width=12)
        self.clear_log_btn.pack(side="right")
        self.log_box = tk.Text(self.log_card, height=10, bg=INPUT_BG, fg=TEXT, insertbackground=TEXT, relief="flat",
                               highlightthickness=1, highlightbackground=BORDER, font=("Consolas", 10), state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    def build_random_tab(self):
        self.random_card = self.make_card(self.random_tab)
        self.random_card.pack(fill="both", expand=True, padx=14, pady=14)
        self.random_title = self.make_title(self.random_card, "")
        self.random_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(14, 4))
        self.random_subtitle = self.make_text(self.random_card, "")
        self.random_subtitle.grid(row=1, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 14))
        self.random_keyboard_check = self.make_check(self.random_card, "", self.random_use_keyboard)
        self.random_keyboard_check.grid(row=2, column=0, sticky="w", padx=14, pady=4)
        self.random_mouse_check = self.make_check(self.random_card, "", self.random_use_mouse)
        self.random_mouse_check.grid(row=2, column=1, sticky="w", padx=14, pady=4)
        self.random_labels = {}
        rows = [
            ("keys_csv", 3, 4, self.random_keys),
            ("key_hold_sec", 5, 6, self.random_key_hold),
            ("key_pause_sec", 5, 6, self.random_key_pause),
            ("mouse_interval_min_sec", 7, 8, self.random_mouse_interval_min),
            ("mouse_interval_max_sec", 7, 8, self.random_mouse_interval_max),
            ("mouse_move_min", 9, 10, self.random_mouse_move_min),
            ("mouse_move_max", 9, 10, self.random_mouse_move_max),
        ]
        positions = [(0,2),(0,1),(1,1),(0,1),(1,1),(0,1),(1,1)]
        for (key, lr, er, var), pos in zip(rows, positions):
            c = 0 if key in ("keys_csv","key_hold_sec","mouse_interval_min_sec","mouse_move_min") else 1
            lbl = self.make_text(self.random_card, "")
            lbl.grid(row=lr, column=c, sticky="w", padx=14, pady=(6 if lr!=3 else 12, 4))
            self.random_labels[key] = lbl
            ent = self.make_entry(self.random_card, var, 30 if key=="keys_csv" else 18)
            span = 2 if key=="keys_csv" else 1
            ent.grid(row=er, column=0 if key=="keys_csv" else c, columnspan=span, sticky="ew", padx=14, pady=(0, 10))
            self.random_labels[key+"_entry"] = ent
        self.random_hotkey_start_label = self.make_text(self.random_card, "")
        self.random_hotkey_start_label.grid(row=11, column=0, sticky="w", padx=14, pady=(8, 4))
        self.random_hotkey_start_box = self.KeyBindBox(self, self.random_card, self.random_start_hotkey, width=18)
        self.random_hotkey_start_box.grid(row=12, column=0, sticky="w", padx=14, pady=(0, 10))
        self.random_hotkey_stop_label = self.make_text(self.random_card, "")
        self.random_hotkey_stop_label.grid(row=11, column=1, sticky="w", padx=14, pady=(8, 4))
        self.random_hotkey_stop_box = self.KeyBindBox(self, self.random_card, self.random_stop_hotkey, width=18)
        self.random_hotkey_stop_box.grid(row=12, column=1, sticky="w", padx=14, pady=(0, 10))
        self.random_status_label = tk.Label(self.random_card, textvariable=self.status_global, bg=CARD, fg=ACCENT, font=("Segoe UI", 10, "bold"))
        self.random_status_label.grid(row=13, column=0, columnspan=2, sticky="w", padx=14, pady=(6, 10))
        btns = tk.Frame(self.random_card, bg=CARD)
        btns.grid(row=14, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 14))
        self.random_start_btn = self.make_button(btns, "", self.start_random_module)
        self.random_start_btn.pack(side="left", padx=(0, 8))
        self.random_stop_btn = self.make_button(btns, "", self.stop_random_module)
        self.random_stop_btn.pack(side="left")
        self.random_card.columnconfigure(0, weight=1)
        self.random_card.columnconfigure(1, weight=1)

    def build_clicker_tab(self):
        self.clicker_card = self.make_card(self.clicker_tab)
        self.clicker_card.pack(fill="both", expand=True, padx=14, pady=14)
        self.clicker_title_label = self.make_title(self.clicker_card, "")
        self.clicker_title_label.grid(row=0, column=0, columnspan=4, sticky="w", padx=14, pady=(14, 4))
        self.clicker_subtitle_label = self.make_text(self.clicker_card, "")
        self.clicker_subtitle_label.grid(row=1, column=0, columnspan=4, sticky="w", padx=14, pady=(0, 14))
        self.click_mode_label = self.make_text(self.clicker_card, "")
        self.click_mode_label.grid(row=2, column=0, sticky="w", padx=14, pady=(6, 4))
        mode_wrap = tk.Frame(self.clicker_card, bg=CARD)
        mode_wrap.grid(row=3, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 10))
        self.click_mouse_radio = self.make_radio(mode_wrap, "", self.clicker_mode, "mouse")
        self.click_mouse_radio.pack(side="left", padx=(0, 10))
        self.click_kb_radio = self.make_radio(mode_wrap, "", self.clicker_mode, "keyboard")
        self.click_kb_radio.pack(side="left")
        self.action_type_label = self.make_text(self.clicker_card, "")
        self.action_type_label.grid(row=2, column=2, sticky="w", padx=14, pady=(6, 4))
        self.action_menu = self.make_option(self.clicker_card, self.clicker_action_type, ["single", "double", "triple", "hold"], width=12)
        self.action_menu.grid(row=3, column=2, sticky="w", padx=14, pady=(0, 10))
        self.hold_label = self.make_text(self.clicker_card, "")
        self.hold_label.grid(row=2, column=3, sticky="w", padx=14, pady=(6, 4))
        self.hold_entry = self.make_entry(self.clicker_card, self.clicker_hold_time)
        self.hold_entry.grid(row=3, column=3, sticky="ew", padx=14, pady=(0, 10))
        self.mouse_button_label = self.make_text(self.clicker_card, "")
        self.mouse_button_label.grid(row=4, column=0, sticky="w", padx=14, pady=(0, 4))
        self.mouse_button_menu = self.make_option(self.clicker_card, self.clicker_mouse_button, ["left", "middle", "right"], width=10)
        self.mouse_button_menu.grid(row=5, column=0, sticky="w", padx=14, pady=(0, 10))
        self.keyboard_key_label = self.make_text(self.clicker_card, "")
        self.keyboard_key_label.grid(row=4, column=2, sticky="w", padx=14, pady=(0, 4))
        self.keyboard_key_box = self.KeyBindBox(self, self.clicker_card, self.clicker_keyboard_key, width=18)
        self.keyboard_key_box.grid(row=5, column=2, sticky="w", padx=14, pady=(0, 10))
        self.interval_mode_label = self.make_text(self.clicker_card, "")
        self.interval_mode_label.grid(row=6, column=0, sticky="w", padx=14, pady=(6, 4))
        im_wrap = tk.Frame(self.clicker_card, bg=CARD)
        im_wrap.grid(row=7, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 10))
        self.fixed_radio = self.make_radio(im_wrap, "", self.clicker_interval_mode, "fixed")
        self.fixed_radio.pack(side="left", padx=(0, 10))
        self.random_radio = self.make_radio(im_wrap, "", self.clicker_interval_mode, "random")
        self.random_radio.pack(side="left")
        self.interval_label = self.make_text(self.clicker_card, "")
        self.interval_label.grid(row=8, column=0, sticky="w", padx=14, pady=(6, 4))
        fwrap = tk.Frame(self.clicker_card, bg=CARD)
        fwrap.grid(row=9, column=0, sticky="w", padx=14, pady=(0, 10))
        self.interval_entry = self.make_entry(fwrap, self.clicker_interval_value, 12)
        self.interval_entry.pack(side="left")
        self.interval_unit_menu = self.make_option(fwrap, self.clicker_interval_unit, ["ms", "sec"], width=6)
        self.interval_unit_menu.pack(side="left", padx=8)
        self.interval_from_to_label = self.make_text(self.clicker_card, "")
        self.interval_from_to_label.grid(row=8, column=2, sticky="w", padx=14, pady=(6, 4))
        rwrap = tk.Frame(self.clicker_card, bg=CARD)
        rwrap.grid(row=9, column=2, sticky="w", padx=14, pady=(0, 10))
        self.interval_min_entry = self.make_entry(rwrap, self.clicker_interval_min, 10)
        self.interval_min_entry.pack(side="left")
        self.interval_max_entry = self.make_entry(rwrap, self.clicker_interval_max, 10)
        self.interval_max_entry.pack(side="left", padx=8)
        self.interval_rand_unit_menu = self.make_option(rwrap, self.clicker_interval_random_unit, ["ms", "sec"], width=6)
        self.interval_rand_unit_menu.pack(side="left")
        self.repeats_label = self.make_text(self.clicker_card, "")
        self.repeats_label.grid(row=10, column=0, sticky="w", padx=14, pady=(6, 4))
        repwrap = tk.Frame(self.clicker_card, bg=CARD)
        repwrap.grid(row=11, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 10))
        self.infinite_radio = self.make_radio(repwrap, "", self.clicker_repeat_mode, "infinite")
        self.infinite_radio.pack(side="left", padx=(0, 10))
        self.count_radio = self.make_radio(repwrap, "", self.clicker_repeat_mode, "count")
        self.count_radio.pack(side="left")
        self.count_label = self.make_text(self.clicker_card, "")
        self.count_label.grid(row=10, column=2, sticky="w", padx=14, pady=(6, 4))
        self.count_entry = self.make_entry(self.clicker_card, self.clicker_repeat_count)
        self.count_entry.grid(row=11, column=2, sticky="ew", padx=14, pady=(0, 10))
        self.target_label = self.make_text(self.clicker_card, "")
        self.target_label.grid(row=12, column=0, sticky="w", padx=14, pady=(6, 4))
        twrap = tk.Frame(self.clicker_card, bg=CARD)
        twrap.grid(row=13, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 10))
        self.current_pos_radio = self.make_radio(twrap, "", self.clicker_target_mode, "current")
        self.current_pos_radio.pack(side="left", padx=(0, 10))
        self.coords_radio = self.make_radio(twrap, "", self.clicker_target_mode, "coords")
        self.coords_radio.pack(side="left")
        self.x_label = self.make_text(self.clicker_card, "X")
        self.x_label.grid(row=12, column=2, sticky="w", padx=14, pady=(6, 4))
        self.y_label = self.make_text(self.clicker_card, "Y")
        self.y_label.grid(row=12, column=3, sticky="w", padx=14, pady=(6, 4))
        self.x_entry = self.make_entry(self.clicker_card, self.clicker_target_x)
        self.x_entry.grid(row=13, column=2, sticky="ew", padx=14, pady=(0, 10))
        self.y_entry = self.make_entry(self.clicker_card, self.clicker_target_y)
        self.y_entry.grid(row=13, column=3, sticky="ew", padx=14, pady=(0, 10))
        self.capture_cursor_btn = self.make_button(self.clicker_card, "", self.capture_current_cursor_position, width=12)
        self.capture_cursor_btn.grid(row=14, column=2, sticky="w", padx=14, pady=(0, 10))
        self.clicker_hotkey_start_label = self.make_text(self.clicker_card, "")
        self.clicker_hotkey_start_label.grid(row=15, column=0, sticky="w", padx=14, pady=(6, 4))
        self.clicker_hotkey_start_box = self.KeyBindBox(self, self.clicker_card, self.clicker_start_hotkey, width=18)
        self.clicker_hotkey_start_box.grid(row=16, column=0, sticky="w", padx=14, pady=(0, 10))
        self.clicker_hotkey_stop_label = self.make_text(self.clicker_card, "")
        self.clicker_hotkey_stop_label.grid(row=15, column=1, sticky="w", padx=14, pady=(6, 4))
        self.clicker_hotkey_stop_box = self.KeyBindBox(self, self.clicker_card, self.clicker_stop_hotkey, width=18)
        self.clicker_hotkey_stop_box.grid(row=16, column=1, sticky="w", padx=14, pady=(0, 10))
        self.done_label = self.make_text(self.clicker_card, "")
        self.done_label.grid(row=15, column=2, sticky="w", padx=14, pady=(6, 4))
        tk.Label(self.clicker_card, textvariable=self.clicker_count_done, bg=INPUT_BG, fg="#5fd38d", font=("Segoe UI", 11, "bold"),
                 padx=10, pady=8, highlightthickness=1, highlightbackground=BORDER).grid(row=16, column=2, sticky="w", padx=14, pady=(0, 10))
        tk.Label(self.clicker_card, textvariable=self.clicker_status, bg=CARD, fg=ACCENT, font=("Segoe UI", 10, "bold")).grid(row=17, column=0, columnspan=4, sticky="w", padx=14, pady=(6, 10))
        btns = tk.Frame(self.clicker_card, bg=CARD)
        btns.grid(row=18, column=0, columnspan=4, sticky="w", padx=14, pady=(0, 14))
        self.clicker_start_btn = self.make_button(btns, "", self.start_clicker)
        self.clicker_start_btn.pack(side="left", padx=(0, 8))
        self.clicker_stop_btn = self.make_button(btns, "", self.stop_clicker)
        self.clicker_stop_btn.pack(side="left", padx=(0, 8))
        self.reset_counter_btn = self.make_button(btns, "", self.reset_click_counter, width=14)
        self.reset_counter_btn.pack(side="left")
        for i in range(4):
            self.clicker_card.columnconfigure(i, weight=1)

    def build_macro_tab(self):
        self.macro_card = self.make_card(self.macro_tab)
        self.macro_card.pack(fill="both", expand=True, padx=14, pady=14)
        self.macro_title_label = self.make_title(self.macro_card, "")
        self.macro_title_label.grid(row=0, column=0, columnspan=4, sticky="w", padx=14, pady=(14, 4))
        self.macro_subtitle_label = self.make_text(self.macro_card, "")
        self.macro_subtitle_label.grid(row=1, column=0, columnspan=4, sticky="w", padx=14, pady=(0, 12))
        help_text = "WAIT 500\nKEY space\nTEXT hello world\nCLICK left\nDOUBLECLICK left\nMOVE 500 300\nHOLDKEY e 1.0\nHOLDMOUSE left 0.4"
        self.help_box = tk.Text(self.macro_card, height=7, bg=INPUT_BG, fg=MUTED, insertbackground=TEXT, relief="flat",
                                highlightthickness=1, highlightbackground=BORDER, font=("Consolas", 10))
        self.help_box.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=14, pady=(0, 10))
        self.help_box.insert("1.0", help_text)
        self.help_box.configure(state="disabled")
        self.macro_editor = tk.Text(self.macro_card, height=14, bg=INPUT_BG, fg=TEXT, insertbackground=TEXT, relief="flat",
                                    highlightthickness=1, highlightbackground=BORDER, font=("Consolas", 10))
        self.macro_editor.grid(row=2, column=2, columnspan=2, sticky="nsew", padx=14, pady=(0, 10))
        self.macro_editor.insert("1.0", "WAIT 500\nKEY space\nWAIT 300\nCLICK left\n")
        self.macro_repeat_label = self.make_text(self.macro_card, "")
        self.macro_repeat_label.grid(row=3, column=0, sticky="w", padx=14, pady=(6, 4))
        rw = tk.Frame(self.macro_card, bg=CARD)
        rw.grid(row=4, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 10))
        self.once_radio = self.make_radio(rw, "", self.macro_repeat_mode, "1")
        self.once_radio.pack(side="left", padx=(0, 10))
        self.macro_infinite_radio = self.make_radio(rw, "", self.macro_repeat_mode, "infinite")
        self.macro_infinite_radio.pack(side="left", padx=(0, 10))
        self.macro_count_radio = self.make_radio(rw, "", self.macro_repeat_mode, "count")
        self.macro_count_radio.pack(side="left")
        self.macro_count_label = self.make_text(self.macro_card, "")
        self.macro_count_label.grid(row=3, column=2, sticky="w", padx=14, pady=(6, 4))
        self.macro_count_entry = self.make_entry(self.macro_card, self.macro_repeat_count)
        self.macro_count_entry.grid(row=4, column=2, sticky="ew", padx=14, pady=(0, 10))
        self.macro_hotkey_start_label = self.make_text(self.macro_card, "")
        self.macro_hotkey_start_label.grid(row=5, column=0, sticky="w", padx=14, pady=(6, 4))
        self.macro_hotkey_start_box = self.KeyBindBox(self, self.macro_card, self.macro_start_hotkey, width=18)
        self.macro_hotkey_start_box.grid(row=6, column=0, sticky="w", padx=14, pady=(0, 10))
        self.macro_hotkey_stop_label = self.make_text(self.macro_card, "")
        self.macro_hotkey_stop_label.grid(row=5, column=1, sticky="w", padx=14, pady=(6, 4))
        self.macro_hotkey_stop_box = self.KeyBindBox(self, self.macro_card, self.macro_stop_hotkey, width=18)
        self.macro_hotkey_stop_box.grid(row=6, column=1, sticky="w", padx=14, pady=(0, 10))
        tk.Label(self.macro_card, textvariable=self.macro_status, bg=CARD, fg=ACCENT, font=("Segoe UI", 10, "bold")).grid(row=7, column=0, columnspan=4, sticky="w", padx=14, pady=(6, 10))
        btns = tk.Frame(self.macro_card, bg=CARD)
        btns.grid(row=8, column=0, columnspan=4, sticky="w", padx=14, pady=(0, 14))
        self.macro_start_btn = self.make_button(btns, "", self.start_macro, width=14)
        self.macro_start_btn.pack(side="left", padx=(0, 8))
        self.macro_stop_btn = self.make_button(btns, "", self.stop_macro, width=14)
        self.macro_stop_btn.pack(side="left", padx=(0, 8))
        self.macro_export_btn = self.make_button(btns, "", self.export_macro_text, width=18)
        self.macro_export_btn.pack(side="left")
        for i in range(4):
            self.macro_card.columnconfigure(i, weight=1)
        self.macro_card.rowconfigure(2, weight=1)

    def refresh_language(self):
        self.root.title(self.tr("title"))
        self.title_label.config(text=self.tr("title"))
        self.subtitle_label.config(text=self.tr("subtitle"))
        self.lang_label.config(text=self.tr("lang"))
        self.profiles_title.config(text=self.tr("profiles"))
        self.profile_name_label.config(text=self.tr("profile_name"))
        self.save_profile_btn.config(text=self.tr("save"))
        self.load_profile_btn.config(text=self.tr("load"))
        self.delete_profile_btn.config(text=self.tr("delete"))
        self.export_btn.config(text=self.tr("export"))
        self.import_btn.config(text=self.tr("import"))
        self.panic_btn.config(text=self.tr("panic"))
        self.notebook.tab(0, text=self.tr("main_tab"))
        self.notebook.tab(1, text=self.tr("clicker_tab"))
        self.notebook.tab(2, text=self.tr("macro_tab"))
        self.log_title.config(text=self.tr("log"))
        self.clear_log_btn.config(text=self.tr("clear_log"))

        self.random_title.config(text=self.tr("random_title"))
        self.random_subtitle.config(text=self.tr("random_subtitle"))
        self.random_keyboard_check.config(text=self.tr("keyboard"))
        self.random_mouse_check.config(text=self.tr("mouse"))
        for key in ["keys_csv","key_hold_sec","key_pause_sec","mouse_interval_min_sec","mouse_interval_max_sec","mouse_move_min","mouse_move_max"]:
            self.random_labels[key].config(text=self.tr(key))
        self.random_hotkey_start_label.config(text=self.tr("hotkey_start"))
        self.random_hotkey_stop_label.config(text=self.tr("hotkey_stop"))
        self.random_start_btn.config(text=self.tr("start"))
        self.random_stop_btn.config(text=self.tr("stop"))

        self.clicker_title_label.config(text=self.tr("clicker_title"))
        self.clicker_subtitle_label.config(text=self.tr("clicker_subtitle"))
        self.click_mode_label.config(text=self.tr("click_mode"))
        self.click_mouse_radio.config(text=self.tr("mouse"))
        self.click_kb_radio.config(text=self.tr("keyboard"))
        self.action_type_label.config(text=self.tr("action_type"))
        self.hold_label.config(text=self.tr("hold_sec"))
        self.mouse_button_label.config(text=self.tr("mouse_button"))
        self.keyboard_key_label.config(text=self.tr("keyboard_key"))
        self.interval_mode_label.config(text=self.tr("interval_mode"))
        self.fixed_radio.config(text=self.tr("fixed"))
        self.random_radio.config(text=self.tr("random"))
        self.interval_label.config(text=self.tr("interval"))
        self.interval_from_to_label.config(text=self.tr("interval_from_to"))
        self.repeats_label.config(text=self.tr("repeats"))
        self.infinite_radio.config(text=self.tr("infinite"))
        self.count_radio.config(text=self.tr("count"))
        self.count_label.config(text=self.tr("count_label"))
        self.target_label.config(text=self.tr("target_point"))
        self.current_pos_radio.config(text=self.tr("current_pos"))
        self.coords_radio.config(text=self.tr("coords"))
        self.capture_cursor_btn.config(text=self.tr("capture_cursor"))
        self.clicker_hotkey_start_label.config(text=self.tr("hotkey_start"))
        self.clicker_hotkey_stop_label.config(text=self.tr("hotkey_stop"))
        self.done_label.config(text=self.tr("done_clicks"))
        self.clicker_start_btn.config(text=self.tr("start"))
        self.clicker_stop_btn.config(text=self.tr("stop"))
        self.reset_counter_btn.config(text=self.tr("reset_counter"))

        self.macro_title_label.config(text=self.tr("macro_title"))
        self.macro_subtitle_label.config(text=self.tr("macro_subtitle"))
        self.macro_repeat_label.config(text=self.tr("repeat"))
        self.once_radio.config(text=self.tr("once"))
        self.macro_infinite_radio.config(text=self.tr("infinite"))
        self.macro_count_radio.config(text=self.tr("count"))
        self.macro_count_label.config(text=self.tr("count_label"))
        self.macro_hotkey_start_label.config(text=self.tr("hotkey_start"))
        self.macro_hotkey_stop_label.config(text=self.tr("hotkey_stop"))
        self.macro_start_btn.config(text=self.tr("start_macro"))
        self.macro_stop_btn.config(text=self.tr("stop_macro"))
        self.macro_export_btn.config(text=self.tr("save_macro_txt"))

        if not self.running_random and not self.running_clicker and not self.running_macro:
            self.set_stopped_statuses()

    def capture_current_cursor_position(self):
        self.clicker_target_x.set(str(self.root.winfo_pointerx()))
        self.clicker_target_y.set(str(self.root.winfo_pointery()))

    def reset_click_counter(self):
        self.clicker_count_done.set("0")

    def release_all_inputs(self):
        for key in ["w","a","s","d","space","shift","ctrl","alt","tab","enter","q","e","r","f","1","2","3","4","5"]:
            try:
                pydirectinput.keyUp(key)
            except Exception:
                pass
        for btn in ["left","middle","right"]:
            try:
                pydirectinput.mouseUp(button=btn)
            except Exception:
                pass

    def start_random_module(self):
        if self.running_random:
            self.status_global.set(self.tr("already_running"))
            return
        use_keyboard = self.random_use_keyboard.get()
        use_mouse = self.random_use_mouse.get()
        if not use_keyboard and not use_mouse:
            self.status_global.set(self.tr("enable_kb_mouse"))
            return
        keys_list = parse_keys_csv(self.random_keys.get())
        if use_keyboard and not keys_list:
            self.status_global.set(self.tr("keys_prompt"))
            return
        hold_time = parse_float(self.random_key_hold.get())
        pause_time = parse_float(self.random_key_pause.get())
        interval_min = parse_float(self.random_mouse_interval_min.get())
        interval_max = parse_float(self.random_mouse_interval_max.get())
        move_min = parse_int(self.random_mouse_move_min.get())
        move_max = parse_int(self.random_mouse_move_max.get())
        if None in (hold_time, pause_time, interval_min, interval_max, move_min, move_max):
            self.status_global.set(self.tr("check_numbers"))
            return
        self.running_random = True
        self.status_global.set(self.tr("status_running"))
        if use_keyboard:
            threading.Thread(target=self.random_keyboard_worker, args=(keys_list, hold_time, pause_time), daemon=True).start()
        if use_mouse:
            threading.Thread(target=self.random_mouse_worker, args=(interval_min, interval_max, move_min, move_max), daemon=True).start()

    def stop_random_module(self):
        self.running_random = False
        self.status_global.set(self.tr("status_stopped"))
        self.release_all_inputs()

    def random_keyboard_worker(self, keys_list, hold_time, pause_time):
        while self.running_random:
            key = random.choice(keys_list)
            try:
                pydirectinput.keyDown(key)
                start = time.time()
                while self.running_random and time.time() - start < hold_time:
                    time.sleep(0.01)
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
                except Exception:
                    pass
                next_move = time.time() + random.uniform(interval_min, interval_max)
            time.sleep(0.01)

    def get_clicker_interval_seconds(self):
        if self.clicker_interval_mode.get() == "fixed":
            value = parse_float(self.clicker_interval_value.get())
            if value is None or value <= 0:
                return None
            return value / 1000.0 if self.clicker_interval_unit.get() == "ms" else value
        vmin = parse_float(self.clicker_interval_min.get())
        vmax = parse_float(self.clicker_interval_max.get())
        if vmin is None or vmax is None or vmin <= 0 or vmax <= 0 or vmin > vmax:
            return None
        factor = 1 / 1000.0 if self.clicker_interval_random_unit.get() == "ms" else 1.0
        return random.uniform(vmin * factor, vmax * factor)

    def get_click_target(self):
        if self.clicker_target_mode.get() == "current":
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
                raise ValueError
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
                pydirectinput.mouseDown(button=btn); time.sleep(max(0.01, hold_time)); pydirectinput.mouseUp(button=btn)
        else:
            key = self.clicker_keyboard_key.get().strip().lower()
            if not key:
                raise ValueError
            if action == "single":
                pydirectinput.press(key)
            elif action == "double":
                pydirectinput.press(key); time.sleep(0.05); pydirectinput.press(key)
            elif action == "triple":
                pydirectinput.press(key); time.sleep(0.05); pydirectinput.press(key); time.sleep(0.05); pydirectinput.press(key)
            elif action == "hold":
                pydirectinput.keyDown(key); time.sleep(max(0.01, hold_time)); pydirectinput.keyUp(key)

    def clicker_worker(self):
        self.clicker_status.set(self.tr("status_running"))
        done = 0
        limit = None
        if self.clicker_repeat_mode.get() == "count":
            limit = parse_int(self.clicker_repeat_count.get())
            if limit is None or limit <= 0:
                self.clicker_status.set(self.tr("check_numbers"))
                self.running_clicker = False
                return
        while self.running_clicker:
            if limit is not None and done >= limit:
                break
            self.perform_clicker_action()
            done += 1
            self.root.after(0, lambda c=done: self.clicker_count_done.set(str(c)))
            interval = self.get_clicker_interval_seconds()
            if interval is None:
                break
            slept = 0.0
            while self.running_clicker and slept < interval:
                step = min(0.01, interval - slept)
                time.sleep(max(0.001, step))
                slept += step
        self.running_clicker = False
        self.root.after(0, lambda: self.clicker_status.set(self.tr("status_stopped")))

    def start_clicker(self):
        if self.running_clicker:
            self.clicker_status.set(self.tr("already_running"))
            return
        if self.clicker_mode.get() == "keyboard" and not self.clicker_keyboard_key.get().strip():
            self.clicker_status.set(self.tr("choose_key"))
            return
        if self.clicker_target_mode.get() == "coords" and self.get_click_target() is None:
            self.clicker_status.set(self.tr("check_coords"))
            return
        if self.get_clicker_interval_seconds() is None:
            self.clicker_status.set(self.tr("check_interval"))
            return
        self.running_clicker = True
        self.clicker_status.set(self.tr("status_starting"))
        threading.Thread(target=self.clicker_worker, daemon=True).start()

    def stop_clicker(self):
        self.running_clicker = False
        self.clicker_status.set(self.tr("status_stopped"))
        self.release_all_inputs()

    def parse_macro_lines(self):
        text = self.macro_editor.get("1.0", "end").strip()
        return [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]

    def execute_macro_line(self, line):
        parts = line.split()
        cmd = parts[0].upper()
        if cmd == "WAIT":
            time.sleep((parse_float(parts[1], 0) or 0) / 1000.0); return
        if cmd == "KEY":
            pydirectinput.press(parts[1].lower()); return
        if cmd == "TEXT":
            pydirectinput.write(line[len("TEXT "):], interval=0.02); return
        if cmd == "CLICK":
            pydirectinput.click(button=parts[1].lower()); return
        if cmd == "DOUBLECLICK":
            pydirectinput.click(button=parts[1].lower(), clicks=2, interval=0.05); return
        if cmd == "MOVE":
            pydirectinput.moveTo(parse_int(parts[1], 0), parse_int(parts[2], 0), duration=0); return
        if cmd == "HOLDKEY":
            key, sec = parts[1].lower(), parse_float(parts[2], 0.3)
            pydirectinput.keyDown(key); time.sleep(max(0.01, sec)); pydirectinput.keyUp(key); return
        if cmd == "HOLDMOUSE":
            btn, sec = parts[1].lower(), parse_float(parts[2], 0.3)
            pydirectinput.mouseDown(button=btn); time.sleep(max(0.01, sec)); pydirectinput.mouseUp(button=btn); return

    def macro_worker(self):
        lines = self.parse_macro_lines()
        if not lines:
            self.macro_status.set(self.tr("status_stopped"))
            self.running_macro = False
            return
        repeat_mode = self.macro_repeat_mode.get()
        repeat_count = 1 if repeat_mode == "1" else None
        if repeat_mode == "count":
            repeat_count = parse_int(self.macro_repeat_count.get(), 1)
        self.macro_status.set(self.tr("status_running"))
        round_index = 0
        while self.running_macro:
            if repeat_count is not None and round_index >= repeat_count:
                break
            round_index += 1
            for line in lines:
                if not self.running_macro:
                    break
                try:
                    self.execute_macro_line(line)
                except Exception:
                    self.running_macro = False
                    break
        self.running_macro = False
        self.root.after(0, lambda: self.macro_status.set(self.tr("status_stopped")))

    def start_macro(self):
        if self.running_macro:
            self.macro_status.set(self.tr("already_running"))
            return
        self.running_macro = True
        self.macro_status.set(self.tr("status_starting"))
        threading.Thread(target=self.macro_worker, daemon=True).start()

    def stop_macro(self):
        self.running_macro = False
        self.macro_status.set(self.tr("status_stopped"))
        self.release_all_inputs()

    def export_macro_text(self):
        path = filedialog.asksaveasfilename(title="Save macro", defaultextension=".txt",
                                            filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.macro_editor.get("1.0", "end"))

    def start_hotkey_listener(self):
        if self.hotkey_listener_started:
            return
        self.hotkey_listener_started = True
        threading.Thread(target=self.hotkey_listener, daemon=True).start()

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
                    if key_name and safe_is_pressed(key_name):
                        if now - last_pressed.get(key_name, 0.0) > 0.5:
                            self.root.after(0, action)
                            last_pressed[key_name] = now
            except Exception:
                pass
            time.sleep(0.05)

    def collect_settings(self):
        return {
            "lang": self.lang.get(),
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
        self.lang.set(data.get("lang", "ru"))
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
        self.refresh_language()

    def save_profiles_to_disk(self):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.profiles, f, ensure_ascii=False, indent=2)

    def load_profiles_from_disk(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    self.profiles = json.load(f)
            except Exception:
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
        if sel:
            self.profile_name_var.set(self.profile_listbox.get(sel[0]))

    def save_current_profile(self):
        name = self.profile_name_var.get().strip() or "default"
        self.profiles[name] = self.collect_settings()
        self.save_profiles_to_disk()
        self.refresh_profile_list()

    def load_selected_profile(self):
        name = self.profile_name_var.get().strip()
        if name in self.profiles:
            self.apply_settings(self.profiles[name])

    def delete_selected_profile(self):
        name = self.profile_name_var.get().strip()
        if name and name != "default" and name in self.profiles:
            del self.profiles[name]
            self.save_profiles_to_disk()
            self.refresh_profile_list()
            self.profile_name_var.set("default")

    def export_profiles(self):
        path = filedialog.asksaveasfilename(title="Export", defaultextension=".json",
                                            filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.profiles, f, ensure_ascii=False, indent=2)

    def import_profiles(self):
        path = filedialog.askopenfilename(title="Import", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                self.profiles.update(data)
                self.save_profiles_to_disk()
                self.refresh_profile_list()
        except Exception:
            pass

    def panic_stop(self):
        self.running_random = False
        self.running_clicker = False
        self.running_macro = False
        self.set_stopped_statuses()
        self.release_all_inputs()


def main():
    root = tk.Tk()
    app = SFToolKeyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
