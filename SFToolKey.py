import time
import random
import threading
import tkinter as tk
from tkinter import ttk

import keyboard
import pydirectinput


# =========================
# GLOBAL STATE
# =========================
running = False
worker_thread = None
hotkey_thread_started = False
editing_hotkey = False
hotkeys_blocked_until = 0.0

autoclicker_running = False
autoclicker_thread = None

DEFAULT_KEY_HOLD_TIME = 0.7
DEFAULT_KEY_PAUSE_TIME = 0.2

DEFAULT_MOUSE_INTERVAL_MIN = 2.0
DEFAULT_MOUSE_INTERVAL_MAX = 5.0
DEFAULT_MOUSE_MOVE_MIN = 20
DEFAULT_MOUSE_MOVE_MAX = 120

# Random tab
start_hotkey_var_global = None
stop_hotkey_var_global = None
status_var_global = None
use_keyboard_var_global = None
use_mouse_var_global = None
keys_entry_global = None
key_hold_entry_global = None
key_pause_entry_global = None
mouse_interval_min_entry_global = None
mouse_interval_max_entry_global = None
mouse_move_min_entry_global = None
mouse_move_max_entry_global = None

# Autoclicker
autoclicker_status_var_global = None
autoclicker_mode_var_global = None
autoclicker_mouse_button_var_global = None
autoclicker_key_var_global = None
autoclicker_interval_value_var_global = None
autoclicker_interval_unit_var_global = None
autoclicker_start_hotkey_var_global = None
autoclicker_stop_hotkey_var_global = None

autoclicker_mouse_frame_global = None
autoclicker_keyboard_frame_global = None


# =========================
# THEME
# =========================
BG = "#111111"
CARD = "#1b1b1b"
CARD_2 = "#202020"
ACCENT = "#ff8a1f"
ACCENT_HOVER = "#ff9b42"
TEXT = "#f2f2f2"
MUTED = "#bdbdbd"
BORDER = "#2a2a2a"
INPUT_BG = "#262626"
INPUT_ACTIVE = "#2d2d2d"
BIND_WAIT_BG = "#3a2a16"


# =========================
# HELPERS
# =========================
def parse_keys(text: str):
    parts = [x.strip().lower() for x in text.split(",")]
    return [x for x in parts if x]


def safe_is_pressed(key_name: str):
    if not key_name:
        return False
    try:
        return keyboard.is_pressed(key_name)
    except Exception:
        return False


def random_mouse_move(move_min, move_max):
    dx = random.randint(move_min, move_max) * random.choice([-1, 1])
    dy = random.randint(move_min, move_max) * random.choice([-1, 1])

    try:
        pydirectinput.moveRel(dx, dy, duration=0)
        print(f"Движение мыши: dx={dx}, dy={dy}")
    except Exception as e:
        print(f"Ошибка движения мыши: {e}")


def create_card(parent):
    return tk.Frame(
        parent,
        bg=CARD,
        bd=0,
        highlightthickness=1,
        highlightbackground=BORDER
    )


def create_title(parent, text):
    return tk.Label(
        parent,
        text=text,
        bg=CARD,
        fg=TEXT,
        font=("Segoe UI", 11, "bold")
    )


def create_text(parent, text):
    return tk.Label(
        parent,
        text=text,
        bg=CARD,
        fg=MUTED,
        font=("Segoe UI", 10)
    )


def create_entry(parent, width=18):
    return tk.Entry(
        parent,
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


def create_button(parent, text, command, width=16):
    return tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        bg=ACCENT,
        fg="black",
        activebackground=ACCENT_HOVER,
        activeforeground="black",
        relief="flat",
        bd=0,
        font=("Segoe UI", 10, "bold"),
        cursor="hand2",
        padx=10,
        pady=8,
    )


def create_checkbutton(parent, text, variable):
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


def create_radiobutton(parent, text, variable, value, command=None):
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


def create_option_menu(parent, variable, options, width=14):
    menu = tk.OptionMenu(parent, variable, *options)
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


