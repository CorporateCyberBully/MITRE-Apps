import json
import os
import requests
import subprocess
import sys
import threading
from queue import Queue, Empty
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from sentence_transformers import SentenceTransformer, util

def install_and_import_packages():
    required_packages = ["sentence-transformers", "requests", "numpy"]
    for package in required_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--user"])
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {package}: {e}")
            sys.exit(1)

install_and_import_packages()

DATA_FILE_PATH = 'enterprise-attack.json'
DATA_URL = 'https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json'

def download_attack_data(url=DATA_URL, file_path=DATA_FILE_PATH):
    if not os.path.exists(file_path):
        print("Downloading MITRE ATT&CK Enterprise data...")
        response = requests.get(url)
        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print("Download completed successfully.")
        else:
            print("Failed to download the data.")
            sys.exit(1)
    else:
        print("MITRE ATT&CK Enterprise data already exists.")

def load_attack_data(file_path=DATA_FILE_PATH):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def find_similar_techniques(sentence, result_queue):
    data = load_attack_data()
    techniques = [
        {
            'id': obj['external_references'][0]['external_id'],
            'name': obj['name'],
            'description': obj['description']
        }
        for obj in data['objects'] if obj['type'] == 'attack-pattern' and 'external_references' in obj and 'description' in obj
    ]

    # Ensure there are techniques to compare against
    if not techniques:
        result_text = "No techniques found in the dataset."
        result_queue.put(result_text)
        return

    sentence_embedding = model.encode(sentence, convert_to_tensor=True)
    descriptions_embeddings = model.encode([tech['description'] for tech in techniques], convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(sentence_embedding, descriptions_embeddings)

    # Make sure there are similarities to sort and select from
    if similarities.size(1) < 3:
        result_text = "Not enough data for similarity comparison."
        result_queue.put(result_text)
        return

    top_matches_indices = similarities.argsort(descending=True)[0][:3].tolist()

    top_matches = [techniques[idx] for idx in top_matches_indices]
    result_text = "\n\n".join([f"ID: {match['id']}\nName: {match['name']}\nDescription: {match['description']}" for match in top_matches])
    result_queue.put(result_text)


def update_progress(value, progress_bar):
    progress_bar['value'] = value
    root.update_idletasks()

def on_submit(entry_sentence, result_text, progress_bar, result_queue):
    sentence = entry_sentence.get("1.0", "end-1c")
    if not sentence.strip():
        messagebox.showinfo("Info", "Please enter a sentence.")
        return

    progress_bar['value'] = 0
    result_text.delete('1.0', tk.END)
    threading.Thread(target=lambda: find_similar_techniques(sentence, result_queue)).start()

def check_queue(result_text, result_queue):
    try:
        result = result_queue.get_nowait()
        result_text.insert(tk.END, result)
    except Empty:
        pass
    root.after(100, lambda: check_queue(result_text, result_queue))

if __name__ == "__main__":
    download_attack_data()

    root = tk.Tk()
    root.title("AI MITRE ATT&CK Technique Correlation")

    tk.Label(root, text="Enter a sentence describing a cybersecurity attack:").pack()
    entry_sentence = scrolledtext.ScrolledText(root, height=5)
    entry_sentence.pack()

    submit_button = tk.Button(root, text="Submit", command=lambda: on_submit(entry_sentence, result_text, progress_bar, result_queue))
    submit_button.pack()

    progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=400, mode='determinate')
    progress_bar.pack()

    tk.Label(root, text="Top 3 Technique Matches:").pack()
    result_text = scrolledtext.ScrolledText(root, height=10)
    result_text.pack()

    result_queue = Queue()
    root.after(100, lambda: check_queue(result_text, result_queue))

    root.mainloop()
