import sqlite3
from tkinter import *
from tkinter import messagebox, ttk
from datetime import date, timedelta
from PIL import Image, ImageTk
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading

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
CREATE TABLE IF NOT EXISTS bounties(
    bounty_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_title TEXT,
    requester_id INTEGER,
    reward TEXT,
    status TEXT DEFAULT 'Open',
    claimed_by INTEGER
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

# ---------------- EMAIL FUNCTION ----------------
def send_email_to_students(book_title, book_author):
    try:
        # --- NEW CONNECTION INSIDE THREAD ---
        conn_thread = sqlite3.connect("library.db")
        cur_thread = conn_thread.cursor()

        sender_email = "dharshinike20@gmail.com"  # your email
        sender_password = "wjujjlsdwedrjbfo"     # App password without spaces

        cur_thread.execute("SELECT email, name FROM students")
        students = cur_thread.fetchall()

        if not students:
            print("No students to send email to.")
            conn_thread.close()
            return

        subject = f"New Book Added: {book_title}"
        for student in students:
            receiver_email, student_name = student

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject

            body = f"Hello {student_name},\n\nA new book '{book_title}' by {book_author} has been added to the library. Check it out!\n\n- Library Team"
            msg.attach(MIMEText(body, 'plain'))

            try:
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, receiver_email, msg.as_string())
                print(f"Email sent to {receiver_email}")
            except Exception as e:
                print(f"Error sending email to {receiver_email}: {e}")

        conn_thread.close()
    except Exception as e:
        print("Email thread error:", e)

# ---------------- GUI ----------------
root = Tk()
root.title("Advanced Policy-Driven Library System")
root.geometry("900x700")

# ---------------- BACKGROUND IMAGE ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BG_PATH = os.path.join(BASE_DIR, "library_bg.png")
if os.path.exists(BG_PATH):
    bg_img = Image.open(BG_PATH)
    bg_img = bg_img.resize((1500, 900))
    bg_photo = ImageTk.PhotoImage(bg_img)
    bg_label = Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    # -------- DARK OVERLAY FOR ELEGANCE --------
overlay = Frame(root, bg="#2B1B17")   # deep chocolate brown
overlay.place(relwidth=1, relheight=1)

overlay.lift()      # bring overlay above bg
overlay.lower()     # keep bg at bottom

# ---------------- MAIN TITLE ----------------
title_label = Label(
    root,
    text="LIBRARY\nMANAGEMENT SYSTEM",
    font=("Georgia", 36, "bold"),
    bg="#2B1B17",
    fg="#F5E6D3",
    justify="center"
)
title_label.place(relx=0.5, rely=0.12, anchor="center")

# ---------------- STYLISH BUTTON STYLE ----------------
def create_style():
    style = ttk.Style()
    style.theme_use("alt")

    style.configure(
        "Custom.TButton",
        font=("Segoe UI Semibold", 12),
        padding=10,
        background="#3E2723",   # dark brown
        foreground="#F5E6D3",   # soft cream
        borderwidth=0
    )

    style.map(
        "Custom.TButton",
        background=[
            ("active", "#5D4037"),   # lighter brown on hover
            ("pressed", "#2B1B17")
        ]
    )

    return style

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

            # Send emails in background
            threading.Thread(target=send_email_to_students, args=(title.get(), author.get()), daemon=True).start()

            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", e)

    win = Toplevel(root)
    win.title("Add Book")
    win.geometry("400x350")
    win.resizable(False, False)
    
    # Center window
    win.transient(root)
    win.grab_set()
    
    # Table-style frame
    frame = Frame(win, padx=20, pady=20)
    frame.pack(expand=True, fill=BOTH)
    
    # Table headers
    headers = ["Field", "Value"]
    for i, header in enumerate(headers):
        Label(frame, text=header, font=('Segoe UI', 10, 'bold'), bg='#f0f0f0', relief='solid', bd=1, padx=10, pady=8, width=15).grid(row=0, column=i, sticky='ew', pady=2)
    
    # Table rows
    Label(frame, text="Book ID", font=('Segoe UI', 9)).grid(row=1, column=0, sticky='w', pady=5)
    bid = Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    bid.grid(row=1, column=1, sticky='ew', pady=5, padx=(5,0))
    
    Label(frame, text="Title", font=('Segoe UI', 9)).grid(row=2, column=0, sticky='w', pady=5)
    title = Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    title.grid(row=2, column=1, sticky='ew', pady=5, padx=(5,0))
    
    Label(frame, text="Author", font=('Segoe UI', 9)).grid(row=3, column=0, sticky='w', pady=5)
    author = Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    author.grid(row=3, column=1, sticky='ew', pady=5, padx=(5,0))
    
    Label(frame, text="Quantity", font=('Segoe UI', 9)).grid(row=4, column=0, sticky='w', pady=5)
    qty = Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    qty.grid(row=4, column=1, sticky='ew', pady=5, padx=(5,0))
    
    Label(frame, text="Category", font=('Segoe UI', 9)).grid(row=5, column=0, sticky='w', pady=5)
    category = Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    category.grid(row=5, column=1, sticky='ew', pady=5, padx=(5,0))
    
    ref_var = IntVar()
    Checkbutton(frame, text="Reference Book (Cannot be issued)", variable=ref_var, font=('Segoe UI', 9)).grid(row=6, column=0, columnspan=2, sticky='w', pady=5)
    
    # Configure column weights
    frame.columnconfigure(1, weight=1)
    
    style = create_style()
    ttk.Button(frame, text="Add Book", style='Custom.TButton', command=submit).grid(row=7, column=0, columnspan=2, pady=20)

