import math
import os
import random
import time
from functools import partial
from operator import attrgetter
from tkinter import *
from tkinter import font
from tkinter import messagebox

import numpy
from asciimatics.effects import Cycle, Stars
from asciimatics.renderers import FigletText
from asciimatics.scene import Scene


class Maze51:
    class CreateToolTip(object):
        def __init__(self, widget, text='widget info'):
            self.waittime = 500  # milliseconds
            self.wraplength = 180  # pixels
            self.widget = widget
            self.text = text
            self.widget.bind("<Enter>", self.enter)
            self.widget.bind("<Leave>", self.leave)
            self.widget.bind("<ButtonPress>", self.leave)
            self._id = None
            self.tw = None

        def enter(self, event=None):
            self.schedule()

        def leave(self, event=None):
            self.unschedule()
            self.hidetip()

        def schedule(self):
            self.unschedule()
            self._id = self.widget.after(self.waittime, self.showtip)

        def unschedule(self):
            _id = self._id
            self._id = None
            if _id:
                self.widget.after_cancel(_id)

        def showtip(self, event=None):
            x, y, cx, cy = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 20  # creates a toplevel window
            self.tw = Toplevel(self.widget)  # Leaves only the label and removes the app window
            self.tw.wm_overrideredirect(True)
            self.tw.wm_geometry("+%d+%d" % (x, y))
            label = Label(self.tw, text=self.text, justify='left', background="#ffffff", relief='solid', borderwidth=1,
                          wraplength=self.wraplength)
            label.pack(ipadx=1)

        def hidetip(self):
            tw = self.tw
            self.tw = None
            if tw:
                tw.destroy()

    class MyMaze(object):
        """  Helper class that creates a random, perfect (without cycles) maze """

        def __init__(self, x_dimension, y_dimension):
            self.dimensionX = x_dimension  # dimension of maze
            self.dimensionY = y_dimension
            self.gridDimensionX = x_dimension * 2 + 1  # dimension of output grid
            self.gridDimensionY = y_dimension * 2 + 1

            self.mazeGrid = [[' ' for y in range(self.gridDimensionY)] for x in
                             range(self.gridDimensionX)]  # output grid
            self.cells = [[self.Cell(x, y, False) for y in range(self.dimensionY)] for x in
                          range(self.dimensionX)]  # 2d array of Cells
            self.generate_maze()
            self.update_grid()

        class Cell(object):
            def __init__(self, x, y, is_wall=True):
                self.neighbors = []  # cells this cell is connected to
                self.open = True  # if true, has yet to be used in generation
                self.x = x  # coordinates
                self.y = y
                self.wall = is_wall  # impassable cell

            def add_neighbor(self, other):
                if other not in self.neighbors:  # avoid duplicates
                    self.neighbors.append(other)
                if self not in other.neighbors:  # avoid duplicates
                    other.neighbors.append(self)

            def is_cell_below_neighbor(self):
                return self.__class__(self.x, self.y + 1) in self.neighbors

            def is_cell_right_neighbor(self):
                return self.__class__(self.x + 1, self.y) in self.neighbors

            def __eq__(self, other):
                if isinstance(other, self.__class__):
                    return self.x == other.x and self.y == other.y
                else:
                    return False

        def generate_maze(self):
            start_at = self.get_cell(0, 0)  # STARTING POINT
            start_at.open = False  # indicate cell closed for generation
            cells = [start_at]
            while cells:
                if random.randint(0, 9) == 0:
                    cell = cells.pop(random.randint(0, cells.__len__()) - 1)
                else:
                    cell = cells.pop(cells.__len__() - 1)
                neighbors = []
                potential_neighbors = [self.get_cell(cell.x + 1, cell.y), self.get_cell(cell.x, cell.y + 1),
                                       self.get_cell(cell.x - 1, cell.y), self.get_cell(cell.x, cell.y - 1)]
                for other in potential_neighbors:
                    if other is None or other.wall or not other.open:
                        continue
                    neighbors.append(other)
                if not neighbors:
                    continue
                selected = neighbors[random.randint(0, neighbors.__len__()) - 1]
                selected.open = False  # indicate cell closed for generation
                cell.add_neighbor(selected)
                cells.append(cell)
                cells.append(selected)

        def get_cell(self, x, y):
            if x < 0 or y < 0:
                return None
            try:
                return self.cells[x][y]
            except IndexError:  # catch out of bounds
                return None

        def update_grid(self):
            """ draw the maze """
            back_char = ' '
            wall_char = 'X'
            cell_char = ' '
            # fill background
            for x in range(self.gridDimensionX):
                for y in range(self.gridDimensionY):
                    self.mazeGrid[x][y] = back_char
            # build walls
            for x in range(self.gridDimensionX):
                for y in range(self.gridDimensionY):
                    if x % 2 == 0 or y % 2 == 0:
                        self.mazeGrid[x][y] = wall_char
            # make meaningful representation
            for x in range(self.dimensionX):
                for y in range(self.dimensionY):
                    current = self.get_cell(x, y)
                    grid_x = x * 2 + 1
                    grid_y = y * 2 + 1
                    self.mazeGrid[grid_x][grid_y] = cell_char
                    if current.is_cell_below_neighbor():
                        self.mazeGrid[grid_x][grid_y + 1] = cell_char
                    if current.is_cell_right_neighbor():
                        self.mazeGrid[grid_x + 1][grid_y] = cell_char

    class Cell(object):
        """ Helper class that represents the cell of the grid """

        def __init__(self, row, col):
            self.row = row
            self.col = col
            self.g = 0
            self.h = 0
            self.f = 0
            self.dist = 0
            self.prev = self.__class__

        def __eq__(self, other):
            """ useful Cell equivalence """
            if isinstance(other, self.__class__):
                return self.row == other.row and self.col == other.col
            else:
                return False

    INFINITY = sys.maxsize  # The representation of the infinite
    EMPTY = 0  # empty cell
    OBST = 1  # cell with obstacle
    ROBOT = 2  # the position of the robot
    TARGET = 3  # the position of the target
    FRONTIER = 4  # cells that form the frontier (OPEN SET)
    CLOSED = 5  # cells that form the CLOSED SET
    ROUTE = 6  # cells that form the robot-to-target path

    MSG_DRAW_AND_SELECT = "\"Paint\" obstacles, then click 'Real-Time' or 'Step-by-Step' or 'Animation'"
    MSG_SELECT_STEP_BY_STEP_ETC = "Click 'Step-by-Step' or 'Animation' or 'Clear'"
    MSG_NO_SOLUTION = "There is no path to the target !!!"

    def __init__(self, maze):
        """Constructor"""
        center(maze)

        self.rows = 41  # the number of rows of the grid
        self.columns = 41  # the number of columns of the grid
        self.square_size = int(500 / self.rows)  # the cell size in pixels
        self.arrow_size = int(self.square_size / 2)  # the size of the tips of the arrow pointing the predecessor cell

        self.openSet = []  # the OPEN SET
        self.closedSet = []  # the CLOSED SET
        self.graph = []  # the set of vertices of the graph to be explored by not best's algorithm

        self.robotStart = self.Cell(self.rows - 2, 1)  # the initial position of the robot
        self.targetPos = self.Cell(1, self.columns - 2)  # the position of the target

        self.grid = [[]]  # the grid
        self.realTime = False  # Solution is displayed instantly
        self.found = False  # flag that the goal was found
        self.searching = False  # flag that the search is in progress
        self.endOfSearch = False  # flag that the search came to an end
        self.animation = False  # flag that the animation is running
        self.delay = 500  # time delay of animation (in msec)
        self.expanded = 0  # the number of nodes that have been expanded
        self.selected_algo = "DFS"  # DFS is initially selected
        self.array = numpy.array([0] * (83 * 83))
        self.cur_row = self.cur_col = self.cur_val = 0
        app_highlight_font = font.Font(app, family='Helvetica', size=10, weight='bold')
        ##########################################
        #   the widgets of the user interface    #
        ##########################################
        self.message = Label(app, text=self.MSG_DRAW_AND_SELECT, width=55, anchor='center', font=('Helvetica', 12),
                             fg="BLUE")
        self.message.place(x=5, y=510)

        rows_lbl = Label(app, text="# of rows (5-83):", width=16, anchor='e', font=("Helvetica", 9))
        rows_lbl.place(x=530, y=5)

        validate_rows_cmd = (app.register(self.validate_rows), '%P')
        invalid_rows_cmd = (app.register(self.invalid_rows))

        self.rows_var = StringVar()
        self.rows_var.set(41)
        self.rowsSpinner = Spinbox(app, width=3, from_=5, to=83, textvariable=self.rows_var, validate='focus',
                                   validatecommand=validate_rows_cmd, invalidcommand=invalid_rows_cmd)
        self.rowsSpinner.place(x=652, y=5)

        cols_lbl = Label(app, text="# of columns (5-83):", width=16, anchor='e', font=("Helvetica", 9))
        cols_lbl.place(x=530, y=35)

        validate_cols_cmd = (app.register(self.validate_cols), '%P')
        invalid_cols_cmd = (app.register(self.invalid_cols))

        self.cols_var = StringVar()
        self.cols_var.set(41)
        self.colsSpinner = Spinbox(app, width=3, from_=5, to=83, textvariable=self.cols_var, validate='focus',
                                   validatecommand=validate_cols_cmd, invalidcommand=invalid_cols_cmd)
        self.colsSpinner.place(x=652, y=35)

        self.buttons = list()
        buttons_tool_tips = ("Clears and redraws the grid according to the given rows and columns",
                             "Creates a random maze",
                             "First click: clears search, Second click: clears obstacles",
                             "Position of obstacles, robot and target can be changed when search is underway",
                             "The search is performed step-by-step for every click",
                             "The search is performed automatically")
        for i, action in enumerate(("New grid", "Maze", "Clear", "Real-Time", "Step-by-Step", "Animation")):
            btn = Button(app, text=action, width=20, font=app_highlight_font, bg="light grey",
                         command=partial(self.select_action, action))
            btn.place(x=515, y=65 + 30 * i)
            self.CreateToolTip(btn, buttons_tool_tips[i])
            self.buttons.append(btn)

        time_delay = Label(app, text="Delay (msec)", width=27, anchor='center', font=("Helvetica", 8))
        time_delay.place(x=515, y=243)
        slider_value = IntVar()
        slider_value.set(500)
        self.slider = Scale(app, orient=HORIZONTAL, length=165, width=10, from_=0, to=1000, showvalue=1,
                            variable=slider_value, )
        self.slider.place(x=515, y=260)
        self.CreateToolTip(self.slider, "Regulates the delay for each step (0 to 1000 msec)")
        self.frame = LabelFrame(app, text="Algorithms", width=170, height=100)
        self.frame.place(x=515, y=300)
        self.radio_buttons = list()
        radio_buttons_tool_tips = (" ", " ", " ", "Greedy search algorithm", " ")

        btn = Radiobutton(self.frame, text="Best First Search", font=app_highlight_font, value=4,
                          command=partial(self.select_algo, "Greedy"))
        btn.place(x=10 if 0 % 2 == 0 else 90, y=int(0 / 2) * 25)
        self.CreateToolTip(btn, radio_buttons_tool_tips[0])
        btn.deselect()
        self.radio_buttons.append(btn)
        self.radio_buttons[0].select()

        self.diagonal = IntVar()
        self.diagonalBtn = Checkbutton(app, text="Diagonal movements", font=app_highlight_font, variable=self.diagonal)
        self.diagonalBtn.place(x=515, y=405)
        self.CreateToolTip(self.diagonalBtn, "Diagonal movements are also allowed")

        self.drawArrows = IntVar()
        self.drawArrowsBtn = Checkbutton(app, text="Arrows to predecessors", font=app_highlight_font,
                                         variable=self.drawArrows)
        self.drawArrowsBtn.place(x=515, y=430)
        self.drawArrowsBtn.select()
        self.CreateToolTip(self.drawArrowsBtn, "Draw arrows to predecessors")

        memo_colors = ("RED", "GREEN", "BLUE", "CYAN")
        for i, memo in enumerate(("Robot", "Target", "Frontier", "Closed set")):
            label = Label(app, text=memo, width=8, anchor='center', fg=memo_colors[i], font=("Helvetica", 11))
            label.place(x=515 if i % 2 == 0 else 605, y=460 + int(i / 2) * 20)
        self.canvas = Canvas(app, bd=0, highlightthickness=0)
        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.initialize_grid(False)

    def validate_rows(self, entry):
        try:
            value = int(entry)
            valid = value in range(5, 84)
        except ValueError:
            valid = False
        if not valid:
            app.bell()
            self.rowsSpinner.after_idle(lambda: self.rowsSpinner.config(validate='focusout'))
        return valid

    def invalid_rows(self):
        self.rows_var.set(41)

    def validate_cols(self, entry):
        try:
            value = int(entry)
            valid = value in range(5, 84)
        except ValueError:
            valid = False
        if not valid:
            app.bell()
            self.colsSpinner.after_idle(lambda: self.colsSpinner.config(validate='focusout'))
        return valid

    def invalid_cols(self):
        self.cols_var.set(41)

    def select_action(self, action):
        if action == "New grid":
            self.reset_click()
        elif action == "Maze":
            self.maze_click()
        elif action == "Clear":
            self.clear_click()
        elif action == "Real-Time":
            self.real_time_click()
        elif action == "Step-by-Step":
            self.step_by_step_click()
        elif action == "Animation":
            self.animation_click()

    def select_algo(self, algorithm):
        self.selected_algo = algorithm

    def left_click(self, event):
        """Handles clicks of left mouse button as we add or remove obstacles"""
        row = int(event.y / self.square_size)
        col = int(event.x / self.square_size)
        if row in range(self.rows) and col in range(self.columns):
            if True if self.realTime else (not self.found and not self.searching):
                if self.realTime:
                    self.fill_grid()
                self.cur_row = row
                self.cur_col = col
                self.cur_val = self.grid[row][col]
                if self.cur_val == self.EMPTY:
                    self.grid[row][col] = self.OBST
                    self.paint_cell(row, col, "BLACK")
                if self.cur_val == self.OBST:
                    self.grid[row][col] = self.EMPTY
                    self.paint_cell(row, col, "WHITE")
                if self.realTime and self.selected_algo == "not best":
                    self.initialize_dijkstra()
            if self.realTime:
                self.real_Time_action()

    def drag(self, event):
        """Handles mouse movements as we "paint" obstacles or move the robot and/or target."""
        row = int(event.y / self.square_size)
        col = int(event.x / self.square_size)
        if row in range(self.rows) and col in range(self.columns):
            if True if self.realTime else (not self.found and not self.searching):
                if self.realTime:
                    self.fill_grid()
                if self.Cell(row, col) != self.Cell(self.cur_row, self.cur_col) and \
                        self.cur_val in [self.ROBOT, self.TARGET]:
                    new_val = self.grid[row][col]
                    if new_val == self.EMPTY:
                        self.grid[row][col] = self.cur_val
                        if self.cur_val == self.ROBOT:
                            self.grid[self.robotStart.row][self.robotStart.col] = self.EMPTY
                            self.paint_cell(self.robotStart.row, self.robotStart.col, "WHITE")
                            self.robotStart.row = row
                            self.robotStart.col = col
                            self.grid[self.robotStart.row][self.robotStart.col] = self.ROBOT
                            self.paint_cell(self.robotStart.row, self.robotStart.col, "RED")
                        else:
                            self.grid[self.targetPos.row][self.targetPos.col] = self.EMPTY
                            self.paint_cell(self.targetPos.row, self.targetPos.col, "WHITE")
                            self.targetPos.row = row
                            self.targetPos.col = col
                            self.grid[self.targetPos.row][self.targetPos.col] = self.TARGET
                            self.paint_cell(self.targetPos.row, self.targetPos.col, "GREEN")
                        self.cur_row = row
                        self.cur_col = col
                        self.cur_val = self.grid[row][col]
                elif self.grid[row][col] != self.ROBOT and self.grid[row][col] != self.TARGET:
                    self.grid[row][col] = self.OBST
                    self.paint_cell(row, col, "BLACK")
                if self.realTime and self.selected_algo == "not best":
                    self.initialize_dijkstra()
            if self.realTime:
                self.real_Time_action()

    def initialize_grid(self, make_maze):
        """Creates a new clean grid or a new maze"""
        self.rows = int(self.rowsSpinner.get())
        self.columns = int(self.colsSpinner.get())
        if make_maze and self.rows % 2 == 0:
            self.rows -= 1
        if make_maze and self.columns % 2 == 0:
            self.columns -= 1
        self.square_size = int(500 / (self.rows if self.rows > self.columns else self.columns))
        self.arrow_size = int(self.square_size / 2)
        self.grid = self.array[:self.rows * self.columns]
        self.grid = self.grid.reshape(self.rows, self.columns)
        self.canvas.configure(width=self.columns * self.square_size + 1, height=self.rows * self.square_size + 1)
        self.canvas.place(x=10, y=10)
        self.canvas.create_rectangle(0, 0, self.columns * self.square_size + 1, self.rows * self.square_size + 1,
                                     width=0, fill="DARK GREY")
        for r in list(range(self.rows)):
            for c in list(range(self.columns)):
                self.grid[r][c] = self.EMPTY
        self.robotStart = self.Cell(self.rows - 2, 1)
        self.targetPos = self.Cell(1, self.columns - 2)
        self.fill_grid()
        if make_maze:
            maze = self.MyMaze(int(self.rows / 2), int(self.columns / 2))
            for x in range(maze.gridDimensionX):
                for y in range(maze.gridDimensionY):
                    if maze.mazeGrid[x][y] == 'X':  # maze.wall_char:
                        self.grid[x][y] = self.OBST
        self.repaint()

    def fill_grid(self):
        """Gives initial values for the cells in the grid."""
        if self.searching or self.endOfSearch:
            for r in list(range(self.rows)):
                for c in list(range(self.columns)):
                    if self.grid[r][c] in [self.FRONTIER, self.CLOSED, self.ROUTE]:
                        self.grid[r][c] = self.EMPTY
                    if self.grid[r][c] == self.ROBOT:
                        self.robotStart = self.Cell(r, c)
            self.searching = False
        else:
            for r in list(range(self.rows)):
                for c in list(range(self.columns)):
                    self.grid[r][c] = self.EMPTY
            self.robotStart = self.Cell(self.rows - 2, 1)
            self.targetPos = self.Cell(1, self.columns - 2)
        if self.selected_algo in ["Greedy"]:
            self.robotStart.g = 0
            self.robotStart.h = 0
            self.robotStart.f = 0
        self.expanded = 0
        self.found = False
        self.searching = False
        self.endOfSearch = False

        self.openSet.clear()
        self.closedSet.clear()
        self.openSet = [self.robotStart]
        self.closedSet = []

        self.grid[self.targetPos.row][self.targetPos.col] = self.TARGET
        self.grid[self.robotStart.row][self.robotStart.col] = self.ROBOT
        self.message.configure(text=self.MSG_DRAW_AND_SELECT)

        self.repaint()

    def repaint(self):
        """Repaints the grid"""
        color = ""
        for r in list(range(self.rows)):
            for c in list(range(self.columns)):
                if self.grid[r][c] == self.EMPTY:
                    color = "WHITE"
                elif self.grid[r][c] == self.ROBOT:
                    color = "RED"
                elif self.grid[r][c] == self.TARGET:
                    color = "GREEN"
                elif self.grid[r][c] == self.OBST:
                    color = "BLACK"
                elif self.grid[r][c] == self.FRONTIER:
                    color = "BLUE"
                elif self.grid[r][c] == self.CLOSED:
                    color = "CYAN"
                elif self.grid[r][c] == self.ROUTE:
                    color = "YELLOW"
                self.paint_cell(r, c, color)

    def paint_cell(self, row, col, color):
        self.canvas.create_rectangle(1 + col * self.square_size, 1 + row * self.square_size,
                                     1 + (col + 1) * self.square_size - 1, 1 + (row + 1) * self.square_size - 1,
                                     width=0, fill=color)

    def reset_click(self):
        """ Action performed when user clicks "New grid" button """
        self.animation = False
        self.realTime = False
        for but in self.buttons:
            but.configure(state="normal")
        self.buttons[3].configure(fg="BLACK")  # Real-Time button
        self.slider.configure(state="normal")
        for but in self.radio_buttons:
            but.configure(state="normal")
        self.diagonalBtn.configure(state="normal")
        self.drawArrowsBtn.configure(state="normal")
        self.initialize_grid(False)

    def maze_click(self):
        """Action performed when user clicks "Maze" button"""
        self.animation = False
        self.realTime = False
        for but in self.buttons:
            but.configure(state="normal")
        self.buttons[3].configure(fg="BLACK")  # Real-Time button
        self.slider.configure(state="normal")
        for but in self.radio_buttons:
            but.configure(state="normal")
        self.diagonalBtn.configure(state="normal")
        self.drawArrowsBtn.configure(state="normal")
        self.initialize_grid(True)

    def clear_click(self):
        """  Action performed when user clicks "Clear" button """
        self.animation = False
        self.realTime = False
        for but in self.buttons:
            but.configure(state="normal")
        self.buttons[3].configure(fg="BLACK")  # Real-Time button
        self.slider.configure(state="normal")
        for but in self.radio_buttons:
            but.configure(state="normal")
        self.diagonalBtn.configure(state="normal")
        self.drawArrowsBtn.configure(state="normal")
        self.fill_grid()

    def real_time_click(self):
        """ Action performed when user clicks "Real-Time" button """
        if self.realTime:
            return
        self.realTime = True
        self.searching = True
        if self.selected_algo == "not best":
            self.initialize_dijkstra()
        self.buttons[3].configure(fg="RED")  # Real-Time button
        self.slider.configure(state="disabled")
        for but in self.radio_buttons:
            but.configure(state="disabled")
        self.diagonalBtn.configure(state="disabled")
        self.drawArrowsBtn.configure(state="disabled")
        self.real_Time_action()

    def real_Time_action(self):
        """Action performed during real-time search"""
        while not self.endOfSearch:
            self.check_termination()

    def step_by_step_click(self):
        """Action performed when user clicks "Step-by-Step" button"""
        if self.found or self.endOfSearch:
            return
        if not self.searching and self.selected_algo == "not best":
            self.initialize_dijkstra()
        self.animation = False
        self.searching = True
        self.message.configure(text=self.MSG_SELECT_STEP_BY_STEP_ETC)
        self.buttons[3].configure(state="disabled")  # Real-Time button
        for but in self.radio_buttons:
            but.configure(state="disabled")
        self.diagonalBtn.configure(state="disabled")
        self.drawArrowsBtn.configure(state="disabled")
        self.check_termination()

    def animation_click(self):
        """Action performed when user clicks "Animation" button"""
        self.animation = True
        if not self.searching and self.selected_algo == "not best":
            self.initialize_dijkstra()
        self.searching = True
        self.message.configure(text=self.MSG_SELECT_STEP_BY_STEP_ETC)
        self.buttons[3].configure(state="disabled")  # Real-Time button
        for but in self.radio_buttons:
            but.configure(state="disabled")
        self.diagonalBtn.configure(state="disabled")
        self.drawArrowsBtn.configure(state="disabled")
        self.delay = self.slider.get()
        self.animation_action()

    def animation_action(self):
        """ The action periodically performed during searching in animation mode """
        if self.animation:
            self.check_termination()
            if self.endOfSearch:
                return
            self.canvas.after(self.delay, self.animation_action)

    def check_termination(self):
        """ Checks if search is completed """
        if (self.selected_algo == "not best" and not self.graph) or \
                self.selected_algo != "not best" and not self.openSet:
            self.endOfSearch = True
            self.grid[self.robotStart.row][self.robotStart.col] = self.ROBOT
            self.message.configure(text=self.MSG_NO_SOLUTION)
            self.buttons[4].configure(state="disabled")  # Step-by-Step button
            self.buttons[5].configure(state="disabled")  # Animation button
            self.slider.configure(state="disabled")
            self.repaint()
            if self.drawArrows.get():
                self.draw_arrows()
        else:
            self.expand_node()
            if self.found:
                self.endOfSearch = True
                self.plot_route()
                self.buttons[4].configure(state="disabled")  # Step-by-Step button
                self.buttons[5].configure(state="disabled")  # Animation button
                self.slider.configure(state="disabled")

    def expand_node(self):
        """ Expands a node and creates his successors """  # not best's algorithm to handle separately
        if self.selected_algo == "not best":  # 11: while Q is not empty:
            if not self.graph:
                return
            u = self.graph.pop(0)
            self.closedSet.append(u)  # Add vertex u in closed set
            if u == self.targetPos:  # If target has been found ...
                self.found = True
                return
            self.expanded += 1
            self.grid[u.row][u.col] = self.CLOSED
            self.paint_cell(u.row, u.col, "CYAN")
            if u.dist == self.INFINITY:
                return
            neighbors = self.create_successors(u, False)
            for v in neighbors:
                alt = u.dist + self.dist_between(u, v)
                if alt < v.dist:
                    v.dist = alt
                    v.prev = u
                    self.grid[v.row][v.col] = self.FRONTIER
                    self.paint_cell(v.row, v.col, "BLUE")
                    self.graph.sort(key=attrgetter("dist"))
        else:
            if self.selected_algo in ["DFS", "BFS"]:
                current = self.openSet.pop(0)
            else:
                self.openSet.sort(key=attrgetter("f"))
                current = self.openSet.pop(0)
            self.closedSet.insert(0, current)
            self.grid[current.row][current.col] = self.CLOSED
            self.paint_cell(current.row, current.col, "CYAN")
            if current == self.targetPos:
                last = self.targetPos
                last.prev = current.prev
                self.closedSet.append(last)
                self.found = True
                return
            self.expanded += 1
            successors = self.create_successors(current, False)
            for cell in successors:
                if self.selected_algo == "DFS":
                    self.openSet.insert(0, cell)
                    self.grid[cell.row][cell.col] = self.FRONTIER
                    self.paint_cell(cell.row, cell.col, "BLUE")
                elif self.selected_algo == "BFS":
                    self.openSet.append(cell)
                    self.grid[cell.row][cell.col] = self.FRONTIER
                    self.paint_cell(cell.row, cell.col, "BLUE")
                elif self.selected_algo in ["Greedy"]:
                    dxg = current.col - cell.col  # ... calculate the value f(Sj) ...
                    dyg = current.row - cell.row
                    dxh = self.targetPos.col - cell.col
                    dyh = self.targetPos.row - cell.row
                    if self.diagonal.get():  # with diagonal movements, calculate the Euclidean distance
                        if self.selected_algo == "Greedy":  # especially for the Greedy ...
                            cell.g = 0
                        else:
                            cell.g = current.g + math.sqrt(dxg * dxg + dyg * dyg)
                        cell.h = math.sqrt(dxh * dxh + dyh * dyh)
                    else:  # without diagonal movements, calculate the Manhattan distance
                        if self.selected_algo == "Greedy":  # especially for the Greedy ...
                            cell.g = 0
                        else:
                            cell.g = current.g + abs(dxg) + abs(dyg)
                        cell.h = abs(dxh) + abs(dyh)
                    cell.f = cell.g + cell.h  # ... If Sj is neither in the OPEN SET nor in the CLOSED SET states ...
                    if cell not in self.openSet and cell not in self.closedSet:  # ... then add Sj in the OPEN SET  ... evaluated as f(Sj)
                        self.openSet.append(cell)  # Update the color of the cell
                        self.grid[cell.row][cell.col] = self.FRONTIER  # paint the cell
                        self.paint_cell(cell.row, cell.col, "BLUE")
                    else:
                        if cell in self.openSet:
                            open_index = self.openSet.index(
                                cell)
                            if self.openSet[open_index].f <= cell.f:
                                pass
                            else:
                                self.openSet.pop(open_index)
                                self.openSet.append(cell)
                                self.grid[cell.row][cell.col] = self.FRONTIER
                                self.paint_cell(cell.row, cell.col, "BLUE")
                        elif cell in self.closedSet:
                            closed_index = self.closedSet.index(
                                cell)
                            if self.closedSet[closed_index].f <= cell.f:
                                pass
                            else:
                                self.closedSet.pop(closed_index)
                                self.openSet.append(cell)
                                self.grid[cell.row][cell.col] = self.FRONTIER
                                self.paint_cell(cell.row, cell.col, "BLUE")

    def create_successors(self, current, make_connected):
        """
        Creates the successors of a state/cell
        :param current:        the cell for which we ask successors
        :param make_connected: flag that indicates that we are interested only on the coordinates
                               of cells and not on the label 'dist'
        :return:               the successors of the cell as a list
        """
        r = current.row
        c = current.col
        temp = []
        if r > 0 and self.grid[r - 1][c] != self.OBST and \
                (self.selected_algo in ["Greedy"] or
                 (self.selected_algo in ["DFS", "BFS"]
                  and not self.Cell(r - 1, c) in self.openSet and not self.Cell(r - 1, c) in self.closedSet)):
            cell = self.Cell(r - 1, c)
            if self.selected_algo == "not best":
                if make_connected:
                    temp.append(cell)
                elif cell in self.graph:
                    graph_index = self.graph.index(cell)
                    temp.append(self.graph[graph_index])
            else:
                cell.prev = current
                temp.append(cell)

        if self.diagonal.get():
            if r > 0 and c < self.columns - 1 and self.grid[r - 1][c + 1] != self.OBST and \
                    (self.grid[r - 1][c] != self.OBST or self.grid[r][c + 1] != self.OBST) and \
                    (self.selected_algo in ["Greedy"] or
                     (self.selected_algo in ["BFS"]
                      and not self.Cell(r - 1, c + 1) in self.openSet and not self.Cell(r - 1,
                                                                                        c + 1) in self.closedSet)):
                cell = self.Cell(r - 1, c + 1)
                if self.selected_algo == "not best":
                    if make_connected:
                        temp.append(cell)
                    elif cell in self.graph:
                        graph_index = self.graph.index(cell)
                        temp.append(self.graph[graph_index])
                else:
                    cell.prev = current
                    temp.append(cell)
        if c < self.columns - 1 and self.grid[r][c + 1] != self.OBST and \
                (self.selected_algo in ["Greedy"] or
                 (self.selected_algo in ["DFS", "BFS"]
                  and not self.Cell(r, c + 1) in self.openSet and not self.Cell(r, c + 1) in self.closedSet)):
            cell = self.Cell(r, c + 1)
            if self.selected_algo == "not best":
                if make_connected:
                    temp.append(cell)
                elif cell in self.graph:
                    graph_index = self.graph.index(cell)
                    temp.append(self.graph[graph_index])
            else:
                cell.prev = current
                temp.append(cell)

        if self.diagonal.get():
            if r < self.rows - 1 and c < self.columns - 1 and self.grid[r + 1][c + 1] != self.OBST and \
                    (self.grid[r + 1][c] != self.OBST or self.grid[r][c + 1] != self.OBST) and \
                    (self.selected_algo in ["Greedy"] or
                     (self.selected_algo in ["DFS", "BFS"]
                      and not self.Cell(r + 1, c + 1) in self.openSet and not self.Cell(r + 1,
                                                                                        c + 1) in self.closedSet)):
                cell = self.Cell(r + 1, c + 1)
                if self.selected_algo == "not best":
                    if make_connected:
                        temp.append(cell)
                    elif cell in self.graph:
                        graph_index = self.graph.index(cell)
                        temp.append(self.graph[graph_index])
                    cell.prev = current
                    temp.append(cell)

        if r < self.rows - 1 and self.grid[r + 1][c] != self.OBST and \
                (self.selected_algo in ["Greedy"] or
                 (self.selected_algo in ["DFS", "BFS"]
                  and not self.Cell(r + 1, c) in self.openSet and not self.Cell(r + 1, c) in self.closedSet)):
            cell = self.Cell(r + 1, c)
            if self.selected_algo == "not best":
                if make_connected:
                    temp.append(cell)
                elif cell in self.graph:
                    graph_index = self.graph.index(cell)
                    temp.append(self.graph[graph_index])
            else:
                cell.prev = current
                temp.append(cell)

        if self.diagonal.get():
            if r < self.rows - 1 and c > 0 and self.grid[r + 1][c - 1] != self.OBST and \
                    (self.grid[r + 1][c] != self.OBST or self.grid[r][c - 1] != self.OBST) and \
                    (self.selected_algo in ["Greedy"] or
                     (self.selected_algo in ["BFS"]
                      and not self.Cell(r + 1, c - 1) in self.openSet and not self.Cell(r + 1,
                                                                                        c - 1) in self.closedSet)):
                cell = self.Cell(r + 1, c - 1)
                if self.selected_algo == "not best":
                    if make_connected:
                        temp.append(cell)
                    elif cell in self.graph:
                        graph_index = self.graph.index(cell)
                        temp.append(self.graph[graph_index])
                else:  # ... update the pointer of the down-left-side cell so it points the current one ...
                    cell.prev = current  # ... and add the down-left-side cell to the successors of the current one.
                    temp.append(cell)

        # If not at the leftmost limit of the grid and the left-side cell is not an obstacle
        # and (only in the case are not running the A* or Greedy) not already belongs neither to the OPEN SET nor to the CLOSED SET ...
        if c > 0 and self.grid[r][c - 1] != self.OBST and \
                (self.selected_algo in ["A*", "Greedy", "not best"] or
                 (self.selected_algo in ["DFS", "BFS"]
                  and not self.Cell(r, c - 1) in self.openSet and not self.Cell(r, c - 1) in self.closedSet)):
            cell = self.Cell(r, c - 1)
            if self.selected_algo == "not best":
                if make_connected:
                    temp.append(cell)
                elif cell in self.graph:
                    graph_index = self.graph.index(cell)
                    temp.append(self.graph[graph_index])
            else:
                cell.prev = current
                temp.append(cell)

        if self.diagonal.get():
            if r > 0 and c > 0 and self.grid[r - 1][c - 1] != self.OBST and \
                    (self.grid[r - 1][c] != self.OBST or self.grid[r][c - 1] != self.OBST) and \
                    (self.selected_algo in ["Greedy"] or
                     (self.selected_algo in ["DFS", "BFS"]
                      and not self.Cell(r - 1, c - 1) in self.openSet and not self.Cell(r - 1,
                                                                                        c - 1) in self.closedSet)):
                cell = self.Cell(r - 1, c - 1)
                if self.selected_algo == "not best":
                    if make_connected:
                        temp.append(cell)
                    elif cell in self.graph:
                        graph_index = self.graph.index(cell)
                        temp.append(self.graph[graph_index])
                else:
                    cell.prev = current
                    temp.append(cell)
        if self.selected_algo == "DFS":
            return reversed(temp)
        else:
            return temp

    def dist_between(self, u, v):
        """
        Returns the distance between two cells
        :param u: the first cell
        :param v: the other cell
        :return:  the distance between the cells u and v
        """
        dx = u.col - v.col
        dy = u.row - v.row
        if self.diagonal.get():  # with diagonal movements calculate the Euclidean distance
            return math.sqrt(dx * dx + dy * dy)
        else:  # without diagonal movements calculate the Manhattan distance
            return abs(dx) + abs(dy)  # .....................HEURISTIC MANHATTEN DISTANCE.........................

    def plot_route(self):
        """
        Calculates the path from the target to the initial position of the robot, counts the corresponding steps and measures the distance traveled.
        """
        self.repaint()
        self.searching = False
        steps = 0
        distance = 0.0
        index = self.closedSet.index(self.targetPos)
        cur = self.closedSet[index]
        self.grid[cur.row][cur.col] = self.TARGET
        self.paint_cell(cur.row, cur.col, "GREEN")
        while cur != self.robotStart:
            steps += 1
            if self.diagonal.get():
                dx = cur.col - cur.prev.col
                dy = cur.row - cur.prev.row
                distance += math.sqrt(dx * dx + dy * dy)
            else:
                distance += 1
            cur = cur.prev
            self.grid[cur.row][cur.col] = self.ROUTE
            self.paint_cell(cur.row, cur.col, "YELLOW")
        self.grid[self.robotStart.row][self.robotStart.col] = self.ROBOT
        self.paint_cell(self.robotStart.row, self.robotStart.col, "RED")
        if self.drawArrows.get():
            self.draw_arrows()
        msg = "Nodes expanded: {0}, Steps: {1}, Distance: {2:.3f}".format(self.expanded, steps, distance)
        self.message.configure(text=msg)

    def find_connected_component(self, v):
        """
        Appends to the list containing the nodes of the graph only
        the cells belonging to the same connected component with node v.
        :param v: the starting node
        """
        stack = [v]
        self.graph.append(v)
        while stack:
            v = stack.pop()
            successors = self.create_successors(v, True)
            for c in successors:
                if c not in self.graph:
                    stack.append(c)
                    self.graph.append(c)

    def initialize_dijkstra(self):
        pass

    def draw_arrows(self):
        """Draws the arrows to predecessors"""
        # We draw black arrows from each open or closed state to its predecessor.
        for r in range(self.rows):
            for c in range(self.columns):
                tail = head = cell = self.Cell(r, c)
                # If the current cell is an open state, or is a closed state but not the initial position of the robot
                if self.grid[r][c] in [self.FRONTIER, self.CLOSED] and not cell == self.robotStart:
                    # The tail of the arrow is the current cell, while the arrowhead is the predecessor cell.
                    if self.grid[r][c] == self.FRONTIER:
                        if self.selected_algo == "not best":
                            tail = self.graph[self.graph.index(cell)]
                            head = tail.prev
                        else:
                            tail = self.openSet[self.openSet.index(cell)]
                            head = tail.prev
                    elif self.grid[r][c] == self.CLOSED:
                        tail = self.closedSet[self.closedSet.index(cell)]
                        head = tail.prev
                    self.draw_arrow(tail, head, self.arrow_size, "BLACK", 2 if self.square_size >= 25 else 1)
        if self.found:
            cur = self.closedSet[self.closedSet.index(self.targetPos)]
            while cur != self.robotStart:
                head = cur
                cur = cur.prev
                tail = cur
                self.draw_arrow(tail, head, self.arrow_size, "RED", 2 if self.square_size >= 25 else 1)

    def draw_arrow(self, tail, head, a, color, width):
        """Draws an arrow from center of tail cell to center of head cell"""
        # The coordinates of the center of the tail cell
        x1 = 1 + tail.col * self.square_size + self.square_size / 2
        y1 = 1 + tail.row * self.square_size + self.square_size / 2
        # The coordinates of the center of the head cell
        x2 = 1 + head.col * self.square_size + self.square_size / 2
        y2 = 1 + head.row * self.square_size + self.square_size / 2

        sin20 = math.sin(20 * math.pi / 180)
        cos20 = math.cos(20 * math.pi / 180)
        sin25 = math.sin(25 * math.pi / 180)
        cos25 = math.cos(25 * math.pi / 180)
        u3 = v3 = u4 = v4 = 0

        if x1 == x2 and y1 > y2:  # up
            u3 = x2 - a * sin20
            v3 = y2 + a * cos20
            u4 = x2 + a * sin20
            v4 = v3
        elif x1 < x2 and y1 > y2:  # up-right
            u3 = x2 - a * cos25
            v3 = y2 + a * sin25
            u4 = x2 - a * sin25
            v4 = y2 + a * cos25
        elif x1 < x2 and y1 == y2:  # right
            u3 = x2 - a * cos20
            v3 = y2 - a * sin20
            u4 = u3
            v4 = y2 + a * sin20
        elif x1 < x2 and y1 < y2:  # righr-down
            u3 = x2 - a * cos25
            v3 = y2 - a * sin25
            u4 = x2 - a * sin25
            v4 = y2 - a * cos25
        elif x1 == x2 and y1 < y2:  # down
            u3 = x2 - a * sin20
            v3 = y2 - a * cos20
            u4 = x2 + a * sin20
            v4 = v3
        elif x1 > x2 and y1 < y2:  # left-down
            u3 = x2 + a * sin25
            v3 = y2 - a * cos25
            u4 = x2 + a * cos25
            v4 = y2 - a * sin25
        elif x1 > x2 and y1 == y2:  # left
            u3 = x2 + a * cos20
            v3 = y2 - a * sin20
            u4 = u3
            v4 = y2 + a * sin20
        elif x1 > x2 and y1 > y2:  # left-up
            u3 = x2 + a * sin25
            v3 = y2 + a * cos25
            u4 = x2 + a * cos25
            v4 = y2 + a * sin25

        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)
        self.canvas.create_line(x2, y2, u3, v3, fill=color, width=width)
        self.canvas.create_line(x2, y2, u4, v4, fill=color, width=width)

    @staticmethod
    def source_code_callback(self):
        pass
        # webbrowser.open_new(r"https://github.com/VedantKhairnar")

    @staticmethod
    def video_callback(self):
        pass


