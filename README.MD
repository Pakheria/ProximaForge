
# ProximaForge

ProximaForge is a powerful and intuitive script that allows developers to quickly generate a complete project folder and file structure from a simple input. Whether you're working on a new Python project, web development setup, or custom configuration, ProximaForge helps you set up your entire project with a single command.

## Features

-   **Customizable Project Structures**: Create tailored folder and file hierarchies to fit different types of projects.
    
-   **Simple Input Format**: Input the desired structure in a tree-like format or load from a text file.
    
-   **GUI Support**: A user-friendly GUI built with Tkinter to easily manage input, configuration, and logs.
    
-   **Log Window**: Detailed logging of folder and file creation, allowing you to track each step.
    
-   **Error Handling**: Clear messages for existing files, permission issues, or any failures during creation.
    
-   **Flexible Output Directory**: Select any location for the project structure to be created, including different drives.
    

## Installation

### Prerequisites

-   Python 3.8 or higher
    
-   Virtual environment recommended for dependencies
    
-   `tkinter` for GUI support (included by default in standard Python installations)
    

### Installation Steps

1.  Clone the repository:
    
    ```
    git clone https://github.com/Pakheria/ProximaForge.git
    ```
    
2.  Navigate to the project directory:
    
    ```
    cd ProximaForge
    ```
    
3.  Create a virtual environment:
    
    ```
    python -m venv venv
    ```
    
4.  Activate the virtual environment:
    
    -   **Windows**:
        
        ```
        venv\Scripts\activate
        ```
        
    -   **Linux/macOS**:
        
        ```
        source venv/bin/activate
        ```
        
5.  Install the required packages:
    
    ```
    pip install -r requirements.txt
    ```
    

## Usage

### Running ProximaForge

After installing, you can run ProximaForge to create your project structure:

```
python main.py
```

### Features Overview

-   **Input Area**: Enter the desired project structure in a tree-like text format.
    
-   **Load Structure from File**: Load the folder structure from a text file for more complex projects.
    
-   **Select Output Directory**: Choose where you want the project to be created.
    
-   **Convert and Preview Structure**: See the parsed dictionary representation of your project structure before creation.
    
-   **Logging Panel**: View real-time logs for folder and file creation status, errors, and completions.
    

### Example Input Format

To create a simple Python project structure, you can use an input like this:

```
proximaguard/
    main.py
    requirements.txt
    database/
        db_connection.py
        init_db.py
    utils/
        helper_functions.py
```

The script will generate the entire structure in the specified output folder.

## Cross-Platform Compatibility

ProximaForge is designed to work across multiple operating systems, including **Windows**, **Linux**, and **macOS**. The following are some platform-specific considerations to ensure smooth functionality:

### File Paths

-   **Windows** uses backslashes (`\`) for file paths, while **Linux** and **macOS** use forward slashes (`/`).
    
-   The script dynamically determines the correct file separator based on the operating system using Python's `os.path` module, ensuring that paths are compatible across all platforms.
    

### Dependencies

-   The script relies on **Tkinter** for GUI support. On most systems, `tkinter` is included with Python by default:
    
    -   **Windows**: Typically, Tkinter comes bundled with Python.
        
    -   **Linux**: You may need to install `tkinter` separately:
        
        ```
        sudo apt-get install python3-tk
        ```
        
    -   **macOS**: Tkinter should also be included, but ensure that the correct version of Python is installed.
        

### Executable Creation

-   **Windows**: PyInstaller can be used to create a `.exe` file:
    
    ```
    pyinstaller main.py --onefile
    ```
    
-   **Linux/macOS**: PyInstaller creates executables without an extension. Ensure that PyInstaller is installed and run:
    
    ```
    pyinstaller main.py --onefile
    ```
    
    Note: You may need to adjust the permissions of the generated executable:
    
    ```
    chmod +x dist/main
    ```
    

## Contributing

Contributions are welcome! If you'd like to improve ProximaForge or report any issues, please:

1.  Fork the repository.
    
2.  Create a new feature branch (`git checkout -b feature-branch-name`).
    
3.  Commit your changes (`git commit -m 'Add new feature'`).
    
4.  Push to the branch (`git push origin feature-branch-name`).
    
5.  Create a Pull Request.
    

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Acknowledgments

-   **Tkinter** for providing a simple yet effective GUI framework.
    
-   **PyInstaller** for creating standalone executables from the script.
    

## Contact

For further questions or suggestions, please contact us at proximalinkpk@gmail.com.
