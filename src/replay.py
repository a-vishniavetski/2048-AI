"""Take history file and replay the game using Tkinter interface"""
import os
import tkinter as tk
from tkinter import Frame, Label, CENTER, Listbox, Scrollbar
import random
import logic
import constants as c
from copy import deepcopy
from history import History
import numpy as np


REPLAY_DIR = "history"
REPLAY_SPEED = 0.1  # Every _ seconds make a move

class GameGrid(Frame):
    
    def __init__(self):
        Frame.__init__(self)
        self.init_commands()
        self.get_files()
        self.replay_speed = REPLAY_SPEED
        self.ms_per_frame = round(1000*self.replay_speed)
        self.grid()
        self.master.title('2048')

        self.create_left_panel()
        self.create_grid_panel()

        self.history = None
        # Matrix on 0
        self.matrix = np.zeros((c.GRID_LEN, c.GRID_LEN))
        self.current_matrix = 0
        self.history_matrixs = []

        self.playing = False
        self.master.bind("<space>", self.toggle_pause)
        # Binds
        self.master.bind("<a>", self.back)
        self.master.bind("<d>", self.forward)
        # Same for arrows
        self.master.bind("<Left>", self.back)
        self.master.bind("<Right>", self.forward)
        self.update_grid_cells()
        self.update_logic()

    def toggle_pause(self, event):
        self.playing = not self.playing

    def create_grid_panel(self):
        # Frame for the game grid
        self.grid_panel = Frame(self, bg=c.BACKGROUND_COLOR_GAME, width=c.GAME_GRID_WIDTH, height=c.GAME_GRID_HEIGHT)
        self.grid_panel.grid(row=0, column=1, sticky="nsew")
        
        # Ensure the grid_panel remains square and expands as needed
        # self.grid_panel.grid_propagate(False)
        self.grid_panel.rowconfigure(4, weight=1)
        self.grid_panel.columnconfigure(4, weight=1)

        self.grid_cells = []
        self.init_grid()

        # Make sure the main frame adjusts properly
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=1)

    def create_left_panel(self):
        # Frame for the scrollable list
        self.left_panel = Frame(self, width=c.SCROLL_PANEL_WIDTH, height=c.SCROLL_PANEL_HEIGHT)
        self.left_panel.grid(row=0, column=0, sticky="ns")
        
        # Listbox to display the list of filenames or other data
        self.listbox = Listbox(self.left_panel)
        # self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox.pack(side=tk.LEFT)


        # Scrollbar for the Listbox
        self.scrollbar = Scrollbar(self.left_panel, orient="vertical")
        self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.scrollbar.config(command=self.listbox.yview)

        # Configure Listbox to work with the Scrollbar
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        
        # Example list items, replace with actual filenames or data
        for filename in self.history_files:
            self.listbox.insert(tk.END, filename)

        # Bind the <<ListboxSelect>> event to the item_selected method
        self.listbox.bind("<ButtonRelease>", self.item_selected)

    def item_selected(self, event):
            # Get the selected item index
            selected_index = self.listbox.curselection()
            
            if selected_index:
                selected_item = self.listbox.get(selected_index)
                # Execute your logic here
                print(f"Selected item: {selected_item}")
                # Example logic: Load a specific matrix based on the selection
                self.loadHistory(selected_item)
    
    def loadHistory(self, filename):
        print("Loading history")
        self.history = History("r", filename=filename, dir=REPLAY_DIR)
        self.matrix = self.history.loadMatrix(0)
        self.current_matrix = 0
        self.history_matrixs = []
        self.playing = False
        self.update_grid_cells()

    def init_grid(self):
        background = self.grid_panel

        for i in range(c.GRID_LEN):
            grid_row = []
            for j in range(c.GRID_LEN):
                cell = Frame(
                    background,
                    bg=c.BACKGROUND_COLOR_CELL_EMPTY,
                    width=c.GAME_GRID_WIDTH / c.GRID_LEN,
                    height=c.GAME_GRID_HEIGHT / c.GRID_LEN
                )
                cell.grid(
                    row=i,
                    column=j,
                    padx=c.GRID_PADDING,
                    pady=c.GRID_PADDING
                )
                t = Label(
                    master=cell,
                    text="",
                    bg=c.BACKGROUND_COLOR_CELL_EMPTY,
                    justify=CENTER,
                    font=c.FONT,
                    width=5,
                    height=2)
                t.grid()
                grid_row.append(t)
            self.grid_cells.append(grid_row)

    def update_grid_cells(self):
        print("Updating grid cells")
        for i in range(c.GRID_LEN):
            for j in range(c.GRID_LEN):
                new_number = self.matrix[i][j]
                if new_number == 0:
                    self.grid_cells[i][j].configure(text="",bg=c.BACKGROUND_COLOR_CELL_EMPTY)
                else:
                    self.grid_cells[i][j].configure(
                        text=str(new_number),
                        bg=c.BACKGROUND_COLOR_DICT[new_number],
                        fg=c.CELL_COLOR_DICT[new_number]
                    )
        self.update_idletasks()

    def update_logic(self):
        # print("Updating logic")
        if not self.playing:
            self.after(self.ms_per_frame, self.update_logic)
            return
        self.matrix = self.history.loadMatrix(self.current_matrix + 1)
        self.current_matrix += 1
        if self.matrix is None:
            # Game has ended
            self.grid_cells[1][1].configure(text="Game", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
            self.grid_cells[1][2].configure(text="Ended", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
            self.playing = False
            self.after(self.ms_per_frame, self.update_logic)
            return
        # record last move
        self.history_matrixs.append(self.matrix)
        self.update_grid_cells()
        if logic.game_state(self.matrix) == 1:
            self.grid_cells[1][1].configure(text="You", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
            self.grid_cells[1][2].configure(text="Win!", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
            self.update_grid_cells()
            self.playing = False
        if logic.game_state(self.matrix) == -1:
            self.grid_cells[1][1].configure(text="You", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
            self.grid_cells[1][2].configure(text="Lose!", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
            self.update_grid_cells()
            self.playing = False
        
        self.after(self.ms_per_frame, self.update_logic)
        
    def back(self, event):
        if self.current_matrix == 0:
            return
        self.matrix = self.history.loadMatrix(self.current_matrix - 1)
        self.current_matrix -= 1
        self.update_grid_cells()

    def forward(self, event):
        if self.current_matrix == self.history.n_of_matrices - 1:
            return
        self.matrix = self.history.loadMatrix(self.current_matrix + 1)
        self.current_matrix += 1
        self.update_grid_cells()

    def init_commands(self):
        self.commands = {
            c.KEY_UP: logic.up,
            c.KEY_DOWN: logic.down,
            c.KEY_LEFT: logic.left,
            c.KEY_RIGHT: logic.right,
            c.KEY_UP_ALT1: logic.up,
            c.KEY_DOWN_ALT1: logic.down,
            c.KEY_LEFT_ALT1: logic.left,
            c.KEY_RIGHT_ALT1: logic.right,
            c.KEY_UP_ALT2: logic.up,
            c.KEY_DOWN_ALT2: logic.down,
            c.KEY_LEFT_ALT2: logic.left,
            c.KEY_RIGHT_ALT2: logic.right,
        }

    def get_files(self):
        self.history_files = [f for f in os.listdir(REPLAY_DIR) if f.endswith(".txt")]

game_grid = GameGrid()
game_grid.mainloop()