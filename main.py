# main.py
from ui.main_window import APITesterGUI
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = APITesterGUI(root)
    root.mainloop()