from tkinter import ttk

def view_books():
    win = Toplevel(root)
    win.title("Books")
    win.geometry("900x400")
    win.configure(bg="#F4F6F9")

    style = ttk.Style()
    style.theme_use("default")

    style.configure("Treeview",
                    background="white",
                    foreground="#111827",
                    rowheight=25,
                    fieldbackground="white")

    style.configure("Treeview.Heading",
                    background="#1F2933",
                    foreground="white",
                    font=('Segoe UI', 10, 'bold'))

    tree = ttk.Treeview(win, columns=("ID","Title","Author","Qty","Category","Reference"), show="headings")

    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=130)

    tree.pack(fill=BOTH, expand=True)

    cur.execute("SELECT * FROM books")
    rows = cur.fetchall()

    for index, b in enumerate(rows):
        ref_status = "Yes" if b[5] else "No"
        tree.insert("", END, values=(b[0], b[1], b[2], b[3], b[4], ref_status))


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
    win.geometry("350x200")
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()
    
    frame = Frame(win, padx=20, pady=20)
    frame.pack(expand=True, fill=BOTH)
    
    headers = ["Field", "Value"]
    for i, header in enumerate(headers):
        Label(frame, text=header, font=('Segoe UI', 10, 'bold'), bg='#f0f0f0', relief='solid', bd=1, padx=10, pady=8, width=15).grid(row=0, column=i, sticky='ew', pady=2)
    
    Label(frame, text="Book ID", font=('Segoe UI', 9)).grid(row=1, column=0, sticky='w', pady=20)
    bid = Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    bid.grid(row=1, column=1, sticky='ew', pady=20, padx=(5,0))
    
    frame.columnconfigure(1, weight=1)
    
    style = create_style()
    ttk.Button(frame, text="Delete Book", style='Custom.TButton', command=submit).grid(row=2, column=0, columnspan=2, pady=10)

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
    win.geometry("400x300")
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()
    
    frame = Frame(win, padx=20, pady=20)
    frame.pack(expand=True, fill=BOTH)
    
    headers = ["Field", "Value"]
    for i, header in enumerate(headers):
        Label(frame, text=header, font=('Segoe UI', 10, 'bold'), bg='#f0f0f0', relief='solid', bd=1, padx=10, pady=8, width=15).grid(row=0, column=i, sticky='ew', pady=2)
    
    Label(frame, text="Student ID", font=('Segoe UI', 9)).grid(row=1, column=0, sticky='w', pady=5)
    sid = Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    sid.grid(row=1, column=1, sticky='ew', pady=5, padx=(5,0))
    
    Label(frame, text="Name", font=('Segoe UI', 9)).grid(row=2, column=0, sticky='w', pady=5)
    name = Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    name.grid(row=2, column=1, sticky='ew', pady=5, padx=(5,0))
    
    Label(frame, text="Email", font=('Segoe UI', 9)).grid(row=3, column=0, sticky='w', pady=5)
    email = Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    email.grid(row=3, column=1, sticky='ew', pady=5, padx=(5,0))
    
    frame.columnconfigure(1, weight=1)
    
    style = create_style()
    ttk.Button(frame, text="Add Student", style='Custom.TButton', command=submit).grid(row=4, column=0, columnspan=2, pady=20)

