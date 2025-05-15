import threading
from tkinter import Frame, Entry, Button, Canvas, Label, Scrollbar
import tkinter as tk
import logging
logger = logging.getLogger(__name__)

class ChatApp:
    def __init__(self, root, dialogue_pipeline):
        self.root = root
        self.dialogue_pipeline = dialogue_pipeline
        self.root.title("ChatApp")
        self.root.configure(bg="#f0f2f5")
        self.root.minsize(400, 300)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.chat_frame = Frame(self.root, bg="#f0f2f5")
        self.chat_frame.grid(row=0, column=0, sticky="nsew")

        self.canvas = Canvas(self.chat_frame, bg="#f0f2f5", highlightthickness=0)
        self.scrollbar = Scrollbar(self.chat_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas, bg="#f0f2f5")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.input_frame = Frame(self.root, bg="#f0f2f5")
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.user_input = Entry(self.input_frame, font=("Segoe UI", 12))
        self.user_input.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.user_input.bind("<Return>", self.send_message)

        self.send_button = Button(self.input_frame, text="Send", bg="#0084ff", fg="white",
                                  font=("Segoe UI", 10, "bold"), relief="flat", command=self.send_message)
        self.send_button.grid(row=0, column=1)

    def send_message(self, event=None):
        message = self.user_input.get().strip()
        if not message:
            return

        self.__add_bubble__("You", message, align="right", bg="#0084ff", fg="white")
        self.user_input.delete(0, tk.END)

        threading.Thread(target=self.__evaluate_message__, args=(message,), daemon=True).start()

    def __evaluate_message__(self, message: str):
        try:
            response = self.dialogue_pipeline.evaluate(message)
        except Exception as e:
            response = f"[Error] {e}"

        self.root.after(0, self.__add_bubble__, "Bot", response, "left", "#e4e6eb", "black")

    def __add_bubble__(self, sender: str, message: str, align: str, bg: str, fg: str):
        bubble_frame = Frame(self.scrollable_frame, bg="#f0f2f5")
        bubble = Label(bubble_frame,
                       text=message,
                       bg=bg,
                       fg=fg,
                       wraplength=300,
                       justify="left",
                       font=("Segoe UI", 10),
                       padx=10,
                       pady=7)

        if align == "right":
            bubble.pack(anchor="e", padx=5, pady=2)
            bubble_frame.pack(anchor="e", fill="x", padx=10)
        else:
            bubble.pack(anchor="w", padx=5, pady=2)
            bubble_frame.pack(anchor="w", fill="x", padx=10)

        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)