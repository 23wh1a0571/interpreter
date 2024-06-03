import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import pygame
import re

pygame.mixer.init()

# Initialize pygame mixer
pygame.mixer.init()

# Function to play the opening sound
def play_opening_sound():
    opening_sound = pygame.mixer.Sound("click.wav")  # Replace "click.wav" with your desired opening sound file
    opening_sound.play()

# Function to play the sound for running the program
def play_run_sound():
    run_sound = pygame.mixer.Sound("run.wav")  # Replace "run.wav" with your desired run sound file
    run_sound.play()

# Function to play the sound for going back to the home page
def play_back_home_sound():
    back_home_sound = pygame.mixer.Sound("click.wav")  # Replace "click.wav" with your desired back home sound file
    back_home_sound.play()

# Function to play the sound for the home page
def play_home_page_sound():
    home_page_sound = pygame.mixer.Sound("welcome.wav")  # Replace "welcome.wav" with your desired home page sound file
    home_page_sound.play()

# Function to play the keyboard click sound
def play_keyboard_click_sound():
    keyboard_click_sound = pygame.mixer.Sound("keyboard.wav")  # Replace "keyboard_click.wav" with your desired keyboard click sound file
    keyboard_click_sound.play()


# Dictionary to store variable values
variables = {}
# Dictionary to store function definitions
functions = {}

# Function to evaluate arithmetic expressions
def evaluate_expression(expression):
    # Replace variables with their values
    expression = re.sub(r'\b([A-Z])\b', lambda match: str(variables.get(match.group(1), 'invalid')), expression)
    
    try:
        # Evaluate the arithmetic expression
        result = eval(expression)
        return result
    except Exception:
        return None

# Function to interpret a single statement
def interpret_statement(statement):
    global current_statement_index
    
    statement = statement.strip()
    output_messages = []  # Store output messages for later concatenation
    
    if '=' in statement and not statement.startswith('def '):
        var, expr = map(str.strip, statement.split('='))
        
        if not var.isalpha() or len(var) != 1:
            output_messages.append(f"Invalid variable name: {var}")
            return False

        value = evaluate_expression(expr)
        
        if value is None:
            output_messages.append(f"Invalid expression: {expr}")
            return False

        variables[var] = value

    elif statement.startswith("def ") and "(" in statement and ")" in statement:
        # Extract function name and parameters
        func_def, block = statement[4:].split(":", 1)
        func_name, params = func_def.split("(")
        func_name = func_name.strip()
        params = params.strip()[:-1].split(",")

        if not func_name.isalpha():
            output_messages.append(f"Invalid function name: {func_name}")
            return False

        # Store the function definition
        functions[func_name] = (params, block.strip())

    elif statement.startswith("if ") and ":" in statement:
        # Extract condition and block
        condition, block = statement[3:].split(":", 1)
        condition = condition.strip()
        block = block.strip()

        # Evaluate condition
        result = evaluate_expression(condition)

        if result is None:
            output_messages.append(f"Invalid condition: {condition}")
            return False

        if result:
            # Interpret block if condition is True
            interpret_block(block)
        else:
            # Check for corresponding else block
            next_statement = statements[current_statement_index + 1].strip()
            if next_statement.startswith("else:"):
                else_block = next_statement[5:].strip()
                interpret_block(else_block)
                increment_statement_index()

    elif statement.startswith("for ") and ":" in statement:
        # Extract loop details and block
        loop_details, block = statement[4:].split(":", 1)
        loop_var, loop_range = loop_details.split("in")
        loop_var = loop_var.strip()
        loop_range = loop_range.strip()

        if not loop_var.isalpha() or len(loop_var) != 1:
            output_messages.append(f"Invalid loop variable name: {loop_var}")
            return False

        try:
            start, end = map(int, loop_range.split(".."))
        except Exception:
            output_messages.append(f"Invalid range: {loop_range}")
            return False

        for i in range(start, end + 1):
            variables[loop_var] = i
            interpret_block(block)

    elif statement.startswith("while ") and ":" in statement:
        # Extract condition and block
        condition, block = statement[6:].split(":", 1)
        condition = condition.strip()
        block = block.strip()

        while evaluate_expression(condition):
            interpret_block(block)

    elif statement.startswith("do ") and "while" in statement:
        # Extract block and condition
        block, condition = statement[3:].split("while", 1)
        block = block.strip()
        condition = condition.strip()

        while True:
            interpret_block(block)
            if not evaluate_expression(condition):
                break

    elif '(' in statement and ')' in statement:
        # This should be a function call
        interpret_function_call(statement)

    elif statement == "stop":
        # Print variables if user inputs "stop"
        print_assigned_variables()

    else:
        output_messages.append(f"Invalid statement: {statement}")
        return False
    
    # Concatenate output messages and insert into output_text
    if output_messages:
        output_text.insert(tk.END, '\n'.join(output_messages) + '\n')
    
    return True