def view_students():
    win = Toplevel(root)
    win.title("Students")
    win.geometry("700x400")
    win.configure(bg="#F4F6F9")

    tree = ttk.Treeview(win, columns=("ID","Name","Email"), show="headings")

    tree.heading("ID", text="ID")
    tree.heading("Name", text="Name")
    tree.heading("Email", text="Email")

    tree.column("ID", width=100)
    tree.column("Name", width=200)
    tree.column("Email", width=300)

    tree.pack(fill=BOTH, expand=True)

    cur.execute("SELECT * FROM students")
    for s in cur.fetchall():
        tree.insert("", END, values=s)


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
    win.geometry("350x200")
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()
    
    frame = Frame(win, padx=20, pady=20)
    frame.pack(expand=True, fill=BOTH)
    
    headers = ["Field", "Value"]
    for i, header in enumerate(headers):
        Label(frame, text=header, font=('Segoe UI', 10, 'bold'), bg='#f0f0f0', relief='solid', bd=1, padx=10, pady=8, width=15).grid(row=0, column=i, sticky='ew', pady=2)
    
    Label(frame, text="Student ID", font=('Segoe UI', 9)).grid(row=1, column=0, sticky='w', pady=20)
    sid = Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    sid.grid(row=1, column=1, sticky='ew', pady=20, padx=(5,0))
    
    frame.columnconfigure(1, weight=1)
    
    style = create_style()
    ttk.Button(frame, text="Delete Student", style='Custom.TButton', command=submit).grid(row=2, column=0, columnspan=2, pady=10)

# ---------------- ISSUE / RETURN ----------------
def issue_book():
    def submit():
        book_name = book.get().strip()
        sid_v = sid.get().strip()

        if not book_name or not sid_v.isdigit():
            messagebox.showerror("Error", "Enter valid Book Name and Student ID")
            return

        sid_v = int(sid_v)

        # Check student exists
        cur.execute("SELECT * FROM students WHERE student_id=?", (sid_v,))
        if not cur.fetchone():
            messagebox.showerror("Error", "Student ID not found")
            return

        # Check book exists by NAME
        cur.execute("SELECT * FROM books WHERE LOWER(title)=LOWER(?)", (book_name,))
        book_data = cur.fetchone()

        if not book_data:
            messagebox.showwarning("Not Available", "Book not present in library")
            return

        book_id = book_data[0]
        quantity = book_data[3]
        category = book_data[4]
        is_reference = book_data[5]

        # Check stock
        if quantity == 0:
            messagebox.showwarning("Out of Stock", "Oops! Book is currently out of stock")
            return

        # Check reference book
        if is_reference == 1:
            messagebox.showwarning("Reference Book", "Cannot issue reference book")
            return

        # Policy check
        cur.execute("SELECT max_books, issue_days FROM policies WHERE category=?", (category,))
        policy = cur.fetchone()

        if not policy:
            messagebox.showerror("Error", "Policy not defined for this category")
            return

        max_books, issue_days = policy

        cur.execute("""
            SELECT COUNT(*) FROM issues
            WHERE student_id=? AND return_date IS NULL
        """, (sid_v,))

        if cur.fetchone()[0] >= max_books:
            messagebox.showwarning("Limit Exceeded", "Maximum book issue limit reached")
            return

        # Issue book
        due_date = date.today() + timedelta(days=issue_days)

        cur.execute("UPDATE books SET quantity=quantity-1 WHERE book_id=?", (book_id,))
        cur.execute("""
            INSERT INTO issues (book_id, student_id, issue_date, due_date)
            VALUES (?,?,?,?)
        """, (book_id, sid_v, date.today(), due_date))

        conn.commit()
        messagebox.showinfo("Issued", f"Book issued successfully!\nDue Date: {due_date}")
        win.destroy()

    win = Toplevel(root)
    win.title("Issue Book")
    win.geometry("400x250")
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()
    
    frame = Frame(win, padx=20, pady=20)
    frame.pack(expand=True, fill=BOTH)
    
    headers = ["Field", "Value"]
    for i, header in enumerate(headers):
        Label(frame, text=header, font=('Segoe UI', 10, 'bold'), bg='#f0f0f0', relief='solid', bd=1, padx=10, pady=8, width=15).grid(row=0, column=i, sticky='ew', pady=2)
    
    Label(frame, text="Book Name", font=('Segoe UI', 9)).grid(row=1, column=0, sticky='w', pady=10)
    book = Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    book.grid(row=1, column=1, sticky='ew', pady=10, padx=(5,0))
    
    Label(frame, text="Student ID", font=('Segoe UI', 9)).grid(row=2, column=0, sticky='w', pady=10)
    sid = Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    sid.grid(row=2, column=1, sticky='ew', pady=10, padx=(5,0))
    
    frame.columnconfigure(1, weight=1)
    
    style = create_style()
    ttk.Button(frame, text="Issue", style='Custom.TButton', command=submit).grid(row=3, column=0, columnspan=2, pady=20)

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
    win.geometry("400x250")
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()
    
    frame = Frame(win, padx=20, pady=20)
    frame.pack(expand=True, fill=BOTH)
    
    headers = ["Field", "Value"]
    for i, header in enumerate(headers):
        Label(frame, text=header, font=('Segoe UI', 10, 'bold'), bg='#f0f0f0', relief='solid', bd=1, padx=10, pady=8, width=15).grid(row=0, column=i, sticky='ew', pady=2)
    
    Label(frame, text="Book ID", font=('Segoe UI', 9)).grid(row=1, column=0, sticky='w', pady=10)
    bid = Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    bid.grid(row=1, column=1, sticky='ew', pady=10, padx=(5,0))
    
    Label(frame, text="Student ID", font=('Segoe UI', 9)).grid(row=2, column=0, sticky='w', pady=10)
    sid = Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    sid.grid(row=2, column=1, sticky='ew', pady=10, padx=(5,0))
    
    frame.columnconfigure(1, weight=1)
    
    style = create_style()
    ttk.Button(frame, text="Return", style='Custom.TButton', command=submit).grid(row=3, column=0, columnspan=2, pady=20)

