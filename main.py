import os
import json
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext, ttk
import re
import errno
import time

HISTORY_FILE = "project_history.json"
TEMPLATES_FILE = "templates.json"

def load_templates():
    """
    Load templates from a JSON file for project structure templates.
    """
    if os.path.exists(TEMPLATES_FILE):
        with open(TEMPLATES_FILE, 'r') as f:
            return json.load(f)
    return {}


def create_project_structure(base_path, structure, log_text):
    """
    Create a folder structure from the provided dictionary.
    Log each step in the log window.
    """
    try:
        for key, value in structure.items():
            current_path = os.path.normpath(os.path.join(base_path, key))
            if isinstance(value, dict):
                # It's a directory, create it and then process its children
                if not os.path.exists(current_path):
                    try:
                        os.makedirs(current_path, exist_ok=True)
                        log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Created folder: {current_path}\n")
                    except Exception as e:
                        log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Error creating folder '{current_path}': {str(e)}\n")
                        continue
                create_project_structure(current_path, value, log_text)
            else:
                # It's a file, create it
                if os.path.exists(current_path):
                    response = messagebox.askyesno("File Exists", f"The file '{current_path}' already exists. Do you want to replace it?")
                    if not response:
                        log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Skipped existing file: {current_path}\n")
                        continue
                try:
                    with open(current_path, 'w') as f:
                        pass  # Create empty file
                    log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Created file: {current_path}\n")
                except PermissionError:
                    log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Permission denied while creating file: {current_path}\n")
                except OSError as e:
                    log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] OS error while creating file '{current_path}': {str(e)}\n")
        log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Project structure creation completed.\n")
    except Exception as e:
        log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Failed to create project structure: {str(e)}\n")


def parse_tree_structure_to_dict(tree_structure):
    """
    Parse a tree-like folder structure text to a dictionary.
    """
    structure_dict = {}
    lines = tree_structure.strip().splitlines()
    stack = [(structure_dict, -1)]  # Each item in stack is (current_dict, depth)

    for line in lines:
        # Remove all leading special characters used for tree representation and clean the line
        cleaned_line = line.lstrip('│├└─| \t').strip()

        # Skip empty lines or invalid lines
        if not cleaned_line:
            continue

        # Determine the depth based on leading spaces or tabs (each level is represented by either 4 spaces or a tab)
        leading_whitespace = len(line) - len(cleaned_line)
        if '\t' in line[:leading_whitespace]:
            depth = line[:leading_whitespace].count('\t')
        else:
            depth = leading_whitespace // 4

        # Check if it's a folder or file by checking if it ends with a '/'
        if cleaned_line.endswith('/') or '.' not in cleaned_line:
            # It's a folder
            folder_name = cleaned_line.rstrip('/')
            current_dict, current_depth = stack[-1]

            # Pop stack until we find the correct parent folder
            while current_depth >= depth:
                stack.pop()
                current_dict, current_depth = stack[-1]

            # Add the new folder and push it onto the stack
            if folder_name not in current_dict:
                current_dict[folder_name] = {}

            stack.append((current_dict[folder_name], depth))
        else:
            # It's a file
            file_name = cleaned_line
            current_dict, current_depth = stack[-1]

            # Pop stack until we find the correct parent folder
            while current_depth >= depth:
                stack.pop()
                current_dict, current_depth = stack[-1]

            # Add the file to the current level
            current_dict[file_name] = None

    return structure_dict


def save_history(structure):
    """
    Save the provided project structure to history for future use.
    """
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        else:
            history = []

        history.append(structure)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=4)
    except Exception as e:
        print(f"Failed to save history: {str(e)}")


def load_history():
    """
    Load the saved project history.
    """
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []


def select_directory():
    """
    Open a dialog to select the directory where the project structure will be created.
    """
    folder_selected = filedialog.askdirectory(title="Select Directory for Project Creation")
    if not folder_selected:
        messagebox.showwarning("Warning", "No directory selected. Please select a directory.")
        return None
    return os.path.normpath(folder_selected)


def load_file():
    """
    Load folder structure from a selected text file.
    """
    file_path = filedialog.askopenfilename(title="Select File with Project Structure", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, 'r') as f:
            return f.read()
    return None