# Function to interpret a block of statements
def interpret_block(block):
    global statements, current_statement_index
    # Split the block into individual statements
    block_statements = block.split("\n")
    original_statements = statements
    original_statement_index = current_statement_index

    statements = block_statements
    current_statement_index = 0

    while current_statement_index < len(statements):
        statement = statements[current_statement_index].strip()
        if statement:
            interpret_statement(statement)
        current_statement_index += 1

    statements = original_statements
    current_statement_index = original_statement_index

# Function to interpret a function call
def interpret_function_call(statement):
    # Extract function name and arguments
    func_name, args = statement.split("(", 1)
    func_name = func_name.strip()
    args = args.strip()[:-1].split(",")

    if func_name not in functions:
        output_text.insert(tk.END, f"Undefined function: {func_name}\n")
        return False

    # Get function definition
    params, block = functions[func_name]
    
    if len(params) != len(args):
        output_text.insert(tk.END, f"Argument count mismatch for function: {func_name}\n")
        return False

    # Backup current variable values
    backup_variables = variables.copy()

    # Assign argument values to parameters
    for param, arg in zip(params, args):
        variables[param.strip()] = evaluate_expression(arg.strip())

    # Execute function block
    interpret_block(block)

    # Restore variable values
    variables.update(backup_variables)

    return True

# Function to print assigned variables
def print_assigned_variables():
    output_text.insert(tk.END, "\nAssigned Variables:\n")
    for var, value in sorted(variables.items()):
        output_text.insert(tk.END, f"{var} = {value}\n")

# Function to run user program
def run_user_program():
    global statements, current_statement_index
    input_text = text_entry.get("1.0", tk.END).strip()
    statements = input_text.split("\n")
    current_statement_index = 0
    while current_statement_index < len(statements):
        interpret_statement(statements[current_statement_index].strip())
        current_statement_index += 1
    print_assigned_variables()

# Event handler for clicking "Run" button
def on_run_button_click():
    play_run_sound()  # Play sound for clicking "Run" button
    run_user_program()

# Function to animate the circles on the home page
def animate_circles():
    colors = ['red', 'yellow', 'green']
    current_color_index = 0

    def update_circle_color():
        nonlocal current_color_index
        canvas.itemconfig(red_circle, fill=colors[current_color_index % 3])
        canvas.itemconfig(yellow_circle, fill=colors[(current_color_index + 1) % 3])
        canvas.itemconfig(green_circle, fill=colors[(current_color_index + 2) % 3])
        current_color_index += 1
        root.after(1000, update_circle_color)

    update_circle_color()

# Function to show interpreter page
def show_interpreter_page():
    home_frame.pack_forget()
    instruction_frame.pack_forget()  # Hide instruction frame
    interpreter_frame.pack(fill=tk.BOTH, expand=True)
    play_opening_sound()  # Play opening sound when showing the interpreter page

# Function to show home page
def show_home_page():
    interpreter_frame.pack_forget()
    instruction_frame.pack_forget()  # Hide instruction frame
    home_frame.pack(fill=tk.BOTH, expand=True)
    play_back_home_sound()  # Play sound when showing the home page

# Function to show instruction page
def show_instruction_page():
    home_frame.pack_forget()
    interpreter_frame.pack_forget()  # Hide interpreter frame
    instruction_frame.pack(fill=tk.BOTH, expand=True)
    play_opening_sound()  # Play opening sound when showing the instruction page

