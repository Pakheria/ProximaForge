import os
import json
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext, ttk, simpledialog

HISTORY_FILE = "project_history.json"

# Function to save the provided project structure to history for future use
def save_history(structure):
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = []
        else:
            history = []

        history.append(structure)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=4)
    except Exception as e:
        print(f"Failed to save history: {str(e)}")

# Function to load the saved project history
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# Function to add a new element (file/folder) to the tree structure view
def add_project_element(tree, parent, element_name, element_type):
    if element_type == "folder":
        # Validate that folder name is not a file with extension
        if '.' in element_name:
            messagebox.showerror("Invalid Folder Name", "Folder name cannot contain an extension.")
            return
        node = tree.insert(parent, 'end', text=element_name, open=True)
        tree.set(node, "type", "folder")
    elif element_type == "file":
        # Validate that file name contains an extension or is a known extension-only file
        if '.' not in element_name and element_name not in ['.env', '.gitignore', '.dockerignore']:
            messagebox.showerror("Invalid File Name", "File name must contain an extension or be a valid special file like .env or .gitignore.")
            return
        node = tree.insert(parent, 'end', text=element_name, open=False)
        tree.set(node, "type", "file")

# Function to parse the tkinter Treeview structure into a nested dictionary
def parse_tree_to_dict(tree, parent=''):
    items = tree.get_children(parent)
    structure = {}
    for item in items:
        item_text = tree.item(item, 'text')
        item_type = tree.set(item, "type")
        if item_type == 'folder':
            structure[item_text] = parse_tree_to_dict(tree, item)
        elif item_type == 'file':
            structure[item_text] = None
    return structure

# Function to create a folder structure from the provided dictionary and log each step
def create_project_structure(base_path, structure, log_text):
    for key, value in structure.items():
        current_path = os.path.join(base_path, key)
        if isinstance(value, dict):
            if not os.path.exists(current_path):
                try:
                    os.makedirs(current_path)
                    log_text.insert(tk.END, f"Created folder: {current_path}\n")
                except Exception as e:
                    log_text.insert(tk.END, f"Failed to create folder {current_path}: {str(e)}\n")
            create_project_structure(current_path, value, log_text)
        else:
            try:
                with open(current_path, 'w') as f:
                    pass  # Create an empty file
                log_text.insert(tk.END, f"Created file: {current_path}\n")
            except Exception as e:
                log_text.insert(tk.END, f"Failed to create file {current_path}: {str(e)}\n")

