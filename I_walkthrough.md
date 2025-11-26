## Tags UX update (added Nov 26, 2025)

CourseMate now handles tags as in-content hashtags. Instead of a separate tag entry and chips UI, users type hashtags directly into the note content (for example, "#exam" or "#main-idea"). Highlights and extraction rules:

- Hashtag extraction and sanitization: on save, hashtags embedded in the text are detected, normalized and de-duplicated before being persisted into the note's `tags` list.
    - Normalization rules: strips punctuation, lowercases characters, collapses whitespace and joins words with hyphens
    - Each stored tag is canonicalized and stored with a leading `#` (e.g. `#cornell-notes`)
    - Example: text containing `#Cornell Notes` will persist as `#cornell-notes` in the data model

- Inline editing model: there is no tags sidebar or chips UI anymore. Hashtags are highlighted inside the content area as-you-type; on Save / Export the app extracts them and stores them in the note metadata.

This simplifies the UX and reduces duplication — tags are now kept in a single place (the note content) and the UI highlights them for quick scanning.
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

## Updated dataset & scenarios (added Nov 26, 2025)

To support testing and the mock defense, the companion dataset `Coursemate_data.json` now includes examples that exercise every built-in study template and every planner template. There are also two new notebooks added: **Ethics in Computing (ETH 100)** and **Planner Examples (PLN 001)**. These are intended to help reviewers see all UI flows and tag behaviors.

What was added
- Study templates used (one or more notes added across notebooks):
    - Cornell Notes — `GEN 001` ("Cornell Notes - Speech Outline")
    - Main Idea & Details — `GEN 002` ("Main Idea & Details - Identity")
    - Modified Frayer Model — `ITE 260` ("Frayer - Variables")
    - Polya's 4 Steps — `GEN 001` and `PED 030` (practice examples)
    - 5W1H — `MAT 152` ("5W1H - Word Problems")
    - Concept Map — `ITE 366` and `ETH 100` (concept maps)

- Planner templates used in `PLN 001` (Planner Examples):
    - Daily Planner
    - Weekly Overview
    - Time Block Grid
    - Assignment Tracker
    - Habit Tracker
    - Weekly Planning

Tags and edge cases
 - Several notes include example tags (e.g. `#ethics`, `#planner`, `#cornell`, `#exercise`). The Note editor highlights in-content hashtags and extracts/normalizes them on save.

Tag sidebar & overflow handling

If users add a large number of tags, tags remain inline in the content and will not expand any additional tag UI layers — tagging is handled within the note text itself.

How to validate these scenarios locally
1. Open the app and go to "Notebooks" → pick a notebook (e.g. "Purposive Communication" or "Ethics in Computing").
2. Open a note that corresponds to a template (see list above) and confirm that the content reflects the template structure.
3. Edit tags in `NoteWindow` — try entering whitespace-only content ("   ") then click out — the entry will clear and the placeholder text will show.
4. Enter tags using a comma-separated list including spaces and stray commas (e.g. " , #exam,  practice ,, #math "). Move focus out — the system will normalize to `#exam, #practice, #math` and save as a list.
5. Use the Planner notebook `PLN 001` to review sample planner templates and confirm tags, content, and that these notes are represented in the app view.

Test checklist for the mock defense:
- Verify each of the study templates above appears in at least one note.
- Verify all planner templates are present as notes in `PLN 001`.
- Verify tags display correctly in lists and in NoteWindow and placeholders appear when appropriate.
- Confirm export & copy actions work for individual notes (NoteWindow) and that word count updates while typing.

If you'd like, I can also add a small unit-test style script (Python) that validates the JSON dataset contains at least one note for each template — would you like that created in the repo?