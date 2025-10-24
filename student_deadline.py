import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap import Style
import json
from datetime import datetime, timedelta

class DeadlineTracker:
    def __init__(self, master):
        self.master = master
        self.master.title("Enhanced Deadline Tracker")
        self.master.geometry("900x600")
        self.style = Style(theme="flatly")

        self.assignments = self.load_assignments()

# Added comment
        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for adding assignments
        left_frame = ttk.Frame(main_frame, padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        ttk.Label(left_frame, text="Add New Assignment", font=("TkDefaultFont", 16, "bold")).pack(pady=(0, 10))

        fields = [("Subject:", "subject"), ("Title:", "title"), ("Deadline:", "deadline")]
        for label_text, attribute in fields:
            ttk.Label(left_frame, text=label_text).pack(anchor="w")
            setattr(self, f"{attribute}_entry", ttk.Entry(left_frame, width=40))
            getattr(self, f"{attribute}_entry").pack(fill=tk.X, pady=(0, 10))

        ttk.Label(left_frame, text="Format: YYYY-MM-DD", font=("TkDefaultFont", 8)).pack(anchor="w")

        ttk.Label(left_frame, text="Priority:").pack(anchor="w")
        self.priority_combobox = ttk.Combobox(left_frame, values=["Low", "Medium", "High"], state="readonly")
        self.priority_combobox.set("Medium")
        self.priority_combobox.pack(fill=tk.X, pady=(0, 10))

        add_button = ttk.Button(left_frame, text="Add Assignment", command=self.add_assignment, style="success.TButton")
        add_button.pack(fill=tk.X, pady=(10, 0))

        # Right frame for displaying assignments
        right_frame = ttk.Frame(main_frame, padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(right_frame, text="Upcoming Deadlines", font=("TkDefaultFont", 16, "bold")).pack(pady=(0, 10))

        # Create a frame for the treeview and scrollbar
        tree_frame = ttk.Frame(right_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=("Subject", "Title", "Deadline", "Days Left", "Priority"), show="headings", style="info.Treeview")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col))
            self.tree.column(col, anchor="center")

        self.update_treeview()

        # Buttons for actions
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="Complete", command=self.complete_assignment, style="success.TButton").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Delete", command=self.delete_assignment, style="danger.TButton").pack(side=tk.LEFT)

# Added comment
    def add_assignment(self):
        subject = self.subject_entry.get()
        title = self.title_entry.get()
        deadline = self.deadline_entry.get()
        priority = self.priority_combobox.get()

        if not all([subject, title, deadline, priority]):
            self.show_error("All fields are required!")
            return

        try:
            deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError:
# Added comment
            self.show_error("Invalid date format. Use YYYY-MM-DD.")
            return

        assignment = {
            "subject": subject,
            "title": title,
            "deadline": deadline,
            "priority": priority
        }

        self.assignments.append(assignment)
        self.save_assignments()
        self.update_treeview()
        self.clear_entries()
        self.show_success(f"Assignment '{title}' added successfully!")

    def update_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        sorted_assignments = sorted(self.assignments, key=lambda x: datetime.strptime(x['deadline'], "%Y-%m-%d"))

        for i, assignment in enumerate(sorted_assignments):
            deadline_date = datetime.strptime(assignment['deadline'], "%Y-%m-%d")
            days_left = (deadline_date - datetime.now()).days
            item = self.tree.insert("", "end", values=(
                assignment['subject'],
                assignment['title'],
                assignment['deadline'],
                days_left,
                assignment['priority']
            ))
            self.tree.item(item, tags=(assignment['priority'].lower(),))

        self.style.configure("Low.Treeview", foreground="green")
        self.style.configure("Medium.Treeview", foreground="orange")
        self.style.configure("High.Treeview", foreground="red")

    def complete_assignment(self):
        selected_item = self.tree.selection()
        if not selected_item:
            self.show_info("Please select an assignment to complete.")
            return

        item = self.tree.item(selected_item)
        assignment = next((a for a in self.assignments if a['title'] == item['values'][1]), None)
        if assignment:
            self.assignments.remove(assignment)
            self.save_assignments()
            self.animate_item_removal(selected_item)
            self.show_success(f"Assignment '{assignment['title']}' marked as completed!")

    def delete_assignment(self):
        selected_item = self.tree.selection()
        if not selected_item:
            self.show_info("Please select an assignment to delete.")
            return

        item = self.tree.item(selected_item)
        assignment = next((a for a in self.assignments if a['title'] == item['values'][1]), None)
        if assignment:
            self.assignments.remove(assignment)
            self.save_assignments()
            self.animate_item_removal(selected_item)
            self.show_success(f"Assignment '{assignment['title']}' deleted!")

    def animate_item_removal(self, item):
        def fade_out(alpha):
            if alpha > 0:
                self.tree.tag_configure("fade", foreground=f"gray{int(alpha/255*100)}")
                self.tree.item(item, tags=("fade",))
                self.master.after(50, fade_out, alpha - 25)
            else:
                self.tree.delete(item)
                self.update_treeview()

        fade_out(255)

    def clear_entries(self):
        for entry in [self.subject_entry, self.title_entry, self.deadline_entry]:
            entry.delete(0, tk.END)
        self.priority_combobox.set("Medium")

    def load_assignments(self):
        try:
            with open("assignments.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def save_assignments(self):
        with open("assignments.json", "w") as file:
            json.dump(self.assignments, file)

    def sort_treeview(self, col):
# Added comment
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        items.sort(reverse=self.tree.heading(col).get('reverse', False))
        for index, (val, k) in enumerate(items):
            self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda: self.sort_treeview(col), text=col)
        self.tree.heading(col, reverse=not self.tree.heading(col).get('reverse', False))

    def show_message(self, title, message, message_type):
        messagebox.showinfo(title, message) if message_type == "info" else \
        messagebox.showwarning(title, message) if message_type == "warning" else \
        messagebox.showerror(title, message)

    def show_info(self, message):
        self.show_message("Info", message, "info")

    def show_error(self, message):
        self.show_message("Error", message, "error")

    def show_success(self, message):
        self.show_message("Success", message, "info")

if __name__ == "__main__":
    root = tk.Tk()
    app = DeadlineTracker(root)
    root.mainloop()