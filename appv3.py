import os
import json
import openai
import customtkinter as ctk
from tkinter import messagebox, filedialog, simpledialog, ttk

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
                    log_text.insert(ctk.END, f"Created folder: {current_path}\n")
                except Exception as e:
                    log_text.insert(ctk.END, f"Failed to create folder {current_path}: {str(e)}\n")
            create_project_structure(current_path, value, log_text)
        else:
            try:
                with open(current_path, 'w') as f:
                    pass  # Create an empty file
                log_text.insert(ctk.END, f"Created file: {current_path}\n")
            except Exception as e:
                log_text.insert(ctk.END, f"Failed to create file {current_path}: {str(e)}\n")

# Function to integrate AI-based suggestions
def get_ai_suggestions(prompt, api_key):
    try:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that generates project folder structures."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.5,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    # Initialize the main GUI window
    global root
    root = ctk.CTk()
    root.title("Project Structure Creator")
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry("{}x{}+0+0".format(width, height))

    # Theme selection
    ctk.set_appearance_mode("System")  # Can be "System", "Dark", or "Light"

    def change_theme(theme):
        ctk.set_appearance_mode(theme)

    # Create the main frame
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

    # Project Name Input
    project_frame = ctk.CTkFrame(main_frame)
    project_frame.grid(row=0, column=3, padx=10, pady=5)
    project_name_label = ctk.CTkLabel(project_frame, text="Enter Project Name:")
    project_name_label.pack(anchor='w')
    project_name_entry = ctk.CTkEntry(main_frame)
    project_name_entry.grid(row=0, column=1, pady=5)

    # API Key Input
    api_key_label = ctk.CTkLabel(main_frame, text="Enter OpenAI API Key (Optional):")
    api_key_label.grid(row=1, column=0, pady=5)
    api_key_entry = ctk.CTkEntry(main_frame, show="*")
    api_key_entry.grid(row=1, column=1, pady=5)

    # Instructions Panel
    instructions_frame = ctk.CTkFrame(main_frame)
    instructions_frame.grid(row=1, column=3, padx=10, pady=10, sticky='n')
    instructions_label = ctk.CTkLabel(instructions_frame, text="Instructions:", font=('Helvetica', 14, 'bold'))
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
        "6. You can also load from history using the dropdown menu.\n"
        "7. Use the 'Get AI Suggestions' button to generate suggestions for the folder structure based on AI."
    )
    instructions_label = ctk.CTkLabel(instructions_frame, text=instructions_text, justify='left')
    instructions_label.pack(anchor='w')

    # Theme Toggle
    theme_frame = ctk.CTkFrame(main_frame)
    theme_frame.grid(row=0, column=3, padx=10, pady=5)
    theme_label = ctk.CTkLabel(theme_frame, text="Select Theme:")
    theme_label.pack(anchor='w')
    theme_button_dark = ctk.CTkButton(theme_frame, text="Dark", command=lambda: change_theme("Dark"))
    theme_button_dark.pack(anchor='w', pady=10, padx=4)
    theme_button_light = ctk.CTkButton(theme_frame, text="Light", command=lambda: change_theme("Light"))
    theme_button_light.pack(anchor='w', pady=10, padx=4)

    # History Dropdown Menu
    history_frame = ctk.CTkFrame(main_frame)
    history_frame.grid(row=0, column=2, padx=10, pady=5)
    history_label = ctk.CTkLabel(history_frame, text="Load From History:")
    history_label.pack(anchor='w')
    history_options = load_history()
    history_names = [list(entry.keys())[0] for entry in history_options] if history_options else []
    history_var = ctk.StringVar()
    history_dropdown = ctk.CTkComboBox(history_frame, values=history_names, variable=history_var)
    history_dropdown.pack(anchor='w', pady=10)

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

    load_history_button = ctk.CTkButton(history_frame, text="Load", command=load_selected_history)
    load_history_button.pack(anchor='w', pady=10)

    # Treeview for project structure visualization
    tree_frame = ctk.CTkFrame(main_frame)
    tree_frame.grid(row=2, column=0, columnspan=3, sticky='nsew', padx=10, pady=10)
    tree = ttk.Treeview(tree_frame, columns=('type',), show="tree", selectmode="browse")
    tree.heading('#0', text='Project Structure')
    tree.pack(fill=ctk.BOTH, expand=True)

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

    def get_ai_suggestions_for_structure():
        prompt = simpledialog.askstring("AI Suggestions", "Enter a brief description of your project (e.g., 'React app structure'):" )
        api_key = api_key_entry.get().strip()
        if prompt:
            suggestions = get_ai_suggestions(f"Suggest a folder and file structure for a project that is: {prompt}", api_key)
            if "Error:" in suggestions:
                messagebox.showerror("AI Error", suggestions)
            else:
                tree.delete(*tree.get_children())
                try:
                    suggested_structure = json.loads(suggestions)
                    build_tree_from_dict(tree, '', suggested_structure)
                except json.JSONDecodeError:
                    messagebox.showerror("Error", "Failed to parse AI suggestions into a valid structure.")

    # Create buttons for the actions
    add_sibling_folder_button = ctk.CTkButton(main_frame, text="Add Sibling Folder", command=add_sibling_folder)
    add_sibling_folder_button.grid(row=3, column=0, pady=10)

    add_sibling_file_button = ctk.CTkButton(main_frame, text="Add Sibling File", command=add_sibling_file)
    add_sibling_file_button.grid(row=3, column=1, pady=10)

    add_child_folder_button = ctk.CTkButton(main_frame, text="Add Child Folder", command=add_child_folder)
    add_child_folder_button.grid(row=3, column=2, pady=10)

    delete_button = ctk.CTkButton(main_frame, text="Delete", command=delete_selected_item, fg_color="red")
    delete_button.grid(row=4, column=1, pady=10)

    get_ai_suggestions_button = ctk.CTkButton(main_frame, text="Get AI Suggestions", command=get_ai_suggestions_for_structure, fg_color="green")
    get_ai_suggestions_button.grid(row=4, column=2, pady=10)

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

    create_button = ctk.CTkButton(main_frame, text="Create Project", command=create_structure, fg_color="blue")
    create_button.grid(row=5, column=1, pady=10)

    # ScrolledText widget for logging
    log_text = ctk.CTkTextbox(main_frame, wrap=ctk.WORD)
    log_text.grid(row=6, column=0, columnspan=3, pady=10, sticky='nsew')

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
