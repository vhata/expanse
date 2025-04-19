#!/usr/bin/env python3

import sys
from pathlib import Path
from pynput import keyboard
import tkinter as tk
from tkinter import ttk, messagebox

from .core import get_expfile, load_expansions, save_expansions


class ExpanseDaemon:
    def __init__(self):
        self.expfile = get_expfile()
        self.expansions = load_expansions(self.expfile)
        self.root = None
        self.listener = None
        self.hotkey = None
        self.setup_gui()

    def save_expansions(self):
        if not save_expansions(self.expfile, self.expansions):
            print(f"Could not write to {self.expfile}.", file=sys.stderr)

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Expanse")
        self.root.geometry("400x300")

        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Listbox for expansions
        self.listbox = tk.Listbox(main_frame, height=10)
        self.listbox.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.refresh_listbox()

        # Buttons
        ttk.Button(main_frame, text="Add", command=self.add_expansion).grid(row=1, column=0, pady=5)
        ttk.Button(main_frame, text="Edit", command=self.edit_expansion).grid(row=1, column=1, pady=5)
        ttk.Button(main_frame, text="Delete", command=self.delete_expansion).grid(row=2, column=0, pady=5)
        ttk.Button(main_frame, text="Set Hotkey", command=self.set_hotkey).grid(row=2, column=1, pady=5)

        # Status label
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.grid(row=3, column=0, columnspan=2, pady=5)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for name in self.expansions["expansions"]:
            self.listbox.insert(tk.END, name)

    def add_expansion(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Expansion")
        dialog.geometry("300x200")

        ttk.Label(dialog, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Content:").grid(row=1, column=0, padx=5, pady=5)
        content_text = tk.Text(dialog, height=5, width=30)
        content_text.grid(row=1, column=1, padx=5, pady=5)

        def save():
            name = name_entry.get()
            content = content_text.get("1.0", tk.END).strip()
            if name and content:
                self.expansions["expansions"][name] = content
                self.save_expansions()
                self.refresh_listbox()
                dialog.destroy()

        ttk.Button(dialog, text="Save", command=save).grid(row=2, column=0, columnspan=2, pady=10)

    def edit_expansion(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an expansion to edit")
            return

        name = self.listbox.get(selection[0])
        content = self.expansions["expansions"][name]

        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Expansion")
        dialog.geometry("300x200")

        ttk.Label(dialog, text=f"Editing: {name}").grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        content_text = tk.Text(dialog, height=5, width=30)
        content_text.insert("1.0", content)
        content_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        def save():
            new_content = content_text.get("1.0", tk.END).strip()
            self.expansions["expansions"][name] = new_content
            self.save_expansions()
            self.refresh_listbox()
            dialog.destroy()

        ttk.Button(dialog, text="Save", command=save).grid(row=2, column=0, columnspan=2, pady=10)

    def delete_expansion(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an expansion to delete")
            return

        name = self.listbox.get(selection[0])
        if messagebox.askyesno("Confirm", f"Delete expansion '{name}'?"):
            del self.expansions["expansions"][name]
            self.save_expansions()
            self.refresh_listbox()

    def set_hotkey(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Hotkey")
        dialog.geometry("300x100")

        ttk.Label(dialog, text="Press the hotkey combination:").grid(row=0, column=0, padx=5, pady=5)
        hotkey_label = ttk.Label(dialog, text="")
        hotkey_label.grid(row=1, column=0, padx=5, pady=5)

        current_keys = set()

        def on_press(key):
            current_keys.add(key)
            hotkey_label.config(text="+".join(str(k) for k in current_keys))

        def on_release(key):
            if key in current_keys:
                current_keys.remove(key)
            if not current_keys:
                self.hotkey = tuple(current_keys)
                self.status_label.config(text=f"Hotkey set to: {hotkey_label.cget('text')}")
                dialog.destroy()

        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()

    def run(self):
        def on_activate():
            # Show a popup with available expansions
            popup = tk.Toplevel(self.root)
            popup.title("Select Expansion")
            popup.geometry("200x300")

            listbox = tk.Listbox(popup)
            for name in self.expansions["expansions"]:
                listbox.insert(tk.END, name)
            listbox.pack(fill=tk.BOTH, expand=True)

            def on_select(event):
                selection = listbox.curselection()
                if selection:
                    name = listbox.get(selection[0])
                    content = self.expansions["expansions"][name]
                    # Copy to clipboard
                    self.root.clipboard_clear()
                    self.root.clipboard_append(content)
                    popup.destroy()

            listbox.bind("<<ListboxSelect>>", on_select)

        def for_canonical(f):
            return lambda k: f(listener.canonical(k))

        hotkey = keyboard.HotKey(keyboard.HotKey.parse("<ctrl>+<alt>+e"), on_activate)

        with keyboard.Listener(
            on_press=for_canonical(hotkey.press),
            on_release=for_canonical(hotkey.release),
        ) as listener:
            self.root.mainloop()


def main():
    daemon = ExpanseDaemon()
    daemon.run()