# =====================================================
# ⭐⭐ BOUNTY SYSTEM ⭐⭐
# =====================================================

# POST BOUNTY
def post_bounty():
    def submit():
        try:
            cur.execute("""
            INSERT INTO bounties(book_title,requester_id,reward)
            VALUES (?,?,?)
            """,(book.get(),int(student.get()),reward.get()))

            conn.commit()
            messagebox.showinfo("Success","Bounty Posted")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error",e)

    win=Toplevel(root)
    win.title("Post Bounty")
    win.geometry("400x300")
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()
    
    frame = Frame(win, padx=20, pady=20)
    frame.pack(expand=True, fill=BOTH)
    
    headers = ["Field", "Value"]
    for i, header in enumerate(headers):
        Label(frame, text=header, font=('Segoe UI', 10, 'bold'), bg='#f0f0f0', relief='solid', bd=1, padx=10, pady=8, width=15).grid(row=0, column=i, sticky='ew', pady=2)
    
    Label(frame, text="Book Title", font=('Segoe UI', 9)).grid(row=1, column=0, sticky='w', pady=5)
    book=Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    book.grid(row=1, column=1, sticky='ew', pady=5, padx=(5,0))
    
    Label(frame, text="Student ID", font=('Segoe UI', 9)).grid(row=2, column=0, sticky='w', pady=5)
    student=Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    student.grid(row=2, column=1, sticky='ew', pady=5, padx=(5,0))
    
    Label(frame, text="Reward / Message", font=('Segoe UI', 9)).grid(row=3, column=0, sticky='w', pady=5)
    reward=Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    reward.grid(row=3, column=1, sticky='ew', pady=5, padx=(5,0))
    
    frame.columnconfigure(1, weight=1)
    
    style = create_style()
    ttk.Button(frame, text="Post", style='Custom.TButton', command=submit).grid(row=4, column=0, columnspan=2, pady=20)

def view_bounties():
    win = Toplevel(root)
    win.title("Bounties")
    win.geometry("1000x400")
    win.configure(bg="#F4F6F9")

    tree = ttk.Treeview(win, columns=("ID","Book","Requester","Reward","Status","ClaimedBy"), show="headings")

    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    tree.pack(fill=BOTH, expand=True)

    cur.execute("SELECT * FROM bounties")
    for b in cur.fetchall():
        tree.insert("", END, values=b)