def create_keyboard(parent):
    keyboard_frame = tk.Frame(parent, bg="black")
    keyboard_frame.pack()

    buttons = [
        '`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace',
        'Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\',
        'Caps', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", 'Enter',
        'Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/','?', 'Shift',
        'Ctrl','+', '*', '(', ')', '{', '}', '>', '<', '%', ':', ';', '_','!','&','#','Ctrl',
         '<','>','^','v','Fn', 'Alt', 'Space', 'Alt', 'Fn', 
    ]

    row, column = 0, 0
    for button in buttons:
        if button == 'Backspace':
            tk.Button(keyboard_frame, text=button, width=7, command=lambda: delete_last_character()).grid(row=row, column=column, columnspan=2)
            column += 1  # Skip an extra column
        elif button == 'Clear':
            tk.Button(keyboard_frame, text=button, width=7, command=lambda: clear_text_entry()).grid(row=row, column=column, columnspan=2)
            column += 1  # Skip an extra column
        elif button == 'Shift':
            tk.Button(keyboard_frame, text=button, width=7, command=lambda: toggle_shift()).grid(row=row, column=column, columnspan=2)
            column += 1  # Skip an extra column
        elif button == 'Caps':
            tk.Button(keyboard_frame, text=button, width=7, command=lambda: toggle_capslock()).grid(row=row, column=column, columnspan=2)
            column += 1  # Skip an extra column
        elif button == 'Tab':
            tk.Button(keyboard_frame, text=button, width=7, command=lambda: insert_character('\t')).grid(row=row, column=column, columnspan=2)
            column += 1  # Skip an extra column
        elif button == 'Space':
            tk.Button(keyboard_frame, text=button, width=7, command=lambda: insert_character(' ')).grid(row=row, column=column, columnspan=2)
            column += 1  # Skip an extra column
        elif button == 'Enter':
            tk.Button(keyboard_frame, text=button, width=7, command=lambda: insert_character('\n')).grid(row=row, column=column, columnspan=2)
            column += 1  # Skip an extra column
        elif button == '<':
            tk.Button(keyboard_frame, text=button, width=3, command=lambda: move_cursor('left')).grid(row=row, column=column)
        elif button == '>':
            tk.Button(keyboard_frame, text=button, width=3, command=lambda: move_cursor('right')).grid(row=row, column=column)
        elif button == '^':
            tk.Button(keyboard_frame, text=button, width=3, command=lambda: move_cursor('up')).grid(row=row, column=column)
        elif button == 'v':
            tk.Button(keyboard_frame, text=button, width=3, command=lambda: move_cursor('down')).grid(row=row, column=column)
        else:
            tk.Button(keyboard_frame, text=button, width=5, command=lambda b=button: insert_character(b)).grid(row=row, column=column)
        column += 1
        if column == 15:
            column = 0
            row += 1

# Function to delete the last character from the text entry box
def delete_last_character():
    current_index = text_entry.index(tk.INSERT)
    if current_index != "1.0":  # Ensure we don't go before the start of the text widget
        text_entry.delete(f"{current_index} - 1 char", current_index)
        play_keyboard_click_sound()  # Play keyboard click sound when deleting a character

# Function to clear the text entry box
def clear_text_entry():
    text_entry.delete("1.0", tk.END)
    play_keyboard_click_sound()  # Play keyboard click sound when clearing the text entry

# Function to move the cursor
def move_cursor(direction):
    index = text_entry.index(tk.INSERT)
    row, col = map(int, index.split('.'))
    if direction == 'left':
        col = max(col - 1, 0)
    elif direction == 'right':
        col += 1
    elif direction == 'up':
        row = max(row - 1, 1)
    elif direction == 'down':
        row += 1
    text_entry.mark_set(tk.INSERT, f"{row}.{col}")
    play_keyboard_click_sound()  # Play keyboard click sound when moving the cursor

# Function to toggle shift mode
shift_mode = False
def toggle_shift():
    global shift_mode
    shift_mode = not shift_mode
    play_keyboard_click_sound()  # Play keyboard click sound when toggling Shift

