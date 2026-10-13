#!/usr/bin/env python3

import pyperclip
import rumps

from .core import get_expfile, load_expansions, save_expansions


class ExpanseDaemon(rumps.App):
    def __init__(self):
        # rumps adds its own Quit button once, when the app starts running, so
        # it would not survive a rebuild; rebuild_menu adds Quit itself.
        super(ExpanseDaemon, self).__init__("Expanse", quit_button=None)
        self.expfile = get_expfile()
        self.expansions = load_expansions(self.expfile)
        self.rebuild_menu()

    def rebuild_menu(self):
        """Replace the whole menu with the current snippets and the management items.

        Assigning to self.menu appends and never removes, so the menu is
        cleared first. rumps keys menu items by title unless given a key, and
        a second item with a key already in use replaces the first in the key
        mapping. Each snippet is keyed by ("snippet", name), which no
        management item or separator key can equal, so a snippet named "Quit"
        or "Add Expansion" keeps its own entry.
        """
        self.menu.clear()
        for name in self.expansions["expansions"]:
            self.menu[("snippet", name)] = rumps.MenuItem(name, callback=self.copy_expansion)
        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem("Add Expansion", callback=self.add_expansion))
        self.menu.add(rumps.MenuItem("Edit Expansion", callback=self.edit_expansion))
        self.menu.add(rumps.MenuItem("Delete Expansion", callback=self.delete_expansion))
        self.menu.add(rumps.MenuItem("Quit", callback=rumps.quit_application))

    def copy_expansion(self, sender):
        name = sender.title
        content = self.expansions["expansions"][name]
        pyperclip.copy(content)
        rumps.notification("Expanse", "Copied to clipboard", name)

    def add_expansion(self, _):
        window = rumps.Window(
            message="Enter expansion name:", title="Add Expansion", dimensions=(100, 20)
        )
        name_response = window.run()
        if not name_response.clicked:
            return

        name = name_response.text
        if not name:
            rumps.alert("Error", "Name cannot be empty")
            return

        window = rumps.Window(
            message="Enter expansion content:", title="Add Expansion", dimensions=(300, 100)
        )
        content_response = window.run()
        if not content_response.clicked:
            return

        content = content_response.text
        if not content:
            rumps.alert("Error", "Content cannot be empty")
            return

        self.expansions["expansions"][name] = content
        self.save_expansions()
        self.rebuild_menu()

    def edit_expansion(self, _):
        window = rumps.Window(
            message="Select expansion to edit:",
            title="Edit Expansion",
            dimensions=(100, 20),
            default_text="",
        )
        response = window.run()
        if not response.clicked:
            return

        name = response.text
        if name not in self.expansions["expansions"]:
            rumps.alert("Error", f"Expansion '{name}' not found")
            return

        window = rumps.Window(
            message="Enter new content:",
            title="Edit Expansion",
            dimensions=(300, 100),
            default_text=self.expansions["expansions"][name],
        )
        content_response = window.run()
        if not content_response.clicked:
            return

        content = content_response.text
        if not content:
            rumps.alert("Error", "Content cannot be empty")
            return

        self.expansions["expansions"][name] = content
        self.save_expansions()
        self.rebuild_menu()

    def delete_expansion(self, _):
        window = rumps.Window(
            message="Select expansion to delete:",
            title="Delete Expansion",
            dimensions=(100, 20),
            default_text="",
        )
        response = window.run()
        if not response.clicked:
            return

        name = response.text
        if name not in self.expansions["expansions"]:
            rumps.alert("Error", f"Expansion '{name}' not found")
            return

        if rumps.alert("Confirm", f"Delete expansion '{name}'?", ok="Delete", cancel="Cancel"):
            del self.expansions["expansions"][name]
            self.save_expansions()
            self.rebuild_menu()

    def save_expansions(self):
        if not save_expansions(self.expfile, self.expansions):
            rumps.alert("Error", f"Could not write to {self.expfile}")


def main():
    app = ExpanseDaemon()
    app.run()