# CLAIM BOUNTY
def claim_bounty():
    def submit():
        try:
            cur.execute("""
            UPDATE bounties
            SET status='Claimed', claimed_by=?
            WHERE bounty_id=? AND status='Open'
            """,(int(student.get()),int(bid.get())))

            if cur.rowcount==0:
                messagebox.showwarning("Error","Already Claimed / Invalid")
            else:
                conn.commit()
                messagebox.showinfo("Success","Bounty Claimed")

            win.destroy()
        except Exception as e:
            messagebox.showerror("Error",e)

    win=Toplevel(root)
    win.title("Claim Bounty")
    win.geometry("400x250")
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()
    
    frame = Frame(win, padx=20, pady=20)
    frame.pack(expand=True, fill=BOTH)
    
    headers = ["Field", "Value"]
    for i, header in enumerate(headers):
        Label(frame, text=header, font=('Segoe UI', 10, 'bold'), bg='#f0f0f0', relief='solid', bd=1, padx=10, pady=8, width=15).grid(row=0, column=i, sticky='ew', pady=2)
    
    Label(frame, text="Bounty ID", font=('Segoe UI', 9)).grid(row=1, column=0, sticky='w', pady=10)
    bid=Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    bid.grid(row=1, column=1, sticky='ew', pady=10, padx=(5,0))
    
    Label(frame, text="Your Student ID", font=('Segoe UI', 9)).grid(row=2, column=0, sticky='w', pady=10)
    student=Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    student.grid(row=2, column=1, sticky='ew', pady=10, padx=(5,0))
    
    frame.columnconfigure(1, weight=1)
    
    style = create_style()
    ttk.Button(frame, text="Claim", style='Custom.TButton', command=submit).grid(row=3, column=0, columnspan=2, pady=20)

# ---------------- VIEW ISSUE RECORDS ----------------
def view_issues():
    win = Toplevel(root)
    win.title("Issue Records")
    win.geometry("1100x500")
    win.configure(bg="#F4F6F9")

    tree = ttk.Treeview(win, columns=("IssueID","Book","Student","Issue","Due","Return","Status"), show="headings")

    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    tree.pack(fill=BOTH, expand=True)

    cur.execute("""
    SELECT issues.issue_id, books.title, students.name,
           issues.issue_date, issues.due_date, issues.return_date, issues.status
    FROM issues
    JOIN books ON books.book_id = issues.book_id
    JOIN students ON students.student_id = issues.student_id
    """)

    for r in cur.fetchall():
        tree.insert("", END, values=r)

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
    win.geometry("400x350")
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()
    
    frame = Frame(win, padx=20, pady=20)
    frame.pack(expand=True, fill=BOTH)
    
    headers = ["Field", "Value"]
    for i, header in enumerate(headers):
        Label(frame, text=header, font=('Segoe UI', 10, 'bold'), bg='#f0f0f0', relief='solid', bd=1, padx=10, pady=8, width=15).grid(row=0, column=i, sticky='ew', pady=2)
    
    Label(frame, text="Category", font=('Segoe UI', 9)).grid(row=1, column=0, sticky='w', pady=5)
    category = Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    category.grid(row=1, column=1, sticky='ew', pady=5, padx=(5,0))
    
    Label(frame, text="Max Books", font=('Segoe UI', 9)).grid(row=2, column=0, sticky='w', pady=5)
    max_books = Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    max_books.grid(row=2, column=1, sticky='ew', pady=5, padx=(5,0))
    
    Label(frame, text="Issue Days", font=('Segoe UI', 9)).grid(row=3, column=0, sticky='w', pady=5)
    issue_days = Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    issue_days.grid(row=3, column=1, sticky='ew', pady=5, padx=(5,0))
    
    Label(frame, text="Fine Rate", font=('Segoe UI', 9)).grid(row=4, column=0, sticky='w', pady=5)
    fine_rate = Entry(frame, font=('Segoe UI', 9), relief='solid', bd=1)
    fine_rate.grid(row=4, column=1, sticky='ew', pady=5, padx=(5,0))
    
    frame.columnconfigure(1, weight=1)
    
    style = create_style()
    ttk.Button(frame, text="Update Policy", style='Custom.TButton', command=submit).grid(row=5, column=0, columnspan=2, pady=20)

