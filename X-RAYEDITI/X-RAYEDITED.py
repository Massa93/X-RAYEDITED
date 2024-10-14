import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date

class XRayRegisterApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("X-Ray Register")
        self.geometry("800x600")

        self.create_database()
        self.create_main_ui()

    def create_database(self):
        conn = sqlite3.connect('xray_register.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS xray_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            xray_number TEXT UNIQUE NOT NULL,
            file_number TEXT NOT NULL,
            patient_name TEXT NOT NULL,
            exam TEXT NOT NULL,
            gender TEXT NOT NULL,
            code TEXT,
            main_member TEXT NOT NULL,
            medical_aid TEXT NOT NULL,
            medical_aid_number TEXT NOT NULL,
            member_id TEXT NOT NULL,
            contact_number TEXT,
            receipt_number TEXT,
            doctor TEXT NOT NULL,
            exam_date DATE NOT NULL
        )
        ''')
        conn.commit()
        conn.close()

    def create_main_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')

        self.main_frame = ttk.Frame(self.notebook, padding="20")
        self.form_frame = ttk.Frame(self.notebook, padding="20")

        self.notebook.add(self.main_frame, text="Main")
        self.notebook.add(self.form_frame, text="Add Patient")

        self.create_search_ui()
        self.create_form_ui()

    def create_search_ui(self):
        # Title
        title_label = ttk.Label(self.main_frame, text="X-Ray Register", font=("Helvetica", 16))
        title_label.grid(row=0, column=0, columnspan=2, pady=20)

        # Search frame
        search_frame = ttk.LabelFrame(self.main_frame, text="Search Patient Records", padding="10")
        search_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(search_frame, text="Enter ID, Name, or File Number:").grid(row=0, column=0, padx=5, pady=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(search_frame, text="Search", command=self.search_records).grid(row=0, column=2, padx=5, pady=5)

        # Results treeview
        self.results_tree = ttk.Treeview(self.main_frame, columns=('ID', 'Name', 'File Number', 'X-Ray Number'), show='headings')
        self.results_tree.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        self.results_tree.heading('ID', text='ID')
        self.results_tree.heading('Name', text='Name')
        self.results_tree.heading('File Number', text='File Number')
        self.results_tree.heading('X-Ray Number', text='X-Ray Number')

        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        scrollbar.grid(row=2, column=2, sticky=(tk.N, tk.S))
        self.results_tree.configure(yscroll=scrollbar.set)

        # Button to view selected record
        ttk.Button(self.main_frame, text="View Selected Record", command=self.view_selected_record).grid(row=3, column=0, columnspan=2, pady=10)

    def create_form_ui(self):
        labels = ["X-Ray Number", "File Number", "Patient Name", "Exam", "Gender", "Code", 
                  "Main Member", "Medical Aid", "Medical Aid Number", "Member ID", 
                  "Contact Number", "Receipt Number", "Doctor"]

        self.entries = {}

        for i, label in enumerate(labels):
            ttk.Label(self.form_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(self.form_frame, width=50)
            entry.grid(row=i, column=1, sticky=tk.W, pady=5)
            self.entries[label] = entry

        # Date picker
        ttk.Label(self.form_frame, text="Exam Date").grid(row=len(labels), column=0, sticky=tk.W, pady=5)
        self.date_entry = ttk.Entry(self.form_frame, width=50)
        self.date_entry.grid(row=len(labels), column=1, sticky=tk.W, pady=5)
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))

        # Submit button
        submit_button = ttk.Button(self.form_frame, text="Submit", command=self.submit_form)
        submit_button.grid(row=len(labels)+1, column=1, sticky=tk.E, pady=20)

    def search_records(self):
        search_term = self.search_entry.get()
        if not search_term:
            messagebox.showwarning("Invalid Search", "Please enter a search term.")
            return

        conn = sqlite3.connect('xray_register.db')
        cursor = conn.cursor()
        cursor.execute('''
        SELECT id, patient_name, file_number, xray_number
        FROM xray_records
        WHERE patient_name LIKE ? OR file_number LIKE ? OR xray_number LIKE ?
        ''', ('%'+search_term+'%', '%'+search_term+'%', '%'+search_term+'%'))
        results = cursor.fetchall()
        conn.close()

        self.results_tree.delete(*self.results_tree.get_children())
        for result in results:
            self.results_tree.insert('', 'end', values=result)

    def view_selected_record(self):
        selected_item = self.results_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a record to view.")
            return

        item_id = self.results_tree.item(selected_item)['values'][0]
        
        conn = sqlite3.connect('xray_register.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM xray_records WHERE id = ?', (item_id,))
        record = cursor.fetchone()
        conn.close()

        if record:
            record_window = tk.Toplevel(self)
            record_window.title("Record Details")
            record_window.geometry("400x300")

            for i, (field, value) in enumerate(zip(cursor.description, record)):
                ttk.Label(record_window, text=f"{field[0]}: {value}").grid(row=i, column=0, sticky=tk.W, pady=2)

    def submit_form(self):
        try:
            data = {label: entry.get() for label, entry in self.entries.items()}
            data['Exam Date'] = self.date_entry.get()

            conn = sqlite3.connect('xray_register.db')
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO xray_records (
                xray_number, file_number, patient_name, exam, gender, code,
                main_member, medical_aid, medical_aid_number, member_id,
                contact_number, receipt_number, doctor, exam_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['X-Ray Number'], data['File Number'], data['Patient Name'],
                data['Exam'], data['Gender'], data['Code'], data['Main Member'],
                data['Medical Aid'], data['Medical Aid Number'], data['Member ID'],
                data['Contact Number'], data['Receipt Number'], data['Doctor'],
                data['Exam Date']
            ))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Record added successfully!")
            self.clear_form()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "X-Ray Number must be unique. This number already exists in the database.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))

if __name__ == "__main__":
    app = XRayRegisterApp()
    app.mainloop()