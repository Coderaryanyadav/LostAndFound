"""
SBMP College Lost & Found Management System
Author: Aryan Yadav
Institution: SBMP College

Desktop GUI application featuring student self-registration,
admin management, live item matching, and audit logging.
"""

import os
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

# ─── Custom Exceptions ────────────────────────────────────────────────────────
class InputError(Exception):
    """Custom exception for form validation errors."""
    pass


# ─── Database Configuration ───────────────────────────────────────────────────
DB_FILE = "lost_found.db"
conn = None
cursor = None


def setup_database():
    """Initializes tables for students, lost items, found items, and matches."""
    global conn, cursor
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS students(
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT NOT NULL,
        department TEXT NOT NULL,
        semester   INTEGER NOT NULL,
        username   TEXT UNIQUE NOT NULL,
        password   TEXT NOT NULL
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS lost_items(
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        item_name  TEXT NOT NULL,
        color      TEXT NOT NULL,
        location   TEXT NOT NULL,
        status     TEXT DEFAULT 'Searching',
        date       TEXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS found_items(
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        watchman_name TEXT NOT NULL,
        item_name     TEXT NOT NULL,
        color         TEXT NOT NULL,
        location      TEXT NOT NULL,
        status        TEXT DEFAULT 'Found',
        date          TEXT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS matches(
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        lost_id  INTEGER,
        found_id INTEGER,
        verified TEXT DEFAULT 'Yes',
        date     TEXT
    )""")

    conn.commit()


# ─── Audit Action Logging ─────────────────────────────────────────────────────
def log_action(text: str):
    """Logs system events with an accurate timestamp."""
    try:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {text}\n")
    except Exception as e:
        print(f"Logging error: {e}")


# ─── Design Tokens & Theme Colors ─────────────────────────────────────────────
BG       = "#0F1117"  # Dark primary background
CARD     = "#1A1D2E"  # Elevated card surface
ACCENT   = "#6C63FF"  # Indigo accent
ACCENT2  = "#FF6584"  # Rose accent (Lost/Alerts)
SUCCESS  = "#43D9AD"  # Teal green (Found/Verified)
TEXT     = "#E8EAF6"  # Main text
SUBTEXT  = "#8B8FA8"  # Dimmed subtitle text
BORDER   = "#2D2F45"  # Subtle borders
ENTRY_BG = "#252840"  # Input field background
HOVER_BG = "#7C74FF"  # Button hover state

FONT_TITLE = ("Helvetica Neue", 20, "bold")
FONT_CARD  = ("Helvetica Neue", 13, "bold")
FONT_BODY  = ("Helvetica Neue", 11)
FONT_SMALL = ("Helvetica Neue", 9)
FONT_MONO  = ("Courier New", 10)


# ─── Widget Builders ──────────────────────────────────────────────────────────
def styled_window(parent, title: str, w: int, h: int):
    """Spawns a centered dark-themed secondary dialog window."""
    win = tk.Toplevel(parent)
    win.title(title)
    win.geometry(f"{w}x{h}")
    win.configure(bg=BG)
    win.resizable(False, False)
    win.update_idletasks()
    x = (win.winfo_screenwidth() - w) // 2
    y = (win.winfo_screenheight() - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")
    return win


def card_frame(parent, **kwargs):
    """Creates a stylized elevated frame container."""
    return tk.Frame(
        parent,
        bg=CARD,
        bd=0,
        highlightthickness=1,
        highlightbackground=BORDER,
        **kwargs
    )


def form_label(parent, text: str):
    return tk.Label(parent, text=text, font=FONT_BODY, fg=SUBTEXT, bg=CARD, anchor="w")


def sub_label(parent, text: str, color=SUBTEXT):
    return tk.Label(parent, text=text, font=FONT_SMALL, fg=color, bg=CARD)


def styled_entry(parent, show=None):
    e = tk.Entry(
        parent,
        font=FONT_BODY,
        bg=ENTRY_BG,
        fg=TEXT,
        insertbackground=TEXT,
        relief=tk.FLAT,
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=ACCENT,
        bd=4
    )
    if show:
        e.config(show=show)
    return e


def accent_button(parent, text: str, command, color=ACCENT, width=None):
    cfg = dict(
        text=text,
        command=command,
        font=FONT_BODY,
        bg=color,
        fg="white",
        activebackground=HOVER_BG,
        activeforeground="white",
        cursor="hand2",
        relief=tk.FLAT,
        bd=0,
        padx=14,
        pady=7
    )
    if width:
        cfg["width"] = width
    btn = tk.Button(parent, **cfg)
    btn.bind("<Enter>", lambda _: btn.config(bg=HOVER_BG))
    btn.bind("<Leave>", lambda _: btn.config(bg=color))
    return btn


def ghost_button(parent, text: str, command, width=None):
    cfg = dict(
        text=text,
        command=command,
        font=FONT_BODY,
        bg=CARD,
        fg=ACCENT,
        activebackground=ENTRY_BG,
        activeforeground=ACCENT,
        cursor="hand2",
        relief=tk.FLAT,
        bd=0,
        padx=14,
        pady=7,
        highlightthickness=1,
        highlightbackground=ACCENT
    )
    if width:
        cfg["width"] = width
    return tk.Button(parent, **cfg)


def styled_listbox(parent):
    frame = tk.Frame(parent, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
    sb = tk.Scrollbar(frame, orient=tk.VERTICAL, bg=BORDER, troughcolor=CARD)
    lb = tk.Listbox(
        frame,
        font=FONT_MONO,
        bg=ENTRY_BG,
        fg=TEXT,
        selectbackground=ACCENT,
        selectforeground="white",
        activestyle="none",
        relief=tk.FLAT,
        bd=0,
        yscrollcommand=sb.set
    )
    sb.config(command=lb.yview)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    return frame, lb


def divider(parent):
    return tk.Frame(parent, bg=BORDER, height=1)


# ─── Matching Algorithm Helper ────────────────────────────────────────────────
def is_match(item1: str, color1: str, loc1: str, item2: str, color2: str, loc2: str) -> bool:
    """Smart matching: case-insensitive with keyword, token overlap, and substring tolerance."""
    i1, i2 = item1.strip().lower(), item2.strip().lower()
    c1, c2 = color1.strip().lower(), color2.strip().lower()
    l1, l2 = loc1.strip().lower(), loc2.strip().lower()

    tokens1 = set(w for w in i1.split() if len(w) >= 3)
    tokens2 = set(w for w in i2.split() if len(w) >= 3)
    token_overlap = bool(tokens1 & tokens2)

    item_match = (i1 == i2) or (i1 in i2) or (i2 in i1) or token_overlap
    color_match = (c1 == c2) or (not c1 or not c2) or (c1 in c2) or (c2 in c1)
    loc_match = (l1 == l2) or (l1 in l2) or (l2 in l1)

    return item_match and (color_match or loc_match)


def auto_match(item: str, color: str, loc: str, reporting_type: str = "found"):
    """Scans and alerts if a counterpart report already exists."""
    try:
        if reporting_type == "found":
            cursor.execute("SELECT id, item_name, color, location FROM lost_items WHERE status='Searching'")
            rows = cursor.fetchall()
            counterpart = "Lost"
        else:
            cursor.execute("SELECT id, item_name, color, location FROM found_items WHERE status='Found'")
            rows = cursor.fetchall()
            counterpart = "Found"

        for r in rows:
            if is_match(item, color, loc, r[1], r[2], r[3]):
                messagebox.showinfo(
                    "🔗 Potential Match Detected!",
                    f"A corresponding {counterpart} report exists:\n\n"
                    f"  Item    : {r[1]}\n"
                    f"  Color   : {r[2]}\n"
                    f"  Location: {r[3]}\n\n"
                    "Admins can review and verify this under 'Check Matches'."
                )
                break
    except Exception as e:
        print(f"Auto-match check error: {e}")


# ─── Main Application Window ──────────────────────────────────────────────────
class LostFoundCampusApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Lost & Found — Campus Recovery System")
        self.root.geometry("540x440")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        # Center on screen
        self.root.update_idletasks()
        sx = (self.root.winfo_screenwidth() - 540) // 2
        sy = (self.root.winfo_screenheight() - 440) // 2
        self.root.geometry(f"540x440+{sx}+{sy}")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        try:
            setup_database()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to initialize database:\n{e}")

        self.build_landing_view()

    def on_closing(self):
        """Clean shutdown handler closing the database connection."""
        global conn
        try:
            if conn:
                conn.close()
        except Exception:
            pass
        self.root.destroy()

    def build_landing_view(self):
        card = card_frame(self.root)
        card.place(relx=0.5, rely=0.5, anchor="center", width=480, height=380)

        strip = tk.Frame(card, bg=ACCENT, height=4)
        strip.pack(fill=tk.X)

        inner = tk.Frame(card, bg=CARD)
        inner.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        logo_row = tk.Frame(inner, bg=CARD)
        logo_row.pack(pady=(6, 0))
        tk.Label(logo_row, text="🔍", font=("Helvetica Neue", 26), bg=CARD, fg=ACCENT).pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(logo_row, text="Lost & Found", font=FONT_TITLE, fg=TEXT, bg=CARD).pack(side=tk.LEFT)

        tk.Label(inner, text="SBMP College Campus Recovery Portal", font=FONT_SMALL, fg=SUBTEXT, bg=CARD).pack(pady=(2, 16))
        divider(inner).pack(fill=tk.X, pady=(0, 16))

        tk.Label(inner, text="Select Portal Login", font=FONT_BODY, fg=TEXT, bg=CARD).pack(pady=(0, 12))

        btn_row = tk.Frame(inner, bg=CARD)
        btn_row.pack(pady=4)

        accent_button(btn_row, "🔐  Admin Login", self.open_admin_login, color=ACCENT, width=17).pack(side=tk.LEFT, padx=6)
        accent_button(btn_row, "🎓  Student Login", self.open_student_login, color=ACCENT2, width=17).pack(side=tk.LEFT, padx=6)

        ghost_button(inner, "✨  New Student? Register Here", self.open_student_registration, width=32).pack(pady=(16, 0))

        tk.Label(inner, text="Default Admin: admin / admin", font=FONT_SMALL, fg=BORDER, bg=CARD).pack(side=tk.BOTTOM, pady=(12, 0))

    # ─── Admin Flow ───────────────────────────────────────────────────────────
    def open_admin_login(self):
        w = styled_window(self.root, "Admin Authentication", 360, 320)
        card = card_frame(w)
        card.place(relx=0.5, rely=0.5, anchor="center", width=320, height=280)

        tk.Frame(card, bg=ACCENT, height=4).pack(fill=tk.X)
        f = tk.Frame(card, bg=CARD)
        f.pack(fill=tk.BOTH, expand=True, padx=28, pady=18)

        tk.Label(f, text="🔐  Admin Portal", font=FONT_CARD, fg=TEXT, bg=CARD).pack(pady=(4, 14))

        form_label(f, "Username").pack(anchor="w")
        e_user = styled_entry(f)
        e_user.pack(fill=tk.X, pady=(2, 10))
        e_user.focus_set()

        form_label(f, "Password").pack(anchor="w")
        e_pass = styled_entry(f, show="•")
        e_pass.pack(fill=tk.X, pady=(2, 16))

        def try_login():
            un = e_user.get().strip()
            pw = e_pass.get().strip()
            if not un or not pw:
                messagebox.showwarning("Warning", "Please enter both username and password.", parent=w)
                return
            if un == "admin" and pw == "admin":
                log_action("Admin logged in successfully")
                w.destroy()
                self.open_admin_panel()
            else:
                messagebox.showerror("Access Denied", "Invalid admin credentials.", parent=w)

        e_pass.bind("<Return>", lambda _: try_login())
        accent_button(f, "Sign In", try_login).pack(fill=tk.X)

    def open_admin_panel(self):
        w = styled_window(self.root, "Admin Dashboard", 420, 450)
        card = card_frame(w)
        card.place(relx=0.5, rely=0.5, anchor="center", width=380, height=410)

        tk.Frame(card, bg=ACCENT, height=4).pack(fill=tk.X)
        f = tk.Frame(card, bg=CARD)
        f.pack(fill=tk.BOTH, expand=True, padx=30, pady=18)

        tk.Label(f, text="⚙️  Admin Management", font=FONT_CARD, fg=TEXT, bg=CARD).pack(pady=(4, 2))
        sub_label(f, "Control center for records and matches").pack(pady=(0, 14))
        divider(f).pack(fill=tk.X, pady=(0, 14))

        actions = [
            ("👤  Register New Student", ACCENT, self.open_student_registration),
            ("📦  Report Found Item", SUCCESS, self.open_add_found),
            ("🔴  View Lost Items", ACCENT2, self.open_show_lost),
            ("🟢  View Found Items", SUCCESS, self.open_show_found),
            ("🔗  Check & Verify Matches", ACCENT, self.open_show_matches),
        ]
        for label, color, cmd in actions:
            accent_button(f, label, cmd, color=color).pack(fill=tk.X, pady=4)

    # ─── Student Flow ─────────────────────────────────────────────────────────
    def open_student_login(self):
        w = styled_window(self.root, "Student Authentication", 360, 350)
        card = card_frame(w)
        card.place(relx=0.5, rely=0.5, anchor="center", width=320, height=310)

        tk.Frame(card, bg=ACCENT2, height=4).pack(fill=tk.X)
        f = tk.Frame(card, bg=CARD)
        f.pack(fill=tk.BOTH, expand=True, padx=28, pady=18)

        tk.Label(f, text="🎓  Student Portal", font=FONT_CARD, fg=TEXT, bg=CARD).pack(pady=(4, 14))

        form_label(f, "Username").pack(anchor="w")
        e_user = styled_entry(f)
        e_user.pack(fill=tk.X, pady=(2, 10))
        e_user.focus_set()

        form_label(f, "Password").pack(anchor="w")
        e_pass = styled_entry(f, show="•")
        e_pass.pack(fill=tk.X, pady=(2, 14))

        def try_login():
            un = e_user.get().strip()
            pw = e_pass.get().strip()
            if not un or not pw:
                messagebox.showwarning("Warning", "Please enter both fields.", parent=w)
                return
            try:
                cursor.execute("SELECT * FROM students WHERE username=? AND password=?", (un, pw))
                row = cursor.fetchone()
                if row:
                    log_action(f"Student login: {row[1]} ({row[4]})")
                    w.destroy()
                    self.open_student_panel(row)
                else:
                    messagebox.showerror("Error", "Invalid username or password.", parent=w)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=w)

        e_pass.bind("<Return>", lambda _: try_login())
        accent_button(f, "Sign In", try_login, color=ACCENT2).pack(fill=tk.X)

        ghost_button(f, "Register New Account", self.open_student_registration).pack(fill=tk.X, pady=(10, 0))

    def open_student_registration(self):
        w = styled_window(self.root, "Student Registration", 400, 460)
        card = card_frame(w)
        card.place(relx=0.5, rely=0.5, anchor="center", width=360, height=420)

        tk.Frame(card, bg=ACCENT, height=4).pack(fill=tk.X)
        f = tk.Frame(card, bg=CARD)
        f.pack(fill=tk.BOTH, expand=True, padx=30, pady=18)

        tk.Label(f, text="👤  Student Registration", font=FONT_CARD, fg=TEXT, bg=CARD).pack(pady=(4, 12))

        fields = ["Full Name", "Department", "Semester (1-8)", "Username", "Password"]
        entries = []
        for label in fields:
            form_label(f, label).pack(anchor="w")
            e = styled_entry(f, show="•" if "Password" in label else None)
            e.pack(fill=tk.X, pady=(1, 6))
            entries.append(e)

        entries[0].focus_set()

        def save():
            vals = [e.get().strip() for e in entries]
            if any(not v for v in vals):
                messagebox.showwarning("Incomplete Form", "Please fill in all registration fields.", parent=w)
                return

            try:
                sem = int(vals[2])
                if not (1 <= sem <= 10):
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Validation Error", "Semester must be a valid number between 1 and 10.", parent=w)
                return

            try:
                cursor.execute(
                    "INSERT INTO students(name, department, semester, username, password) VALUES (?, ?, ?, ?, ?)",
                    (vals[0], vals[1], sem, vals[3], vals[4])
                )
                conn.commit()
                log_action(f"New student registered: {vals[0]} ({vals[3]})")
                messagebox.showinfo("Success", "✓ Account registered successfully! You can now log in.", parent=w)
                w.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "That username is already taken. Please choose another.", parent=w)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=w)

        accent_button(f, "Create Account", save).pack(fill=tk.X, pady=(10, 0))

    def open_student_panel(self, student_row):
        w = styled_window(self.root, "Student Portal", 400, 370)
        card = card_frame(w)
        card.place(relx=0.5, rely=0.5, anchor="center", width=360, height=330)

        tk.Frame(card, bg=ACCENT2, height=4).pack(fill=tk.X)
        f = tk.Frame(card, bg=CARD)
        f.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        tk.Label(f, text=f"👋  Welcome, {student_row[1]}", font=FONT_CARD, fg=TEXT, bg=CARD).pack(pady=(4, 2))
        sub_label(f, f"{student_row[2]}  •  Semester {student_row[3]}").pack(pady=(0, 14))
        divider(f).pack(fill=tk.X, pady=(0, 16))

        tk.Label(f, text="What would you like to do?", font=FONT_BODY, fg=SUBTEXT, bg=CARD).pack(pady=(0, 12))

        accent_button(
            f, "🔴  Report a Lost Item",
            lambda: self.open_add_lost(student_row),
            color=ACCENT2
        ).pack(fill=tk.X, pady=5)

        accent_button(
            f, "📋  View My Reported Items",
            lambda: self.open_my_reports(student_row),
            color=ACCENT
        ).pack(fill=tk.X, pady=5)

    # ─── Report Lost & Found ──────────────────────────────────────────────────
    def open_add_lost(self, student_row):
        w = styled_window(self.root, "Report Lost Item", 400, 400)
        card = card_frame(w)
        card.place(relx=0.5, rely=0.5, anchor="center", width=360, height=360)

        tk.Frame(card, bg=ACCENT2, height=4).pack(fill=tk.X)
        f = tk.Frame(card, bg=CARD)
        f.pack(fill=tk.BOTH, expand=True, padx=30, pady=18)

        tk.Label(f, text="🔴  Report Lost Belonging", font=FONT_CARD, fg=TEXT, bg=CARD).pack(pady=(4, 14))

        form_label(f, "Item Name (e.g. Blue Bottle, Calculator)").pack(anchor="w")
        e_item = styled_entry(f)
        e_item.pack(fill=tk.X, pady=(2, 8))

        form_label(f, "Color / Distinguishing Feature").pack(anchor="w")
        e_color = styled_entry(f)
        e_color.pack(fill=tk.X, pady=(2, 8))

        form_label(f, "Last Seen Location / Room").pack(anchor="w")
        e_loc = styled_entry(f)
        e_loc.pack(fill=tk.X, pady=(2, 16))

        def save():
            item = e_item.get().strip()
            color = e_color.get().strip()
            loc = e_loc.get().strip()
            if not item or not color or not loc:
                messagebox.showwarning("Warning", "Please fill in all item fields.", parent=w)
                return

            try:
                date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                cursor.execute(
                    "INSERT INTO lost_items(student_id, item_name, color, location, status, date) VALUES (?, ?, ?, ?, ?, ?)",
                    (student_row[0], item, color, loc, "Searching", date_str)
                )
                conn.commit()
                log_action(f"Lost item reported by {student_row[1]}: {item}")
                messagebox.showinfo("Submitted", "✓ Lost report logged successfully!", parent=w)
                w.destroy()
                auto_match(item, color, loc, reporting_type="lost")
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=w)

        accent_button(f, "Submit Lost Report", save, color=ACCENT2).pack(fill=tk.X)

    def open_add_found(self):
        w = styled_window(self.root, "Report Found Item", 400, 440)
        card = card_frame(w)
        card.place(relx=0.5, rely=0.5, anchor="center", width=360, height=400)

        tk.Frame(card, bg=SUCCESS, height=4).pack(fill=tk.X)
        f = tk.Frame(card, bg=CARD)
        f.pack(fill=tk.BOTH, expand=True, padx=30, pady=18)

        tk.Label(f, text="🟢  Report Found Belonging", font=FONT_CARD, fg=TEXT, bg=CARD).pack(pady=(4, 14))

        form_label(f, "Finder / Staff Name").pack(anchor="w")
        e_finder = styled_entry(f)
        e_finder.pack(fill=tk.X, pady=(2, 8))

        form_label(f, "Item Name").pack(anchor="w")
        e_item = styled_entry(f)
        e_item.pack(fill=tk.X, pady=(2, 8))

        form_label(f, "Color / Feature").pack(anchor="w")
        e_color = styled_entry(f)
        e_color.pack(fill=tk.X, pady=(2, 8))

        form_label(f, "Found Location / Room").pack(anchor="w")
        e_loc = styled_entry(f)
        e_loc.pack(fill=tk.X, pady=(2, 16))

        def save():
            finder = e_finder.get().strip()
            item = e_item.get().strip()
            color = e_color.get().strip()
            loc = e_loc.get().strip()
            if not finder or not item or not color or not loc:
                messagebox.showwarning("Warning", "Please complete all fields.", parent=w)
                return

            try:
                date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                cursor.execute(
                    "INSERT INTO found_items(watchman_name, item_name, color, location, status, date) VALUES (?, ?, ?, ?, ?, ?)",
                    (finder, item, color, loc, "Found", date_str)
                )
                conn.commit()
                log_action(f"Found item logged by {finder}: {item}")
                messagebox.showinfo("Saved", "✓ Found item recorded in registry!", parent=w)
                w.destroy()
                auto_match(item, color, loc, reporting_type="found")
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=w)

        accent_button(f, "Submit Found Report", save, color=SUCCESS).pack(fill=tk.X)

    # ─── Viewing Records ──────────────────────────────────────────────────────
    def open_show_lost(self):
        w = styled_window(self.root, "Lost Items Registry", 620, 420)
        card = card_frame(w)
        card.place(relx=0.5, rely=0.5, anchor="center", width=580, height=380)

        tk.Frame(card, bg=ACCENT2, height=4).pack(fill=tk.X)
        f = tk.Frame(card, bg=CARD)
        f.pack(fill=tk.BOTH, expand=True, padx=16, pady=14)

        hdr = tk.Frame(f, bg=CARD)
        hdr.pack(fill=tk.X, pady=(0, 8))
        tk.Label(hdr, text="🔴  Registered Lost Items", font=FONT_CARD, fg=TEXT, bg=CARD).pack(side=tk.LEFT)

        lb_frame, lb = styled_listbox(f)
        lb_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        item_rows = []

        def refresh():
            lb.delete(0, tk.END)
            item_rows.clear()
            try:
                cursor.execute("SELECT id, item_name, color, location, status, date FROM lost_items")
                rows = cursor.fetchall()
                if not rows:
                    lb.insert(tk.END, "  No lost items recorded.")
                for i, r in enumerate(rows):
                    item_rows.append(r)
                    icon = "⏳" if r[4] == "Searching" else "✅"
                    txt = f"  {icon} #{r[0]} | {r[1]:<16} | {r[2]:<10} | {r[3]:<16} | {r[4]}"
                    lb.insert(tk.END, txt)
                    if r[4] == "Returned":
                        lb.itemconfig(i, fg=SUCCESS)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=w)

        def mark_returned():
            sel = lb.curselection()
            if not sel or not item_rows:
                messagebox.showwarning("Select Item", "Please select an item first.", parent=w)
                return
            item = item_rows[sel[0]]
            try:
                cursor.execute("UPDATE lost_items SET status='Returned' WHERE id=?", (item[0],))
                conn.commit()
                log_action(f"Marked lost item #{item[0]} ({item[1]}) as Returned")
                refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=w)

        btn_bar = tk.Frame(f, bg=CARD)
        btn_bar.pack(fill=tk.X)
        accent_button(btn_bar, "✓  Mark as Returned", mark_returned, color=SUCCESS).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        accent_button(btn_bar, "🔄  Refresh", refresh, color=ACCENT).pack(side=tk.LEFT, padx=(4, 0))

        refresh()

    def open_show_found(self):
        w = styled_window(self.root, "Found Items Registry", 620, 420)
        card = card_frame(w)
        card.place(relx=0.5, rely=0.5, anchor="center", width=580, height=380)

        tk.Frame(card, bg=SUCCESS, height=4).pack(fill=tk.X)
        f = tk.Frame(card, bg=CARD)
        f.pack(fill=tk.BOTH, expand=True, padx=16, pady=14)

        hdr = tk.Frame(f, bg=CARD)
        hdr.pack(fill=tk.X, pady=(0, 8))
        tk.Label(hdr, text="🟢  Registered Found Items", font=FONT_CARD, fg=TEXT, bg=CARD).pack(side=tk.LEFT)

        lb_frame, lb = styled_listbox(f)
        lb_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        item_rows = []

        def refresh():
            lb.delete(0, tk.END)
            item_rows.clear()
            try:
                cursor.execute("SELECT id, item_name, color, location, status, watchman_name FROM found_items")
                rows = cursor.fetchall()
                if not rows:
                    lb.insert(tk.END, "  No found items recorded.")
                for i, r in enumerate(rows):
                    item_rows.append(r)
                    icon = "📦" if r[4] == "Found" else "✅"
                    txt = f"  {icon} #{r[0]} | {r[1]:<16} | {r[2]:<10} | {r[3]:<16} | {r[4]}"
                    lb.insert(tk.END, txt)
                    if r[4] == "Returned":
                        lb.itemconfig(i, fg=SUCCESS)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=w)

        def mark_claimed():
            sel = lb.curselection()
            if not sel or not item_rows:
                messagebox.showwarning("Select Item", "Please select an item first.", parent=w)
                return
            item = item_rows[sel[0]]
            try:
                cursor.execute("UPDATE found_items SET status='Returned' WHERE id=?", (item[0],))
                conn.commit()
                log_action(f"Marked found item #{item[0]} ({item[1]}) as Claimed/Returned")
                refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=w)

        btn_bar = tk.Frame(f, bg=CARD)
        btn_bar.pack(fill=tk.X)
        accent_button(btn_bar, "✓  Mark as Claimed", mark_claimed, color=SUCCESS).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        accent_button(btn_bar, "🔄  Refresh", refresh, color=ACCENT).pack(side=tk.LEFT, padx=(4, 0))

        refresh()

    def open_my_reports(self, student_row):
        w = styled_window(self.root, "My Reported Items", 560, 380)
        card = card_frame(w)
        card.place(relx=0.5, rely=0.5, anchor="center", width=520, height=340)

        tk.Frame(card, bg=ACCENT, height=4).pack(fill=tk.X)
        f = tk.Frame(card, bg=CARD)
        f.pack(fill=tk.BOTH, expand=True, padx=16, pady=14)

        tk.Label(f, text=f"📋  Reports by {student_row[1]}", font=FONT_CARD, fg=TEXT, bg=CARD).pack(anchor="w", pady=(0, 8))

        lb_frame, lb = styled_listbox(f)
        lb_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        my_items = []

        def refresh():
            lb.delete(0, tk.END)
            my_items.clear()
            try:
                cursor.execute("SELECT id, item_name, color, location, status FROM lost_items WHERE student_id=?", (student_row[0],))
                rows = cursor.fetchall()
                if not rows:
                    lb.insert(tk.END, "  You have not submitted any lost reports yet.")
                for i, r in enumerate(rows):
                    my_items.append(r)
                    icon = "⏳" if r[4] == "Searching" else "✅"
                    txt = f"  {icon} #{r[0]} | {r[1]:<18} | {r[2]:<10} | {r[3]:<16} | {r[4]}"
                    lb.insert(tk.END, txt)
                    if r[4] == "Returned":
                        lb.itemconfig(i, fg=SUCCESS)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=w)

        def mark_recovered():
            sel = lb.curselection()
            if not sel or not my_items:
                messagebox.showwarning("Select Item", "Please select an item to update.", parent=w)
                return
            it = my_items[sel[0]]
            try:
                cursor.execute("UPDATE lost_items SET status='Returned' WHERE id=?", (it[0],))
                conn.commit()
                log_action(f"Student marked lost item #{it[0]} as Recovered")
                refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=w)

        btn_bar = tk.Frame(f, bg=CARD)
        btn_bar.pack(fill=tk.X)
        accent_button(btn_bar, "✓  I Found My Item", mark_recovered, color=SUCCESS).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        accent_button(btn_bar, "🔄  Refresh", refresh, color=ACCENT).pack(side=tk.LEFT, padx=(4, 0))

        refresh()

    def open_show_matches(self):
        w = styled_window(self.root, "Item Matches", 600, 420)
        card = card_frame(w)
        card.place(relx=0.5, rely=0.5, anchor="center", width=560, height=380)

        tk.Frame(card, bg=ACCENT, height=4).pack(fill=tk.X)
        f = tk.Frame(card, bg=CARD)
        f.pack(fill=tk.BOTH, expand=True, padx=16, pady=14)

        hdr = tk.Frame(f, bg=CARD)
        hdr.pack(fill=tk.X, pady=(0, 8))
        tk.Label(hdr, text="🔗  Matched Items", font=FONT_CARD, fg=TEXT, bg=CARD).pack(side=tk.LEFT)
        sub_label(hdr, "  Select a pair and verify return").pack(side=tk.LEFT, pady=2)

        lb_frame, lb = styled_listbox(f)
        lb_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        pairs = []

        def refresh():
            lb.delete(0, tk.END)
            pairs.clear()
            try:
                cursor.execute("SELECT id, student_id, item_name, color, location FROM lost_items WHERE status='Searching'")
                lost_list = cursor.fetchall()

                cursor.execute("SELECT id, watchman_name, item_name, color, location FROM found_items WHERE status='Found'")
                found_list = cursor.fetchall()

                count = 0
                for a in lost_list:
                    for b in found_list:
                        if is_match(a[2], a[3], a[4], b[2], b[3], b[4]):
                            line = f"  🔗  Lost #{a[0]} ({a[2]}) ↔ Found #{b[0]} ({b[2]}) | Loc: {a[4]}"
                            lb.insert(tk.END, line)
                            lb.itemconfig(count, fg=SUCCESS)
                            pairs.append({"lid": a[0], "fid": b[0], "name": a[2]})
                            count += 1

                if count == 0:
                    lb.insert(tk.END, "  No active matches found at this time.")
            except Exception as e:
                print(f"Match calculation error: {e}")

        def do_verify():
            sel = lb.curselection()
            if not sel or not pairs:
                messagebox.showwarning("Warning", "Please select a match pair first.", parent=w)
                return
            p = pairs[sel[0]]
            try:
                date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                cursor.execute("UPDATE lost_items SET status='Returned' WHERE id=?", (p["lid"],))
                cursor.execute("UPDATE found_items SET status='Returned' WHERE id=?", (p["fid"],))
                cursor.execute(
                    "INSERT INTO matches(lost_id, found_id, verified, date) VALUES (?, ?, 'Yes', ?)",
                    (p["lid"], p["fid"], date_str)
                )
                conn.commit()
                log_action(f"Verified match: Lost #{p['lid']} matched with Found #{p['fid']}")
                messagebox.showinfo("Verified", "✓ Match verified and items marked as Returned!", parent=w)
                refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=w)

        refresh()
        accent_button(f, "✔  Verify Selected Match", do_verify, color=SUCCESS).pack(fill=tk.X)


# ─── Application Entry Point ──────────────────────────────────────────────────
def main():
    root = tk.Tk()
    app = LostFoundCampusApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
