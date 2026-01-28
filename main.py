# main.py
# SBMP College Lost and Found System
# Made by: Aryan Yadav
# Diploma Computer Science Project

import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import sqlite3
import csv
import os
from datetime import datetime
from typing import List, Tuple, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ==========================================
# 🎨 CONSTANTS & CONFIGURATION
# ==========================================
DB_NAME = "college_data.db"
WINDOW_SIZE = "1100x800"

# Theme Colors 
BG_DARK = "#121212"
BG_CARD = "#1e1e1e"
BG_INPUT = "#2d2d2d"
TEXT_WHITE = "#ffffff"
TEXT_GRAY = "#a0a0a0"
ACCENT_BLUE = "#3b82f6"
ACCENT_GREEN = "#22c55e"
ACCENT_RED = "#ef4444"
ACCENT_PURPLE = "#a855f7"
BORDER_COLOR = "#333333"

# ==========================================
# 📊 DATABASE SETUP
# ==========================================

def setup_database() -> None:
    """Initializes the SQLite database and creates necessary tables."""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # LOST ITEMS TABLE
        c.execute("""
            CREATE TABLE IF NOT EXISTS lost_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                roll_no TEXT NOT NULL,
                item_name TEXT NOT NULL,
                room_no TEXT,
                date TEXT,
                category TEXT DEFAULT 'Other',
                status TEXT DEFAULT 'Pending'
            )
        """)
        
        # FOUND ITEMS TABLE
        c.execute("""
            CREATE TABLE IF NOT EXISTS found_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                finder_name TEXT,
                item_name TEXT NOT NULL,
                room_no TEXT,
                date TEXT,
                category TEXT DEFAULT 'Other',
                status TEXT DEFAULT 'Available'
            )
        """)
        
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Database Error: {e}")

# ==========================================
# 🖥️ MAIN APPLICATION
# ==========================================

