"""Take history file and replay the game using Tkinter interface"""

from tkinter import Frame, Label, CENTER
import random
import logic
import constants as c
from copy import deepcopy
from history import History


REPLAY_FILE = "history/test.txt"
REPLAY_SPEED = 1.5  # Every _ seconds make a move

class GameGrid(Frame):
    def __init__(self):
        Frame.__init__(self)

        self.replay_speed = REPLAY_SPEED
        self.ms_per_frame = round(1000*self.replay_speed)
        self.grid()
        self.master.title('2048')
        # self.master.bind("<Key>", self.key_down)

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

        self.grid_cells = []
        self.init_grid()
        self.history = History("r", REPLAY_FILE)
        self.matrix = self.history.loadMatrix(0)
        self.current_matrix = 0
        self.history_matrixs = []
        self.update_grid_cells()

        self.playing = True
        self.master.bind("<space>", self.toggle_pause)
        self.master.bind("<b>", self.back)
        self.update_logic()

    def toggle_pause(self, event):
        self.playing = not self.playing

    def init_grid(self):
        background = Frame(self, bg=c.BACKGROUND_COLOR_GAME,width=c.SIZE, height=c.SIZE)
        background.grid()

        for i in range(c.GRID_LEN):
            grid_row = []
            for j in range(c.GRID_LEN):
                cell = Frame(
                    background,
                    bg=c.BACKGROUND_COLOR_CELL_EMPTY,
                    width=c.SIZE / c.GRID_LEN,
                    height=c.SIZE / c.GRID_LEN
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
        if not self.playing:
            self.after(self.ms_per_frame, self.update_logic)
            return
        self.matrix = self.history.loadMatrix(self.current_matrix + 1)
        self.current_matrix += 1
        if self.matrix is None:
            # Game has ended
            self.grid_cells[1][1].configure(text="Game", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
            self.grid_cells[1][2].configure(text="Ended", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
            self.after(1000, self.update_logic)
            return
        # record last move
        self.history_matrixs.append(self.matrix)
        self.update_grid_cells()
        if logic.game_state(self.matrix) == 1:
            self.grid_cells[1][1].configure(text="You", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
            self.grid_cells[1][2].configure(text="Win!", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
        if logic.game_state(self.matrix) == -1:
            self.grid_cells[1][1].configure(text="You", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
            self.grid_cells[1][2].configure(text="Lose!", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
        
        self.after(1000, self.update_logic)
        
    def back(self, event):
        if self.current_matrix == 0:
            return
        self.matrix = self.history.loadMatrix(self.current_matrix - 1)
        self.current_matrix -= 1
        self.update_grid_cells()


game_grid = GameGrid()
game_grid.mainloop()