# Function to toggle capslock mode
capslock_mode = False
def toggle_capslock():
    global capslock_mode
    capslock_mode = not capslock_mode
    play_keyboard_click_sound()  # Play keyboard click sound when toggling Caps Lock
# Create the main window
root = tk.Tk()
root.title("Team 2 Interpreter")

# Load the background image
background_image = Image.open("wise5.png")  # Replace "background.jpg" with your desired background image file
background_image = background_image.resize((1600, 1000))
background_photo = ImageTk.PhotoImage(background_image)

# Home Page
home_frame = tk.Frame(root, bg="black")

# Create a label to display the background image for home page
home_background_label = tk.Label(home_frame, image=background_photo)
home_background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Add a terminal-like frame using Canvas
canvas = tk.Canvas(home_frame, width=600, height=400, bg="black", highlightthickness=0)
canvas.pack()

# Draw the code-style border
canvas.create_rectangle(10, 10, 590, 390, outline="lime", width=2)

# Draw top bar to mimic a terminal window
canvas.create_rectangle(10, 10, 590, 40, fill="grey20", outline="grey20")
red_circle = canvas.create_oval(20, 20, 30, 30, fill="")
yellow_circle = canvas.create_oval(40, 20, 50, 30, fill="")
green_circle = canvas.create_oval(60, 20, 70, 30, fill="")

# Add some pseudo-code text
canvas.create_text(300, 100, text="def welcome():", fill="lime", font=("Courier", 16), anchor="center")
canvas.create_text(300, 140, text='    print("Welcome to Team 2 Interpreter!")', fill="lime", font=("Courier", 16), anchor="center")

# Add some ASCII art or "hacker" text
canvas.create_text(300, 220, text=">>> SYSTEM READY", fill="lime", font=("Courier", 14), anchor="center")

# Place the inner content
inner_frame = tk.Frame(canvas, bg="black")
inner_frame.place(relx=0.5, rely=0.75, anchor=tk.CENTER)

instruction_button = tk.Button(inner_frame, text="Start", command=show_instruction_page, font=("Courier", 14), bg="black", fg="lime", bd=0)
instruction_button.pack(pady=10)

home_frame.pack(fill=tk.BOTH, expand=True)

# Play sound when showing the home page
play_opening_sound()
play_home_page_sound()

# Start circle animation
animate_circles()

# Instruction Page
instruction_frame = tk.Frame(root, bg="black")

# Create a label to display the background image for instruction page
instruction_background_label = tk.Label(instruction_frame, image=background_photo)
instruction_background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Instruction text
instruction_text = """
Welcome to Team 2 Interpreter!

This interpreter allows you to write and execute Python-like statements. Follow these steps to get started:

1.Input Box: Enter your Python code in the input box provided. You can define variables, functions, use if-else conditions, loops (for, while, do-while), and make function calls.
2.Run Button: Click the "Run" button to execute the code entered in the input box. The output will be displayed in the output box below.
3.Virtual Keyboard: You can use the virtual keyboard provided to input text into the input box. Click on the buttons to enter characters, navigate, and delete text.
4.Back to Home Button: Click the "Back to Home" button at any time to return to the home page.

Writing and Assigning Values Syntax:
1.Variable Assignment:
    # To assign a value to a variable, use the syntax: variable_name = value.
    # Variable names should consist of a single letter (e.g., x, y, z).
    # Always use capital letters to assign values.
    example: A = 1
             B = 3
2.Arithmetic Expressions:
    #  You can use arithmetic expressions when assigning values.
    # Always use capital letters to this.
    example: C = A + B
3.Supported Operations: 
    #This supports basic arithmetic operations such as:
        addition (+), subtraction (-), multiplication (*), division (/), and modulus (%).
4.Conditional Statements:
    # Use 'if' or 'if else' statements to execute code conditionally.
    example: if A > C:
                D = B
             else:
                D = A
5.Loops:
    # Use for, while, or do-while loops to iterate over sequences or execute code repeatedly.
    # Use only one at a time.
    example: for I in 1..2:
                E = A + 1
6.Function Calls:
    # Call a function by typing its name followed by parentheses containing arguments, if any.
      exapmle: def add(A,B):
                F = A
                add(A,B)
                  or
               def add(X,Y):
                F = A
                add(9,4)

Enjoy coading!!
"""
# Instruction label with scrollbar
instruction_scrollbar = tk.Scrollbar(instruction_frame, orient=tk.VERTICAL)
instruction_text_box = tk.Text(instruction_frame, font=("Courier", 12), bg="black", fg="lime", yscrollcommand=instruction_scrollbar.set)
instruction_text_box.insert(tk.END, instruction_text)
instruction_text_box.config(state=tk.DISABLED)  # Disable editing of the text box
instruction_scrollbar.config(command=instruction_text_box.yview)

