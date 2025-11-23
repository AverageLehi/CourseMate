# CourseMate Code Walkthrough

## Introduction
This walkthrough is designed for beginners in Python. We'll go through the CourseMate application code step by step. CourseMate is a note-taking app built with CustomTkinter (a modern Tkinter wrapper). It uses JSON for data storage and includes features like themes, templates, and organization.

## Prerequisites
- Basic Python knowledge (variables, functions, classes)
- Understanding of Tkinter (GUI basics)
- JSON file handling

## Code Structure Overview
The code is organized into:
1. Imports and constants
2. Data management
3. UI components (classes)
4. Main application class
5. Entry point

## Section 1: Imports and Setup
```python
import customtkinter as ctk
import json
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog
import ctypes
import os
```

**Explanation:**
- `customtkinter`: Modern GUI library
- `json`: For saving/loading data
- `datetime`: For timestamps
- `pathlib`: Modern file path handling
- `tkinter`: Base GUI (used with customtkinter)
- `ctypes`: For loading custom fonts on Windows
- `os`: File system operations

## Section 2: Constants and Themes
The code defines color themes and default settings. Themes are dictionaries with color values for different UI elements.

**Key Points:**
- Themes make the app customizable
- Default settings include theme, font, quotes
- Templates are predefined note structures

## Section 3: DataManager Class
This class handles all data operations.

**Methods:**
- `__init__`: Loads data from JSON file
- `load_data()`: Reads JSON, merges with defaults
- `save_data()`: Writes data to JSON
- CRUD operations for notebooks, notes, tasks

**For Beginners:**
- Think of it as a "database manager" but using JSON instead of a real database
- It ensures data persistence between app runs

## Section 4: UI Components
Several classes build the interface:

### Sidebar
- Navigation buttons (Home, Notebooks, Settings)
- Quick stats display
- Inspiration quotes section
- Notebook quick access list

### HomeView
- Write new notes area
- Notes list display
- Template selection
- Assignment to notebooks

### NotebooksView
- Grid/list of notebooks
- Individual notebook view with notes

### SettingsView
- Theme selection
- Font customization
- Quote management
- Template creation/editing

## Section 5: Main Application Class (CourseMate)
This is the main window class inheriting from `ctk.CTk`.

**Key Methods:**
- `__init__`: Sets up window, loads data, initializes UI
- `load_custom_fonts()`: Loads TTF/OTF fonts from assets
- `apply_settings()`: Updates theme/font dynamically
- View switching methods (`show_home()`, `show_notebooks()`, etc.)

## Section 6: Helper Classes
- `InputDialog`: Custom input popup
- `TemplateDialog`: For creating/editing templates
- `CreateNotebookDialog`: New notebook creation
- `NoteWindow`: Individual note viewer/editor

## Section 7: Entry Point
```python
if __name__ == "__main__":
    app = CourseMate()
    app.mainloop()
```

This creates the app instance and starts the GUI event loop.

## Learning Tips for Your Group
1. Start with understanding the data flow: User action → DataManager → JSON file
2. Focus on one view at a time (HomeView is a good start)
3. Practice with the template system - it's a good example of dynamic content
4. Understand the theme system for customization concepts
5. The app demonstrates MVC pattern: Data (DataManager), View (UI classes), Controller (CourseMate)

## Common Questions
- **Why CustomTkinter?** More modern look than standard Tkinter
- **Why JSON?** Simple, human-readable, no database needed
- **How does theming work?** Colors stored in dictionaries, applied to widgets
- **What are templates?** Predefined text structures for notes

## Practice Exercises
1. Add a new theme color
2. Create a simple custom template
3. Add a new setting option
4. Modify the sidebar layout

This walkthrough should give your group a solid foundation to understand and modify the CourseMate application.