def main():
    # Initialize the main GUI window
    global root
    root = tk.Tk()
    root.title("Project Structure Creator")
    root.state('zoomed')  # Start in maximized mode

    # Create the main frame
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Project Name Input
    project_name_label = tk.Label(main_frame, text="Enter Project Name:")
    project_name_label.grid(row=0, column=0, pady=5)
    project_name_entry = tk.Entry(main_frame)
    project_name_entry.grid(row=0, column=1, pady=5)

    # Instructions Panel
    instructions_frame = tk.Frame(main_frame)
    instructions_frame.grid(row=1, column=3, padx=10, pady=10, sticky='n')
    instructions_label = tk.Label(instructions_frame, text="Instructions:", font=('Helvetica', 14, 'bold'))
    instructions_label.pack(anchor='w')
    instructions_text = (
        "1. Enter the Project Name in the input box.\n"
        "2. Use the buttons below to add folders or files to your project structure.\n"
        "   - 'Add Sibling Folder': Adds a folder at the same level as the selected item.\n"
        "   - 'Add Sibling File': Adds a file at the same level as the selected item.\n"
        "   - 'Add Child Folder': Adds a sub-folder under the selected folder.\n"
        "3. File names must have valid extensions (e.g., .py, .txt) or be valid special files (e.g., .env).\n"
        "4. Click 'Create Project Structure' to generate the folders and files at the selected location.\n"
        "5. Use 'Delete' to remove any selected item from the structure.\n"
        "6. You can also load from history using the dropdown menu."
    )
    instructions_label = tk.Label(instructions_frame, text=instructions_text, justify='left')
    instructions_label.pack(anchor='w')

    # History Dropdown Menu
    history_frame = tk.Frame(main_frame)
    history_frame.grid(row=0, column=2, padx=10, pady=5)
    history_label = tk.Label(history_frame, text="Load From History:")
    history_label.pack(anchor='w')
    history_options = load_history()
    history_names = [list(entry.keys())[0] for entry in history_options] if history_options else []
    history_var = tk.StringVar()
    history_dropdown = ttk.Combobox(history_frame, textvariable=history_var, values=history_names)
    history_dropdown.pack(anchor='w')

    def load_selected_history():
        selected_project = history_var.get()
        if not selected_project:
            return

        for entry in history_options:
            if selected_project in entry:
                tree.delete(*tree.get_children())
                project_structure = entry[selected_project]
                build_tree_from_dict(tree, '', project_structure)
                break

    load_history_button = tk.Button(history_frame, text="Load", command=load_selected_history)
    load_history_button.pack(anchor='w')

    # Treeview for project structure visualization
    tree_frame = tk.Frame(main_frame)
    tree_frame.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=10, pady=10)
    tree = ttk.Treeview(tree_frame, columns=('type',), show="tree", selectmode="browse")
    tree.heading('#0', text='Project Structure')
    tree.pack(fill=tk.BOTH, expand=True)

    # Buttons to Add Elements
    def add_sibling_folder():
        selected_item = tree.selection()
        if not selected_item:
            parent = ""
        else:
            parent = tree.parent(selected_item[0])
        element_name = simpledialog.askstring("New Folder", "Enter folder name:")
        if element_name:
            add_project_element(tree, parent, element_name, "folder")

    def add_sibling_file():
        selected_item = tree.selection()
        if not selected_item:
            parent = ""
        else:
            parent = tree.parent(selected_item[0])
        element_name = simpledialog.askstring("New File", "Enter file name (with extension):")
        if element_name:
            add_project_element(tree, parent, element_name, "file")

    def add_child_folder():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select a folder where you want to add a child folder.")
            return
        item_type = tree.set(selected_item[0], "type")
        if item_type != 'folder':
            messagebox.showerror("Selection Error", "Cannot add a child folder to a file.")
            return
        element_name = simpledialog.askstring("New Folder", "Enter child folder name:")
        if element_name:
            add_project_element(tree, selected_item[0], element_name, "folder")

    def delete_selected_item():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select an item to delete.")
            return
        tree.delete(selected_item[0])

    # Create buttons for the actions
    add_sibling_folder_button = tk.Button(main_frame, text="Add Sibling Folder", command=add_sibling_folder)
    add_sibling_folder_button.grid(row=2, column=0, pady=10)

    add_sibling_file_button = tk.Button(main_frame, text="Add Sibling File", command=add_sibling_file)
    add_sibling_file_button.grid(row=2, column=1, pady=10)

    add_child_folder_button = tk.Button(main_frame, text="Add Child Folder", command=add_child_folder)
    add_child_folder_button.grid(row=2, column=2, pady=10)

    delete_button = tk.Button(main_frame, text="Delete", command=delete_selected_item)
    delete_button.grid(row=3, column=1, pady=10)

    # Button to create the project structure
    def create_structure():
        output_directory = filedialog.askdirectory(title="Select Output Directory")
        if not output_directory:
            return

        project_name = project_name_entry.get().strip()
        if not project_name:
            messagebox.showerror("Error", "Project name cannot be empty.")
            return

        project_structure_dict = {project_name: parse_tree_to_dict(tree)}
        create_project_structure(output_directory, project_structure_dict, log_text)
        save_history(project_structure_dict)

    create_button = tk.Button(main_frame, text="Create Project Structure", command=create_structure)
    create_button.grid(row=4, column=1, pady=10)

    # ScrolledText widget for logging
    log_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=100, height=10)
    log_text.grid(row=5, column=0, columnspan=3, pady=10)

    root.mainloop()

def build_tree_from_dict(tree, parent, structure):
    for key, value in structure.items():
        if isinstance(value, dict):
            node = tree.insert(parent, 'end', text=key, open=True)
            tree.set(node, "type", "folder")
            build_tree_from_dict(tree, node, value)
        else:
            node = tree.insert(parent, 'end', text=key, open=False)
            tree.set(node, "type", "file")

if __name__ == "__main__":
    main()