def main():
    # Initialize the main GUI window
    root = tk.Tk()
    root.title("Project Structure Creator")
    root.state('zoomed')  # Start in maximized mode

    # Load templates from external JSON file
    templates = load_templates()

    # Create the main frame
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Instructions frame on the left
    instructions_frame = tk.Frame(main_frame, width=300)
    instructions_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    instruction_text = """
    Instructions:
    1. Enter your project structure in the text area (use tabs or 4 spaces for indentation).
    2. Load a project structure from a text file if needed.
    3. Select a pre-defined template from the dropdown menu.
    4. Click 'Convert and Show Structure' to view the parsed structure.
    5. Click 'Create Project Structure' to generate files and folders.
    6. The history of all previously created structures is saved and can be reused.

    Example Input Format:
    ProjectRoot
        main.py
        config.py
        FirstFolder
            file1.txt
            SecondFolder
                file2.txt
    """
    instructions_label = tk.Label(instructions_frame, text=instruction_text, justify=tk.LEFT, anchor='nw')
    instructions_label.pack(fill=tk.Y)

    # Project structure frame on the right
    project_frame = tk.Frame(main_frame)
    project_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Label for instructions
    instruction_label = tk.Label(project_frame, text="Enter your project structure (e.g. tree-like format) or load from a text file:")
    instruction_label.pack(pady=10)

    # Dropdown menu for templates
    def select_template(event):
        template_name = template_dropdown.get()
        if template_name in templates:
            text_area.delete('1.0', tk.END)
            text_area.insert(tk.END, templates[template_name])

    template_label = tk.Label(project_frame, text="Select a Template:")
    template_label.pack(pady=5)
    template_dropdown = ttk.Combobox(project_frame, values=list(templates.keys()))
    template_dropdown.bind("<<ComboboxSelected>>", select_template)
    template_dropdown.pack(pady=5)

    # ScrolledText widget for project structure input
    text_area = scrolledtext.ScrolledText(project_frame, wrap=tk.WORD, width=100, height=20)
    text_area.pack(pady=10)

    # ScrolledText widget for logging
    log_text = scrolledtext.ScrolledText(project_frame, wrap=tk.WORD, width=100, height=10)
    log_text.pack(pady=10)

    # Button to load file
    def load_file_content():
        file_content = load_file()
        if file_content:
            text_area.delete('1.0', tk.END)
            text_area.insert(tk.END, file_content)

    load_file_button = tk.Button(project_frame, text="Load from File", command=load_file_content)
    load_file_button.pack(pady=5)

    # Button to load history
    def load_history_content():
        history = load_history()
        if history:
            # Display a history selection window
            history_window = tk.Toplevel(root)
            history_window.title("Select from History")
            history_window.geometry("600x400")

            history_listbox = tk.Listbox(history_window, width=100, height=20)
            history_listbox.pack(pady=10, padx=10)

            for idx, item in enumerate(history):
                history_listbox.insert(tk.END, f"History {idx + 1}: {list(item.keys())[0]}")

            def select_history():
                selected_idx = history_listbox.curselection()
                if selected_idx:
                    selected_structure = history[selected_idx[0]]
                    text_area.delete('1.0', tk.END)
                    text_area.insert(tk.END, json.dumps(selected_structure, indent=4))
                    history_window.destroy()

            select_button = tk.Button(history_window, text="Select", command=select_history)
            select_button.pack(pady=5)
        else:
            messagebox.showinfo("History", "No history found.")

    load_history_button = tk.Button(project_frame, text="Load from History", command=load_history_content)
    load_history_button.pack(pady=5)

    # Button to convert project structure to dictionary and display
    def convert_and_display_structure():
        tree_structure = text_area.get('1.0', tk.END).strip()
        if not tree_structure:
            messagebox.showerror("Error", "Please enter a project structure or load one.")
            return

        try:
            project_structure_dict = parse_tree_structure_to_dict(tree_structure)
            # Show parsed structure as a pop-up instead of logging multiple times
            parsed_window = tk.Toplevel(root)
            parsed_window.title("Parsed Structure")
            parsed_window.geometry("600x400")
            parsed_text = scrolledtext.ScrolledText(parsed_window, wrap=tk.WORD, width=80, height=20)
            parsed_text.pack(pady=10)
            parsed_text.insert(tk.END, json.dumps(project_structure_dict, indent=4))
        except Exception as e:
            log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Failed to convert structure: {str(e)}\n")

    convert_button = tk.Button(project_frame, text="Convert and Show Structure", command=convert_and_display_structure)
    convert_button.pack(pady=5)

    # Button to create the project structure
    def create_structure():
        output_directory = select_directory()
        if not output_directory:
            return

        tree_structure = text_area.get('1.0', tk.END).strip()
        if not tree_structure:
            messagebox.showerror("Error", "Please enter a project structure or load one.")
            return

        try:
            project_structure_dict = parse_tree_structure_to_dict(tree_structure)
            create_project_structure(output_directory, project_structure_dict, log_text)
            save_history(project_structure_dict)
        except Exception as e:
            log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Failed to create project: {str(e)}\n")

    create_button = tk.Button(project_frame, text="Create Project Structure", command=create_structure)
    create_button.pack(pady=5)

    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()
