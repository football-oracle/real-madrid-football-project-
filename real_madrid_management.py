import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import re
import ttkbootstrap as tb
import oracledb

DB_USER, DB_PASSWORD = "madrid", "1212"

DB_HOST, DB_PORT, DB_SERVICE = "localhost", 1522, "orcl"


NAVY, BLUE, GOLD, WHITE, BG = "#102B4C", "#245889", "#E5B13D", "#FFFFFF", "#F1F4F8"
GREEN, RED, TEXT = "#16865B", "#C94343", "#18324F"

TABLES = {
    "Players": {
        "table": "PLAYER", "pk": "PLAYER_ID",
        "fields": [("FIRST_NAME", "First name", "text"), ("LAST_NAME", "Last name", "text"), ("AGE", "Age", "integer"), ("NATIONALITY", "Nationality", "text"), ("POSITION", "Position", "text"), ("PREFERRED_FOOT", "Preferred foot", "choice"), ("HEIGHT_CM", "Height (cm)", "number"), ("WEIGHT_KG", "Weight (kg)", "number"), ("JERSEY_NUMBER", "Jersey number", "integer"), ("SALARY", "Salary", "money"), ("JOINED_DATE", "Joined date (YYYY-MM-DD)", "date"), ("CONTRACT_END_DATE", "Contract end date (YYYY-MM-DD)", "date")],
        "columns": ["PLAYER_ID", "FIRST_NAME", "LAST_NAME", "AGE", "NATIONALITY", "POSITION", "PREFERRED_FOOT", "HEIGHT_CM", "WEIGHT_KG", "JERSEY_NUMBER", "SALARY", "JOINED_DATE", "CONTRACT_END_DATE"],
    },
    "Coaches": {
        "table": "COACH", "pk": "COACH_ID",
        "fields": [("COACH_NAME", "Coach name", "text"), ("AGE", "Age", "integer"), ("NATIONALITY", "Nationality", "text"), ("GAME_STYLE", "Game style", "text"), ("SALARY", "Salary", "money")],
        "columns": ["COACH_ID", "COACH_NAME", "AGE", "NATIONALITY", "GAME_STYLE", "SALARY"],
    },
    "Medical Records": {
        "table": "MEDICAL_RECORD", "pk": "RECORD_ID",
        "fields": [("PLAYER_ID", "Player ID", "integer"), ("INJURY_TYPE", "Injury type", "text"), ("INJURY_DATE", "Injury date (YYYY-MM-DD)", "date"), ("RETURN_DATE", "Return date (YYYY-MM-DD)", "date")],
        "columns": ["RECORD_ID", "PLAYER_ID", "INJURY_TYPE", "INJURY_DATE", "RETURN_DATE"],
    },
    "Achievements": {
        "table": "ACHIEVEMENT", "pk": "ACHIEVEMENT_ID",
        "fields": [("ACHIEVEMENT_NAME", "Achievement name", "text"), ("ACHIEVEMENT_YEAR", "Achievement year", "integer")],
        "columns": ["ACHIEVEMENT_ID", "ACHIEVEMENT_NAME", "ACHIEVEMENT_YEAR"],
    },
    "Stadium": {
        "table": "STADIUM", "pk": "STADIUM_ID",
        "fields": [("STADIUM_NAME", "Stadium name", "text"), ("LOCATION", "Location", "text"), ("CAPACITY", "Capacity", "integer"), ("OPENED_YEAR", "Opened year", "integer")],
        "columns": ["STADIUM_ID", "STADIUM_NAME", "LOCATION", "CAPACITY", "OPENED_YEAR"],
    },
}

