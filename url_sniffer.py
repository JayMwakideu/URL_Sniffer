import tkinter as tk
from tkinter import ttk, messagebox
import pyfiglet
import json
import os
import sqlite3
from datetime import datetime

# Configuration file for storing API keys
CONFIG_FILE = 'api_keys.json'
DATABASE_FILE = 'url_sniffer.db'

# Check if config file exists, if not, create it with default empty keys
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"virustotal": "", "ipqualityscore": ""}, f)

# Database setup
def setup_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Create checks table
    cursor.execute('''CREATE TABLE IF NOT EXISTS checks 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     url TEXT, 
                     result TEXT, 
                     timestamp DATETIME)''')
    
    # Create logs table
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     message TEXT, 
                     timestamp DATETIME)''')
    
    conn.commit()
    conn.close()

# Database operations
def save_check_to_db(url, result):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO checks (url, result, timestamp) VALUES (?, ?, ?)', 
                   (url, json.dumps(result), datetime.now()))
    conn.commit()
    conn.close()

def log_message(message):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO logs (message, timestamp) VALUES (?, ?)', 
                   (message, datetime.now()))
    conn.commit()
    conn.close()

def load_api_keys():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_api_keys(keys):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(keys, f)

# Load API keys
api_keys = load_api_keys()

# UI Setup
root = tk.Tk()
root.title("URL Sniffer")
root.geometry("800x600")  # Increased window size

# Custom style for ttk widgets
style = ttk.Style()
style.theme_use('default')
style.configure("TNotebook.Tab", background="#333333", foreground="white")
style.configure("TButton", background="#4CAF50", foreground="white", font=('Helvetica', 10, 'bold'))
style.configure("TLabel", background="#333333", foreground="white", font=('Helvetica', 12, 'bold'))
style.configure("TEntry", background="white", foreground="black", font=('Helvetica', 10))

# Set the main window's background color
root.configure(bg="#333333")

# Custom window control buttons
control_frame = tk.Frame(root, bg="#333333")
control_frame.pack(side=tk.TOP, fill=tk.X)

def close_window():
    root.destroy()

def minimize_window():
    root.iconify()

def maximize_window():
    if root.state() == 'zoomed':
        root.state('normal')
    else:
        root.state('zoomed')

tk.Button(control_frame, text="❌", command=close_window, bg="#FF0000", fg="white", font=('Helvetica', 10, 'bold')).pack(side=tk.RIGHT)
tk.Button(control_frame, text="🗖", command=maximize_window, bg="#0078D7", fg="white", font=('Helvetica', 10, 'bold')).pack(side=tk.RIGHT)
tk.Button(control_frame, text="🗕", command=minimize_window, bg="#0078D7", fg="white", font=('Helvetica', 10, 'bold')).pack(side=tk.RIGHT)

# Banner with pyfiglet
banner_text = pyfiglet.figlet_format("URL Sniffer", font="slant")
banner_label = tk.Label(root, text=banner_text, bg="#333333", fg="#4CAF50", font=("Courier", 10))
banner_label.pack()

github_link = tk.Label(root, text="GitHub: https://github.com/JayMwakideu/URL_Sniffer\nDeveloper: Jay Mwakideu", bg="#333333", fg="#0078D7", cursor="hand2")
github_link.pack()
github_link.bind("<Button-1>", lambda e: root.clipboard_clear() or root.clipboard_append("https://github.com/JayMwakideu/URL_Sniffer"))

# Create notebook (tabs)
notebook = ttk.Notebook(root)

# Frame for each tab
home_frame = ttk.Frame(notebook, style="TFrame")
edit_frame = ttk.Frame(notebook, style="TFrame")
view_frame = ttk.Frame(notebook, style="TFrame")
logs_frame = ttk.Frame(notebook, style="TFrame")
about_frame = ttk.Frame(notebook, style="TFrame")

notebook.add(home_frame, text='Home')
notebook.add(edit_frame, text='Edit API Keys')
notebook.add(view_frame, text='View Results')
notebook.add(logs_frame, text='Logs')
notebook.add(about_frame, text='About')

# Home tab with URL check
ttk.Label(home_frame, text="URL to Check:", style="TLabel").pack(pady=5)
url_entry_home = ttk.Entry(home_frame, width=50, style="TEntry")
url_entry_home.pack(pady=5)

def check_url_from_home():
    url = url_entry_home.get()
    if not api_keys['virustotal'] or not api_keys['ipqualityscore']:
        messagebox.showerror("Error", "Please enter API keys before checking URLs.")
    else:
        notebook.select(view_frame)
        url_entry.set(url)  # Set the URL in the View tab
        check_url()

ttk.Button(home_frame, text="Check URL", command=check_url_from_home, style="TButton").pack(pady=10)

# Edit API Keys tab
ttk.Label(edit_frame, text="VirusTotal API Key:", style="TLabel").pack(pady=5)
virustotal_entry = ttk.Entry(edit_frame, width=50, style="TEntry")
virustotal_entry.insert(0, api_keys['virustotal'])
virustotal_entry.pack(pady=5)

ttk.Label(edit_frame, text="IPQualityScore API Key:", style="TLabel").pack(pady=5)
ipqs_entry = ttk.Entry(edit_frame, width=50, style="TEntry")
ipqs_entry.insert(0, api_keys['ipqualityscore'])
ipqs_entry.pack(pady=5)

def save_keys():
    api_keys['virustotal'] = virustotal_entry.get()
    api_keys['ipqualityscore'] = ipqs_entry.get()
    save_api_keys(api_keys)
    messagebox.showinfo("Success", "API Keys Saved!")

ttk.Button(edit_frame, text="Save Keys", command=save_keys, style="TButton").pack(pady=10)

# View Results tab
url_entry = tk.StringVar()
ttk.Label(view_frame, text="URL to Check:", style="TLabel").pack(pady=5)
ttk.Entry(view_frame, textvariable=url_entry, width=50, style="TEntry").pack(pady=5)

result_text = tk.Text(view_frame, width=60, height=20, bg="white", fg="black")
result_text.pack(pady=5)

def check_url():
    url = url_entry.get()
    if not api_keys['virustotal'] or not api_keys['ipqualityscore']:
        messagebox.showerror("Error", "Please enter API keys before checking URLs.")
    else:
        # Here you would call your URL validation function. For demo purposes:
        result = {
            "valid": True,
            "malicious": False,
            "details": {
                "virustotal": "No malicious activity detected by VirusTotal.",
                "ipqualityscore": "No malicious activity detected by IPQualityScore."
            }
        }
        result_text.delete('1.0', tk.END)
        result_text.insert('1.0', json.dumps(result, indent=2))
        save_check_to_db(url, result)
        log_message(f"Checked URL: {url}, Result: {result['malicious']}")

ttk.Button(view_frame, text="Check URL", command=check_url, style="TButton").pack(pady=10)

# Logs tab
logs_text = tk.Text(logs_frame, width=60, height=30, bg="white", fg="black")
logs_text.pack(pady=5)

def load_logs():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Check if the logs table exists before attempting SELECT
    cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='logs'")
    if cursor.fetchone()[0] == 0:
        messagebox.showerror("Error", "Logs table does not exist. Please restart the application.")
        return

    cursor.execute("SELECT message, timestamp FROM logs ORDER BY timestamp DESC LIMIT 100")
    logs = cursor.fetchall()
    conn.close()
    logs_text.delete('1.0', tk.END)
    for log in logs:
        logs_text.insert('1.0', f"{log[1]} - {log[0]}\n")

load_logs()  # Load logs on startup
ttk.Button(logs_frame, text="Refresh Logs", command=load_logs, style="TButton").pack(pady=5)

# About page
about_text = "URL Sniffer\nDeveloped by: Jay Mwakideu\nGitHub: https://github.com/JayMwakideu/URL_Sniffer"
tk.Label(about_frame, text=about_text, bg="#333333", fg="white", font=("Helvetica", 12, 'bold'), justify='center').pack(expand=True)

# Pack the notebook into the main window
notebook.pack(expand=True, fill='both')

# Setup the database automatically when the script runs
setup_database()

# Start the GUI loop
root.mainloop()