class KeyBindBox(tk.Label):
    def __init__(self, parent, textvariable, width=16):
        super().__init__(
            parent,
            textvariable=textvariable,
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
        self.var = textvariable
        self.waiting = False

        self.bind("<Button-1>", self.start_capture)
        self.bind("<Enter>", lambda e: self.config(bg=INPUT_ACTIVE if not self.waiting else BIND_WAIT_BG))
        self.bind("<Leave>", lambda e: self.config(bg=INPUT_BG if not self.waiting else BIND_WAIT_BG))

    def start_capture(self, event=None):
        global editing_hotkey
        editing_hotkey = True
        self.waiting = True
        self.config(bg=BIND_WAIT_BG, highlightbackground=ACCENT)
        self.var.set("Нажми клавишу...")
        self.after(50, self.poll_key)

    def poll_key(self):
        global editing_hotkey, hotkeys_blocked_until

        if not self.waiting:
            return

        try:
            pressed = keyboard.read_event(suppress=False)
            if pressed.event_type == keyboard.KEY_DOWN:
                name = (pressed.name or "").lower()
                if name:
                    self.var.set(name)
                    self.waiting = False
                    editing_hotkey = False
                    hotkeys_blocked_until = time.time() + 2.0
                    self.config(bg=INPUT_BG, highlightbackground=BORDER)
                    return
        except Exception:
            pass

        self.after(50, self.poll_key)


# =========================
# RANDOM KEYBOARD + MOUSE
# =========================
def keyboard_loop(keys_list, key_hold_time, key_pause_time):
    global running

    while running:
        key = random.choice(keys_list)
        print(f"Случайная клавиша: {key}")

        try:
            pydirectinput.keyDown(key)
            start_time = time.time()

            while running and (time.time() - start_time < key_hold_time):
                time.sleep(0.01)

            pydirectinput.keyUp(key)
        except Exception as e:
            print(f"Ошибка клавиши {key}: {e}")
            try:
                pydirectinput.keyUp(key)
            except Exception:
                pass

        pause_start = time.time()
        while running and (time.time() - pause_start < key_pause_time):
            time.sleep(0.01)


def mouse_loop(interval_min, interval_max, move_min, move_max):
    global running

    next_move_time = time.time() + random.uniform(interval_min, interval_max)

    while running:
        now = time.time()
        if now >= next_move_time:
            random_mouse_move(move_min, move_max)
            next_move_time = time.time() + random.uniform(interval_min, interval_max)

        time.sleep(0.01)


def automation_loop(use_keyboard, use_mouse, keys_list, key_hold_time, key_pause_time,
                    interval_min, interval_max, move_min, move_max):
    global running

    if status_var_global is not None:
        status_var_global.set("Работает")

    threads = []

    if use_keyboard and keys_list:
        t = threading.Thread(
            target=keyboard_loop,
            args=(keys_list, key_hold_time, key_pause_time),
            daemon=True
        )
        threads.append(t)
        t.start()

    if use_mouse:
        t = threading.Thread(
            target=mouse_loop,
            args=(interval_min, interval_max, move_min, move_max),
            daemon=True
        )
        threads.append(t)
        t.start()

    while running:
        time.sleep(0.05)

    if status_var_global is not None:
        status_var_global.set("Остановлено")


def start_script():
    global running, worker_thread

    if running:
        status_var_global.set("Уже запущено")
        return

    use_keyboard = use_keyboard_var_global.get()
    use_mouse = use_mouse_var_global.get()

    if not use_keyboard and not use_mouse:
        status_var_global.set("Включи клавиатуру или мышь")
        return

    keys_text = keys_entry_global.get().strip()
    keys_list = parse_keys(keys_text)

    if use_keyboard and not keys_list:
        status_var_global.set("Укажи клавиши, например: w,a,s,d")
        return

    try:
        key_hold_time = float(key_hold_entry_global.get())
        key_pause_time = float(key_pause_entry_global.get())
        interval_min = float(mouse_interval_min_entry_global.get())
        interval_max = float(mouse_interval_max_entry_global.get())
        move_min = int(mouse_move_min_entry_global.get())
        move_max = int(mouse_move_max_entry_global.get())
    except ValueError:
        status_var_global.set("Проверь числовые значения")
        return

    if interval_min > interval_max:
        status_var_global.set("Мин. интервал мыши больше макс.")
        return

    if move_min > move_max:
        status_var_global.set("Мин. движение мыши больше макс.")
        return

    running = True
    status_var_global.set("Запуск...")

    worker_thread = threading.Thread(
        target=automation_loop,
        args=(
            use_keyboard,
            use_mouse,
            keys_list,
            key_hold_time,
            key_pause_time,
            interval_min,
            interval_max,
            move_min,
            move_max,
        ),
        daemon=True
    )
    worker_thread.start()


def stop_script():
    global running
    running = False
    status_var_global.set("Останавливается...")

    keys_to_release = [
        "w", "a", "s", "d", "space", "shift", "ctrl",
        "alt", "tab", "enter", "q", "e", "r", "f"
    ]

    for key in keys_to_release:
        try:
            pydirectinput.keyUp(key)
        except Exception:
            pass

    for btn in ["left", "right", "middle"]:
        try:
            pydirectinput.mouseUp(button=btn)
        except Exception:
            pass


# =========================
# AUTOCLICKER
# =========================
def get_autoclicker_interval_seconds():
    try:
        value = float(autoclicker_interval_value_var_global.get())
    except ValueError:
        return None

    unit = autoclicker_interval_unit_var_global.get()

    if value < 0:
        return None

    if unit == "ms":
        return value / 1000.0
    return value


def autoclicker_loop(mode, mouse_button, keyboard_key, interval_seconds):
    global autoclicker_running

    if autoclicker_status_var_global is not None:
        autoclicker_status_var_global.set("Автокликер работает")

    while autoclicker_running:
        try:
            if mode == "mouse":
                pydirectinput.click(button=mouse_button)
                print(f"Автоклик: mouse {mouse_button}")
            else:
                if keyboard_key:
                    pydirectinput.press(keyboard_key)
                    print(f"Автоклик: key {keyboard_key}")
        except Exception as e:
            print("Ошибка автокликера:", e)

        slept = 0.0
        while autoclicker_running and slept < interval_seconds:
            step = min(0.01, max(0.001, interval_seconds - slept))
            time.sleep(step)
            slept += step

    if autoclicker_status_var_global is not None:
        autoclicker_status_var_global.set("Автокликер остановлен")


def start_autoclicker():
    global autoclicker_running, autoclicker_thread

    if autoclicker_running:
        autoclicker_status_var_global.set("Уже запущен")
        return

    mode = autoclicker_mode_var_global.get()
    mouse_button = autoclicker_mouse_button_var_global.get()
    keyboard_key = autoclicker_key_var_global.get().strip().lower()
    interval_seconds = get_autoclicker_interval_seconds()

    if interval_seconds is None:
        autoclicker_status_var_global.set("Проверь интервал")
        return

    if interval_seconds <= 0:
        autoclicker_status_var_global.set("Интервал должен быть больше 0")
        return

    if mode == "keyboard" and not keyboard_key:
        autoclicker_status_var_global.set("Выбери клавишу")
        return

    autoclicker_running = True
    autoclicker_status_var_global.set("Запуск...")

    autoclicker_thread = threading.Thread(
        target=autoclicker_loop,
        args=(mode, mouse_button, keyboard_key, interval_seconds),
        daemon=True
    )
    autoclicker_thread.start()


def stop_autoclicker():
    global autoclicker_running
    autoclicker_running = False

    if autoclicker_status_var_global is not None:
        autoclicker_status_var_global.set("Останавливается...")

    for btn in ["left", "right", "middle"]:
        try:
            pydirectinput.mouseUp(button=btn)
        except Exception:
            pass


def update_autoclicker_ui():
    mode = autoclicker_mode_var_global.get()

    if mode == "mouse":
        autoclicker_mouse_frame_global.grid()
        autoclicker_keyboard_frame_global.grid_remove()
    else:
        autoclicker_mouse_frame_global.grid_remove()
        autoclicker_keyboard_frame_global.grid()


# =========================
# HOTKEY LISTENER
# =========================
def hotkey_listener():
    global editing_hotkey, hotkeys_blocked_until

    last_start_press = 0.0
    last_stop_press = 0.0
    last_ac_start_press = 0.0
    last_ac_stop_press = 0.0

    while True:
        try:
            now = time.time()

            if editing_hotkey:
                time.sleep(0.05)
                continue

            if now < hotkeys_blocked_until:
                time.sleep(0.05)
                continue

            start_key = start_hotkey_var_global.get().strip().lower()
            stop_key = stop_hotkey_var_global.get().strip().lower()

            if safe_is_pressed(start_key):
                if now - last_start_press > 0.5:
                    start_script()
                    last_start_press = now

            if safe_is_pressed(stop_key):
                if now - last_stop_press > 0.5:
                    stop_script()
                    last_stop_press = now

            ac_start_key = autoclicker_start_hotkey_var_global.get().strip().lower()
            ac_stop_key = autoclicker_stop_hotkey_var_global.get().strip().lower()

            if safe_is_pressed(ac_start_key):
                if now - last_ac_start_press > 0.5:
                    start_autoclicker()
                    last_ac_start_press = now

            if safe_is_pressed(ac_stop_key):
                if now - last_ac_stop_press > 0.5:
                    stop_autoclicker()
                    last_ac_stop_press = now

        except Exception as e:
            print("Ошибка hotkey_listener:", e)

        time.sleep(0.05)


# =========================
# GUI BUILDERS
# =========================
def build_random_tab(parent):
    global start_hotkey_var_global, stop_hotkey_var_global, status_var_global
    global use_keyboard_var_global, use_mouse_var_global
    global keys_entry_global, key_hold_entry_global, key_pause_entry_global
    global mouse_interval_min_entry_global, mouse_interval_max_entry_global
    global mouse_move_min_entry_global, mouse_move_max_entry_global

    frame = tk.Frame(parent, bg=BG)

    use_keyboard_var_global = tk.BooleanVar(value=True)
    use_mouse_var_global = tk.BooleanVar(value=True)
    start_hotkey_var_global = tk.StringVar(value="f8")
    stop_hotkey_var_global = tk.StringVar(value="f9")
    status_var_global = tk.StringVar(value="Остановлено")

    card = create_card(frame)
    card.pack(fill="both", expand=True, padx=14, pady=14)

    create_title(card, "Случайные клавиши и движение мыши").grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(14, 4))
    create_text(card, "Настрой рандомные клавиши, интервалы и горячие кнопки").grid(row=1, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 14))

    create_checkbutton(card, "Клавиатура", use_keyboard_var_global).grid(row=2, column=0, sticky="w", padx=14, pady=4)
    create_checkbutton(card, "Мышь", use_mouse_var_global).grid(row=2, column=1, sticky="w", padx=14, pady=4)

    create_text(card, "Клавиши через запятую").grid(row=3, column=0, sticky="w", padx=14, pady=(12, 4))
    keys_entry_global = create_entry(card, width=28)
    keys_entry_global.insert(0, "w,a,s,d")
    keys_entry_global.grid(row=4, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 10))

    create_text(card, "Удержание клавиши (сек)").grid(row=5, column=0, sticky="w", padx=14, pady=(6, 4))
    key_hold_entry_global = create_entry(card, width=14)
    key_hold_entry_global.insert(0, str(DEFAULT_KEY_HOLD_TIME))
    key_hold_entry_global.grid(row=6, column=0, sticky="ew", padx=14, pady=(0, 10))

    create_text(card, "Пауза между клавишами (сек)").grid(row=5, column=1, sticky="w", padx=14, pady=(6, 4))
    key_pause_entry_global = create_entry(card, width=14)
    key_pause_entry_global.insert(0, str(DEFAULT_KEY_PAUSE_TIME))
    key_pause_entry_global.grid(row=6, column=1, sticky="ew", padx=14, pady=(0, 10))

    create_text(card, "Мин. интервал мыши (сек)").grid(row=7, column=0, sticky="w", padx=14, pady=(6, 4))
    mouse_interval_min_entry_global = create_entry(card, width=14)
    mouse_interval_min_entry_global.insert(0, str(DEFAULT_MOUSE_INTERVAL_MIN))
    mouse_interval_min_entry_global.grid(row=8, column=0, sticky="ew", padx=14, pady=(0, 10))

    create_text(card, "Макс. интервал мыши (сек)").grid(row=7, column=1, sticky="w", padx=14, pady=(6, 4))
    mouse_interval_max_entry_global = create_entry(card, width=14)
    mouse_interval_max_entry_global.insert(0, str(DEFAULT_MOUSE_INTERVAL_MAX))
    mouse_interval_max_entry_global.grid(row=8, column=1, sticky="ew", padx=14, pady=(0, 10))

    create_text(card, "Мин. движение мыши").grid(row=9, column=0, sticky="w", padx=14, pady=(6, 4))
    mouse_move_min_entry_global = create_entry(card, width=14)
    mouse_move_min_entry_global.insert(0, str(DEFAULT_MOUSE_MOVE_MIN))
    mouse_move_min_entry_global.grid(row=10, column=0, sticky="ew", padx=14, pady=(0, 10))

    create_text(card, "Макс. движение мыши").grid(row=9, column=1, sticky="w", padx=14, pady=(6, 4))
    mouse_move_max_entry_global = create_entry(card, width=14)
    mouse_move_max_entry_global.insert(0, str(DEFAULT_MOUSE_MOVE_MAX))
    mouse_move_max_entry_global.grid(row=10, column=1, sticky="ew", padx=14, pady=(0, 10))

    create_text(card, "Горячая клавиша старта").grid(row=11, column=0, sticky="w", padx=14, pady=(8, 4))
    KeyBindBox(card, start_hotkey_var_global, width=18).grid(row=12, column=0, sticky="w", padx=14, pady=(0, 10))

    create_text(card, "Горячая клавиша стопа").grid(row=11, column=1, sticky="w", padx=14, pady=(8, 4))
    KeyBindBox(card, stop_hotkey_var_global, width=18).grid(row=12, column=1, sticky="w", padx=14, pady=(0, 10))

    tk.Label(
        card,
        textvariable=status_var_global,
        bg=CARD,
        fg=ACCENT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=13, column=0, columnspan=2, sticky="w", padx=14, pady=(6, 10))

    buttons = tk.Frame(card, bg=CARD)
    buttons.grid(row=14, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 14))

    create_button(buttons, "Старт", start_script, width=14).pack(side="left", padx=(0, 8))
    create_button(buttons, "Стоп", stop_script, width=14).pack(side="left")

    card.columnconfigure(0, weight=1)
    card.columnconfigure(1, weight=1)

    return frame


