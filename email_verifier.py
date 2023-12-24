import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import requests
import json
import time
import threading
from queue import Queue
from tqdm import tqdm

class EmailVerifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Verifier")

        self.api_key_entry = tk.Entry(root, width=30)
        self.api_key_entry.grid(row=0, column=0, padx=5, pady=5, columnspan=2)

        self.save_api_key_button = tk.Button(root, text="Save API Key", command=self.save_api_key)
        self.save_api_key_button.grid(row=0, column=2, padx=5, pady=5)

        self.email_list_text = tk.Text(root, height=10, width=50)
        self.email_list_text.grid(row=1, column=0, padx=5, pady=5, columnspan=3)

        self.browse_button = tk.Button(root, text="Browse", command=self.browse_email_file)
        self.browse_button.grid(row=1, column=3, padx=5, pady=5)

        self.run_button = tk.Button(root, text="Run", command=self.run_verification)
        self.run_button.grid(row=1, column=4, padx=5, pady=5)

        self.pause_button = tk.Button(root, text="Pause", command=self.pause_verification)
        self.pause_button.grid(row=1, column=5, padx=5, pady=5)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_verification)
        self.stop_button.grid(row=1, column=6, padx=5, pady=5)

        self.open_button = tk.Button(root, text="Open List", command=self.open_list)
        self.open_button.grid(row=1, column=7, padx=5, pady=5)

        self.status_label = tk.Label(root, text="")
        self.status_label.grid(row=2, column=0, columnspan=8, pady=10)

        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.grid(row=3, column=0, columnspan=7, pady=5)

        self.emails = []
        self.processing = False
        self.paused = False
        self.queue = Queue()
        self.api_key_file = "api_key.txt"
        self.load_api_key()

    def save_api_key(self):
        api_key = self.api_key_entry.get()
        if api_key:
            with open(self.api_key_file, "w") as api_key_file:
                api_key_file.write(api_key)
            self.status_label.config(text="API Key saved.")
        else:
            self.status_label.config(text="Please enter an API Key.")

    def load_api_key(self):
        try:
            with open(self.api_key_file, "r") as api_key_file:
                api_key = api_key_file.read()
                self.api_key_entry.insert(tk.END, api_key)
        except FileNotFoundError:
            pass  # Ignore if the API key file doesn't exist

    def browse_email_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        with open(file_path, "r") as file:
            content = file.read()
            self.email_list_text.delete("1.0", tk.END)
            self.email_list_text.insert(tk.END, content)

    def run_verification(self):
        if not self.processing:
            self.processing = True
            self.paused = False
            email_list = self.email_list_text.get("1.0", tk.END)

            if not email_list.strip():
                self.status_label.config(text="Please enter email addresses.")
                return

            self.emails = email_list.strip().split("\n")
            self.progress_bar["value"] = 0  # Reset progress bar
            self.progress_bar["maximum"] = len(self.emails)
            threading.Thread(target=self.verify_emails).start()

    def verify_emails(self):
        api_key = self.api_key_entry.get()
        progress_file = "progress.txt"

        last_processed_index = 0

        try:
            with open(progress_file, "r") as progress_file_reader:
                last_processed_index = int(progress_file_reader.read())
        except FileNotFoundError:
            pass  # Ignore if the progress file doesn't exist

        with open("Checked_Emails.txt", "a") as output_file:
            for i in tqdm(range(last_processed_index, len(self.emails)), desc="Processing Emails", unit="email"):
                if not self.processing:
                    break
                if self.paused:
                    while self.paused:
                        time.sleep(1)

                email = self.emails[i]
                verifymail = f"https://verifymail.io/api/{email}?key={api_key}"
                r = requests.get(verifymail)

                if r.status_code == 200:
                    try:
                        if "application/json" in r.headers.get("content-type", "").lower():
                            data = r.json()
                            if data and data.get("disposable", False):
                                output_file.write(f"Is {email} a disposable email?\n")
                                output_file.write("Yes\n")
                                self.queue.put(f"Is {email} a disposable email? - Yes")
                            else:
                                self.queue.put(f"Is {email} a disposable email? - No")
                        else:
                            print(f"Non-JSON response for {email}")
                            self.queue.put(f"Non-JSON response for {email}")
                    except json.JSONDecodeError as json_err:
                        print(f"Error decoding JSON for {email}: {json_err}")
                        self.queue.put(f"Error decoding JSON for {email}: {json_err}")
                elif r.status_code == 403:
                    self.queue.put("Error 403 - Check API Key [Might be out of Requests]")
                    self.processing = False
                    return
                else:
                    print(f"Error in request for {email}: HTTP Status {r.status_code}")
                    self.queue.put(f"Error in request for {email}: HTTP Status {r.status_code}")

                with open(progress_file, "w") as progress_file_writer:
                    progress_file_writer.write(str(i + 1))

                self.status_label.config(text=f"Processing: {email}")

                self.progress_bar["value"] = i + 1
                self.root.update()

                time.sleep(1)

        self.processing = False
        self.status_label.config(text="Verification completed.")

    def pause_verification(self):
        self.paused = not self.paused
        if self.paused:
            self.status_label.config(text="Verification paused.")
        else:
            self.status_label.config(text="Verification resumed.")

    def stop_verification(self):
        self.processing = False
        self.status_label.config(text="Verification stopped.")

    def open_list(self):
        file_path = "Checked_Emails.txt"
        try:
            with open(file_path, "r") as file:
                content = file.read()
                if content:
                    self.status_label.config(text="List contents:\n" + content)
                else:
                    self.status_label.config(text="List is empty.")
        except FileNotFoundError:
            self.status_label.config(text="List file not found.")

        while not self.queue.empty():
            self.status_label["text"] += "\n" + self.queue.get()

if __name__ == "__main__":
    root = tk.Tk()
    app = EmailVerifierApp(root)
    root.mainloop()