class RealMadridApp:
    def __init__(self, root, connection):
        self.root, self.connection = root, connection
        self.root.title("Real Madrid | Management System")
        screen_w, screen_h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{min(1300, max(900, screen_w - 60))}x{min(900, max(600, screen_h - 80))}")
        self.root.minsize(900, 600)
        self.root.configure(bg=BG)
        self.style = tb.Style("flatly")
        self.style.configure("Treeview", rowheight=30, font=("Segoe UI", 9))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        self.entries, self.trees, self.current_ids, self.foot_values = {}, {}, {}, []
        self.build_layout()
        self.show_dashboard()
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

    def load_foot_values(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT search_condition FROM user_constraints WHERE table_name = 'PLAYER' AND constraint_name = 'CHK_PLAYER_FOOT' AND constraint_type = 'C'")
                result = cursor.fetchone()
                if not result or not result[0]: return []
                values = re.findall(r"'((?:''|[^'])*)'", str(result[0]))
                return list(dict.fromkeys([v.replace("''", "'") for v in values]))
        except Exception: return []

    def build_layout(self):
        self.root.grid_rowconfigure(0, weight=1); self.root.grid_columnconfigure(1, weight=1)
        self.sidebar = tk.Frame(self.root, bg=NAVY, width=185); self.sidebar.grid(row=0, column=0, sticky="ns"); self.sidebar.grid_propagate(False)
        self.main_area = tk.Frame(self.root, bg=BG); self.main_area.grid(row=0, column=1, sticky="nsew"); self.main_area.grid_rowconfigure(1, weight=1); self.main_area.grid_columnconfigure(0, weight=1)
        self.build_sidebar(); self.build_header()
        self.content = tk.Frame(self.main_area, bg=BG); self.content.grid(row=1, column=0, sticky="nsew", padx=14, pady=12)
        self.status = tk.Label(self.main_area, text="Oracle database connected", bg=WHITE, fg=BLUE, anchor="w", font=("Segoe UI", 9), padx=12, pady=7); self.status.grid(row=2, column=0, sticky="ew")

    def build_sidebar(self):
        logo = tk.Frame(self.sidebar, bg=NAVY); logo.pack(fill="x", pady=(22, 15))
        tk.Label(logo, text="REAL MADRID", bg=NAVY, fg=WHITE, font=("Segoe UI", 17, "bold")).pack()
        tk.Label(logo, text="MANAGEMENT SYSTEM", bg=NAVY, fg=GOLD, font=("Segoe UI", 8, "bold")).pack(pady=(5, 0))
        tk.Frame(self.sidebar, bg=GOLD, height=2).pack(fill="x", padx=15, pady=15)
        self.nav_buttons = {}
        for name in ["Dashboard", "Players", "Coaches", "Medical Records", "Achievements", "Stadium", "Update Center"]:
            btn = tk.Button(self.sidebar, text=f"    {name}", bg=NAVY, fg=WHITE, activebackground=BLUE, activeforeground=WHITE, font=("Segoe UI", 10, "bold"), relief="flat", bd=0, anchor="w", padx=15, pady=12, cursor="hand2", command=lambda n=name: self.open_page(n))
            btn.pack(fill="x", padx=8, pady=2); self.nav_buttons[name] = btn
        tk.Frame(self.sidebar, bg="#34516D", height=1).pack(fill="x", padx=15, pady=15)
        tk.Label(self.sidebar, text="ORACLE 19c", bg=NAVY, fg=GOLD, font=("Segoe UI", 9, "bold")).pack(side="bottom", pady=20)

    def build_header(self):
        header = tk.Frame(self.main_area, bg=WHITE, height=62); header.grid(row=0, column=0, sticky="ew"); header.grid_propagate(False)
        self.header_title = tk.Label(header, text="Dashboard", bg=WHITE, fg=NAVY, font=("Segoe UI", 16, "bold")); self.header_title.pack(side="left", padx=22, pady=15)
        tk.Label(header, text="DATABASE CONNECTED", bg=WHITE, fg=GREEN, font=("Segoe UI", 8, "bold")).pack(side="right", padx=18)

    def clear_content(self):
        for widget in self.content.winfo_children(): widget.destroy()

    def set_status(self, message): self.status.config(text=message)
    def open_page(self, name): self.show_dashboard() if name == "Dashboard" else (self.show_update_center() if name == "Update Center" else self.show_table_page(name))
    def update_navigation(self, selected):
        for name, button in self.nav_buttons.items(): button.config(bg=BLUE if name == selected else NAVY)

    def show_dashboard(self):
        self.clear_content(); self.header_title.config(text="Dashboard"); self.update_navigation("Dashboard")
        tk.Label(self.content, text="Welcome to Real Madrid", bg=BG, fg=NAVY, font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(5, 3))
        tk.Label(self.content, text="Football Team Management System", bg=BG, fg="#718096", font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 15))
        banner = tk.Frame(self.content, bg=NAVY, height=110); banner.pack(fill="x", pady=(0, 15)); banner.pack_propagate(False)
        tk.Label(banner, text="HALA MADRID", bg=NAVY, fg=GOLD, font=("Segoe UI", 24, "bold")).pack(pady=(20, 2))
        tk.Label(banner, text="THE ROYAL CLUB  |  FOOTBALL MANAGEMENT", bg=NAVY, fg=WHITE, font=("Segoe UI", 9, "bold")).pack()
        tk.Label(self.content, text="DATABASE OVERVIEW", bg=BG, fg=NAVY, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(3, 8))
        cards = tk.Frame(self.content, bg=BG); cards.pack(fill="both", expand=True)
        for col in range(3): cards.grid_columnconfigure(col, weight=1, uniform="card")
        for index, name in enumerate(TABLES):
            config = TABLES[name]; count = self.get_count(config["table"]); row, col = index // 3, index % 3
            cards.grid_rowconfigure(row, weight=1, uniform="row")
            card = tk.Frame(cards, bg=WHITE, highlightbackground="#DCE3EB", highlightthickness=1); card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
            inner = tk.Frame(card, bg=WHITE); inner.pack(fill="both", expand=True, padx=13, pady=10)
            tk.Label(inner, text=name, bg=WHITE, fg=NAVY, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(2,0))
            tk.Label(inner, text=str(count), bg=WHITE, fg=BLUE, font=("Segoe UI", 24, "bold")).pack(anchor="w", pady=(2, 5))
            tk.Button(inner, text="OPEN SECTION", bg=BLUE, fg=WHITE, activebackground=NAVY, activeforeground=WHITE, relief="flat", cursor="hand2", font=("Segoe UI", 8, "bold"), command=lambda n=name: self.show_table_page(n)).pack(anchor="e")
        self.set_status("Dashboard | Database statistics loaded.")

    def get_count(self, table):
        try:
            with self.connection.cursor() as cursor: cursor.execute(f"SELECT COUNT(*) FROM {table}"); return cursor.fetchone()[0]
        except oracledb.Error: return "N/A"

    def show_update_center(self):
        self.clear_content(); self.header_title.config(text="Update Center"); self.update_navigation("Update Center")
        tk.Label(self.content, text="Update Center", bg=BG, fg=NAVY, font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(5, 3))
        tk.Label(self.content, text="Select a table below to modify its records.", bg=BG, fg="#718096", font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 20))
        
        # Added Total Salary Button right here in Update Center
        self.make_action_button(self.content, "Show Total Salary (Players & Coaches)", GOLD, self.show_all_total_salary).pack(fill="x", pady=(0, 15), ipady=8)
        
        menu_frame = tk.Frame(self.content, bg=BG); menu_frame.pack(fill="both", expand=True)
        for i in range(2): menu_frame.grid_columnconfigure(i, weight=1, uniform="menu")
        for i in range(3): menu_frame.grid_rowconfigure(i, weight=1, uniform="menur")
        for idx, (name, config) in enumerate(TABLES.items()):
            row, col = idx // 2, idx % 2
            btn_frame = tk.Frame(menu_frame, bg=WHITE, highlightbackground="#DCE3EB", highlightthickness=1); btn_frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
            inner_btn = tk.Button(btn_frame, text=f"Edit {name}", bg=WHITE, fg=NAVY, font=("Segoe UI", 14, "bold"), relief="flat", cursor="hand2", activebackground="#E9EEF5", activeforeground=NAVY, command=lambda n=name: self.show_table_page(n))
            inner_btn.pack(fill="both", expand=True, pady=20)

    def show_all_total_salary(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT FN_TOTAL_SALARY('PLAYER'), FN_TOTAL_SALARY('COACH') FROM DUAL")
                result = cursor.fetchone()
                player_total = result[0] if result[0] else 0
                coach_total = result[1] if result[1] else 0
            messagebox.showinfo("Total Salaries", f"Total Players Salary: ${player_total:,.2f}\n\nTotal Coaches Salary: ${coach_total:,.2f}")
        except oracledb.Error as error: 
            messagebox.showerror("Database Error", str(error))

    def show_table_page(self, name):
        self.clear_content(); self.current_ids[name] = None; config = TABLES[name]
        self.header_title.config(text=f"Manage {name}"); self.update_navigation(name)
        heading = tk.Frame(self.content, bg=BG); heading.pack(fill="x", pady=(0, 10))
        tk.Label(heading, text=f"Manage {name}", bg=BG, fg=NAVY, font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tk.Label(heading, text="Click a row on the right to load it into the form, then click 'UPDATE SELECTED'.", bg=BG, fg="#718096", font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))
        body = tk.Frame(self.content, bg=BG); body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=0); body.grid_columnconfigure(1, weight=1); body.grid_rowconfigure(0, weight=1)
        form_panel = tk.Frame(body, bg=WHITE, width=290, highlightbackground="#D8E0E9", highlightthickness=1); form_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10)); form_panel.grid_propagate(False)
        tk.Label(form_panel, text="RECORD INFORMATION", bg=NAVY, fg=WHITE, font=("Segoe UI", 10, "bold"), anchor="w", padx=12, pady=11).pack(fill="x")
        fields_area = tk.Frame(form_panel, bg=WHITE); fields_area.pack(fill="both", expand=True, padx=8, pady=5)
        canvas = tk.Canvas(fields_area, bg=WHITE, highlightthickness=0); scrollbar = ttk.Scrollbar(fields_area, orient="vertical", command=canvas.yview); canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y"); canvas.pack(side="left", fill="both", expand=True)
        fields_frame = tk.Frame(canvas, bg=WHITE); canvas_window = canvas.create_window((0, 0), window=fields_frame, anchor="nw")
        fields_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(canvas_window, width=e.width))
        self.entries[name] = {}
        if name == "Players": self.foot_values = self.load_foot_values()
        field_widgets = []
        for column, label, field_type in config["fields"]:
            field_box = tk.Frame(fields_frame, bg=WHITE); field_box.pack(fill="x", padx=7, pady=5)
            tk.Label(field_box, text=label, bg=WHITE, fg=TEXT, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 4))
            if field_type == "choice" and self.foot_values:
                entry = ttk.Combobox(field_box, values=self.foot_values, state="readonly", font=("Segoe UI", 10)); entry.current(0)
            else: entry = ttk.Entry(field_box, font=("Segoe UI", 10))
            entry.pack(fill="x", ipady=4); field_widgets.append(entry); self.entries[name][column] = (entry, field_type)
        for i, widget in enumerate(field_widgets):
            widget.bind("<Return>", (lambda e, w=field_widgets[i+1]: w.focus_set()) if i < len(field_widgets) - 1 else (lambda e: self.add_record(name)))
        actions = tk.Frame(form_panel, bg="#E9EEF5", padx=8, pady=8); actions.pack(fill="x", side="bottom")
        self.make_action_button(actions, "ADD RECORD", GREEN, lambda: self.add_record(name)).pack(fill="x", pady=3)
        self.make_action_button(actions, "UPDATE SELECTED", BLUE, lambda: self.update_record(name)).pack(fill="x", pady=3)
        self.make_action_button(actions, "DELETE SELECTED", RED, lambda: self.delete_record(name)).pack(fill="x", pady=3)
        self.make_action_button(actions, "Back to Menu", NAVY, lambda: self.show_update_center()).pack(fill="x", pady=(10, 3))
        if name in ["Players", "Coaches"]: self.make_action_button(actions, "Show Total Salary", GOLD, lambda: self.show_total_salary(name)).pack(fill="x", pady=3)
        table_panel = tk.Frame(body, bg=WHITE, highlightbackground="#D8E0E9", highlightthickness=1); table_panel.grid(row=0, column=1, sticky="nsew")
        table_heading = tk.Frame(table_panel, bg=WHITE); table_heading.pack(fill="x", padx=12, pady=10)
        tk.Label(table_heading, text="DATABASE RECORDS", bg=WHITE, fg=NAVY, font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(table_heading, text="Select a row to update or delete", bg=WHITE, fg="#718096", font=("Segoe UI", 8)).pack(side="right")
        tree_frame = tk.Frame(table_panel, bg=WHITE); tree_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        tree = ttk.Treeview(tree_frame, columns=config["columns"], show="headings", selectmode="browse"); self.trees[name] = tree
        for column in config["columns"]: tree.heading(column, text=column.replace("_", " ").title()); tree.column(column, width=130, minwidth=90, anchor="center")
        y_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview); x_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        tree.grid(row=0, column=0, sticky="nsew"); y_scroll.grid(row=0, column=1, sticky="ns"); x_scroll.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1); tree_frame.grid_columnconfigure(0, weight=1)
        tree.bind("<<TreeviewSelect>>", lambda event, n=name: self.on_select(n))
        self.refresh_table(name)

    def make_action_button(self, parent, text, color, command):
        return tk.Button(parent, text=text, bg=color, fg=WHITE, activebackground=NAVY, activeforeground=WHITE, font=("Segoe UI", 9, "bold"), relief="flat", bd=0, cursor="hand2", pady=9, command=command)

    def convert_value(self, value, field_type, column):
        value = value.strip()
        if value == "": return None
        if field_type == "integer":
            try: return int(value)
            except ValueError: raise ValueError(f"{column} must be a whole number.")
        if field_type == "money":
            try: return float(re.sub(r'[$, ]', '', value))
            except ValueError: raise ValueError(f"{column} must be a valid money amount.")
        if field_type == "number":
            try: return float(value)
            except ValueError: raise ValueError(f"{column} must be a number.")
        if field_type == "date":
            try: return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError: raise ValueError(f"{column} must use YYYY-MM-DD format.")
        return value

    def get_form_values(self, name): return {column: self.convert_value(entry.get(), field_type, column) for column, (entry, field_type) in self.entries[name].items()}

    def validate_values(self, name, values):
        req = {"Players": ["FIRST_NAME", "LAST_NAME", "PREFERRED_FOOT", "JERSEY_NUMBER"], "Coaches": ["COACH_NAME"], "Medical Records": ["PLAYER_ID", "INJURY_TYPE", "INJURY_DATE"], "Achievements": ["ACHIEVEMENT_NAME", "ACHIEVEMENT_YEAR"], "Stadium": ["STADIUM_NAME"]}
        for column in req.get(name, []):
            if values.get(column) is None: raise ValueError(f"{column.replace('_', ' ').title()} is required.")
        if name == "Players" and self.foot_values and values["PREFERRED_FOOT"] not in self.foot_values: raise ValueError("Please select a valid Preferred Foot value.")

    def add_record(self, name):
        config = TABLES[name]
        try:
            values = self.get_form_values(name); self.validate_values(name, values)
            columns = [config["pk"]] + list(values.keys()); expressions = [":new_id"]; binds = {"new_id": None}
            for column, value in values.items():
                bind_name = f"v_{column.lower()}"
                if (config["table"] == "PLAYER" and column == "JOINED_DATE" and value is None) or (config["table"] == "MEDICAL_RECORD" and column == "INJURY_DATE" and value is None): expressions.append("SYSDATE")
                else: expressions.append(f":{bind_name}"); binds[bind_name] = value
            sql = f"INSERT INTO {config['table']} ({', '.join(columns)}) VALUES ({', '.join(expressions)})"
            with self.connection.cursor() as cursor: cursor.execute(sql, binds)
            self.connection.commit(); self.refresh_table(name); self.clear_form(name)
            messagebox.showinfo("Success", f"New {name} record added successfully.")
            self.set_status(f"{name}: new record added successfully.")
        except ValueError as error: messagebox.showerror("Input error", str(error))
        except oracledb.Error as error: self.connection.rollback(); messagebox.showerror("Oracle error", str(error))

    def update_record(self, name):
        config = TABLES[name]; selected_id = self.current_ids.get(name)
        if selected_id is None: messagebox.showwarning("Select record", "Please select a record from the table first."); return
        try:
            values = self.get_form_values(name); self.validate_values(name, values)
            assignments = []; binds = {"record_id": selected_id}
            for column, value in values.items():
                if column == config["pk"]: continue
                bind_name = f"v_{column.lower()}"; assignments.append(f"{column} = :{bind_name}"); binds[bind_name] = value
            sql = f"UPDATE {config['table']} SET {', '.join(assignments)} WHERE {config['pk']} = :record_id"
            with self.connection.cursor() as cursor:
                cursor.execute(sql, binds)
                if cursor.rowcount == 0: raise ValueError("Record was not found.")
            self.connection.commit(); self.refresh_table(name); self.clear_form(name)
            messagebox.showinfo("Updated", "Record updated successfully.")
            self.set_status(f"{name}: record updated.")
        except ValueError as error: self.connection.rollback(); messagebox.showerror("Update error", str(error))
        except oracledb.Error as error: self.connection.rollback(); messagebox.showerror("Oracle error", str(error))

    def delete_record(self, name):
        config = TABLES[name]; selected_id = self.current_ids.get(name)
        if selected_id is None: messagebox.showwarning("Select record", "Please select a record from the table first."); return
        if not messagebox.askyesno("Confirm deletion", f"Are you sure you want to delete record {selected_id}?"): return
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM {config['table']} WHERE {config['pk']} = :record_id", {"record_id": selected_id})
                if cursor.rowcount == 0: raise ValueError("Record was not found.")
            self.connection.commit(); self.refresh_table(name); self.clear_form(name)
            messagebox.showinfo("Deleted", "Record deleted successfully.")
            self.set_status(f"{name}: record deleted.")
        except ValueError as error: self.connection.rollback(); messagebox.showerror("Delete error", str(error))
        except oracledb.Error as error: self.connection.rollback(); messagebox.showerror("Oracle error", "Could not delete this record.\n\nIf this player has medical records, delete those related records first.\n\n" + str(error))

    def show_total_salary(self, name):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT FN_TOTAL_SALARY(:tbl) FROM DUAL", {"tbl": "PLAYER" if name == "Players" else "COACH"})
                total = cursor.fetchone()[0]
            messagebox.showinfo("Total Salary", f"The total salary for all {name} is:\n\n${total:,.2f}")
        except oracledb.Error as error: messagebox.showerror("Database Error", str(error))

    def refresh_table(self, name):
        config = TABLES[name]; tree = self.trees.get(name)
        if tree is None or not tree.winfo_exists(): return
        for item in tree.get_children(): tree.delete(item)
        select_columns = [f"FN_FORMAT_MONEY({col}) AS {col}" if col == "SALARY" else col for col in config["columns"]]
        sql = f"SELECT {', '.join(select_columns)} FROM {config['table']} ORDER BY {config['pk']}"
        with self.connection.cursor() as cursor:
            cursor.execute(sql); rows = cursor.fetchall()
            for row in rows:
                display_values = [value.strftime("%Y-%m-%d") if isinstance(value, (datetime, date)) else ("" if value is None else str(value)) for value in row]
                tree.insert("", "end", values=display_values)
        self.set_status(f"{name}: {len(rows)} records loaded.")

    def on_select(self, name):
        config = TABLES[name]; tree = self.trees[name]; selected = tree.selection()
        if not selected: return
        row_data = dict(zip(config["columns"], tree.item(selected[0], "values")))
        self.current_ids[name] = row_data[config["pk"]]
        for column, (entry, field_type) in self.entries[name].items():
            value = row_data.get(column, "")
            if isinstance(entry, ttk.Combobox): entry.set(value)
            else: entry.delete(0, tk.END); entry.insert(0, value)
        self.set_status(f"Selected record ID: {self.current_ids[name]}")

    def clear_form(self, name):
        self.current_ids[name] = None
        for entry, field_type in self.entries[name].values():
            if isinstance(entry, ttk.Combobox): entry.set("")
            else: entry.delete(0, tk.END)
        tree = self.trees.get(name)
        if tree and tree.winfo_exists():
            for selected in tree.selection(): tree.selection_remove(selected)

    def close_app(self):
        try: self.connection.close()
        except Exception: pass
        self.root.destroy()

def main():
    dsn = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE}"
    try: connection = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=dsn)
    except oracledb.Error as error:
        temp = tk.Tk(); temp.withdraw(); messagebox.showerror("Oracle Connection Error", f"Could not connect to Oracle.\n\n{error}"); temp.destroy(); return
    root = tb.Window(themename="flatly")
    app = RealMadridApp(root, connection)
    root.mainloop()

if __name__ == "__main__":
    main()