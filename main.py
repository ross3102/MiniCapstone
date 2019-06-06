from tkinter import *
from machine import *


class Builder(Toplevel):
    def __init__(self, runner):
        super(Builder, self).__init__(runner.master)

        self.runner = runner

        self.canvas = Canvas(self, width=1000, height=600)
        self.canvas.grid(row=0, column=0)
        Button(self, text="FINISH BUILDING", command=self.finish).grid(row=1, column=0)

        self.states = []

        self.mouse = False
        self.draggingState = False

        self.bind('<ButtonPress-1>', self.mouse_clicked)
        self.bind('<ButtonRelease-1>', self.mouse_released)
        self.bind("<B1-Motion>", self.mouse_moved)

        self.draw_side_menu()

    def in_circle(self, x, y, cx, cy, r):
        pass

    def mouse_clicked(self, event):
        self.mouse = True
        if self.in_circle(event.x, event.y, 45, 45, 70):
            self.draggingState = True

    def mouse_released(self, event):
        self.mouse = False

    def mouse_moved(self):
        pass

    def draw_side_menu(self):
        self.canvas.create_oval(10, 10, 80, 80)
        self.canvas.create_text(45, 45, text="New State")

    def finish(self):
        pass


class Runner(Frame):
    def __init__(self, master):
        super(Runner, self).__init__(master)

        self.master = master

        self.numBoxes = 9
        self.canvasWidth = 400
        self.canvasHeight = 100

        self.bufferSize = 5
        self.boxSize = (self.canvasWidth - self.bufferSize * 2) / self.numBoxes

        self.going = False
        self.correct = None

        self.inputTape = Tape()
        self.machine = Machine()

        self.current_state = None

        self.inputBox = Text(self, height=1, width=50)
        self.inputBox.grid(row=0, column=0)

        Button(self, text="LOAD INPUT", command=self.load).grid(row=0, column=1)

        self.playButton = Button(self, text="PLAY", command=self.play)
        self.playButton.grid(row=0, column=2)

        Button(self, text="PAUSE", command=self.pause).grid(row=0, column=3)

        Button(self, text="STEP", command=self.step_button_pressed).grid(row=0, column=4)

        self.canvas = Canvas(self, width=400, height=100)
        self.canvas.grid(row=1, column=0, columnspan=4)

        Label(self, text="Start State").grid(row=2, column=0)

        self.start_state_box = Text(self, height=1, width=30)
        self.start_state_box.grid(row=3, column=0)

        Label(self, text="Transitions").grid(row=4, column=0)

        self.transitionBox = Text(self, height=10, width=30)
        self.transitionBox.grid(row=5, column=0)

        Label(self, text="End States").grid(row=6, column=0)

        self.end_state_box = Text(self, height=3, width=30)
        self.end_state_box.grid(row=7, column=0)

        self.loadMachineButton = Button(self, text="LOAD MACHINE", command=self.load_machine)
        self.loadMachineButton.grid(row=8, column=0)

        Button(self, text="LAUNCH MACHINE BUILDER", command=self.launch_builder).grid(row=9, column=0)

        self.erase_tape()
        self.grid()

        self.loop()

    def launch_builder(self):
        self.builder = Builder(self)

    def reset(self):
        self.playButton.config(text="PLAY")
        self.current_state = self.machine.start_state()
        self.going = False
        self.correct = None

    def load_machine(self):
        transitions = [t.split() for t in self.transitionBox.get("1.0", END).split("\n") if len(t) !=  0]

        start_state = self.start_state_box.get("1.0", END).strip()
        end_states = self.end_state_box.get("1.0", END).strip().split(" ")

        self.machine.set_start_end(start_state, end_states)
        for i in range(len(transitions)):
            start, read, write, direction, end = transitions[i]
            self.machine.addTransition(start, read, write, direction, end)

        self.load()
        self.reset()

    def loop(self):
        if self.correct is None:
            if self.going:
                if not self.step():
                    self.correct = False
                    print("NO MATCH")
                    self.playButton.config(text="RESET")
            if self.current_state is not None and self.current_state.name in self.machine.final_state_names:
                self.correct = True
                print("MATCH")
                self.playButton.config(text="RESET")

        self.master.after(1, self.loop)

    def step(self):
        state_info = self.current_state.transition(self.inputTape)
        if not state_info:
            return False
        direction = state_info[0]
        self.current_state = state_info[1]
        if direction == "0":
            self.left()
        elif direction == "1":
            self.right()
        return True

    def erase_tape(self, offset=0):
        self.canvas.delete("all")
        self.canvas.create_polygon(190, 5, 210, 5, 200, 20)
        for i in range(-2, self.numBoxes+2):
            self.canvas.create_rectangle(self.bufferSize + self.boxSize * i + offset, 22, self.bufferSize + self.boxSize * (i + 1) + offset, 22 + self.boxSize)

    def display_tape(self, text, offset=0):
        self.erase_tape(offset)
        for i in range(-2, min(self.numBoxes, len(text))+2):
            self.canvas.create_text(self.bufferSize + self.boxSize * (i+.5) + offset, 22+self.boxSize/2, text=text[i+2])
        self.canvas.update()

    def load(self):
        self.reset()
        self.inputTape.set_input(self.inputBox.get("1.0", END)[:-1])
        self.display_tape(self.inputTape.display_tape(self.numBoxes//2+3))

    def left(self):
        self.display_tape(self.inputTape.display_tape(self.numBoxes // 2 + 3))
        self.move_tape(LEFT)
        self.inputTape.move_left()
        self.display_tape(self.inputTape.display_tape(self.numBoxes//2+3))

    def right(self):
        self.display_tape(self.inputTape.display_tape(self.numBoxes // 2 + 3))
        self.move_tape(RIGHT)
        self.inputTape.move_right()
        self.display_tape(self.inputTape.display_tape(self.numBoxes // 2 + 3))

    def move_tape(self, direction):
        text = self.inputTape.display_tape(self.numBoxes // 2 + 3)
        offset = 0
        if direction == LEFT:
            while offset < self.boxSize:
                offset += 1
                self.display_tape(text, offset)
        else:
            while offset > -self.boxSize:
                offset -= 1
                self.display_tape(text, offset)

    def play(self):
        if self.correct is not None:
            self.load()
        else:
            self.going = True

    def pause(self):
        self.going = False

    def step_button_pressed(self):
        self.pause()
        if self.correct is None and not self.step():
            self.correct = False
            print("NO MATCH")
            return

root = Tk()
root.title("Turing Machine Runner")
app = Runner(root)
root.mainloop()