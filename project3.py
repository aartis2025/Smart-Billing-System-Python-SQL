import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

# ========== DATABASE SETUP ==========
conn = sqlite3.connect("billing_system.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS bills(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    items TEXT,
    subtotal REAL,
    gst REAL,
    total REAL
)
""")
conn.commit()

# ========== MAIN APPLICATION ==========
root = tk.Tk()
root.title("Aarti Smart Billing System")
root.geometry("700x600")
root.config(bg="#f5f5f5")

# ---------- VARIABLES ----------
item_name = tk.StringVar()
item_qty = tk.StringVar()
item_price = tk.StringVar()
gst_rate = tk.DoubleVar(value=18.0)
subtotal = 0
items_list = []

# ---------- FUNCTIONS ----------
def add_item():
    global subtotal
    name = item_name.get()
    try:
        qty = int(item_qty.get())
        price = float(item_price.get())
    except:
        messagebox.showerror("Error", "Enter valid quantity and price")
        return

    if name == "":
        messagebox.showwarning("Missing", "Enter item name")
        return

    total = qty * price
    subtotal += total
    items_list.append((name, qty, price, total))

    bill_table.insert("", "end", values=(name, qty, price, total))

    item_name.set("")
    item_qty.set("")
    item_price.set("")

def generate_bill():
    global subtotal
    if not items_list:
        messagebox.showwarning("Empty", "Add items first")
        return

    gst = subtotal * (gst_rate.get() / 100)
    final_total = subtotal + gst

    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    items_text = "; ".join([f"{i[0]}({i[1]}x{i[2]})" for i in items_list])

    cursor.execute("INSERT INTO bills (date, items, subtotal, gst, total) VALUES (?, ?, ?, ?, ?)",
                   (date_str, items_text, subtotal, gst, final_total))
    conn.commit()

    # Show Bill Summary
    messagebox.showinfo("Bill Generated",
                        f"Subtotal: ₹{subtotal:.2f}\nGST ({gst_rate.get()}%): ₹{gst:.2f}\nTotal: ₹{final_total:.2f}")

    # Reset
    reset_fields()

def reset_fields():
    global subtotal, items_list
    item_name.set("")
    item_qty.set("")
    item_price.set("")
    subtotal = 0
    items_list = []
    for i in bill_table.get_children():
        bill_table.delete(i)

def show_history():
    hist_window = tk.Toplevel(root)
    hist_window.title("Bill History")
    hist_window.geometry("600x400")

    cols = ("ID", "Date", "Items", "Total")
    tree = ttk.Treeview(hist_window, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=130)
    tree.pack(fill=tk.BOTH, expand=True)

    cursor.execute("SELECT id, date, items, total FROM bills ORDER BY id DESC")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

# ---------- GUI LAYOUT ----------
tk.Label(root, text="Aarti Smart Billing System", font=("Helvetica", 18, "bold"), bg="#f5f5f5").pack(pady=10)

frame = tk.Frame(root, bg="#f5f5f5")
frame.pack(pady=10)

tk.Label(frame, text="Item Name:", bg="#f5f5f5").grid(row=0, column=0, padx=5, pady=5)
tk.Entry(frame, textvariable=item_name, width=25).grid(row=0, column=1)

tk.Label(frame, text="Quantity:", bg="#f5f5f5").grid(row=1, column=0, padx=5, pady=5)
tk.Entry(frame, textvariable=item_qty, width=25).grid(row=1, column=1)

tk.Label(frame, text="Price per Item:", bg="#f5f5f5").grid(row=2, column=0, padx=5, pady=5)
tk.Entry(frame, textvariable=item_price, width=25).grid(row=2, column=1)

tk.Button(frame, text="Add Item", command=add_item, bg="#4CAF50", fg="black", width=15).grid(row=3, column=0, columnspan=2, pady=10)

# ---------- BILL TABLE ----------
cols = ("Item Name", "Qty", "Price", "Total")
bill_table = ttk.Treeview(root, columns=cols, show="headings", height=10)
for col in cols:
    bill_table.heading(col, text=col)
    bill_table.column(col, width=150)
bill_table.pack(pady=10)

# ---------- BUTTONS ----------
bottom_frame = tk.Frame(root, bg="#f5f5f5")
bottom_frame.pack(pady=10)

tk.Label(bottom_frame, text="GST %:", bg="#f5f5f5").grid(row=0, column=0, padx=5)
tk.Entry(bottom_frame, textvariable=gst_rate, width=8).grid(row=0, column=1)

tk.Button(bottom_frame, text="Generate Bill", command=generate_bill, bg="#FFC0CB", fg="black", width=15).grid(row=0, column=2, padx=10)
tk.Button(bottom_frame, text="Reset", command=reset_fields, bg="#FFC0CB", fg="black", width=15).grid(row=0, column=3, padx=10)
tk.Button(bottom_frame, text="View History", command=show_history, bg="#FFC0CB", fg="black", width=15).grid(row=0, column=4, padx=10)

root.mainloop()