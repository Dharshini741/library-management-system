import sqlite3
from tkinter import *
from tkinter import messagebox
from datetime import date, timedelta
from PIL import Image, ImageTk
import os

# ---------------- DATABASE ----------------
conn = sqlite3.connect("library.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS books(
    book_id INTEGER PRIMARY KEY,
    title TEXT,
    author TEXT,
    quantity INTEGER,
    category TEXT,
    reference INTEGER DEFAULT 0
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS students(
    student_id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS issues(
    issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER,
    student_id INTEGER,
    issue_date TEXT,
    due_date TEXT,
    return_date TEXT,
    status TEXT DEFAULT 'Not Returned'
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS policies(
    category TEXT PRIMARY KEY,
    max_books INTEGER,
    issue_days INTEGER,
    fine_rate REAL
)
""")

cur.execute("INSERT OR IGNORE INTO policies VALUES ('General', 3, 14, 1.0)")
cur.execute("INSERT OR IGNORE INTO policies VALUES ('Reference', 1, 0, 0.0)")
conn.commit()

# ---------------- GUI ----------------
root = Tk()
root.title("Advanced Policy-Driven Library System")
root.geometry("900x700")

# ---------------- BACKGROUND IMAGE (ONLY ADDITION) ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BG_PATH = os.path.join(BASE_DIR, "library_bg.png")

bg_img = Image.open(BG_PATH)
bg_img = bg_img.resize((1500, 900))
bg_photo = ImageTk.PhotoImage(bg_img)

bg_label = Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# ---------------- BOOK ----------------
def add_book():
    def submit():
        try:
            ref = 1 if ref_var.get() else 0
            cur.execute(
                "INSERT INTO books VALUES (?,?,?,?,?,?)",
                (int(bid.get()), title.get(), author.get(), int(qty.get()), category.get(), ref)
            )
            conn.commit()
            messagebox.showinfo("Success", f"Book '{title.get()}' added.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", e)

    win = Toplevel(root)
    win.title("Add Book")

    Label(win, text="Book ID").grid(row=0, column=0)
    bid = Entry(win); bid.grid(row=0, column=1)

    Label(win, text="Title").grid(row=1, column=0)
    title = Entry(win); title.grid(row=1, column=1)

    Label(win, text="Author").grid(row=2, column=0)
    author = Entry(win); author.grid(row=2, column=1)

    Label(win, text="Quantity").grid(row=3, column=0)
    qty = Entry(win); qty.grid(row=3, column=1)

    Label(win, text="Category").grid(row=4, column=0)
    category = Entry(win); category.grid(row=4, column=1)

    ref_var = IntVar()
    Checkbutton(win, text="Reference Book (Cannot be issued)", variable=ref_var).grid(row=5, columnspan=2)

    Button(win, text="Add Book", command=submit).grid(row=6, columnspan=2, pady=5)

def view_books():
    win = Toplevel(root)
    win.title("Books")
    text = Text(win, width=120, height=30)
    text.pack()
    cur.execute("SELECT * FROM books")
    for b in cur.fetchall():
        ref_status = "Yes" if b[5] else "No"
        text.insert(END, f"ID:{b[0]}  Title:{b[1]}  Author:{b[2]}  Qty:{b[3]}  Category:{b[4]}  Reference:{ref_status}\n")

        # ---------------- DELETE BOOK ----------------
def delete_book():
    def submit():
        bid_v = bid.get()
        cur.execute("SELECT * FROM books WHERE book_id=?", (bid_v,))
        if not cur.fetchone():
            messagebox.showerror("Error", "Book ID not found")
            return
        cur.execute("DELETE FROM books WHERE book_id=?", (bid_v,))
        conn.commit()
        messagebox.showinfo("Deleted", "Book deleted successfully")
        win.destroy()

    win = Toplevel(root)
    win.title("Delete Book")

    Label(win, text="Book ID").grid(row=0, column=0)
    bid = Entry(win); bid.grid(row=0, column=1)

    Button(win, text="Delete Book", command=submit).grid(row=1, columnspan=2, pady=5)

# ---------------- STUDENT ----------------
def add_student():
    def submit():
        try:
            cur.execute(
                "INSERT INTO students VALUES (?,?,?)",
                (int(sid.get()), name.get(), email.get())
            )
            conn.commit()
            messagebox.showinfo("Success", "Student added")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", e)

    win = Toplevel(root)
    win.title("Add Student")

    Label(win, text="Student ID").grid(row=0, column=0)
    sid = Entry(win); sid.grid(row=0, column=1)

    Label(win, text="Name").grid(row=1, column=0)
    name = Entry(win); name.grid(row=1, column=1)

    Label(win, text="Email").grid(row=2, column=0)
    email = Entry(win); email.grid(row=2, column=1)

    Button(win, text="Add Student", command=submit).grid(row=3, columnspan=2, pady=5)

def view_students():
    win = Toplevel(root)
    win.title("Students")
    text = Text(win, width=120, height=30)
    text.pack()
    cur.execute("SELECT * FROM students")
    for s in cur.fetchall():
        text.insert(END, f"ID:{s[0]}  Name:{s[1]}  Email:{s[2]}\n")

        # ---------------- DELETE STUDENT ----------------
def delete_student():
    def submit():
        sid_v = sid.get()
        cur.execute("SELECT * FROM students WHERE student_id=?", (sid_v,))
        if not cur.fetchone():
            messagebox.showerror("Error", "Student ID not found")
            return
        cur.execute("DELETE FROM students WHERE student_id=?", (sid_v,))
        conn.commit()
        messagebox.showinfo("Deleted", "Student deleted successfully")
        win.destroy()

    win = Toplevel(root)
    win.title("Delete Student")

    Label(win, text="Student ID").grid(row=0, column=0)
    sid = Entry(win); sid.grid(row=0, column=1)

    Button(win, text="Delete Student", command=submit).grid(row=1, columnspan=2, pady=5)


# ---------------- ISSUE / RETURN ----------------
def issue_book():
    def submit():
        bid_v = int(bid.get())
        sid_v = int(sid.get())

        cur.execute("SELECT * FROM students WHERE student_id=?", (sid_v,))
        if not cur.fetchone():
            messagebox.showerror("Error", "Student ID not found")
            return

        cur.execute("SELECT * FROM books WHERE book_id=?", (bid_v,))
        book = cur.fetchone()
        if not book:
            messagebox.showerror("Error", "Book ID not found")
            return

        if book[5] == 1:
            messagebox.showwarning("Reference Book", "Cannot issue reference book.")
            return

        category = book[4]
        cur.execute("SELECT max_books, issue_days FROM policies WHERE category=?", (category,))
        policy = cur.fetchone()

        if not policy:
            messagebox.showerror("Error", "Policy not defined")
            return

        max_books, issue_days = policy
        cur.execute("SELECT COUNT(*) FROM issues WHERE student_id=? AND return_date IS NULL", (sid_v,))
        if cur.fetchone()[0] >= max_books:
            messagebox.showwarning("Limit Exceeded", "Max books issued")
            return

        due_date = date.today() + timedelta(days=issue_days)
        cur.execute("UPDATE books SET quantity=quantity-1 WHERE book_id=?", (bid_v,))
        cur.execute("INSERT INTO issues (book_id, student_id, issue_date, due_date) VALUES (?,?,?,?)",
                    (bid_v, sid_v, date.today(), due_date))
        conn.commit()
        messagebox.showinfo("Issued", f"Due Date: {due_date}")
        win.destroy()

    win = Toplevel(root)
    win.title("Issue Book")

    Label(win, text="Book ID").grid(row=0, column=0)
    bid = Entry(win); bid.grid(row=0, column=1)

    Label(win, text="Student ID").grid(row=1, column=0)
    sid = Entry(win); sid.grid(row=1, column=1)

    Button(win, text="Issue", command=submit).grid(row=2, columnspan=2, pady=5)

def return_book():
    def submit():
        bid_v = int(bid.get())
        sid_v = int(sid.get())

        cur.execute("""
        SELECT issue_id FROM issues
        WHERE book_id=? AND student_id=? AND return_date IS NULL
        """, (bid_v, sid_v))

        issue = cur.fetchone()
        if issue:
            cur.execute("UPDATE issues SET return_date=?, status='Returned' WHERE issue_id=?",
                        (date.today(), issue[0]))
            cur.execute("UPDATE books SET quantity=quantity+1 WHERE book_id=?", (bid_v,))
            conn.commit()
            messagebox.showinfo("Returned", "Book returned successfully")
            win.destroy()
        else:
            messagebox.showwarning("Error", "No active issue found")

    win = Toplevel(root)
    win.title("Return Book")

    Label(win, text="Book ID").grid(row=0, column=0)
    bid = Entry(win); bid.grid(row=0, column=1)

    Label(win, text="Student ID").grid(row=1, column=0)
    sid = Entry(win); sid.grid(row=1, column=1)

    Button(win, text="Return", command=submit).grid(row=2, columnspan=2, pady=5)

# ---------------- VIEW ISSUE RECORDS ----------------
def view_issues():
    win = Toplevel(root)
    win.title("Issue Records")
    text = Text(win, width=120, height=35)
    text.pack()

    cur.execute("""
    SELECT issues.issue_id, books.title, students.name,
           issues.issue_date, issues.due_date, issues.return_date, issues.status
    FROM issues
    JOIN books ON books.book_id = issues.book_id
    JOIN students ON students.student_id = issues.student_id
    """)
    for r in cur.fetchall():
        text.insert(END,
            f"IssueID:{r[0]}  Book:{r[1]}  Student:{r[2]}  "
            f"Issue:{r[3]}  Due:{r[4]}  Return:{r[5]}  Status:{r[6]}\n")

# ---------------- POLICY MANAGEMENT ----------------
def manage_policies():
    def submit():
        try:
            cur.execute("INSERT OR REPLACE INTO policies VALUES (?,?,?,?)",
                        (category.get(), int(max_books.get()), int(issue_days.get()), float(fine_rate.get())))
            conn.commit()
            messagebox.showinfo("Success", "Policy updated")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", e)

    win = Toplevel(root)
    win.title("Manage Policies")

    Label(win, text="Category").grid(row=0, column=0)
    category = Entry(win); category.grid(row=0, column=1)

    Label(win, text="Max Books").grid(row=1, column=0)
    max_books = Entry(win); max_books.grid(row=1, column=1)

    Label(win, text="Issue Days").grid(row=2, column=0)
    issue_days = Entry(win); issue_days.grid(row=2, column=1)

    Label(win, text="Fine Rate").grid(row=3, column=0)
    fine_rate = Entry(win); fine_rate.grid(row=3, column=1)

    Button(win, text="Update Policy", command=submit).grid(row=4, columnspan=2, pady=5)

# ---------------- CENTER BUTTON FRAME ----------------
btn_frame = Frame(root, bg="", padx=20, pady=20)
btn_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

Button(btn_frame, text="Add Book", width=25, command=add_book).pack(pady=5)
Button(btn_frame, text="View Books", width=25, command=view_books).pack(pady=5)
Button(btn_frame, text="Delete Book", width=25, command=delete_book).pack(pady=5)
Button(btn_frame, text="Add Student", width=25, command=add_student).pack(pady=5)
Button(btn_frame, text="View Students", width=25, command=view_students).pack(pady=5)
Button(btn_frame, text="Delete Student", width=25, command=delete_student).pack(pady=5)
Button(btn_frame, text="Issue Book", width=25, command=issue_book).pack(pady=5)
Button(btn_frame, text="Return Book", width=25, command=return_book).pack(pady=5)
Button(btn_frame, text="View Issue Records", width=25, command=view_issues).pack(pady=5)
Button(btn_frame, text="Manage Policies", width=25, command=manage_policies).pack(pady=5)
Button(btn_frame, text="Exit", width=25, command=root.destroy).pack(pady=15)


bg_label.lower()
root.mainloop()
conn.close()
