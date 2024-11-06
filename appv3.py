import os
import json
import openai
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QTreeWidget, QTreeWidgetItem, QFileDialog, QMessageBox, QComboBox, QTextEdit, QInputDialog, QFrame, QCheckBox)
from PySide6.QtGui import QIcon, QColor, QPalette
from PySide6.QtCore import Qt

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
            QMessageBox.critical(None, "Invalid Folder Name", "Folder name cannot contain an extension.")
            return
        node = QTreeWidgetItem(parent, [element_name])
        node.setData(0, Qt.UserRole, "folder")
    elif element_type == "file":
        # Validate that file name contains an extension or is a known extension-only file
        if '.' not in element_name and element_name not in ['.env', '.gitignore', '.dockerignore']:
            QMessageBox.critical(None, "Invalid File Name", "File name must contain an extension or be a valid special file like .env or .gitignore.")
            return
        node = QTreeWidgetItem(parent, [element_name])
        node.setData(0, Qt.UserRole, "file")

# Function to parse the QTreeWidget structure into a nested dictionary
def parse_tree_to_dict(tree, parent=None):
    structure = {}
    for i in range(parent.childCount() if parent else tree.topLevelItemCount()):
        item = parent.child(i) if parent else tree.topLevelItem(i)
        item_text = item.text(0)
        item_type = item.data(0, Qt.UserRole)
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
                    log_text.append(f"Created folder: {current_path}\n")
                except Exception as e:
                    log_text.append(f"Failed to create folder {current_path}: {str(e)}\n")
            create_project_structure(current_path, value, log_text)
        else:
            try:
                with open(current_path, 'w') as f:
                    pass  # Create an empty file
                log_text.append(f"Created file: {current_path}\n")
            except Exception as e:
                log_text.append(f"Failed to create file {current_path}: {str(e)}\n")

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

class ProjectStructureApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Structure Creator")
        self.setGeometry(0, 0, 1000, 800)
        self.setWindowIcon(QIcon("app_icon.png"))  # Set the application icon
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        # Top Row: Project Name and Theme Toggle
        self.top_row_layout = QHBoxLayout()
        self.top_row_layout.setSpacing(10)

        # Project Name Input
        self.project_name_label = QLabel("Enter Project Name:")
        self.project_name_label.setStyleSheet("font-size: 16px;")
        self.project_name_entry = QLineEdit()
        self.project_name_entry.setFixedHeight(30)
        self.project_name_entry.setFixedWidth(400)
        
        # Theme Toggle Button
        self.theme_button = QPushButton("Toggle Theme")
        self.theme_button.setFixedSize(150, 40)
        self.theme_button.clicked.connect(self.toggle_theme)

        self.top_row_layout.addWidget(self.project_name_label)
        self.top_row_layout.addWidget(self.project_name_entry)
        self.top_row_layout.addStretch()
        self.top_row_layout.addWidget(self.theme_button)
        self.layout.addLayout(self.top_row_layout)

        # API Key Input
        self.api_key_label = QLabel("Enter OpenAI API Key (Optional):")
        self.api_key_label.setStyleSheet("font-size: 16px;")
        self.api_key_entry = QLineEdit()
        self.api_key_entry.setEchoMode(QLineEdit.Password)
        self.api_key_entry.setFixedHeight(30)
        self.layout.addWidget(self.api_key_label)
        self.layout.addWidget(self.api_key_entry)

        # History Dropdown
        self.history_label = QLabel("Load From History:")
        self.history_label.setStyleSheet("font-size: 16px;")
        self.history_dropdown = QComboBox()
        self.history_dropdown.setFixedHeight(30)
        self.load_history_options()
        self.layout.addWidget(self.history_label)
        self.layout.addWidget(self.history_dropdown)

        self.load_history_button = QPushButton("Load")
        self.load_history_button.setFixedSize(150, 40)
        self.load_history_button.clicked.connect(self.load_selected_history)
        self.layout.addWidget(self.load_history_button)

        # Tree for project structure visualization and Manual Paste Toggle
        self.tree_layout = QHBoxLayout()
        self.tree_layout.setSpacing(10)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Project Structure")
        self.tree.setStyleSheet("font-size: 14px;")
        self.tree_layout.addWidget(self.tree)

        # Toggle to add manually or by buttons
        self.manual_add_toggle = QCheckBox("Add Project Structure Manually")
        self.manual_add_toggle.setStyleSheet("font-size: 14px;")
        self.manual_add_toggle.toggled.connect(self.toggle_manual_add)
        self.tree_layout.addWidget(self.manual_add_toggle)
        
        # Manual Paste Area
        self.manual_paste_text = QTextEdit()
        self.manual_paste_text.setPlaceholderText("Paste your pre-defined project structure here...")
        self.manual_paste_text.setDisabled(True)
        self.tree_layout.addWidget(self.manual_paste_text)
        
        self.layout.addLayout(self.tree_layout)

        # Buttons to Add Elements
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(10)
        self.add_sibling_folder_button = QPushButton("Add Sibling Folder")
        self.add_sibling_folder_button.setFixedSize(200, 50)
        
        self.add_sibling_file_button = QPushButton("Add Sibling File")
        self.add_sibling_file_button.setFixedSize(200, 50)
        
        self.add_child_folder_button = QPushButton("Add Child Folder")
        self.add_child_folder_button.setFixedSize(200, 50)

        self.button_layout.addWidget(self.add_sibling_folder_button)
        self.button_layout.addWidget(self.add_sibling_file_button)
        self.button_layout.addWidget(self.add_child_folder_button)

        self.add_sibling_folder_button.clicked.connect(self.add_sibling_folder)
        self.add_sibling_file_button.clicked.connect(self.add_sibling_file)
        self.add_child_folder_button.clicked.connect(self.add_child_folder)

        self.layout.addLayout(self.button_layout)

        # Separator between Add Elements and Main Functions
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(self.separator)

        # Buttons for Delete, Create Project, and AI Suggestions
        self.function_button_layout = QHBoxLayout()
        self.function_button_layout.setSpacing(10)
        self.delete_button = QPushButton("Delete")
        self.delete_button.setFixedSize(200, 50)
        
        self.create_button = QPushButton("Create Project Structure")
        self.create_button.setFixedSize(200, 50)
        self.create_button.clicked.connect(self.create_structure)
        
        self.get_ai_suggestions_button = QPushButton("Get AI Suggestions")
        self.get_ai_suggestions_button.setFixedSize(200, 50)
        self.get_ai_suggestions_button.clicked.connect(self.get_ai_suggestions_for_structure)

        self.function_button_layout.addWidget(self.delete_button)
        self.function_button_layout.addWidget(self.create_button)
        self.function_button_layout.addWidget(self.get_ai_suggestions_button)

        self.layout.addLayout(self.function_button_layout)

        # Separator to visually differentiate
        self.separator_2 = QFrame()
        self.separator_2.setFrameShape(QFrame.HLine)
        self.separator_2.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(self.separator_2)

        # Textbox for logging
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(self.log_text)

        # Apply initial theme (light theme)
        self.apply_light_theme()

    def toggle_theme(self):
        current_palette = self.palette()
        if current_palette.color(QPalette.Window) == QColor(Qt.white):
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def apply_light_theme(self):
        self.setStyleSheet("background-color: white; color: black;")
        self.project_name_label.setStyleSheet("font-size: 16px; color: black;")
        self.api_key_label.setStyleSheet("font-size: 16px; color: black;")
        self.history_label.setStyleSheet("font-size: 16px; color: black;")
        self.manual_add_toggle.setStyleSheet("font-size: 14px; color: black;")
        self.theme_button.setStyleSheet("background-color: #8A2BE2; font-size: 14px; color: white;")
        self.add_sibling_folder_button.setStyleSheet("background-color: #4682B4; font-size: 14px; color: white;")
        self.add_sibling_file_button.setStyleSheet("background-color: #4682B4; font-size: 14px; color: white;")
        self.add_child_folder_button.setStyleSheet("background-color: #4682B4; font-size: 14px; color: white;")
        self.delete_button.setStyleSheet("background-color: #FF6347; font-size: 14px; color: white;")
        self.create_button.setStyleSheet("background-color: #1E90FF; font-size: 14px; color: white;")
        self.get_ai_suggestions_button.setStyleSheet("background-color: #32CD32; font-size: 14px; color: white;")

    def apply_dark_theme(self):
        self.setStyleSheet("background-color: #2E2E2E; color: white;")
        self.project_name_label.setStyleSheet("font-size: 16px; color: white;")
        self.api_key_label.setStyleSheet("font-size: 16px; color: white;")
        self.history_label.setStyleSheet("font-size: 16px; color: white;")
        self.manual_add_toggle.setStyleSheet("font-size: 14px; color: white;")
        self.theme_button.setStyleSheet("background-color: #8A2BE2; font-size: 14px; color: white;")
        self.add_sibling_folder_button.setStyleSheet("background-color: #4682B4; font-size: 14px; color: white;")
        self.add_sibling_file_button.setStyleSheet("background-color: #4682B4; font-size: 14px; color: white;")
        self.add_child_folder_button.setStyleSheet("background-color: #4682B4; font-size: 14px; color: white;")
        self.delete_button.setStyleSheet("background-color: #FF6347; font-size: 14px; color: white;")
        self.create_button.setStyleSheet("background-color: #1E90FF; font-size: 14px; color: white;")
        self.get_ai_suggestions_button.setStyleSheet("background-color: #32CD32; font-size: 14px; color: white;")

    def toggle_manual_add(self, checked):
        self.add_sibling_folder_button.setEnabled(not checked)
        self.add_sibling_file_button.setEnabled(not checked)
        self.add_child_folder_button.setEnabled(not checked)
        self.manual_paste_text.setDisabled(not checked)

    def load_history_options(self):
        history_options = load_history()
        self.history_names = [list(entry.keys())[0] for entry in history_options] if history_options else []
        self.history_dropdown.addItems(self.history_names)

    def load_selected_history(self):
        selected_project = self.history_dropdown.currentText()
        if not selected_project:
            return

        history_options = load_history()
        for entry in history_options:
            if selected_project in entry:
                self.tree.clear()
                project_structure = entry[selected_project]
                self.build_tree_from_dict(self.tree, project_structure)
                break

    def build_tree_from_dict(self, tree, structure, parent=None):
        for key, value in structure.items():
            node = QTreeWidgetItem(parent, [key])
            node.setData(0, Qt.UserRole, "folder" if isinstance(value, dict) else "file")
            if parent is None:
                tree.addTopLevelItem(node)
            if isinstance(value, dict):
                self.build_tree_from_dict(tree, value, node)

    def add_sibling_folder(self):
        selected_item = self.tree.selectedItems()
        if selected_item:
            parent = selected_item[0].parent()
        else:
            parent = None
        element_name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if ok and element_name:
            add_project_element(self.tree, parent if parent else self.tree.invisibleRootItem(), element_name, "folder")

    def add_sibling_file(self):
        selected_item = self.tree.selectedItems()
        if selected_item:
            parent = selected_item[0].parent()
        else:
            parent = None
        element_name, ok = QInputDialog.getText(self, "New File", "Enter file name (with extension):")
        if ok and element_name:
            add_project_element(self.tree, parent if parent else self.tree.invisibleRootItem(), element_name, "file")

    def add_child_folder(self):
        selected_item = self.tree.selectedItems()
        if not selected_item:
            QMessageBox.critical(self, "Selection Error", "Please select a folder where you want to add a child folder.")
            return
        item_type = selected_item[0].data(0, Qt.UserRole)
        if item_type != 'folder':
            QMessageBox.critical(self, "Selection Error", "Cannot add a child folder to a file.")
            return
        element_name, ok = QInputDialog.getText(self, "New Folder", "Enter child folder name:")
        if ok and element_name:
            add_project_element(self.tree, selected_item[0], element_name, "folder")

    def delete_selected_item(self):
        selected_item = self.tree.selectedItems()
        if not selected_item:
            QMessageBox.critical(self, "Selection Error", "Please select an item to delete.")
            return
        root = self.tree.invisibleRootItem()
        (parent := selected_item[0].parent()) if selected_item[0].parent() else root.removeChild(selected_item[0])

    def create_structure(self):
        output_directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_directory:
            return

        project_name = self.project_name_entry.text().strip()
        if not project_name:
            QMessageBox.critical(self, "Error", "Project name cannot be empty.")
            return

        project_structure_dict = {project_name: parse_tree_to_dict(self.tree)}
        create_project_structure(output_directory, project_structure_dict, self.log_text)
        save_history(project_structure_dict)
        QMessageBox.information(self, "Success", "Project structure created and saved successfully!")

    def get_ai_suggestions_for_structure(self):
        prompt = QInputDialog.getText(self, "AI Suggestions", "Enter a brief description of your project (e.g., 'React app structure'):")[0]
        api_key = self.api_key_entry.text().strip()
        if prompt:
            suggestions = get_ai_suggestions(f"Suggest a folder and file structure for a project that is: {prompt}", api_key)
            if "Error:" in suggestions:
                QMessageBox.critical(self, "AI Error", suggestions)
            else:
                self.tree.clear()
                try:
                    suggested_structure = json.loads(suggestions)
                    self.build_tree_from_dict(self.tree, suggested_structure)
                except json.JSONDecodeError:
                    QMessageBox.critical(self, "Error", "Failed to parse AI suggestions into a valid structure.")

if __name__ == "__main__":
    app = QApplication([])
    window = ProjectStructureApp()
    window.show()
    app.exec()