def center(window):
    window.update_idletasks()
    w = window.winfo_screenwidth()
    h = window.winfo_screenheight()
    size = tuple(int(_) for _ in window.geometry().split('+')[0].split('x'))
    x = w / 2 - size[0] / 2
    y = h / 2 - size[1] / 2
    window.geometry("%dx%d+%d+%d" % (size + (x, y)))


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        os._exit(0)


def demo(screen):
    effects = [
        Cycle(
            screen,
            FigletText("The Maze Runner", font='big'),
            int(screen.height / 2 - 8)),
        Cycle(
            screen,
            FigletText("Press 'q' to Start", font='chunky'),
            int(screen.height * (3 / 4) - 8)),
        Stars(screen, 200)
    ]
    screen.play([Scene(effects, 500)])


def load_animation():
    load_str = "starting The Maze Runner..."  # String to be displayed when the application is loading
    ls_len = len(load_str)
    animation = "|/-\\"  # String for creating the rotating line
    anicount = 0
    counttime = 0  # used to keep the track of the duration of animation
    i = 0  # pointer for travelling the loading string
    while counttime != 100:
        time.sleep(0.05)  # used to change the animation speed .. smaller the value, faster will be the animation
        load_str_list = list(load_str)  # converting the string to list as string is immutable
        x = ord(load_str_list[i])  # x->obtaining the ASCII code
        y = 0  # y->for storing altered ASCII code
        if x != 32 and x != 46:  # if the character is "." or " ", keep it unaltered switch uppercase to lowercase and vice-versa
            if x > 90:
                y = x - 32
            else:
                y = x + 32
            load_str_list[i] = chr(y)
        res = ''
        for j in range(ls_len):
            res = res + load_str_list[j]
        sys.stdout.write("\r" + res + animation[anicount])  # displaying the resultant string
        sys.stdout.flush()
        load_str = res  # Assigning loading string to the resultant string
        anicount = (anicount + 1) % 4
        i = (i + 1) % ls_len
        counttime = counttime + 1

    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


if __name__ == '__main__':
    app = Tk()
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.title("The Maze Runner")
    app.geometry("693x545")
    app.resizable(False, False)

    # Animation Effects
    # load_animation()  # uncomment this line for animation 1
    # Screen.wrapper(demo)  # uncomment this line for animation 2

    # Let the party begin
    Maze51(app)
    app.mainloop()