class LostFoundApp:
    def __init__(self, root: tk.Tk):
        """Initializes the main application window and layout."""
        self.root = root
        self.root.title("SBMP | Assets & Recovery System")
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(bg=BG_DARK)
        
        setup_database()

        # Handle Window Close (Low Fix #102)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # UI Sidebar
        sidebar = tk.Frame(self.root, bg=BG_CARD, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        tk.Label(sidebar, text="SBMP", font=("Arial", 22, "bold"), bg=BG_CARD, fg=ACCENT_BLUE).pack(pady=(40, 5))
        tk.Label(sidebar, text="Portal Management", font=("Arial", 10), bg=BG_CARD, fg=TEXT_GRAY).pack(pady=(0, 40))
        
        # Navigation Menu
        self.add_nav_btn(sidebar, "🏠 Dashboard", self.show_dashboard, "View system overview")
        self.add_nav_btn(sidebar, "📋 Add Lost", self.show_add_lost, "Report a lost item")
        self.add_nav_btn(sidebar, "🔍 Add Found", self.show_add_found, "Log a recovered item")
        self.add_nav_btn(sidebar, "📦 Inventory", self.show_all_items, "View all records")
        self.add_nav_btn(sidebar, "📊 Analytics", self.show_analytics, "View statistical graphs")
        self.add_nav_btn(sidebar, "💾 Export", self.export_data, "Backup data to CSV")
        self.add_nav_btn(sidebar, "ℹ️ About", self.show_about, "Project info") # Low Fix #66
        self.add_nav_btn(sidebar, "❓ Help", self.show_help, "User guide")     # Low Fix #67
        
        tk.Label(sidebar, text="v2.6 Stable Build", font=("Arial", 8), bg=BG_CARD, fg=BORDER_COLOR).pack(side="bottom", pady=20)
        
        # Status Bar (Low Fix #69)
        self.status_bar = tk.Label(self.root, text="System Ready", bd=1, relief="sunken", anchor="w", bg=BG_CARD, fg=TEXT_GRAY, font=("Arial", 9))
        self.status_bar.pack(side="bottom", fill="x")

        # Main Content
        self.content = tk.Frame(self.root, bg=BG_DARK)
        self.content.pack(side="left", fill="both", expand=True, padx=25, pady=25)
        
        self.show_dashboard()

    def on_closing(self):
        """LOW FIX #102: Confirmation on closing."""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            self.root.destroy()

    def update_status(self, msg: str):
        """Updates the status bar message."""
        self.status_bar.config(text=f" Status: {msg}")

    def add_nav_btn(self, parent: tk.Frame, text: str, command: callable, tooltip: str = "") -> None:
        """Helper to create menu buttons with hover effects."""
        btn = tk.Button(parent, text=text, font=("Arial", 11, "bold"), bg=BG_CARD, fg=TEXT_WHITE,
                       activebackground=BG_INPUT, activeforeground=ACCENT_BLUE, bd=0, 
                       padx=20, pady=12, anchor="w", cursor="hand2", command=command)
        btn.pack(fill="x")
        btn.bind("<Enter>", lambda e: [btn.config(bg=BG_INPUT), self.update_status(tooltip)])
        btn.bind("<Leave>", lambda e: [btn.config(bg=BG_CARD), self.update_status("System Ready")])
    
    def clear_ui(self) -> None:
        """Clears the main content area for new page load."""
        for widget in self.content.winfo_children():
            widget.destroy()

    # ==========================================
    # PAGE: DASHBOARD
    # ==========================================
    def show_dashboard(self) -> None:
        self.clear_ui()
        tk.Label(self.content, text="OVERVIEW DASHBOARD", font=("Arial", 20, "bold"), bg=BG_DARK, fg=TEXT_WHITE).pack(pady=(0, 20), anchor="w")
        
        stats_frame = tk.Frame(self.content, bg=BG_DARK)
        stats_frame.pack(fill="x")
        
        conn = sqlite3.connect(DB_NAME)
        lost_c = conn.execute("SELECT COUNT(*) FROM lost_items WHERE status='Pending'").fetchone()[0]
        found_c = conn.execute("SELECT COUNT(*) FROM found_items WHERE status='Available'").fetchone()[0]
        conn.close()
        
        self.draw_card(stats_frame, "ACTIVE LOSSES", lost_c, ACCENT_RED)
        self.draw_card(stats_frame, "ITEMS RECOVERED", found_c, ACCENT_GREEN)
        self.draw_card(stats_frame, "STATUS", "STABLE", ACCENT_BLUE)

        # Room Match Logic
        tk.Label(self.content, text="Room-Match Suggestions", font=("Arial", 14, "bold"), bg=BG_DARK, fg=TEXT_WHITE).pack(pady=(40, 10), anchor="w")
        
        list_f = tk.Frame(self.content, bg=BG_CARD, bd=1, relief="solid", highlightbackground=BORDER_COLOR)
        list_f.pack(fill="both", expand=True)
        
        lb = tk.Listbox(list_f, bg=BG_CARD, fg=TEXT_WHITE, font=("Arial", 11), bd=0, highlightthickness=0)
        lb.pack(fill="both", expand=True, padx=10, pady=10)
        
        conn = sqlite3.connect(DB_NAME)
        matches = conn.execute("""
            SELECT l.student_name, l.item_name, l.room_no 
            FROM lost_items l JOIN found_items f ON l.room_no = f.room_no 
            WHERE l.status='Pending' AND f.status='Available' AND l.room_no != ''
        """).fetchall()
        conn.close()
        
        if not matches:
            lb.insert(tk.END, " No potential room overlaps found.")
        else:
            for m in matches:
                lb.insert(tk.END, f" 🔔 {m[0]} lost '{m[1]}' - Item match in Room {m[2]}")

    def draw_card(self, parent: tk.Frame, title: str, val: any, color: str) -> None:
        c = tk.Frame(parent, bg=BG_CARD, padx=30, pady=25, bd=1, relief="solid", highlightbackground=BORDER_COLOR)
        c.pack(side="left", expand=True, fill="both", padx=10)
        tk.Label(c, text=title, font=("Arial", 10, "bold"), bg=BG_CARD, fg=TEXT_GRAY).pack()
        tk.Label(c, text=str(val), font=("Arial", 28, "bold"), bg=BG_CARD, fg=color).pack(pady=5)

    # ==========================================
    # PAGE: ADD LOST / FOUND
    # ==========================================
    def show_add_lost(self) -> None:
        self.clear_ui()
        tk.Label(self.content, text="REPORT NEW LOSS", font=("Arial", 20, "bold"), bg=BG_DARK, fg=TEXT_WHITE).pack(pady=10, anchor="w")
        
        f = tk.Frame(self.content, bg=BG_CARD, padx=40, pady=40, bd=1, relief="solid", highlightbackground=BORDER_COLOR)
        f.pack(pady=20)
        
        self.l_name = self.add_entry(f, "Student Name*", 0)
        self.l_roll = self.add_entry(f, "Roll Number*", 1)
        self.l_item = self.add_entry(f, "Item Lost*", 2)
        self.l_room = self.add_entry(f, "Room No", 3)
        
        tk.Label(f, text="Category:", bg=BG_CARD, fg=TEXT_WHITE).grid(row=4, column=0, sticky="w", pady=10)
        self.l_cat = ttk.Combobox(f, values=["Electronics", "Keys", "Documents", "Bottle", "Wallet", "Other"])
        self.l_cat.set("Other"); self.l_cat.grid(row=4, column=1, padx=10, pady=10)
        
        tk.Button(self.content, text="COMMIT TO RECORD", bg=ACCENT_BLUE, fg="white", font=("Arial", 12, "bold"), 
                  padx=40, pady=12, bd=0, command=self.save_lost).pack(pady=20)

    def add_entry(self, parent: tk.Frame, label: str, row: int) -> tk.Entry:
        tk.Label(parent, text=label+":", bg=BG_CARD, fg=TEXT_WHITE).grid(row=row, column=0, sticky="w", pady=10)
        e = tk.Entry(parent, width=35, bg=BG_INPUT, fg=TEXT_WHITE, insertbackground="white", bd=0, highlightthickness=1)
        e.grid(row=row, column=1, padx=10, pady=10); return e

    def save_lost(self) -> None:
        n, r, i, rm, cat = self.l_name.get(), self.l_roll.get(), self.l_item.get(), self.l_room.get(), self.l_cat.get()
        if not n or not i:
            messagebox.showerror("Error", "Required fields (*) are missing!")
            return
        
        conn = sqlite3.connect(DB_NAME)
        conn.execute("INSERT INTO lost_items (student_name, roll_no, item_name, room_no, date, category) VALUES (?,?,?,?,?,?)",
                    (n, r, i, rm, datetime.now().strftime("%Y-%m-%d"), cat))
        conn.commit(); conn.close()
        messagebox.showinfo("Success", "Incident Logged."); self.show_dashboard()

    def show_add_found(self) -> None:
        self.clear_ui()
        tk.Label(self.content, text="LOG ASSET RECOVERY", font=("Arial", 20, "bold"), bg=BG_DARK, fg=TEXT_WHITE).pack(pady=10, anchor="w")
        f = tk.Frame(self.content, bg=BG_CARD, padx=40, pady=40, bd=1, relief="solid")
        f.pack(pady=20)
        
        self.f_name = self.add_entry(f, "Finder Name", 0)
        self.f_item = self.add_entry(f, "Item Name*", 1)
        self.f_room = self.add_entry(f, "Room Found", 2)
        
        tk.Label(f, text="Category:", bg=BG_CARD, fg=TEXT_WHITE).grid(row=3, column=0, sticky="w", pady=10)
        self.f_cat = ttk.Combobox(f, values=["Electronics", "Keys", "Documents", "Bottle", "Wallet", "Other"])
        self.f_cat.set("Other"); self.f_cat.grid(row=3, column=1, padx=10, pady=10)
        
        tk.Button(self.content, text="LOG TO VAULT", bg=ACCENT_GREEN, fg="white", font=("Arial", 12, "bold"), 
                  padx=40, pady=12, bd=0, command=self.save_found).pack(pady=20)

    def save_found(self) -> None:
        n, i, rm, cat = self.f_name.get(), self.f_item.get(), self.f_room.get(), self.f_cat.get()
        if not i: messagebox.showerror("Error", "Item name is needed."); return
        conn = sqlite3.connect(DB_NAME)
        conn.execute("INSERT INTO found_items (finder_name, item_name, room_no, date, category) VALUES (?,?,?,?,?)",
                    (n, i, rm, datetime.now().strftime("%Y-%m-%d"), cat))
        conn.commit(); conn.close()
        messagebox.showinfo("Logged", "Record Added."); self.show_dashboard()

    # ==========================================
    # PAGE: INVENTORY & EDIT
    # ==========================================
    def show_all_items(self) -> None:
        self.clear_ui()
        tk.Label(self.content, text="SYSTEM INVENTORY", font=("Arial", 20, "bold"), bg=BG_DARK, fg=TEXT_WHITE).pack(pady=10, anchor="w")
        
        top = tk.Frame(self.content, bg=BG_DARK)
        top.pack(fill="x", pady=10)
        
        self.search_in = tk.Entry(top, bg=BG_INPUT, fg=TEXT_WHITE, width=35, bd=0)
        self.search_in.pack(side="left", pady=10)
        tk.Button(top, text="🔍 Refresh", bg=ACCENT_BLUE, fg="white", command=self.refresh_list).pack(side="left", padx=10)
        
        tk.Label(top, text="Filter:", bg=BG_DARK, fg=TEXT_GRAY).pack(side="left", padx=(20, 5))
        self.filter_val = ttk.Combobox(top, values=["All", "Lost", "Found"], width=10)
        self.filter_val.set("All"); self.filter_val.pack(side="left")
        
        # Low Fix #77: Count Label
        self.count_label = tk.Label(top, text="", bg=BG_DARK, fg=ACCENT_GREEN, font=("Arial", 10, "bold"))
        self.count_label.pack(side="right")

        f = tk.Frame(self.content, bg=BG_CARD)
        f.pack(fill="both", expand=True)
        
        self.lb = tk.Listbox(f, bg=BG_INPUT, fg=TEXT_WHITE, font=("Arial", 11), bd=0, selectbackground=ACCENT_BLUE)
        self.lb.pack(fill="both", expand=True, padx=5, pady=5)
        self.lb.bind("<Double-Button-1>", self.open_manager)
        
        self.refresh_list()

    def refresh_list(self) -> None:
        self.lb.delete(0, tk.END)
        self.lb_map = {}
        q = f"%{self.search_in.get()}%"
        flt = self.filter_val.get()
        conn = sqlite3.connect(DB_NAME)
        
        total_items = 0
        
        if flt in ["All", "Lost"]:
            lost = conn.execute("SELECT * FROM lost_items WHERE item_name LIKE ? OR student_name LIKE ?", (q, q)).fetchall()
            for r in lost:
                # Low Fix #76 & #80: Formatting Date and showing ID
                date_obj = datetime.strptime(r[5], "%Y-%m-%d")
                friendly_date = date_obj.strftime("%d %b %Y")
                self.lb.insert(tk.END, f" #{r[0]} | [Lost] {r[3]} - {r[1]} | {friendly_date}")
                self.lb_map[self.lb.size()-1] = ("lost", r[0])
                self.lb.itemconfig(tk.END, fg=ACCENT_RED) # Low Fix #81: Visual distinction
                total_items += 1
        
        if flt in ["All", "Found"]:
            found = conn.execute("SELECT * FROM found_items WHERE item_name LIKE ?", (q,)).fetchall()
            for r in found:
                date_obj = datetime.strptime(r[4], "%Y-%m-%d")
                friendly_date = date_obj.strftime("%d %b %Y")
                self.lb.insert(tk.END, f" #{r[0]} | [Found] {r[2]} - by {r[1]} | {friendly_date}")
                self.lb_map[self.lb.size()-1] = ("found", r[0])
                self.lb.itemconfig(tk.END, fg=ACCENT_GREEN) # Low Fix #81: Visual distinction
                total_items += 1
        conn.close()
        self.count_label.config(text=f"Total: {total_items} items")

    def open_manager(self, event) -> None:
        idx = self.lb.curselection()
        if not idx or idx[0] not in self.lb_map: return
        tab, rid = self.lb_map[idx[0]]
        
        pop = tk.Toplevel(self.root)
        pop.title("Edit Record")
        pop.geometry("400x300"); pop.configure(bg=BG_CARD)
        
        tk.Label(pop, text="MODIFY RECORD", font=("Arial", 12, "bold"), bg=BG_CARD, fg=ACCENT_BLUE).pack(pady=20)
        
        def resolve():
            conn = sqlite3.connect(DB_NAME)
            st = "Resolved" if tab == "lost" else "Claimed"
            conn.execute(f"UPDATE {tab}_items SET status=? WHERE id=?", (st, rid))
            conn.commit(); conn.close(); pop.destroy(); self.refresh_list()
            
        def delete():
            if messagebox.askyesno("Delete", "Delete record forever?"):
                conn = sqlite3.connect(DB_NAME)
                conn.execute(f"DELETE FROM {tab}_items WHERE id=?", (rid,))
                conn.commit(); conn.close(); pop.destroy(); self.refresh_list()

        tk.Button(pop, text="✅ Resolve / Mark Claimed", bg=ACCENT_GREEN, width=25, command=resolve).pack(pady=10)
        tk.Button(pop, text="🗑️ Delete Permanently", bg=ACCENT_RED, width=25, command=delete).pack(pady=10)

    # ==========================================
    # PAGE: ANALYTICS
    # ==========================================
    def show_analytics(self) -> None:
        self.clear_ui()
        tk.Label(self.content, text="CAMPUS ANALYTICS", font=("Arial", 20, "bold"), bg=BG_DARK, fg=TEXT_WHITE).pack(pady=10, anchor="w")
        
        conn = sqlite3.connect(DB_NAME)
        data = conn.execute("SELECT category, COUNT(*) FROM lost_items GROUP BY category").fetchall()
        conn.close()
        
        if not data:
            tk.Label(self.content, text="No analytical data found.", bg=BG_DARK, fg=TEXT_GRAY).pack(pady=100)
            return

        cats = [x[0] for x in data]; cnts = [x[1] for x in data]
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(6, 5))
        fig.patch.set_facecolor(BG_DARK)
        ax.pie(cnts, labels=cats, autopct='%1.1f%%', colors=[ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED, ACCENT_PURPLE, "orange"])
        ax.set_title("Lost Items by Category", color=TEXT_WHITE)
        
        canv = FigureCanvasTkAgg(fig, master=self.content)
        canv.draw(); canv.get_tk_widget().pack(pady=20)

    def export_data(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if not path: return
        conn = sqlite3.connect(DB_NAME)
        data = conn.execute("SELECT * FROM lost_items").fetchall()
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Roll", "Item", "Room", "Date", "Category", "Status"])
            writer.writerows(data)
        conn.close()
        messagebox.showinfo("Success", "Backup generated.")

    # ==========================================
    # LOW FIXES: INFO PAGES
    # ==========================================
    def show_about(self) -> None:
        """Low Fix #66: About Page."""
        self.clear_ui()
        tk.Label(self.content, text="ABOUT PROJECT", font=("Arial", 20, "bold"), bg=BG_DARK, fg=TEXT_WHITE).pack(pady=10, anchor="w")
        info = (
            "SBMP Lost & Found System v2.6\n\n"
            "Developed by: Aryan Yadav\n"
            "Diploma Computer Science Project\n\n"
            "Features:\n"
            "- SQLite Database Persistence\n"
            "- Room Matching Algorithm\n"
            "- Category Classification\n"
            "- Data Analytics & Visualization\n"
            "- CSV Export Module"
        )
        tk.Label(self.content, text=info, font=("Arial", 12), bg=BG_DARK, fg=TEXT_WHITE, justify="left").pack(pady=20, anchor="w")

    def show_help(self) -> None:
        """Low Fix #67: Help Page."""
        self.clear_ui()
        tk.Label(self.content, text="USER GUIDE / HELP", font=("Arial", 20, "bold"), bg=BG_DARK, fg=TEXT_WHITE).pack(pady=10, anchor="w")
        guide = (
           "1. Dashboard: Overview of active reports.\n"
           "2. Add Lost: Fill details to report something you lost.\n"
           "3. Add Found: Fill details if you found an item on campus.\n"
           "4. Inventory: Search and double-click entries to resolve or delete them.\n"
           "5. Analytics: View graphs of lost items.\n"
           "6. Export: Save database as CSV for offline records.\n\n"
           "Tip: Double-click an item in Inventory to mark it as found!"
        )
        tk.Frame(self.content, bg=BG_CARD, padx=20, pady=20).pack(fill="x", pady=10)
        tk.Label(self.content, text=guide, font=("Arial", 11), bg=BG_DARK, fg=TEXT_GRAY, justify="left").pack(pady=10, anchor="w")

# RUN
if __name__ == "__main__":
    rt = tk.Tk()
    app = LostFoundApp(rt)
    rt.mainloop()