# ---------------- TOP NAVBAR ----------------
topbar = Frame(root, bg="#0B3C5D", height=60)
topbar.pack(side=TOP, fill=X)

Label(
    topbar,
    text="Library Management with Bounty System",
    bg="#0B3C5D",
    fg="white",
    font=("Segoe UI", 16, "bold")
).pack(expand=True, padx=20)

# ---------------- SIDEBAR ----------------
sidebar = Frame(root, bg="#08324A", width=220)
sidebar.pack(side=LEFT, fill=Y)

# --- Admin Section ---
admin_frame = Frame(sidebar, bg="#08324A")
admin_frame.pack(pady=20)

Label(admin_frame, text="Welcome to", fg="white", bg="#08324A", font=("Segoe UI", 10)).pack()

Label(admin_frame, text="Library", fg="white", bg="#08324A", font=("Segoe UI", 14, "bold")).pack(pady=5)
def sidebar_button(text, command):
    Button(
        sidebar,
        text=text,
        command=command,
        bg="#0E4A6C",
        fg="white",
        relief="flat",
        anchor="w",
        font=("Segoe UI", 10),
        padx=20,
        pady=8
    ).pack(fill=X, pady=2)

sidebar_button("Add Book", add_book)
sidebar_button("View Books", view_books)
sidebar_button("Add Student", add_student)
sidebar_button("Issue Book", issue_book)
sidebar_button("Return Book", return_book)
sidebar_button("Policies", manage_policies)

# ---------------- MAIN CONTENT AREA ----------------
main_area = Frame(root, bg="#F5F5F5")
main_area.pack(side=LEFT, fill=BOTH, expand=True)
# ---------------- LOAD ICON FUNCTION ----------------
icon_images = {}

def load_icon(path):
    img = Image.open(path)
    img = img.resize((250, 260))
    return ImageTk.PhotoImage(img)
# ---------------- DASHBOARD / TILE GRID ----------------
dashboard_frame = Frame(main_area, bg="#F5F5F5")
dashboard_frame.pack(padx=30, pady=30, fill=BOTH, expand=True)


# Define tile info (button text + function + color)
from PIL import Image, ImageTk

tiles = [
    ("Add Book", add_book, "#00CFFF", "icons/add_book.png"),
    ("View Books", view_books, "#2ECC71", "icons/view_books.png"),
    ("Delete Book", delete_book, "#E74C3C", "icons/delete_book.png"),
    ("Add Student", add_student, "#F39C12", "icons/add_student.png"),
    ("View Students", view_students, "#00CFFF", "icons/view_students.png"),
    ("Delete Student", delete_student, "#2ECC71", "icons/delete_student.png"),
    ("Issue Book", issue_book, "#E74C3C", "icons/issue.png"),
    ("Return Book", return_book, "#F39C12", "icons/return.png"),
    ("Post Bounty", post_bounty, "#00CFFF", "icons/post_bounty.png"),
    ("View Bounties", view_bounties, "#2ECC71", "icons/view_bounty.png"),
    ("Claim Bounty", claim_bounty, "#E74C3C", "icons/claim.png"),
    ("View Issue Records", view_issues, "#F39C12", "icons/records.png"),
    ("Manage Policies", manage_policies, "#00CFFF", "icons/policy.png")
]

# Keep references so images don't get garbage collected
tile_images = []

rows = 3
cols = 5

for idx, (text, func, color, icon_path) in enumerate(tiles):
    r = idx // cols
    c = idx % cols

    tile = Frame(dashboard_frame, bg=color, width=220, height=180)
    tile.grid_propagate(False)
    tile.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")

    # Load icon if it exists
    if os.path.exists(icon_path):
        img = Image.open(icon_path)
        img = img.resize((240, 170))  # resize to fit tile
        photo = ImageTk.PhotoImage(img)
        tile_images.append(photo)  # keep reference
        lbl_img = Label(tile, image=photo, bg=color)
        lbl_img.pack(pady=(10,5))
    else:
        lbl_img = None

    lbl_text = Label(tile, text=text, bg=color, fg="white", font=("Segoe UI", 10, "bold"))
    lbl_text.pack()

    tile.bind("<Button-1>", lambda e, f=func: f())
    lbl_text.bind("<Button-1>", lambda e, f=func: f())
    if lbl_img:
        lbl_img.bind("<Button-1>", lambda e, f=func: f())


root.mainloop()
conn.close()