def build_autoclicker_tab(parent):
    global autoclicker_status_var_global
    global autoclicker_mode_var_global
    global autoclicker_mouse_button_var_global
    global autoclicker_key_var_global
    global autoclicker_interval_value_var_global
    global autoclicker_interval_unit_var_global
    global autoclicker_start_hotkey_var_global
    global autoclicker_stop_hotkey_var_global
    global autoclicker_mouse_frame_global
    global autoclicker_keyboard_frame_global

    frame = tk.Frame(parent, bg=BG)

    autoclicker_status_var_global = tk.StringVar(value="Автокликер остановлен")
    autoclicker_mode_var_global = tk.StringVar(value="mouse")
    autoclicker_mouse_button_var_global = tk.StringVar(value="left")
    autoclicker_key_var_global = tk.StringVar(value="space")
    autoclicker_interval_value_var_global = tk.StringVar(value="50")
    autoclicker_interval_unit_var_global = tk.StringVar(value="ms")
    autoclicker_start_hotkey_var_global = tk.StringVar(value="f6")
    autoclicker_stop_hotkey_var_global = tk.StringVar(value="f7")

    card = create_card(frame)
    card.pack(fill="both", expand=True, padx=14, pady=14)

    create_title(card, "Автокликер").grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(14, 4))
    create_text(card, "Выбери мышь или клавиатуру, интервал и горячие клавиши").grid(row=1, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 14))

    create_text(card, "Режим").grid(row=2, column=0, sticky="w", padx=14, pady=(4, 4))
    mode_wrap = tk.Frame(card, bg=CARD)
    mode_wrap.grid(row=3, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 12))

    create_radiobutton(mode_wrap, "Мышь", autoclicker_mode_var_global, "mouse", command=update_autoclicker_ui).pack(side="left", padx=(0, 10))
    create_radiobutton(mode_wrap, "Клавиатура", autoclicker_mode_var_global, "keyboard", command=update_autoclicker_ui).pack(side="left")

    autoclicker_mouse_frame_global = tk.Frame(card, bg=CARD)
    autoclicker_mouse_frame_global.grid(row=4, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 12))

    create_text(autoclicker_mouse_frame_global, "Кнопка мыши").grid(row=0, column=0, sticky="w", pady=(0, 4))
    create_option_menu(
        autoclicker_mouse_button_var_global and autoclicker_mouse_frame_global,
        autoclicker_mouse_button_var_global,
        ["left", "middle", "right"],
        width=12
    ).grid(row=1, column=0, sticky="w")

    autoclicker_keyboard_frame_global = tk.Frame(card, bg=CARD)
    autoclicker_keyboard_frame_global.grid(row=5, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 12))

    create_text(autoclicker_keyboard_frame_global, "Клавиша").grid(row=0, column=0, sticky="w", pady=(0, 4))
    KeyBindBox(autoclicker_keyboard_frame_global, autoclicker_key_var_global, width=18).grid(row=1, column=0, sticky="w")

    create_text(card, "Интервал").grid(row=6, column=0, sticky="w", padx=14, pady=(6, 4))
    interval_wrap = tk.Frame(card, bg=CARD)
    interval_wrap.grid(row=7, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 12))

    interval_entry = create_entry(interval_wrap, width=12)
    interval_entry.insert(0, autoclicker_interval_value_var_global.get())
    interval_entry.pack(side="left", padx=(0, 8))

    def sync_interval_var(event=None):
        autoclicker_interval_value_var_global.set(interval_entry.get())

    interval_entry.bind("<KeyRelease>", sync_interval_var)
    interval_entry.bind("<FocusOut>", sync_interval_var)

    create_option_menu(
        interval_wrap,
        autoclicker_interval_unit_var_global,
        ["ms", "sec"],
        width=8
    ).pack(side="left")

    create_text(card, "Горячая клавиша старта").grid(row=8, column=0, sticky="w", padx=14, pady=(6, 4))
    KeyBindBox(card, autoclicker_start_hotkey_var_global, width=18).grid(row=9, column=0, sticky="w", padx=14, pady=(0, 10))

    create_text(card, "Горячая клавиша стопа").grid(row=8, column=1, sticky="w", padx=14, pady=(6, 4))
    KeyBindBox(card, autoclicker_stop_hotkey_var_global, width=18).grid(row=9, column=1, sticky="w", padx=14, pady=(0, 10))

    tk.Label(
        card,
        textvariable=autoclicker_status_var_global,
        bg=CARD,
        fg=ACCENT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=10, column=0, columnspan=2, sticky="w", padx=14, pady=(6, 10))

    buttons = tk.Frame(card, bg=CARD)
    buttons.grid(row=11, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 14))

    create_button(buttons, "Старт", start_autoclicker, width=14).pack(side="left", padx=(0, 8))
    create_button(buttons, "Стоп", stop_autoclicker, width=14).pack(side="left")

    update_autoclicker_ui()

    card.columnconfigure(0, weight=1)
    card.columnconfigure(1, weight=1)

    return frame


