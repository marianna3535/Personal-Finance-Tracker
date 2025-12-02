#Librarys imported
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
from datetime import datetime
import os
from collections import defaultdict
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

#Saves the file when you're done using it
DATA_FILE = os.path.join(os.path.expanduser("~"), ".personal_finance_data.json")

#Main application functions
class FinanceTrackerApp:

    DATE_FORMAT = "%Y-%m-%d"

    #Window size and basic format
    def __init__(window, box):
        window.box = box
        window.box.title("Personal Finance Tracker")
        window.box.geometry("1000x800")

        window.transactions = []
        window.load_data()

        window.build_interactive()
        window.refresh_table()
        window.update_summary()

    #Interactions/Structure of the application
    def build_interactive(window):
        top = ttk.Frame(window.box)
        top.pack(side=tk.TOP, fill=tk.X, padx=12, pady=8)

        ttk.Label(top, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(top, text="Amount *+/-*:").grid(row=0, column=2, sticky=tk.W)
        ttk.Label(top, text="Category:").grid(row=0, column=4, sticky=tk.W)
        ttk.Label(top, text="Description:").grid(row=0, column=6, sticky=tk.W)

        window.date_var = tk.StringVar()
        window.amount_var = tk.StringVar()
        window.category_var = tk.StringVar()
        window.description_var = tk.StringVar()

        ttk.Entry(top, textvariable=window.date_var, width=15).grid(row=0, column=1, padx=4)
        ttk.Entry(top, textvariable=window.amount_var, width=15).grid(row=0, column=3, padx=4)
        ttk.Entry(top, textvariable=window.category_var, width=15).grid(row=0, column=5, padx=4)
        ttk.Entry(top, textvariable=window.description_var, width=30).grid(row=0, column=7, padx=4)

        ttk.Button(top, text="Add Transaction", command=window.on_add).grid(row=0, column=8, padx=8)

     
        middle_frame = ttk.Frame(window.box)
        middle_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        filter_frame = ttk.LabelFrame(middle_frame, text="Filters")
        filter_frame.pack(side=tk.TOP, fill=tk.X, padx=4, pady=4)

        ttk.Label(filter_frame, text="From:").grid(row=0, column=0)
        ttk.Label(filter_frame, text="To:").grid(row=0, column=2)
        ttk.Label(filter_frame, text="Category:").grid(row=0, column=4)

        window.from_var = tk.StringVar()
        window.to_var = tk.StringVar()
        window.filter_category_var = tk.StringVar()
        window.filter_category_var.set("All")

        ttk.Entry(filter_frame, textvariable=window.from_var, width=12).grid(row=0, column=1, padx=4)
        ttk.Entry(filter_frame, textvariable=window.to_var, width=12).grid(row=0, column=3, padx=4)
        window.category_combo = ttk.Combobox(filter_frame, textvariable=window.filter_category_var, values=window.get_category_list(), state="readonly", width=18)
        window.category_combo.grid(row=0, column=5, padx=4)

        ttk.Button(filter_frame, text="Apply Filters", command=window.apply_filters).grid(row=0, column=6, padx=6)
        ttk.Button(filter_frame, text="Clear Filters", command=window.clear_filters).grid(row=0, column=7)

        table_frame = ttk.Frame(middle_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("Date", "Amount", "Category", "Description")
        window.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            window.tree.heading(col, text=col.title())
            window.tree.column(col, anchor=tk.W, width=150)
        window.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=window.tree.yview)
        window.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        right = ttk.Frame(window.box)
        right.pack(fill=tk.X, padx=10, pady=6)

        ttk.Button(right, text="Edit Selected", command=window.edit_selected).pack(side=tk.LEFT, padx=6)
        ttk.Button(right, text="Delete Selected", command=window.delete_selected).pack(side=tk.LEFT, padx=6)
        ttk.Button(right, text="Categorys of Spending (Pie Chart)", command=lambda: window.show_category_chart(kind="pie")).pack(side=tk.LEFT, padx=6)
        ttk.Button(right, text="Categorys of Spending (Bar Chart)", command=lambda: window.show_category_chart(kind="bar")).pack(side=tk.LEFT, padx=6)
        ttk.Button(right, text="Export CSV", command=window.export_csv).pack(side=tk.RIGHT, padx=6)

        bottom = ttk.LabelFrame(window.box, text="Summary")
        bottom.pack(side=tk.BOTTOM, fill=tk.X, padx=12, pady=6)

        window.income_label = ttk.Label(bottom, text="Total Income: $0.00")
        window.expense_label = ttk.Label(bottom, text="Total Expenses: $0.00")
        window.balance_label = ttk.Label(bottom, text="Balance: $0.00")

        window.income_label.pack(side=tk.LEFT, padx=10)
        window.expense_label.pack(side=tk.LEFT, padx=10)
        window.balance_label.pack(side=tk.LEFT, padx=10)

    #Sorts the list by category
    def get_category_list(window):
        cats = {t["category"] for t in window.transactions if t.get("category")}
        lst = sorted(cats)
        return ["All"] + lst

    #When saved data is opened it will go into the table
    def load_data(window):
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    window.transactions = json.load(f)
            else:
                window.transactions = []
        except Exception as e:
            messagebox.showwarning("Load Error", f"Could not load data file: {e}")
            window.transactions = []

    #Saves data in JSON 
    def save_data(window):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(window.transactions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save data: {e}")

    #ensures all values are in the correct format
    def validate_input(window, date_str, amount_str):
        try:
            datetime.strptime(date_str, window.DATE_FORMAT)
        except Exception:
            messagebox.showerror("Invalid Date", f"Date must be in {window.DATE_FORMAT} format")
            return False
        try:
            float(amount_str)
        except Exception:
            messagebox.showerror("Invalid Amount", "Amount must be a number (use negative for expenses)" )
            return False
        return True

    #adds transaction to table
    def on_add(window):
        date = window.date_var.get().strip()
        amount = window.amount_var.get().strip()
        category = window.category_var.get().strip() or "Uncategorized"
        desc = window.description_var.get().strip()

        #Invalid pop up 
        if not date or not amount:
            messagebox.showwarning("Missing Data", "Please supply both date and amount")
            return

        if not window.validate_input(date, amount):
            return

        try:
            amt = float(amount)
        except Exception:
            messagebox.showerror("Invalid Amount", "Amount must be a number")
            return

        new = {"date": date, "amount": amt, "category": category, "description": desc}
        window.transactions.append(new)
        window.save_data()
        window.clear_input_fields()
        window.refresh_table()
        window.update_summary()
        window.category_combo.configure(values=window.get_category_list())

    #Clears input values from table
    def clear_input_fields(window):
        window.date_var.set("")
        window.amount_var.set("")
        window.category_var.set("")
        window.description_var.set("")

    #refreshes table of values
    def refresh_table(window, filtered=None):
        for r in window.tree.get_children():
            window.tree.delete(r)
        data = filtered if filtered is not None else window.transactions

        try:
            data_sorted = sorted(data, key=lambda t: t.get("date", ""), reverse=True)
        except Exception:
            data_sorted = data
        for t in data_sorted:
            window.tree.insert("", tk.END, values=(t.get("date"), f"{t.get('amount'):.2f}", t.get("category"), t.get("description")))

    #Deletes transactions
    def delete_selected(window):
        sel = window.tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Please select a transaction to delete")
            return
        indx = window.tree.index(sel[0])
       
        vals = window.tree.item(sel[0], "values")
        
        for i, t in enumerate(window.transactions):
            if (t.get("date"), f"{t.get('amount'):.2f}", t.get("category"), t.get("description")) == vals:
                del window.transactions[i]
                break
        window.save_data()
        window.refresh_table()
        window.update_summary()
        window.category_combo.configure(values=window.get_category_list())

#edits transactions
    def edit_selected(window):
        sel = window.tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Please select a transaction to edit")
            return
        vals = window.tree.item(sel[0], "values")
       
        for i, t in enumerate(window.transactions):
            if (t.get("date"), f"{t.get('amount'):.2f}", t.get("category"), t.get("description")) == vals:
                window.open_edit_window(i)
                return
        messagebox.showerror("Not found", "Could not find the selected transaction in data")

    #places the values on the table 
    def open_edit_window(window, index):
        t = window.transactions[index]
        win = tk.Toplevel(window.box)
        win.title("Edit Transaction")
        win.transient(window.box)

        ttk.Label(win, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky=tk.W, padx=6, pady=4)
        ttk.Label(win, text="Amount:").grid(row=1, column=0, sticky=tk.W, padx=6, pady=4)
        ttk.Label(win, text="Category:").grid(row=2, column=0, sticky=tk.W, padx=6, pady=4)
        ttk.Label(win, text="Description:").grid(row=3, column=0, sticky=tk.W, padx=6, pady=4)

        dvar = tk.StringVar(value=t.get("date"))
        avar = tk.StringVar(value=str(t.get("amount")))
        cvar = tk.StringVar(value=t.get("category"))
        desvar = tk.StringVar(value=t.get("description"))

        ttk.Entry(win, textvariable=dvar).grid(row=0, column=1, padx=6, pady=4)
        ttk.Entry(win, textvariable=avar).grid(row=1, column=1, padx=6, pady=4)
        ttk.Entry(win, textvariable=cvar).grid(row=2, column=1, padx=6, pady=4)
        ttk.Entry(win, textvariable=desvar).grid(row=3, column=1, padx=6, pady=4)

    #Edits dates, ampunt, description and category
        def save_edit():
            ndate = dvar.get().strip()
            namount = avar.get().strip()
            ncat = cvar.get().strip() or "Uncategorized"
            ndes = desvar.get().strip()
            if not window.validate_input(ndate, namount):
                return
            window.transactions[index] = {"date": ndate, "amount": float(namount), "category": ncat, "description": ndes}
            window.save_data()
            window.refresh_table()
            window.update_summary()
            window.category_combo.configure(values=window.get_category_list())
            win.destroy()

        ttk.Button(win, text="Save", command=save_edit).grid(row=4, column=0, columnspan=2, pady=8)

       #Filters for sorting 
    def apply_filters(window):
        from_date = window.from_var.get().strip()
        to_date = window.to_var.get().strip()
        category = window.filter_category_var.get()

        def in_range(d):
            try:
                if from_date:
                    if d < from_date:
                        return False
                if to_date:
                    if d > to_date:
                        return False
            except Exception:
                return False
            return True

        filtered = []
        for t in window.transactions:
            if category and category != "All" and t.get("category") != category:
                continue
            if from_date or to_date:
                if not in_range(t.get("date", "")):
                    continue
            filtered.append(t)
        window.refresh_table(filtered=filtered)

    #Clears Filters
    def clear_filters(window):
        window.from_var.set("")
        window.to_var.set("")
        window.filter_category_var.set("All")
        window.refresh_table()

        #Exports transactions
    def export_csv(window):
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files','*.csv'),('All files','*.*')])
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["date","amount","category","description"])
                writer.writeheader()
                for t in window.transactions:
                    writer.writerow(t)
            messagebox.showinfo("Exported", f"Data exported to {path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export CSV: {e}")

    #Calculates totals for each Category
    def aggregate_expenses_by_category(window):
        total = defaultdict(float)

        for t in window.transactions:
            amt = t.get('amount', 0)
            category = t.get('category', 'Uncategorized')
            if amt < 0:
                total[category] += abs(amt)
            else:
                total["Income"] += amt

        return dict(total)

    #Charts to compare Values
    def show_category_chart(window, kind='pie'):
        cat_totals = window.aggregate_expenses_by_category()
        if not cat_totals:
            messagebox.showinfo("No data", "No expense data to chart")
            return

        win = tk.Toplevel(window.box)
        win.title("Spending, Income vs Expense")
        win.geometry("600x500")

        fig = Figure(figsize=(6,5), dpi=100)
        ax = fig.add_subplot(111)

        labels = list(cat_totals.keys())
        values = list(cat_totals.values())

        if kind == 'pie':
            ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.set_title('Spending, Income vs Expense')
        else:
            ax.bar(labels, values)
            ax.set_title('Spending, Income vs Expense')
            ax.set_ylabel('Amount')
            ax.tick_params(axis='x', rotation=45)

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    #Bottom summary of total income, expense, and balance
    def update_summary(window):
        income = sum(t.get('amount',0) for t in window.transactions if t.get('amount',0) > 0)
        expenses = sum(t.get('amount',0) for t in window.transactions if t.get('amount',0) < 0)
        balance = income + expenses
        window.income_label.config(text=f"Total Income: ${income:.2f}")
        window.expense_label.config(text=f"Total Expenses: ${abs(expenses):.2f}")
        window.balance_label.config(text=f"Balance: ${balance:.2f}")

#Keeps it running
if __name__ == '__main__':
    box = tk.Tk()
    app = FinanceTrackerApp(box)
    box.mainloop()
