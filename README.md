# Turing Machine Visualizer
Turing Machine Visualizer is a python program intended for the visual representation and simulation of Turing Machines, allowing for an interactive interface for building machines.
## Controlling the machine builder
To create a state, drag a circle from the corner of the screen. A prompt will appear asking to name the state.
To designate a start state, double click on a state. The start state will be indicated with a green border. To designate an end state, right click on the state (specific to Windows).
In the create transition mode, click on a state and then another to create a transition between the two.

## Building a machine from text
Transitions are formatted as follows: start_state read write direction end_state

Valid direction characters are > meaning left, and < meaning right

~ signifies a null character or blank

Multiple end states are separated by spaces (ex. endstate1 endstate2 endstate3 ... etc)