def apply_notebook_style(style):
    style.theme_use("default")

    style.configure(
        "TNotebook",
        background=BG,
        borderwidth=0,
        tabmargins=[8, 8, 8, 0]
    )
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
# MAIN GUI
# =========================
def build_gui():
    global hotkey_thread_started

    root = tk.Tk()
    root.title("SFToolKey")
    root.geometry("760x820")
    root.minsize(760, 700)
    root.configure(bg=BG)
    root.resizable(True, True)

    style = ttk.Style()
    apply_notebook_style(style)

    outer = tk.Frame(root, bg=BG)
    outer.pack(fill="both", expand=True)

    canvas = tk.Canvas(
        outer,
        bg=BG,
        highlightthickness=0,
        bd=0
    )
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    content = tk.Frame(canvas, bg=BG)
    canvas_window = canvas.create_window((0, 0), window=content, anchor="nw")

    def on_content_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)

    content.bind("<Configure>", on_content_configure)
    canvas.bind("<Configure>", on_canvas_configure)

    def on_mousewheel_windows(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_mousewheel_linux_up(event):
        canvas.yview_scroll(-1, "units")

    def on_mousewheel_linux_down(event):
        canvas.yview_scroll(1, "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel_windows)
    canvas.bind_all("<Button-4>", on_mousewheel_linux_up)
    canvas.bind_all("<Button-5>", on_mousewheel_linux_down)

    header = tk.Frame(content, bg=BG)
    header.pack(fill="x", padx=14, pady=(14, 6))

    tk.Label(
        header,
        text="SFToolKey",
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 16, "bold")
    ).pack(anchor="w")

    tk.Label(
        header,
        text="Случайные клавиши, движение мыши и автокликер",
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 10)
    ).pack(anchor="w", pady=(2, 0))

    notebook = ttk.Notebook(content)
    notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    random_tab = build_random_tab(notebook)
    autoclicker_tab = build_autoclicker_tab(notebook)

    notebook.add(random_tab, text="Основное")
    notebook.add(autoclicker_tab, text="Автокликер")

    if not hotkey_thread_started:
        threading.Thread(target=hotkey_listener, daemon=True).start()
        hotkey_thread_started = True

    root.mainloop()


if __name__ == "__main__":
    build_gui()