import argparse
import json
import os
import tkinter as tk
import tkinter.ttk as ttk
import webbrowser
from tkinter import filedialog
from tkinter import font
from tkinter import messagebox


# === Config ===
MAX_N_SHOW_ITEM = 300
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


class JSONTreeFrame(ttk.Frame):
    class Listbox(tk.Listbox):
        

        def autowidth(self, maxwidth):
            f = font.Font(font=self.cget("font"))
            pixels = 0
            for item in self.get(0, "end"):
                pixels = max(pixels, f.measure(item))

            pixels = pixels + 10
            width = int(self.cget("width"))
            for w in range(0, maxwidth + 1, 5):
                if self.winfo_reqwidth() >= pixels:
                    break
                self.config(width=width + w)

    def __init__(self, master, json_path=None, initial_dir="~/"):
        super().__init__(master)
        self.tree = ttk.Treeview(self)
        self.create_widgets()
        self.sub_win = None
        self.initial_dir = initial_dir

        if json_path:
            self.set_table_data_from_json(json_path)

    def create_widgets(self):
        self.tree.bind('<Double-1>', self.click_item)

        ysb = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=ysb.set)

        self.tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        ysb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def insert_node(self, parent, key, value):
        node = self.tree.insert(parent, 'end', text=key, open=False)

        if value is None:
            return

        if type(value) is not dict:
            if type(value) is list:
                value = value[0:MAX_N_SHOW_ITEM]
            self.tree.insert(node, 'end', text=value, open=False)
        else:
            for (key, value) in value.items():
                self.insert_node(node, key, value)

    def click_item(self, _):

        item_id = self.tree.selection()
        item_text = self.tree.item(item_id, 'text')

    def select_json_file(self):
        file_path = filedialog.askopenfilename(
            initialdir=self.initial_dir, filetypes=[("JSON files", "*.json")])
        self.set_table_data_from_json(file_path)

    def get_all_children(self, tree, item=""):
        children = tree.get_children(item)
        for child in children:
            children += self.get_all_children(tree, child)
        return children


    def set_table_data_from_json(self, file_path):
        data = self.load_json_data(file_path)
        self.insert_nodes(data)

    def insert_nodes(self, data):
        parent = ""

        for (key, value) in data.items():
            self.insert_node(parent, key, value)


    @staticmethod
    def load_json_data(file_path):
        with open(file_path) as f:
            return json.load(f)
