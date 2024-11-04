import os
import json
import time
import tkinter as tk

from tkinter import messagebox, filedialog, scrolledtext

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
        cleaned_line = line.lstrip('│├└─| ').strip()

        # Skip empty lines or invalid lines
        if not cleaned_line:
            continue

        # Determine the depth based on leading spaces (each level is 4 spaces)
        depth = (len(line) - len(cleaned_line)) // 4

        # Debugging: Print cleaned line and its depth
        print(f"Cleaned Line: '{cleaned_line}', Depth: {depth}")

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
    root.geometry("1280x768")

    # Label for instructions
    instruction_label = tk.Label(root, text="Enter your project structure (e.g. tree-like format) or load from a text file:")
    instruction_label.pack(pady=10)

    # ScrolledText widget for project structure input
    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=20)
    text_area.pack(pady=10)

    # ScrolledText widget for logging
    log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=10)
    log_text.pack(pady=10)

    # Button to load file
    def load_file_content():
        file_content = load_file()
        if file_content:
            text_area.delete('1.0', tk.END)
            text_area.insert(tk.END, file_content)

    load_file_button = tk.Button(root, text="Load from File", command=load_file_content)
    load_file_button.pack(pady=5)

    # Button to convert project structure to dictionary and display
    def convert_and_display_structure():
        project_text = text_area.get("1.0", tk.END).strip()
        if not project_text:
            messagebox.showwarning("Warning", "Please provide the project structure.")
            return

        project_structure = parse_tree_structure_to_dict(project_text)
        if not project_structure:
            messagebox.showerror("Error", "Failed to parse the project structure. Please check the input format.")
            return

        # Display the converted dictionary in a new window
        dict_window = tk.Toplevel(root)
        dict_window.title("Converted Project Structure Dictionary")
        dict_window.geometry("600x400")

        dict_text = scrolledtext.ScrolledText(dict_window, wrap=tk.WORD, width=70, height=20)
        dict_text.pack(pady=10)
        dict_text.insert(tk.END, json.dumps(project_structure, indent=4))

    convert_button = tk.Button(root, text="Convert and Show Structure", command=convert_and_display_structure)
    convert_button.pack(pady=5)

    # Button to select directory and create project structure
    def select_directory_and_create():
        project_text = text_area.get("1.0", tk.END).strip()
        if not project_text:
            messagebox.showwarning("Warning", "Please provide the project structure.")
            return

        try:
            # Try to load JSON structure first
            project_structure = json.loads(project_text)
        except json.JSONDecodeError:
            # If JSON fails, use tree structure parsing
            project_structure = parse_tree_structure_to_dict(project_text)

        if not project_structure:
            messagebox.showerror("Error", "Failed to parse the project structure. Please check the input format.")
            return

        # Remove any empty string keys from the project structure
        project_structure = {k: v for k, v in project_structure.items() if k}

        # Select the base path for creating the project structure
        base_path = select_directory()
        if not base_path:
            return

        # Treat the project structure root key as the root folder
        root_key = list(project_structure.keys())[0]
        root_structure = project_structure[root_key]
        root_folder_path = os.path.join(base_path, root_key)

        # Create the root folder if applicable and everything inside it
        if not os.path.exists(root_folder_path):
            os.makedirs(root_folder_path, exist_ok=True)
            log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Created root folder: {root_folder_path}\n")

        # Create the entire project structure under the root folder
        create_project_structure(root_folder_path, root_structure, log_text)

    create_button = tk.Button(root, text="Create Project Structure", command=select_directory_and_create)
    create_button.pack(pady=20)

    # Run the main loop
    root.mainloop()

if __name__ == "__main__":
    main()
