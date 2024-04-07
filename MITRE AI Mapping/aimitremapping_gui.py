import datetime
import json
import os
import requests
import sys
import threading
from queue import Queue, Empty
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from sentence_transformers import SentenceTransformer, util
try:
    import win32gui
    import win32con
    def hide_console_window():
        """Hides the console window in GUI mode."""
        hwnd = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
except ImportError:
    def hide_console_window():
        """Fallback function if win32gui is not available."""
        pass

DATA_FILE_PATH = 'enterprise-attack.json'
DATA_URL = 'https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json'

def download_attack_data(url=DATA_URL, file_path=DATA_FILE_PATH):
    """Downloads the MITRE ATT&CK Enterprise data if it's older than 30 days or does not exist."""
    try:
        if os.path.exists(file_path):
            last_modified_time = os.path.getmtime(file_path)
            last_modified_date = datetime.date.fromtimestamp(last_modified_time)
            current_date = datetime.date.today()
            delta = current_date - last_modified_date

            if delta.days <= 30:
                print("The existing MITRE ATT&CK Enterprise data is up-to-date.")
                return
            else:
                print("The existing data is older than 30 days. Redownloading...")

        print("Downloading MITRE ATT&CK Enterprise data...")
        response = requests.get(url)
        response.raise_for_status()
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print("Download completed successfully.")
    except requests.RequestException as e:
        print(f"Failed to download the data: {e}")
        sys.exit(1)

def load_attack_data(file_path=DATA_FILE_PATH):
    """Loads the MITRE ATT&CK data from a local file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading attack data: {e}")
        sys.exit(1)

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def find_similar_techniques(sentence, result_queue):
    """Finds and queues the top 3 similar MITRE ATT&CK techniques based on the input sentence."""
    data = load_attack_data()
    techniques = [
        {
            'id': obj['external_references'][0]['external_id'],
            'name': obj['name'],
            'description': obj['description']
        }
        for obj in data['objects'] if obj['type'] == 'attack-pattern' and 'external_references' in obj and 'description' in obj
    ]

    sentence_embedding = model.encode(sentence, convert_to_tensor=True)
    descriptions_embeddings = model.encode([tech['description'] for tech in techniques], convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(sentence_embedding, descriptions_embeddings)

    top_matches_indices = similarities.argsort(descending=True)[0][:3].tolist()
    top_matches = [techniques[idx] for idx in top_matches_indices]

    result_text = "\n\n".join([f"ID: {match['id']}\nName: {match['name']}\nDescription: {match['description']}" for match in top_matches])
    result_queue.put(result_text)

def apply_dark_theme(root):
    """Applies a dark theme to the Tkinter root window."""
    root.configure(bg='#333333')
    style = ttk.Style(root)
    style.theme_use('alt')
    style.configure('TLabel', background='#333333', foreground='white')
    style.configure('TButton', background='#555555', foreground='white', borderwidth=1)
    style.map('TButton', background=[('active', '#666666')], foreground=[('active', 'white')])

def on_submit(entry_sentence, result_text, please_wait_var, result_queue):
    """Handles the submit action for the sentence input."""
    sentence = entry_sentence.get("1.0", "end-1c")
    if not sentence.strip():
        messagebox.showinfo("Info", "Please enter a sentence.")
        return

    result_text.delete('1.0', tk.END)
    please_wait_var.set("Please Wait...")
    threading.Thread(target=lambda: find_similar_techniques(sentence, result_queue)).start()

def check_queue(result_text, result_queue, please_wait_var):
    """Checks the queue for results and updates the GUI accordingly."""
    try:
        result = result_queue.get_nowait()
        result_text.insert(tk.END, result)
        please_wait_var.set("")
    except Empty:
        pass
    root.after(100, lambda: check_queue(result_text, result_queue, please_wait_var))

if __name__ == "__main__":
    hide_console_window()
    download_attack_data()

    root = tk.Tk()
    root.title("AI MITRE ATT&CK Technique Correlation")
    apply_dark_theme(root)

    tk.Label(root, text="Enter a sentence describing a cybersecurity attack:", fg="white", bg="#333333").pack()
    entry_sentence = scrolledtext.ScrolledText(root, height=10, width=70, bg='#2b2b2b', fg='white', insertbackground='white')
    entry_sentence.pack(padx=10, pady=5)

    please_wait_var = tk.StringVar(value="")
    please_wait_label = tk.Label(root, textvariable=please_wait_var, fg="white", bg="#333333")
    please_wait_label.pack(pady=5)

    submit_button = ttk.Button(root, text="Submit", command=lambda: on_submit(entry_sentence, result_text, please_wait_var, result_queue))
    submit_button.pack(pady=5)

    tk.Label(root, text="Top 3 Technique Matches:", fg="white", bg="#333333").pack()
    result_text = scrolledtext.ScrolledText(root, height=15, width=70, bg='#2b2b2b', fg='white', insertbackground='white')
    result_text.pack(padx=10, pady=5)

    result_queue = Queue()
    root.after(100, lambda: check_queue(result_text, result_queue, please_wait_var))

    root.mainloop()
