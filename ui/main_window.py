# ui/main_window.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import requests
import time
import os
from datetime import datetime

class APITesterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("K API Tester")
        self.root.geometry("1000x700")

        # --- Create Main Frames ---
        # Left Frame for History
        self.history_frame = tk.Frame(root, bg="#F0F0F0", padx=5, pady=5)
        self.history_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Right Frame for Input/Output
        self.input_output_frame = tk.Frame(root, bg="#F0F0F0", padx=5, pady=5)
        self.input_output_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights for resizing
        root.columnconfigure(0, weight=0)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)
        self.history_frame.rowconfigure(1, weight=1)
        self.input_output_frame.columnconfigure(0, weight=1)
        self.input_output_frame.rowconfigure(3, weight=1)  # Body text expands
        self.input_output_frame.rowconfigure(5, weight=1)  # Response text expands

        # --- History Frame Widgets ---
        tk.Label(self.history_frame, text="History", bg="#F0F0F0", fg="black").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.history_listbox = tk.Listbox(self.history_frame, width=30, height=25, selectmode=tk.SINGLE, bg="white", fg="black")
        self.history_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))

        # --- Input/Output Frame Widgets ---
        # URL and Method Row
        tk.Label(self.input_output_frame, text="URL:", bg="#F0F0F0", fg="black").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.method_var = tk.StringVar(value="GET")
        self.method_combo = ttk.Combobox(self.input_output_frame, textvariable=self.method_var, values=["GET", "POST", "PUT", "DELETE"], state="readonly", width=10)
        self.method_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 5))
        self.url_entry = ttk.Entry(self.input_output_frame, width=70)
        self.url_entry.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=(0, 5))

        # Action Buttons Row
        self.send_button = tk.Button(self.input_output_frame, text="Send", command=self.on_send_click, bg="#0D47A1", fg="white", relief="raised")
        self.send_button.grid(row=0, column=3, sticky=tk.W, padx=(5, 5))

        self.save_button = tk.Button(self.input_output_frame, text="Save", command=self.on_save_click, bg="#0D47A1", fg="white", relief="raised")
        self.save_button.grid(row=0, column=4, sticky=tk.W, padx=(0, 5))

        self.clear_button = tk.Button(self.input_output_frame, text="Clear", command=self.on_clear_click, bg="#0D47A1", fg="white", relief="raised")
        self.clear_button.grid(row=0, column=5, sticky=tk.W, padx=(0, 5))

        self.dark_mode_button = tk.Button(self.input_output_frame, text="Dark Mode", command=self.toggle_dark_mode, bg="#0D47A1", fg="white", relief="raised")
        self.dark_mode_button.grid(row=0, column=6, sticky=tk.W, padx=(0, 5))

        # Headers Section
        tk.Label(self.input_output_frame, text="Headers:", bg="#F0F0F0", fg="black").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.headers_text = scrolledtext.ScrolledText(self.input_output_frame, height=8, width=80, bg="white", fg="black")
        self.headers_text.grid(row=2, column=0, columnspan=7, sticky=(tk.W, tk.E), pady=(5, 0))

        # Body (JSON) Section
        tk.Label(self.input_output_frame, text="Body (JSON):", bg="#F0F0F0", fg="black").grid(row=3, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.body_text = scrolledtext.ScrolledText(self.input_output_frame, height=8, width=80, bg="white", fg="black")
        self.body_text.grid(row=4, column=0, columnspan=7, sticky=(tk.W, tk.E), pady=(5, 0))

        # Response Section
        tk.Label(self.input_output_frame, text="Response:", bg="#F0F0F0", fg="black").grid(row=5, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.resp_body_text = scrolledtext.ScrolledText(self.input_output_frame, height=15, width=80, bg="white", fg="black")
        self.resp_body_text.grid(row=6, column=0, columnspan=7, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))

        # Export Response Button
        self.export_resp_button = tk.Button(self.input_output_frame, text="Export Response", command=self.on_export_response_click, bg="#0D47A1", fg="white", relief="raised")
        self.export_resp_button.grid(row=6, column=6, sticky=tk.SE, padx=(0, 5), pady=(0, 5))

        # --- Configure resizing for input_output_frame ---
        self.input_output_frame.columnconfigure(2, weight=1)

        # --- Initialize History File Path ---
        self.history_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'history.json')
        os.makedirs(os.path.dirname(self.history_file_path), exist_ok=True)

        # --- Load History into Listbox ---
        self.load_history_into_listbox()

        # --- Dark Mode Variables ---
        self.dark_mode = False

    def load_history_into_listbox(self):
        """Loads history from the history.json file and populates the history listbox."""
        try:
            with open(self.history_file_path, 'r', encoding='utf-8') as file:
                history = json.load(file)
        except FileNotFoundError:
            history = []
        except json.JSONDecodeError:
            print(f"Warning: Could not decode history file {self.history_file_path}. Starting with empty history.")
            history = []

        self.history_listbox.delete(0, tk.END)

        for entry in reversed(history):
            display_text = f"[{entry['timestamp'].split('T')[1][:8]}] {entry['method']} → {entry['url']}"
            self.history_listbox.insert(tk.END, display_text)

    def send_request(self, method, url, headers=None, json_data=None):
        """
        Send an API request and return the response details.
        """
        try:
            # Convert headers string to dictionary
            if headers is None:
                headers = {}
            elif isinstance(headers, str):
                if headers.strip():
                    headers = json.loads(headers)
                else:
                    headers = {}
            
            # Prepare the request
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                timeout=30
            )
            
            # Get response details
            status_code = response.status_code
            response_headers = dict(response.headers)
            
            # Safely get response body
            try:
                response_body = response.json()
                response_body = json.dumps(response_body, indent=2)
            except json.JSONDecodeError:
                response_body = response.text or "Empty response"
            except Exception:
                response_body = response.text or "Empty response"
            
            return {
                'status_code': status_code,
                'headers': response_headers,
                'body': response_body
            }
            
        except requests.exceptions.ConnectionError:
            return {
                'status_code': 0,
                'headers': {},
                'body': "Connection Error: Could not connect to the server"
            }
        except requests.exceptions.Timeout:
            return {
                'status_code': 0,
                'headers': {},
                'body': "Timeout Error: Request took too long"
            }
        except requests.exceptions.RequestException as e:
            return {
                'status_code': 0,
                'headers': {},
                'body': f"Request Error: {str(e)}"
            }
        except Exception as e:
            return {
                'status_code': 0,
                'headers': {},
                'body': f"Unexpected Error: {str(e)}"
            }

    def on_send_click(self):
        """Handles the Send button click event."""
        try:
            method = self.method_var.get()
            url = self.url_entry.get().strip()
            
            if not url:
                messagebox.showerror("Error", "Please enter a URL")
                return
            
            # Get headers
            headers_str = self.headers_text.get('1.0', tk.END).strip()
            headers = {}
            if headers_str:
                headers = json.loads(headers_str)
            
            # Get body
            json_body_str = self.body_text.get('1.0', tk.END).strip()
            json_body = None
            if json_body_str:
                json_body = json.loads(json_body_str)
            
            # Send request
            response = self.send_request(method, url, headers, json_body)
            
            # Format response for display
            response_text = f"Status: {response['status_code']}\n\n"
            response_text += "--- Headers ---\n"
            response_text += json.dumps(response['headers'], indent=2) + "\n\n"
            response_text += "--- Body ---\n"
            response_text += response['body']
            
            # Update GUI
            self.resp_body_text.delete('1.0', tk.END)
            self.resp_body_text.insert('1.0', response_text)
            
            # Add to history
            history_entry = f"{method} {url} - Status: {response['status_code']}"
            self.history_listbox.insert(0, history_entry)
            
            # Save to file
            self.save_request_to_file(method, url, headers, json_body, response)
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON parsing error: {e}"
            self.resp_body_text.delete('1.0', tk.END)
            self.resp_body_text.insert('1.0', error_msg)
            messagebox.showerror("JSON Error", error_msg)
        except Exception as e:
            error_msg = f"Error occurred: {str(e)}"
            self.resp_body_text.delete('1.0', tk.END)
            self.resp_body_text.insert('1.0', error_msg)
            messagebox.showerror("Error", error_msg)

    def save_request_to_file(self, method, url, headers, json_body, response):
        """Saves the request and response to the history file."""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "url": url,
            "request_headers": headers,
            "request_body": json_body,
            "response_status_code": response['status_code'],
            "response_headers": response['headers'],
            "response_body": response['body']
        }

        try:
            with open(self.history_file_path, 'r', encoding='utf-8') as file:
                history = json.load(file)
        except FileNotFoundError:
            history = []
        except json.JSONDecodeError:
            print(f"Warning: Could not decode existing history file {self.history_file_path}. Starting with empty history.")
            history = []

        history.append(history_entry)

        try:
            with open(self.history_file_path, 'w', encoding='utf-8') as file:
                json.dump(history, file, indent=2)
        except Exception as e:
            print(f"Error saving history to JSON: {e}")
            messagebox.showerror("Error", f"Failed to save history: {e}")

    def on_clear_click(self):
        """Clears all input and output fields in the GUI."""
        self.url_entry.delete(0, tk.END)
        self.headers_text.delete('1.0', tk.END)
        self.body_text.delete('1.0', tk.END)
        self.resp_body_text.delete('1.0', tk.END)

    def on_save_click(self):
        """Placeholder for 'Save' button functionality."""
        pass

    def on_export_response_click(self):
        """Saves the current response body to a file."""
        response_body = self.resp_body_text.get('1.0', tk.END).strip()
        if response_body and response_body != "Error occurred" and response_body != "Error occurred: ":
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(response_body)
                    messagebox.showinfo("Success", f"Response saved to {file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file: {e}")
        else:
            messagebox.showwarning("Warning", "No response to save.")

    def toggle_dark_mode(self):
        """Toggles between dark and light mode for the GUI."""
        if self.dark_mode:
            bg_color = "white"
            fg_color = "black"
            button_bg = "SystemButtonFace"
            button_fg = "black"
        else:
            bg_color = "#2d2d2d"
            fg_color = "white"
            button_bg = "#444444"
            button_fg = "white"

        self.root.configure(bg=bg_color)
        self.history_frame.configure(bg=bg_color)
        self.input_output_frame.configure(bg=bg_color)

        for widget in self.root.winfo_children():
            if isinstance(widget, (ttk.Frame, tk.Frame)):
                for child in widget.winfo_children():
                    if isinstance(child, (ttk.Label, tk.Label)):
                        child.configure(background=bg_color, foreground=fg_color)
                    elif isinstance(child, (ttk.Entry, tk.Entry, ttk.Combobox, tk.Listbox, scrolledtext.ScrolledText)):
                        child.configure(background=bg_color, foreground=fg_color, insertbackground=fg_color)
                    elif isinstance(child, (ttk.Button, tk.Button)):
                        child.configure(background=button_bg, foreground=button_fg)

        self.dark_mode = not self.dark_mode

if __name__ == "__main__":
    root = tk.Tk()
    app = APITesterGUI(root)
    root.mainloop()
