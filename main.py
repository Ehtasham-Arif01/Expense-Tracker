# imporing python libraries

import csv
import sqlite3
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import datetime

# Initialize main window
root = Tk()
root.title("Expense Tracker - Login")
root.geometry("1250x650")
root.resizable(False, False)
root.configure(bg="#1F2833")  # Background color


# Function to handle login
def login():
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showerror("Error", "Username and Password cannot be empty!")
        return

    try:
        conn = sqlite3.connect("expense_tracker.db")
        # Defining cursor
        c = conn.cursor()

        # Fetch both user ID and username
        c.execute("SELECT id, username FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            messagebox.showinfo("Login Success", f"Welcome {user[1]}!")
            expense_window(user[0], user[1])  # Open dashboard
        else:
            messagebox.showerror("Login Failed", "Invalid Username or Password")
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

######################################################################################################################

# Function to fetch and display records
def view_records(user_id, expense_text, income_text):
    conn = sqlite3.connect("expense_tracker.db")
    c = conn.cursor()

    # Fetch last 10 expense records
    # IF you want to check all the transaction you can check it in CSV file
    c.execute("SELECT category, amount, date, description FROM expenses WHERE user_id=? ORDER BY date DESC LIMIT 10", (user_id,))
    expenses = c.fetchall()

    # Fetch last 10 income records
    # IF you want to check all the transaction you can check it in CSV file
    c.execute("SELECT source, amount, date FROM income WHERE user_id=? ORDER BY date DESC LIMIT 10", (user_id,))
    income = c.fetchall()

    conn.close()

    # Format data into a table-like structure
    expense_text.config(state=NORMAL)
    income_text.config(state=NORMAL)

    expense_text.delete(1.0, END)  # Clear previous data
    income_text.delete(1.0, END)

    # Expense Table Header
    expense_text.insert(END, "Category               Amount           Date           Description\n")
    expense_text.insert(END, "-" * 74 + "\n")

    # Insert expenses
    for row in expenses:
        expense_text.insert(END, f"{row[0]:<20} {row[1]:<15} {row[2]:<15} {row[3]:<25}".rstrip() + "\n")

    # Income Table Header
    income_text.insert(END, "Source                    Amount               Date\n")
    income_text.insert(END, "-" * 74 + "\n")

    # Insert income records
    for row in income:
        income_text.insert(END, f"{row[0]:<25} {row[1]:<15} {row[2]:<18}".rstrip() + "\n")


    expense_text.config(state=DISABLED)
    income_text.config(state=DISABLED)

def close_app(adder):
    adder.destroy()  # Close the expense window
    root.destroy()   # Completely exit the application

def logout(adder):
    adder.destroy()  # Close the expense window
    entry_username.delete(0, END)  
    entry_password.delete(0, END)  
    root.deiconify()  # Show the login window again

######################################################################################################################

# FUNCTION to visualize data
def visualize_data(user_id):
    conn = sqlite3.connect("expense_tracker.db")
    c = conn.cursor()

    # Fetch Expense Data (Group by Category)
    c.execute("SELECT category, SUM(amount) FROM expenses WHERE user_id=? GROUP BY category", (user_id,))
    expense_data = c.fetchall()
    expense_categories = [row[0] for row in expense_data]
    expense_amounts = [row[1] for row in expense_data]

    # Fetch Income Data (Group by Source)
    c.execute("SELECT source, SUM(amount) FROM income WHERE user_id=? GROUP BY source", (user_id,))
    income_data = c.fetchall()
    income_sources = [row[0] for row in income_data]
    income_amounts = [row[1] for row in income_data]

    # Fetch Total Income & Expense
    c.execute("SELECT SUM(amount) FROM income WHERE user_id=?", (user_id,))
    total_income = c.fetchone()[0] or 0

    c.execute("SELECT SUM(amount) FROM expenses WHERE user_id=?", (user_id,))
    total_expense = c.fetchone()[0] or 0

    conn.close()

    # Create Subplots
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Expense Pie Chart
    axes[0].pie(expense_amounts, labels=expense_categories, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    axes[0].set_title("Expense Distribution")

    # Income Pie Chart
    axes[1].pie(income_amounts, labels=income_sources, autopct='%1.1f%%', startangle=90, colors=plt.cm.Set3.colors)
    axes[1].set_title("Income Distribution")

    # Bar Graph (Income vs. Expense)
    axes[2].bar(["Income", "Expense"], [total_income, total_expense], color=['green', 'red'])
    axes[2].set_title("Income vs Expense")
    axes[2].set_ylabel("Amount")

    # Display the graphs
    plt.tight_layout()
    plt.show()

######################################################################################################################

# Function to toggle theme
def toggle_theme():
    if root.cget('bg') == "#1F2833":  # Dark mode
        # Change to light mode
        root.configure(bg="#FFFFFF")
        root.configure(bg="#FFFFFF", fg="#000000")  # Update label colors for light mode
        toggle_button.configure(bg="#FFFFFF", fg="#000000")  # Update button colors for light mode
        frame.configure(bg="#FFFFFF")  # Change frame color for light mode
    else:  # Light mode
        # Change to dark mode
        root.configure(bg="#1F2833")
        root.configure(bg="#1F2833", fg="white")  # Update label colors for dark mode
        toggle_button.configure(bg="#1F2833", fg="white")  # Update button colors for dark mode
        frame.configure(bg="#0B0C10")  # Change frame color for dark mode


######################################################################################################################

# Function to Save the CSV File
def export_to_csv(user_id):
    conn = sqlite3.connect("expense_tracker.db")
    c = conn.cursor()

    # Fetch Expense Records
    c.execute("SELECT category, amount, date, description FROM expenses WHERE user_id=?", (user_id,))
    expenses = c.fetchall()

    # Fetch Income Records
    c.execute("SELECT source, amount, date FROM income WHERE user_id=?", (user_id,))
    income = c.fetchall()

    # Open CSV file to write both Expense and Income records
    with open("expense_and_income_records.csv", mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write Expense Records Header
        writer.writerow(["Category", "Amount", "Date", "Description"])
        writer.writerows(expenses)

        # separator row between Expense and Income
        writer.writerow([])  # Empty row for separation

        # Write Income Records Header
        writer.writerow(["Source", "Amount", "Date"])
        writer.writerows(income)

    conn.close()

    # Show confirmation message
    messagebox.showinfo("Success", "Data exported to CSV!")


######################################################################################################################

# Function to display the Expense and income windows and transactions
def expense_window(user_id, username):
    root.withdraw()  # To Hide the login window

    adder = Toplevel(root)
    adder.title("Expense Tracker - Expense and Income ")
    adder.geometry("1250x650")  # window size
    adder.resizable(False, False)
    adder.configure(bg="#1F2833")

    # Ensure app exits when this window is closed
    adder.protocol("WM_DELETE_WINDOW", lambda: close_app(adder))

    # Welcome message
    welcome_label = Label(adder, text=f"WELCOME, {username}!", font=("Arial", 14, "bold"), fg="#66FCF1", bg="#1F2833")
    welcome_label.place(x=50, y=10)

    # Vertical Separator Line
    canvas = Canvas(adder, width=3, height=600, bg="white", highlightthickness=0)
    canvas.place(x=450, y=30)  # Line separates sections

    # Left Side (Form Section)
    form_frame = Frame(adder, width=400, height=550, bg="#0B0C10")
    form_frame.place(x=30, y=50)

    # Expense Entry Fields
    Label(form_frame, text="EXPENSE AMOUNT :", bg="#0B0C10", fg="white").place(x=20, y=20)
    amount_entry = Entry(form_frame, width=30)
    amount_entry.place(x=150, y=20)

    Label(form_frame, text="CATEGORY :", bg="#0B0C10", fg="white").place(x=20, y=60)
    category_entry = Entry(form_frame, width=30)
    category_entry.place(x=150, y=60)

    Label(form_frame, text="DESCRIPTION :", bg="#0B0C10", fg="white").place(x=20, y=100)
    description_entry = Entry(form_frame, width=30)
    description_entry.place(x=150, y=100)

    Label(form_frame, text="DATE (YYYY-MM-DD):", bg="#0B0C10", fg="white").place(x=20, y=140)
    date_entry = Entry(form_frame, width=30)
    date_entry.place(x=150, y=140)

    # Button to add expense
    Button(form_frame, text="SUBMIT EXPENSE", width=20, bg="#28A745", fg="black",
           command=lambda: add_expense(user_id, amount_entry, category_entry, description_entry, date_entry)).place(x=100, y=180)

    # Income Entry Fields
    Label(form_frame, text="INCOME AMOUNT :", bg="#0B0C10", fg="white").place(x=20, y=240)
    income_amount = Entry(form_frame, width=30)
    income_amount.place(x=150, y=240)

    Label(form_frame, text="SOURCE :", bg="#0B0C10", fg="white").place(x=20, y=280)
    source = Entry(form_frame, width=30)
    source.place(x=150, y=280)

    Label(form_frame, text="DATE (YYYY-MM-DD):", bg="#0B0C10", fg="white").place(x=20, y=320)
    income_date = Entry(form_frame, width=30)
    income_date.place(x=150, y=320)

    # Button to add income
    Button(form_frame, text="SUBMIT INCOME", width=20, bg="#28A745", fg="black",
           command=lambda: add_income(user_id, income_amount, source, income_date)).place(x=100, y=360)

    #"View Records" Button
    Button(form_frame, text="VIEW RECORDS", width=30, height=2, bg="#17A2B8", fg="white",
       command=lambda: view_records(user_id, expense_text, income_text)).place(x=100, y=420)

    # "Logout" Button 
    Button(form_frame, text="LOGOUT", width=30, height=2, bg="red", fg="white",
       command=lambda: logout(adder)).place(x=100, y=500)

    # Records Display
    records_frame = Frame(adder, width=750, height=550, bg="#0D1B2A")  
    records_frame.place(x=480, y=50)

    # EXPENSES TABLE
    Label(records_frame, text="EXPENSE RECORD DETAILS ", font=("Arial", 12, "bold"), fg="white", bg="#0D1B2A").place(x=50, y=10)
    expense_text = Text(records_frame, width=75, height=12, bg="#172A45", fg="white", font=("Courier", 10))
    expense_text.place(x=50, y=40)
    expense_text.config(state=DISABLED)

    # INCOME TABLE
    Label(records_frame, text="INCOME RECORD DETAILS ", font=("Arial", 12, "bold"), fg="white", bg="#0D1B2A").place(x=50, y=280)
    income_text = Text(records_frame, width=75, height=10, bg="#172A45", fg="white", font=("Courier", 10))
    income_text.place(x=50, y=310)
    income_text.config(state=DISABLED)

    # "Export to CSV" Button
    Button(records_frame, text="EXPORT TO CSV", width=30, height=2, bg="#16A085", fg="black", 
       command=lambda: export_to_csv(user_id)).place(x=50, y=500)  

    # "Visualize Records" Button 
    Button(records_frame, text="VISUALIZE RECORDS", width=30, height=2, bg="#F39C12", fg="black", 
       command=lambda:visualize_data(user_id)).place(x=400, y=500)  


######################################################################################################################

# Function to add EXPENSE to the database
def add_expense(user_id, amount_entry, category_entry, description_entry, date_entry):
    amount = amount_entry.get()
    category = category_entry.get()
    description = description_entry.get()
    date = date_entry.get()

    # Ensure category and amount are provided
    if not amount or not category:
        messagebox.showerror("Error", "Category and Amount are required!")
        return
    
    # Check if the amount is a valid positive integer
    if not amount.isdigit() or int(amount) <= 0:
        messagebox.showerror("Error", "Amount must be a positive number!")
        return
    
    # Default current date if not provided
    if not date:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Set description to an empty string if not provided
    if not description:
        description = ""

    try:
        conn = sqlite3.connect("expense_tracker.db")
        c = conn.cursor()

        # Insert the expense record into the database
        c.execute("INSERT INTO expenses (user_id, category, date, amount, description) VALUES (?, ?, ?, ?, ?)",
                  (user_id, category, date, amount, description))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Expense added successfully!")

        # Clear input fields after adding data
        amount_entry.delete(0, END)
        category_entry.delete(0, END)
        description_entry.delete(0, END)
        date_entry.delete(0, END)

    except Exception as e:
        messagebox.showerror("Database Error", str(e))


######################################################################################################################

# Function to add INCOME to the database
def add_income(user_id, amount_entry, source_entry, date_entry):
    amount = amount_entry.get()
    source = source_entry.get()
    date = date_entry.get()

    # Ensure source and amount are provided
    if not amount or not source:
        messagebox.showerror("Error", "Source and Amount are required!")
        return

    # Check if the amount is a valid positive integer
    if not amount.isdigit() or int(amount) <= 0:
        messagebox.showerror("Error", "Amount must be a positive number!")
        return

    # Default current date if not provided
    if not date:
        date = datetime.datetime.now().strftime("%Y-%m-%d")

    try:
        conn = sqlite3.connect("expense_tracker.db")
        c = conn.cursor()

        # Insert the income record into the database
        c.execute("INSERT INTO income (user_id, source, date, amount) VALUES (?, ?, ?, ?)",
                  (user_id, source, date, amount))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Income added successfully!")

        # Clear input fields after adding data
        amount_entry.delete(0, END)
        source_entry.delete(0, END)
        date_entry.delete(0, END)

    except Exception as e:
        messagebox.showerror("Database Error", str(e))


######################################################################################################################

# Function to handle signup
def signup():
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showerror("Error", "All fields are required!")
        return

    try:
        conn = sqlite3.connect("expense_tracker.db")
        c = conn.cursor()

        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Account Created Successfully! You can now log in.")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists! Choose a different one.")

# Load and Display Image (Left Side)
try:
    image = Image.open("image3.png")  
    image = image.resize((450, 500))  
    img = ImageTk.PhotoImage(image)
    image_label = Label(root, image=img, bg="#1F2833")
    image_label.place(x=100, y=75)
except Exception as e:
    messagebox.showerror("Image Error", f"Could not load image: {e}")

# Login Frame
frame = Frame(root, width=500, height=420, bg="#0B0C10")
frame.place(x=700, y=115)

# "LOGIN PAGE" 
Label(frame, text="LOGIN PAGE", font=("Arial", 18, "bold"), fg="#66FCF1", bg="#0B0C10").place(x=180, y=25)

# Username and Password Fields
Label(frame, text="Enter Username", font=("Arial", 12), fg="white", bg="#0B0C10").place(x=60, y=80)
entry_username = Entry(frame, width=40, font=("Arial", 12), bg="#45A29E", fg="white", insertbackground="white")
entry_username.place(x=60, y=110)

Label(frame, text="Enter Password", font=("Arial", 12), fg="white", bg="#0B0C10").place(x=60, y=150)
entry_password = Entry(frame, width=40, font=("Arial", 12), bg="#45A29E", fg="white", show="*", insertbackground="white")
entry_password.place(x=60, y=180)

# Login and Register Buttons
Button(frame, text="Login", width=30, bg="#1F618D", fg="white", font=("Arial", 12, "bold"), command=login).place(x=60, y=230)
Button(frame, text="Register", width=30, bg="#34495E", fg="white", font=("Arial", 12, "bold"), command=lambda: signup()).place(x=60, y=280)
toggle_button = Button(frame, text="Toggle Theme", width=30, bg="#1F2833", fg="white", font=("Arial", 12, "bold"), command=toggle_theme)
toggle_button.place(x=60, y=330)

Button(frame, text="Quit", width=30, bg="red", fg="white", font=("Arial", 12, "bold"), command=root.quit).place(x=60, y=370)

root.mainloop()


##########################################################################################################################