instruction_text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
instruction_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)



# Start button
start_button = tk.Button(instruction_frame, text="Next", command=show_interpreter_page, font=("Courier", 14), bg="black", fg="lime", bd=0)
start_button.pack(pady=10)

# Home button
home_button = tk.Button(instruction_frame, text="Back to Home", command=show_home_page, font=("Courier", 12), bg="black", fg="lime", bd=0)
home_button.pack(pady=10)

# Interpreter Page
interpreter_frame = tk.Frame(root, bg="black")

# Create a label to display the background image for interpreter page
interpreter_background_label = tk.Label(interpreter_frame, image=background_photo)
interpreter_background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Input frame with border
input_outer_frame = tk.Frame(interpreter_frame, bg="black", bd=10)
input_middle_frame = tk.Frame(input_outer_frame, bg="lime", bd=10)
input_inner_frame = tk.Frame(input_middle_frame, bg="black", bd=10)

label_input = tk.Label(input_inner_frame, text="Enter statements:", font=("Courier", 12), bg="black", fg="lime")
label_input.pack(pady=5)

text_entry = scrolledtext.ScrolledText(input_inner_frame, width=50, height=5, font=("Courier", 12), bg="black", fg="lime", insertbackground="lime")
text_entry.pack(pady=5)

input_inner_frame.pack(padx=10, pady=10)
input_middle_frame.pack(padx=10, pady=10)
input_outer_frame.pack(padx=10, pady=10)

# Output frame with border
output_outer_frame = tk.Frame(interpreter_frame, bg="black", bd=10)
output_middle_frame = tk.Frame(output_outer_frame, bg="lime", bd=10)
output_inner_frame = tk.Frame(output_middle_frame, bg="black", bd=10)

label_output = tk.Label(output_inner_frame, text="Output:", font=("Courier", 12), bg="black", fg="lime")
label_output.pack(pady=5)

output_text = scrolledtext.ScrolledText(output_inner_frame, width=50, height=5, state='normal', font=("Courier", 12), bg="black", fg="lime", insertbackground="lime")
output_text.pack(pady=5)

output_inner_frame.pack(padx=10, pady=10)
output_middle_frame.pack(padx=10, pady=10)
output_outer_frame.pack(padx=10, pady=10)

# Buttons frame
frame_buttons = tk.Frame(interpreter_frame, bg="black")
frame_buttons.pack(padx=10, pady=5)

run_button = tk.Button(frame_buttons, text="Run", command=on_run_button_click, font=("Courier", 10), bg="black", fg="lime", bd=0)
run_button.pack(side=tk.LEFT, padx=5)

back_button = tk.Button(frame_buttons, text="Back to Home", command=show_home_page, font=("Courier", 10), bg="black", fg="lime", bd=0)
back_button.pack(side=tk.LEFT, padx=5)

# Create the virtual keyboard
keyboard_frame = tk.Frame(interpreter_frame, bg="black")
keyboard_frame.pack(padx=10, pady=10)

create_keyboard(keyboard_frame)

# Hide instruction frame initially
instruction_frame.pack_forget()

# Hide interpreter frame initially
interpreter_frame.pack_forget()

# Display the home page initially
home_frame.pack(fill=tk.BOTH, expand=True)

# Run the tkinter event loop
root.mainloop()


