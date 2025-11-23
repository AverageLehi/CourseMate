import customtkinter as ctk
import json
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog
import ctypes
import os

# ============================================================================
# CONFIGURATION & THEMES
# ============================================================================

THEMES = {
    'CourseMate Theme': {
        'primary_dark':     '#253241',
        'primary':          '#334a66',
        'accent':           '#4a90e2',
        'background':       '#f4f7fb',
        'sidebar_button':   '#334a66',
        'sidebar_hover':    '#405977',
        'sidebar_text':     '#F4F4F4',
        'card_bg':          '#e1e7ed',
        'success':          '#27ae60',
        'info':             '#3498db',
        'warning':          '#ffe082',
        'muted':            '#9aa6b1',
        'header_text':      '#F4F4F4',
        'main_text':        '#0b2740',
        'secondary_text':   '#8193a1', 
        'danger':           '#e74c3c',
        'card_hover':       '#cfd8e1'
    },
    'Light Theme': {
        'primary_dark':     '#e0e0e0',
        'primary':          '#f5f5f5',
        'accent':           '#2196f3',
        'background':       '#ffffff',
        'sidebar_button':   '#f5f5f5',
        'sidebar_hover':    '#e0e0e0',
        'sidebar_text':     '#333333',
        'card_bg':          '#f5f5f5',
        'success':          '#4caf50',
        'info':             '#2196f3',
        'warning':          '#ffeb3b',
        'muted':            '#9e9e9e',
        'header_text':      '#333333',
        'main_text':        '#000000',
        'secondary_text':   '#757575',
        'danger':           '#f44336',
        'card_hover':       '#eeeeee'
    },
    'Dark Theme': {
        'primary_dark':     '#121212',
        'primary':          '#1e1e1e',
        'accent':           '#bb86fc',
        'background':       '#121212',
        'sidebar_button':   '#1e1e1e',
        'sidebar_hover':    '#333333',
        'sidebar_text':     '#ffffff',
        'card_bg':          '#1e1e1e',
        'success':          '#03dac6',
        'info':             '#3700b3',
        'warning':          '#cf6679',
        'muted':            '#b0b0b0',
        'header_text':      '#ffffff',
        'main_text':        '#ffffff',
        'secondary_text':   '#b0b0b0',
        'danger':           '#cf6679',
        'card_hover':       '#2d2d2d'
    },
    'Baby Pink': {
        'primary_dark':     '#f8bbd0',
        'primary':          '#fce4ec',
        'accent':           '#ec407a',
        'background':       '#fff0f5',
        'sidebar_button':   '#fce4ec',
        'sidebar_hover':    '#f8bbd0',
        'sidebar_text':     '#880e4f',
        'card_bg':          '#ffebee',
        'success':          '#66bb6a',
        'info':             '#42a5f5',
        'warning':          '#ffee58',
        'muted':            '#bdbdbd',
        'header_text':      '#880e4f',
        'main_text':        '#4a148c',
        'secondary_text':   '#ad1457',
        'danger':           '#ef5350',
        'card_hover':       '#ffcdd2'
    },
    'Baby Blue': {
        'primary_dark':     '#b3e5fc',
        'primary':          '#e1f5fe',
        'accent':           '#29b6f6',
        'background':       '#f0f8ff',
        'sidebar_button':   '#e1f5fe',
        'sidebar_hover':    '#b3e5fc',
        'sidebar_text':     '#01579b',
        'card_bg':          '#e3f2fd',
        'success':          '#66bb6a',
        'info':             '#29b6f6',
        'warning':          '#ffee58',
        'muted':            '#bdbdbd',
        'header_text':      '#01579b',
        'main_text':        '#0d47a1',
        'secondary_text':   '#0277bd',
        'danger':           '#ef5350',
        'card_hover':       '#bbdefb'
    }
}

DEFAULT_SETTINGS = {
    "theme": "CourseMate Theme",
    "font_family": "Helvetica",
    "font_size": "Normal", # Normal, Large
    "quotes": [],
    "quote_timer": 30 # seconds
}

# ============================================================================
# DATA MANAGER
# ============================================================================

class DataManager:
    def __init__(self, filepath="Coursemate_data.json"):
        self.filepath = Path(filepath)
        self.data = {
            "courses": {}, # Now acting as Notebooks
            "tasks": [],
            "completed_tasks": [],
            "unassigned_notes": [], # New: Notes created in Home without assignment
            "settings": DEFAULT_SETTINGS.copy()
        }
        self.load_data()

    def load_data(self):
        if self.filepath.exists():
            try:
                with open(self.filepath, 'r') as f:
                    loaded_data = json.load(f)
                    # Merge loaded data with defaults to handle missing keys (migrations)
                    self.data["courses"] = loaded_data.get("courses", {})
                    self.data["tasks"] = loaded_data.get("tasks", [])
                    self.data["completed_tasks"] = loaded_data.get("completed_tasks", [])
                    self.data["unassigned_notes"] = loaded_data.get("unassigned_notes", [])
                    
                    # Merge settings carefully
                    saved_settings = loaded_data.get("settings", {})
                    for k, v in DEFAULT_SETTINGS.items():
                        if k not in saved_settings:
                            saved_settings[k] = v
                    self.data["settings"] = saved_settings
                    
            except Exception as e:
                print(f"Error loading data: {e}")
                # Keep default initialized data
        else:
            self.save_data() # Create file if not exists

    def save_data(self):
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
            messagebox.showerror("Save Error", f"Could not save data: {e}")

    # --- Helper Accessors ---
    def get_notebooks(self):
        return self.data["courses"]

    def get_unassigned_notes(self):
        return self.data["unassigned_notes"]

    def get_settings(self):
        return self.data["settings"]
    
    def update_setting(self, key, value):
        self.data["settings"][key] = value
        self.save_data()

    def add_unassigned_note(self, note):
        self.data["unassigned_notes"].append(note)
        self.save_data()

    def add_note_to_notebook(self, notebook_name, note):
        if notebook_name in self.data["courses"]:
            self.data["courses"][notebook_name]["notes"].append(note)
            self.save_data()

    def add_notebook(self, name, code="", instructor=""):
        # Case-insensitive check
        existing_names = [n.lower() for n in self.data["courses"].keys()]
        if name.lower() not in existing_names:
            self.data["courses"][name] = {
                "notes": [], 
                "tasks": [],
                "code": code,
                "instructor": instructor
            }
            self.save_data()
            return True
        return False

    def rename_notebook(self, old_name, new_name):
        existing_names = [n.lower() for n in self.data["courses"].keys()]
        if old_name in self.data["courses"] and new_name.lower() not in existing_names:
            self.data["courses"][new_name] = self.data["courses"].pop(old_name)
            self.save_data()
            return True
        return False

    def delete_notebook(self, name):
        if name in self.data["courses"]:
            del self.data["courses"][name]
            self.save_data()
            return True
        return False

    def note_exists(self, notebook_name, title):
        # Check unassigned
        if notebook_name is None or notebook_name == "• Unassigned Notes" or notebook_name == "Unassigned Notes":
            notes = self.data["unassigned_notes"]
        # Check assigned
        elif notebook_name in self.data["courses"]:
            notes = self.data["courses"][notebook_name]["notes"]
        else:
            return False
            
        # Case-insensitive title check
        for note in notes:
            if note.get("title", "").lower() == title.lower():
                return True
        return False

    def delete_note(self, notebook_name, note_index):
        if notebook_name in self.data["courses"]:
            if 0 <= note_index < len(self.data["courses"][notebook_name]["notes"]):
                self.data["courses"][notebook_name]["notes"].pop(note_index)
                self.save_data()
                return True
        return False

# ============================================================================
# MAIN APPLICATION
# ============================================================================

class CourseMateRevampApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Data Setup
        # Data Setup
        self.data_manager = DataManager()
        self.load_custom_fonts()
        
        self.current_theme = self.data_manager.get_settings()["theme"]
        self.colors = THEMES.get(self.current_theme, THEMES['CourseMate Theme'])
        
        # Font State
        self.font_family = self.data_manager.get_settings().get("font_family", "Helvetica")
        self.font_size_mode = self.data_manager.get_settings().get("font_size", "Normal")
        self.base_font_size = 14 if self.font_size_mode == "Normal" else 18
        
        # Window Setup
        self.title("CourseMate")
        self.geometry("1400x800")
        self.minsize(1400, 800)
        ctk.set_appearance_mode("System")
        
        # Layout Setup
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.sidebar = None
        self.main_area = None
        
        self._init_ui()
        self.show_home() # Default view

    def _init_ui(self):
        # Sidebar
        self.sidebar = Sidebar(self, self.data_manager, self.colors, self.show_home, self.show_notebooks, self.show_settings)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Main Content Area
        self.main_area = ctk.CTkFrame(self, fg_color=self.colors['background'], corner_radius=0)
        self.main_area.grid(row=0, column=1, sticky="nsew")

    def clear_main_area(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()

    def show_home(self):
        self.clear_main_area()
        self.current_view = HomeView(self.main_area, self.data_manager, self.colors)

    def show_notebooks(self, notebook_name=None):
        self.clear_main_area()
        self.current_view = NotebooksView(self.main_area, self.data_manager, self.colors, notebook_name)

    def show_settings(self):
        self.clear_main_area()
        self.current_view = SettingsView(self.main_area, self.data_manager, self.colors)

    def load_custom_fonts(self):
        # Load fonts from assets/fonts
        font_dir = os.path.join(os.path.dirname(__file__), "assets", "fonts")
        if not os.path.exists(font_dir):
            return

        # Windows Font Loading
        gdi32 = ctypes.windll.gdi32
        for font_file in os.listdir(font_dir):
            if font_file.lower().endswith((".ttf", ".otf")):
                font_path = os.path.join(font_dir, font_file)
                ret = gdi32.AddFontResourceExW(font_path, 0x10, 0) # FR_PRIVATE = 0x10
                if ret == 0:
                    print(f"Failed to load font: {font_file}")
                else:
                    print(f"Loaded font: {font_file}")

    def get_font(self, size_offset=0, weight="normal", slant="roman"):
        # Helper to get font tuple
        size = self.base_font_size + size_offset
        return (self.font_family, size, weight, slant)

    def apply_settings(self):
        settings = self.data_manager.get_settings()
        
        # Update Theme
        theme_name = settings.get("theme", "CourseMate Theme")
        if theme_name in THEMES:
            self.current_theme = theme_name
            self.colors = THEMES[theme_name]
        
        # Update Font
        self.font_family = settings.get("font_family", "Helvetica")
        self.font_size_mode = settings.get("font_size", "Normal")
        self.base_font_size = 14 if self.font_size_mode == "Normal" else 18
        
        # Update Sidebar
        self.sidebar.destroy()
        self.sidebar = Sidebar(self, self.data_manager, self.colors, self.show_home, self.show_notebooks, self.show_settings)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Update Main Area Background
        self.main_area.configure(fg_color=self.colors['background'])
        
        # Refresh Current View
        # Re-instantiate the current view class
        if isinstance(self.current_view, HomeView):
            self.show_home()
        elif isinstance(self.current_view, NotebooksView):
            self.show_notebooks()
        elif isinstance(self.current_view, SettingsView):
            self.show_settings()
        else:
            self.show_settings()

    def apply_theme(self, theme_name):
        # Deprecated, use apply_settings, but kept for compatibility if needed
        self.data_manager.update_setting("theme", theme_name)
        self.apply_settings()

    def truncate_text(self, text, limit=25):
        if len(text) > limit:
            return text[:limit-3] + "..."
        return text


# ============================================================================
# UI COMPONENTS (Placeholders for now)
# ============================================================================

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, data_manager, colors, home_cb, notebooks_cb, settings_cb):
        super().__init__(master, width=250, corner_radius=0, fg_color=colors['primary_dark'])
        self.colors = colors
        self.data_manager = data_manager
        self.home_cb = home_cb
        self.notebooks_cb = notebooks_cb
        
        # Title
        # Title
        ctk.CTkLabel(self, text="CourseMate", font=master.get_font(10, "bold"), text_color=colors['header_text']).pack(pady=(30, 10))
        ctk.CTkLabel(self, text="Stay Organized • Learn Deeper", font=master.get_font(-2), text_color=colors['secondary_text']).pack(pady=(0, 20))
        
        # Quick Stats
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=20, pady=(0, 20))
        self.lbl_notebooks_count = ctk.CTkLabel(self.stats_frame, text="Notebooks: 0", font=master.get_font(-2, "bold"), text_color=colors['header_text'], anchor="w")
        self.lbl_notebooks_count.pack(fill="x")
        self.lbl_notes_count = ctk.CTkLabel(self.stats_frame, text="Total Notes: 0", font=master.get_font(-2, "bold"), text_color=colors['header_text'], anchor="w")
        self.lbl_notes_count.pack(fill="x")
        
        # Navigation
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(fill="x", pady=10)
        
        self._create_nav_btn("Home", home_cb)
        self._create_nav_btn("Notebooks", notebooks_cb)
        self._create_nav_btn("Settings", settings_cb)
        
        # Notebooks Quick Access (Scrollable)
        ctk.CTkLabel(self, text="NOTEBOOKS", font=master.get_font(-2, "bold"), text_color=colors['secondary_text'], anchor="w").pack(fill="x", padx=20, pady=(20, 5))
        
        self.notebooks_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", height=150)
        self.notebooks_frame.pack(fill="x", padx=10, pady=5)
        
        # Inspiration Section (Bottom)
        self.inspiration_frame = ctk.CTkFrame(self, fg_color=colors['card_bg'], corner_radius=10)
        self.inspiration_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(self.inspiration_frame, text="Inspiration", font=master.get_font(-2, "bold"), text_color=colors['main_text']).pack(pady=(10, 5))
        self.lbl_quote = ctk.CTkLabel(self.inspiration_frame, text="Loading quote...", font=master.get_font(-3, "italic"), 
                                      text_color=colors['main_text'], wraplength=180)
        self.lbl_quote.pack(pady=(0, 10), padx=10)
        
        # Initial Data Load
        self.refresh_stats()
        self.refresh_notebooks_list()
        self.start_quote_timer()

    def _create_nav_btn(self, text, command):
        btn = ctk.CTkButton(self.nav_frame, text=text, command=command, 
                            fg_color="transparent", hover_color=self.colors['sidebar_hover'], 
                            anchor="w", height=40, font=self.master.get_font(2, "bold"), text_color=self.colors['sidebar_text'])
        btn.pack(fill="x", padx=10, pady=2)

    def refresh_stats(self):
        notebooks = self.data_manager.get_notebooks()
        total_notes = sum(len(nb.get('notes', [])) for nb in notebooks.values()) + len(self.data_manager.get_unassigned_notes())
        
        self.lbl_notebooks_count.configure(text=f"Notebooks: {len(notebooks)}")
        self.lbl_notes_count.configure(text=f"Total Notes: {total_notes}")

    def refresh_notebooks_list(self):
        # Clear existing
        for widget in self.notebooks_frame.winfo_children():
            widget.destroy()
            
        notebooks = self.data_manager.get_notebooks()
        if not notebooks:
             ctk.CTkLabel(self.notebooks_frame, text="No notebooks yet", font=self.master.get_font(-3), text_color=self.colors['secondary_text']).pack(anchor="w", padx=10)
        else:
            for name in notebooks:
                display_name = self.master.truncate_text(name)
                btn = ctk.CTkButton(self.notebooks_frame, text=f"📓 {display_name}", 
                                    command=lambda n=name: self.open_notebook(n),
                                    fg_color="transparent", hover_color=self.colors['sidebar_hover'], 
                                    anchor="w", height=30, font=self.master.get_font(-2), text_color=self.colors['sidebar_text'])
                btn.pack(fill="x", pady=1)

    def open_notebook(self, name):
        # Switch to Notebooks view and select the notebook
        self.notebooks_cb(name)
        # Ideally, we'd pass the notebook name to the view, but we'll implement that later
        # by storing 'selected_notebook' in the app state or similar.

    def start_quote_timer(self):
        self.update_quote()
        # Timer logic would go here, using self.after
        # For now, simple rotation
        timer_interval = self.data_manager.get_settings().get("quote_timer", 30) * 1000
        self.after(timer_interval, self.start_quote_timer)

    def update_quote(self):
        quotes = self.data_manager.get_settings().get("quotes", [])
        if not quotes:
            quotes = ["The only way to do great work is to love what you do.", "Believe you can and you're halfway there.", "Success is not final, failure is not fatal."]
        
        import random
        quote = random.choice(quotes)
        self.lbl_quote.configure(text=f'"{quote}"')

class HomeView:
    TEMPLATES = {
        "Cornell Notes": "Title: ___\n\nQuestion/Keyword\n-\n-\n\nNotes\n-\n-\n\nSummary\n-\n_",
        "Main Idea & Details": "Main Idea: ___\n\nDetail 1:\n-\n\nDetail 2:\n-\n\nDetail 3:\n-\n\nSummary:\n-",
        "Modified Frayer Model": "Definition:\n-\n\nCharacteristics:\n-\n\nExamples:\n-\n\nNon-Examples:\n-",
        "Polya's 4 Steps": "1. Understand the Problem:\n-\n\n2. Devise a Plan:\n-\n\n3. Carry Out the Plan:\n-\n\n4. Look Back:\n-",
        "5W1H": "Who:\n-\n\nWhat:\n-\n\nWhen:\n-\n\nWhere:\n-\n\nWhy:\n-\n\nHow:\n-",
        "Concept Map": "Central Concept:\n-\n\nRelated Concept 1:\n-\n\nRelated Concept 2:\n-\n\nConnections:\n-"
    }

    def __init__(self, master, data_manager, colors):
        self.master = master
        self.data_manager = data_manager
        self.colors = colors
        
        # Load custom templates
        custom_templates = data_manager.get_settings().get("custom_templates", {})
        self.TEMPLATES.update(custom_templates)
        
        # Main container with two columns
        self.container = ctk.CTkFrame(master, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left Column: Write Frame (70% width)
        self.write_frame = ctk.CTkFrame(self.container, fg_color=colors['card_bg'], corner_radius=15)
        self.write_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Right Column: Notes List (30% width)
        self.notes_frame = ctk.CTkFrame(self.container, fg_color=colors['card_bg'], corner_radius=15, width=300)
        self.notes_frame.pack(side="right", fill="y", padx=(10, 0))
        
        self._setup_write_ui()
        self._setup_notes_ui()

    def _setup_write_ui(self):
        # Header
        header = ctk.CTkFrame(self.write_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(header, text="Write", font=self.master.master.get_font(6, "bold"), text_color=self.colors['main_text']).pack(side="left")
        
        # Controls Row
        self.controls_frame = ctk.CTkFrame(self.write_frame, fg_color="transparent")
        self.controls_frame.pack(fill="x", padx=20, pady=(0, 10))
        controls = self.controls_frame
        
        # Assign to
        ctk.CTkLabel(controls, text="Assign to:", font=self.master.master.get_font(-2), text_color=self.colors['main_text']).pack(side="left", padx=(0, 5))
        self.notebook_var = ctk.StringVar(value="• Unassigned Notes")
        self.update_notebook_dropdown()
        
        # Template
        ctk.CTkLabel(controls, text="Template:", font=self.master.master.get_font(-2), text_color=self.colors['main_text']).pack(side="left", padx=(0, 5))
        self.template_var = ctk.StringVar(value="Select...")
        templates = ["Select..."] + list(self.TEMPLATES.keys())
        self.template_dropdown = ctk.CTkOptionMenu(controls, variable=self.template_var, values=templates,
                                                   command=self.insert_template,
                                                   fg_color=self.colors['primary'], button_color=self.colors['primary_dark'],
                                                   text_color="white", width=150)
        self.template_dropdown.pack(side="left")
        
        # Save Button
        ctk.CTkButton(controls, text="Save Note", command=self.save_note,
                      fg_color=self.colors['success'], hover_color='#219150', text_color="white", width=100).pack(side="right")
                      
        # Clear Button
        ctk.CTkButton(controls, text="Clear", command=self.clear_write_area,
                      fg_color=self.colors['danger'], hover_color='#c0392b', text_color="white", width=80).pack(side="right", padx=(0, 10))
        
        # Title Entry
        self.title_entry = ctk.CTkEntry(self.write_frame, placeholder_text="Note Title (Required)", 
                                        font=self.master.master.get_font(0, "bold"), height=40,
                                        fg_color=self.colors['background'], text_color=self.colors['main_text'], border_width=0)
        self.title_entry.pack(fill="x", padx=20, pady=(0, 10))

        # Text Area
        self.text_area = ctk.CTkTextbox(self.write_frame, font=self.master.master.get_font(-2), 
                                        fg_color=self.colors['background'], text_color=self.colors['main_text'],
                                        wrap="word", corner_radius=10)
        self.text_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    def update_notebook_dropdown(self):
        # Add bullets to notebook names and truncate
        self.notebook_map = {} # Map display name -> full name
        notebook_list = []
        
        for name in self.data_manager.get_notebooks().keys():
            display_name = f"• {self.master.master.truncate_text(name)}"
            notebook_list.append(display_name)
            self.notebook_map[display_name] = name
            
        notebooks = ["+ Create new notebook...", "• Unassigned Notes"] + notebook_list
        
        if hasattr(self, 'notebook_dropdown'):
            self.notebook_dropdown.configure(values=notebooks)
            
            current_val = self.notebook_var.get()
            # Ensure current selection is valid format
            if current_val not in notebooks:
                # Try to find it with bullet/truncated
                # This is tricky if we don't know the full name of current selection easily
                # But usually we set it explicitly.
                # Let's just default to Unassigned if invalid
                self.notebook_var.set("• Unassigned Notes")
        else:
            self.notebook_dropdown = ctk.CTkOptionMenu(self.controls_frame, variable=self.notebook_var, values=notebooks,
                                                       command=self.handle_notebook_selection,
                                                       fg_color=self.colors['primary'], button_color=self.colors['primary_dark'],
                                                       text_color="white", width=180)
            self.notebook_dropdown.pack(side="left", padx=(0, 20))

    def _setup_notes_ui(self):
        # Header
        ctk.CTkLabel(self.notes_frame, text="Unassigned Notes", font=self.master.master.get_font(2, "bold"), 
                     text_color=self.colors['main_text']).pack(pady=(20, 10), padx=20, anchor="w")
        
        # Search Bar
        search_frame = ctk.CTkFrame(self.notes_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search notes...", 
                                         fg_color=self.colors['background'], text_color=self.colors['main_text'],
                                         height=30)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.filter_notes)
        
        # Filter Emoji
        ctk.CTkLabel(search_frame, text="🔍", font=self.master.master.get_font(0), text_color=self.colors['secondary_text']).pack(side="right", padx=(5, 0))
        
        # Scrollable List
        self.notes_list = ctk.CTkScrollableFrame(self.notes_frame, fg_color="transparent")
        self.notes_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.refresh_notes_list()
        
    def filter_notes(self, event=None):
        self.refresh_notes_list()

    def insert_template(self, template_name):
        if template_name in self.TEMPLATES:
            content = self.TEMPLATES[template_name]
            current_text = self.text_area.get("1.0", "end-1c")
            
            if len(current_text.strip()) > 0:
                self.text_area.insert("end", "\n\n" + content)
            else:
                self.text_area.insert("1.0", content)
            
            # Reset dropdown
            self.template_var.set("Select...")

    def handle_notebook_selection(self, selection):
        if selection == "+ Create new notebook...":
            # Open dialog
            CreateNotebookDialog(self.master, self.data_manager, self.colors, self.on_notebook_created)
            # Reset dropdown temporarily until created or cancelled
            self.notebook_var.set("• Unassigned Notes")

    def on_notebook_created(self, new_notebook_name):
        self.update_notebook_dropdown()
        # Find the display name for this new notebook
        display_name = f"• {self.master.master.truncate_text(new_notebook_name)}"
        self.notebook_var.set(display_name)
        # Also refresh sidebar
        if isinstance(self.master.master, CourseMateRevampApp):
             self.master.master.sidebar.refresh_notebooks_list()
             self.master.master.sidebar.refresh_stats()

    def clear_write_area(self):
        if not self.text_area.get("1.0", "end-1c").strip() and not self.title_entry.get().strip():
            return # Already empty
            
        if messagebox.askyesno("Clear Note", "Are you sure you want to clear the current note?"):
            self.title_entry.delete(0, "end")
            self.text_area.delete("1.0", "end")
            self.notebook_var.set("• Unassigned Notes")
            self.template_var.set("Select...")

    def save_note(self):
        title = self.title_entry.get().strip()
        content = self.text_area.get("1.0", "end-1c").strip()
        assigned_notebook = self.notebook_var.get()
        
        if not title:
            messagebox.showwarning("Missing Title", "A title is required to save the note.")
            return
        
        # Content can be empty if title is present? User said "No title, no saving". Didn't explicitly say content is required, but usually it is.
        # Let's allow empty content if title is there, or maybe just warn.
        # "The first three words of the text. If none, then leave it blank." implies content can be empty.
        
        # Resolve full notebook name
        if assigned_notebook in self.notebook_map:
            clean_notebook_name = self.notebook_map[assigned_notebook]
        else:
            clean_notebook_name = assigned_notebook.replace("• ", "") # Fallback
            
        # Check for duplicate title
        if self.data_manager.note_exists(clean_notebook_name, title):
            messagebox.showwarning("Duplicate Title", f"A note with the title '{title}' already exists in '{assigned_notebook}'.")
            return
        
        note = {
            "title": title,
            "content": content,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "notebook": clean_notebook_name if assigned_notebook != "• Unassigned Notes" else None
        }
        
        if assigned_notebook != "• Unassigned Notes" and assigned_notebook != "+ Create new notebook...":
            self.data_manager.add_note_to_notebook(clean_notebook_name, note)
            messagebox.showinfo("Saved", f"Note saved to '{clean_notebook_name}'")
        else:
            self.data_manager.add_unassigned_note(note)
            self.refresh_notes_list()
            
        # Clear inputs
        self.title_entry.delete(0, "end")
        self.text_area.delete("1.0", "end")
        self.notebook_var.set("• Unassigned Notes")
        
        # Refresh sidebar stats
        if isinstance(self.master.master, CourseMateRevampApp):
             self.master.master.sidebar.refresh_stats()

    def refresh_notes_list(self):
        for widget in self.notes_list.winfo_children():
            widget.destroy()
            
        notes = self.data_manager.get_unassigned_notes()
        search_term = self.search_entry.get().lower().strip() if hasattr(self, 'search_entry') else ""
        
        if not notes:
            ctk.CTkLabel(self.notes_list, text="No unassigned notes", font=self.master.master.get_font(-2, "italic"), 
                         text_color=self.colors['secondary_text']).pack(pady=20)
            return

        # Filter and Sort (Newest first)
        filtered_notes = []
        for note in reversed(notes):
            if search_term:
                if search_term in note.get('title', '').lower() or search_term in note.get('content', '').lower():
                    filtered_notes.append(note)
            else:
                filtered_notes.append(note)
                
        if not filtered_notes and search_term:
             ctk.CTkLabel(self.notes_list, text="No matches found", font=self.master.master.get_font(-2, "italic"), 
                         text_color=self.colors['secondary_text']).pack(pady=20)
             return

        for note in filtered_notes:
            self._create_note_card(note)

    def _create_note_card(self, note):
        card = ctk.CTkFrame(self.notes_list, fg_color=self.colors['background'], corner_radius=8)
        card.pack(fill="x", pady=5)
        
        # Click event to open note
        card.bind("<Button-1>", lambda e, n=note: self.open_note_window(n))
        
        title = note.get('title', 'Untitled')
        
        # Date formatting: "Nov 23"
        try:
            created_dt = datetime.strptime(note.get('created', ''), "%Y-%m-%d %H:%M")
            date_str = created_dt.strftime("%b %d")
        except:
            date_str = note.get('created', '').split(' ')[0]
            
        # Preview: First 3 words
        content_words = note.get('content', '').split()
        preview_text = " ".join(content_words[:3]) if content_words else ""
        
        # Row 1: Title
        lbl_title = ctk.CTkLabel(card, text=title, font=self.master.master.get_font(-1, "bold"), text_color=self.colors['main_text'], anchor="w")
        lbl_title.pack(fill="x", padx=10, pady=(5, 0))
        lbl_title.bind("<Button-1>", lambda e, n=note: self.open_note_window(n))
        
        # Row 2: Date | Preview
        meta_text = f"{date_str} | {preview_text}"
        lbl_meta = ctk.CTkLabel(card, text=meta_text, font=self.master.master.get_font(-3), text_color=self.colors['secondary_text'], anchor="w")
        lbl_meta.pack(fill="x", padx=10, pady=(0, 5))
        lbl_meta.bind("<Button-1>", lambda e, n=note: self.open_note_window(n))

    def open_note_window(self, note):
        # Open note in new window
        NoteWindow(self.master, note, self.colors, self.data_manager, self.refresh_notes_list)

class NoteWindow(ctk.CTkToplevel):
    def __init__(self, master, note, colors, data_manager, callback):
        super().__init__(master)
        self.title(note.get('title', 'Note'))
        self.geometry("600x600")
        
        self.colors = colors
        self.note = note
        self.data_manager = data_manager
        self.callback = callback
        
        # Make modal and stay on top
        self.transient(master)
        self.grab_set()
        self.focus_force()
        
        # Use master's font helper if available
        get_font = master.master.get_font if hasattr(master.master, 'get_font') else lambda s=0, w="normal": ("Helvetica", 14+s, w)
        
        # Title
        # Title
        self.title_label = ctk.CTkLabel(self, text=note.get('title', 'Untitled'), font=get_font(6, "bold"), text_color=colors['main_text'])
        self.title_label.pack(pady=20, padx=20, anchor="w")
        
        # Content
        self.text_area = ctk.CTkTextbox(self, font=get_font(-2), fg_color=colors['background'], text_color=colors['main_text'], wrap="word")
        self.text_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.text_area.insert("1.0", note.get('content', ''))
        
        # Actions Frame
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=20)
        
        # Save Button
        ctk.CTkButton(actions_frame, text="Save Changes", command=self.save_changes, fg_color=colors['success'], text_color="white").pack(side="left", padx=(0, 10))
        
        # Delete Button
        ctk.CTkButton(actions_frame, text="Delete Note", command=self.delete_note, fg_color=colors['danger'], text_color="white").pack(side="right")
        
        # Rename Button
        ctk.CTkButton(actions_frame, text="Rename Title", command=self.rename_note, fg_color=colors['info'], text_color="white").pack(side="right", padx=(0, 10))
        
        # Move to Notebook
        move_frame = ctk.CTkFrame(self, fg_color="transparent")
        move_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(move_frame, text="Move to:", font=get_font(-2), text_color=colors['main_text']).pack(side="left", padx=(0, 5))
        
        self.notebook_var = ctk.StringVar(value="Select Notebook...")
        
        self.notebook_map = {}
        notebook_list = []
        for name in self.data_manager.get_notebooks().keys():
            display_name = master.master.truncate_text(name)
            notebook_list.append(display_name)
            self.notebook_map[display_name] = name
            
        notebooks = notebook_list
        if not notebooks:
            notebooks = ["No Notebooks"]
            
        self.notebook_dropdown = ctk.CTkOptionMenu(move_frame, variable=self.notebook_var, values=notebooks,
                                                   fg_color=colors['primary'], button_color=colors['primary_dark'],
                                                   text_color="white")
        self.notebook_dropdown.pack(side="left", padx=(0, 10))

        # Move Button
        ctk.CTkButton(move_frame, text="Move", command=self.move_note, width=60,
                      fg_color=colors['info'], text_color="white").pack(side="left")

    def rename_note(self):
        new_title = simpledialog.askstring("Rename Note", "Enter new title:", initialvalue=self.note.get('title', ''), parent=self)
        if new_title and new_title.strip():
             self.note['title'] = new_title.strip()
             self.title(self.note['title'])
             # Update title label
             for widget in self.winfo_children():
                 if isinstance(widget, ctk.CTkLabel) and widget.cget("text") == self.note.get('title', ''): # Tricky to find exact label without ref
                     # Let's just recreate title label or store ref. Storing ref is better but requires init change.
                     # For now, let's just update data and save. The window title updates.
                     pass
             
             # Actually, let's store the title label in init
             if hasattr(self, 'title_label'):
                 self.title_label.configure(text=self.note['title'])
                 
             self.data_manager.save_data()
             if self.callback:
                 self.callback()


    def save_changes(self):
        new_content = self.text_area.get("1.0", "end-1c")
        self.note['content'] = new_content
        self.data_manager.save_data()
        messagebox.showinfo("Saved", "Note changes saved.")
        if self.callback:
            self.callback()

    def delete_note(self):
        if messagebox.askyesno("Delete Note", "Are you sure you want to delete this note? This cannot be undone."):
            # Try to remove from unassigned first
            unassigned = self.data_manager.get_unassigned_notes()
            if self.note in unassigned:
                unassigned.remove(self.note)
                self.data_manager.save_data()
                self.destroy()
                if self.callback:
                    self.callback()
                # Refresh sidebar stats
                if isinstance(self.master.master, CourseMateRevampApp):
                     self.master.master.sidebar.refresh_stats()
                return

            # If not in unassigned, check all notebooks
            for notebook_name, notebook_data in self.data_manager.get_notebooks().items():
                if self.note in notebook_data.get("notes", []):
                    notebook_data["notes"].remove(self.note)
                    self.data_manager.save_data()
                    self.destroy()
                    if self.callback:
                        self.callback()
                    # Refresh sidebar stats
                    if isinstance(self.master.master, CourseMateRevampApp):
                         self.master.master.sidebar.refresh_stats()
                    return
            
            messagebox.showerror("Error", "Could not find note to delete.")

    def move_note(self):
        target_display = self.notebook_var.get()
        if target_display == "Select Notebook..." or target_display == "No Notebooks":
            return
            
        target_notebook = self.notebook_map.get(target_display, target_display)
            
        if messagebox.askyesno("Move Note", f"Move this note to '{target_notebook}'?"):
            # Remove from unassigned
            unassigned = self.data_manager.get_unassigned_notes()
            if self.note in unassigned:
                unassigned.remove(self.note)
                self.data_manager.add_note_to_notebook(target_notebook, self.note)
                self.destroy()
                if self.callback: self.callback()
                if isinstance(self.master.master, CourseMateRevampApp):
                     self.master.master.sidebar.refresh_stats()
                     self.master.master.sidebar.refresh_notebooks_list()
                return

            # If not in unassigned, check all notebooks
            for notebook_name, notebook_data in self.data_manager.get_notebooks().items():
                if self.note in notebook_data.get("notes", []):
                    notebook_data["notes"].remove(self.note)
                    self.data_manager.add_note_to_notebook(target_notebook, self.note)
                    self.destroy()
                    if self.callback: self.callback()
                    if isinstance(self.master.master, CourseMateRevampApp):
                         self.master.master.sidebar.refresh_stats()
                         self.master.master.sidebar.refresh_notebooks_list()
                    return
            
            messagebox.showerror("Error", "Could not move note.")

class CreateNotebookDialog(ctk.CTkToplevel):
    def __init__(self, master, data_manager, colors, callback):
        super().__init__(master)
        self.title("Create New Notebook")
        self.geometry("400x350")
        self.data_manager = data_manager
        self.colors = colors
        self.callback = callback
        
        self.configure(fg_color=colors['background'])
        
        # Make modal and stay on top
        self.transient(master)
        self.grab_set()
        self.focus_force()
        
        # Use master's font helper
        get_font = master.master.get_font if hasattr(master.master, 'get_font') else lambda s=0, w="normal": ("Helvetica", 14+s, w)
        
        ctk.CTkLabel(self, text="New Notebook", font=get_font(4, "bold"), text_color=colors['main_text']).pack(pady=20)
        
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Notebook Name (Required)", width=300, fg_color=colors['card_bg'], text_color=colors['main_text'])
        self.name_entry.pack(pady=10)
        # self.name_entry.focus() # Moved to after() call at end of init
        
        self.code_entry = ctk.CTkEntry(self, placeholder_text="Course Code (Optional)", width=300, fg_color=colors['card_bg'], text_color=colors['main_text'])
        self.code_entry.pack(pady=10)
        
        self.instructor_entry = ctk.CTkEntry(self, placeholder_text="Instructor (Optional)", width=300, fg_color=colors['card_bg'], text_color=colors['main_text'])
        self.instructor_entry.pack(pady=10)
        
        ctk.CTkButton(self, text="Create Notebook", command=self.create, fg_color=colors['success'], text_color="white").pack(pady=20)
        
        # Bind Enter key to all inputs and window
        self.bind("<Return>", lambda e: self.create())
        self.name_entry.bind("<Return>", lambda e: self.create())
        self.code_entry.bind("<Return>", lambda e: self.create())
        self.instructor_entry.bind("<Return>", lambda e: self.create())
        
        # Ensure focus lands on name entry after window is ready
        self.after(100, self.name_entry.focus)
        
    def create(self):
        name = self.name_entry.get().strip()
        code = self.code_entry.get().strip()
        instructor = self.instructor_entry.get().strip()
        
        if not name:
            messagebox.showwarning("Required", "Notebook name is required.")
            return
            
        if len(name) > 25:
            messagebox.showwarning("Name Too Long", "Notebook name must be 25 characters or less.")
            return
            
        if self.data_manager.add_notebook(name, code, instructor):
            self.callback(name)
            self.destroy()
        else:
            messagebox.showerror("Error", "Notebook already exists!")

class NotebooksView:
    def __init__(self, master, data_manager, colors, initial_notebook=None):
        self.master = master
        self.data_manager = data_manager
        self.colors = colors
        
        self.container = ctk.CTkFrame(master, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        if initial_notebook and initial_notebook in self.data_manager.get_notebooks():
            self.show_notebook(initial_notebook)
        else:
            self.show_all_notebooks()

    def show_all_notebooks(self):
        # Clear container
        for widget in self.container.winfo_children():
            widget.destroy()
            
        # Header
        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="Your Notebooks", font=self.master.master.get_font(6, "bold"), text_color=self.colors['main_text']).pack(side="left")
        ctk.CTkButton(header, text="+ Create Notebook", command=self.add_notebook, fg_color=self.colors['success'], text_color="white").pack(side="right")
        
        # Grid Container
        self.grid_frame = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True)
        
        # Grid Layout Logic
        notebooks = self.data_manager.get_notebooks()
        if not notebooks:
             ctk.CTkLabel(self.grid_frame, text="No notebooks yet. Create one to get started!", font=self.master.master.get_font(0), text_color=self.colors['secondary_text']).pack(pady=50)
             return

        # Configure grid columns
        columns = 3
        for i in range(columns):
            self.grid_frame.grid_columnconfigure(i, weight=1)

        for i, (name, data) in enumerate(notebooks.items()):
            row = i // columns
            col = i % columns
            self._create_notebook_card(name, data, row, col)

    def _create_notebook_card(self, name, data, row, col):
        # Card Frame
        card = ctk.CTkFrame(self.grid_frame, fg_color=self.colors['card_bg'], corner_radius=15)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Make card clickable
        for widget in [card]: # We'll bind children too if needed, but frame binding usually works if children don't block
             widget.bind("<Button-1>", lambda e, n=name: self.show_notebook(n))
             widget.bind("<Enter>", lambda e, c=card: c.configure(fg_color=self.colors.get('card_hover', self.colors['sidebar_hover'])))
             widget.bind("<Leave>", lambda e, c=card: c.configure(fg_color=self.colors['card_bg']))

        # Content
        # Title
        display_name = self.master.master.truncate_text(name, 20)
        lbl_title = ctk.CTkLabel(card, text=display_name, font=self.master.master.get_font(2, "bold"), text_color=self.colors['main_text'])
        lbl_title.pack(padx=15, pady=(15, 5), anchor="w")
        lbl_title.bind("<Button-1>", lambda e, n=name: self.show_notebook(n))
        
        # Meta (Code | Instructor)
        meta = []
        if data.get("code"): meta.append(data["code"])
        if data.get("instructor"): meta.append(data["instructor"])
        meta_text = " • ".join(meta) if meta else "No details"
        
        lbl_meta = ctk.CTkLabel(card, text=meta_text, font=self.master.master.get_font(-2), text_color=self.colors['secondary_text'])
        lbl_meta.pack(padx=15, pady=(0, 10), anchor="w")
        lbl_meta.bind("<Button-1>", lambda e, n=name: self.show_notebook(n))
        
        # Stats (Note Count)
        note_count = len(data.get("notes", []))
        lbl_count = ctk.CTkLabel(card, text=f"{note_count} Notes", font=self.master.master.get_font(-2, "bold"), text_color=self.colors['accent'])
        lbl_count.pack(padx=15, pady=(0, 15), anchor="w")
        lbl_count.bind("<Button-1>", lambda e, n=name: self.show_notebook(n))

        # Actions Row
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(actions_frame, text="Rename", width=60, height=25, 
                      command=lambda n=name: self.rename_notebook(n),
                      fg_color=self.colors['info'], font=self.master.master.get_font(-3)).pack(side="left", padx=(0, 5), expand=True, fill="x")
                      
        ctk.CTkButton(actions_frame, text="Delete", width=60, height=25, 
                      command=lambda n=name: self.delete_notebook(n),
                      fg_color=self.colors['danger'], font=self.master.master.get_font(-3)).pack(side="right", padx=(5, 0), expand=True, fill="x")

    def show_notebook(self, name):
        self.selected_notebook = name
        
        # Clear container
        for widget in self.container.winfo_children():
            widget.destroy()
            
        # Header
        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        # Back Button
        ctk.CTkButton(header, text="← Back", width=60, command=self.show_all_notebooks, 
                      fg_color="transparent", text_color=self.colors['main_text'], hover_color=self.colors['sidebar_hover']).pack(side="left", padx=(0, 10))
        
        # Title
        ctk.CTkLabel(header, text=name, font=self.master.master.get_font(6, "bold"), text_color=self.colors['main_text']).pack(side="left")
        
        # Actions
        ctk.CTkButton(header, text="Delete", width=80, command=self.delete_notebook,
                      fg_color=self.colors['danger'], text_color="white").pack(side="right", padx=5)
        ctk.CTkButton(header, text="Rename", width=80, command=self.rename_notebook,
                      fg_color=self.colors['info'], text_color="white").pack(side="right", padx=5)
        
        # Notes List
        self.notes_area = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        self.notes_area.pack(fill="both", expand=True)
        
        notes = self.data_manager.get_notebooks()[name].get('notes', [])
        
        if not notes:
            ctk.CTkLabel(self.notes_area, text="No notes in this notebook", font=self.master.master.get_font(-2, "italic"), text_color=self.colors['secondary_text']).pack(pady=50)
        else:
            for i, note in enumerate(notes):
                self._create_note_item(note, i)

    def _create_note_item(self, note, index):
        card = ctk.CTkFrame(self.notes_area, fg_color=self.colors['card_bg'], corner_radius=10)
        card.pack(fill="x", pady=5)
        
        # Header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(header, text=note.get('title', 'Untitled'), font=self.master.master.get_font(0, "bold"), text_color=self.colors['main_text']).pack(side="left")
        ctk.CTkLabel(header, text=note.get('created', ''), font=self.master.master.get_font(-3), text_color=self.colors['secondary_text']).pack(side="left", padx=10)
        
        # Delete Note Button
        ctk.CTkButton(header, text="×", width=30, height=20, command=lambda: self.delete_note(index),
                      fg_color="transparent", hover_color=self.colors['danger'], text_color=self.colors['danger']).pack(side="right")
        
        # Preview
        preview = note.get('content', '')[:100].replace('\n', ' ') + "..."
        ctk.CTkLabel(card, text=preview, font=self.master.master.get_font(-2), text_color=self.colors['main_text'], anchor="w").pack(fill="x", padx=15, pady=(0, 10))
        
        # Open Button
        ctk.CTkButton(card, text="Open Note", command=lambda: self.open_note(note),
                      fg_color=self.colors['primary'], height=25, font=self.master.master.get_font(-3)).pack(fill="x", padx=15, pady=(0, 10))

    def add_notebook(self):
        # Open dialog
        CreateNotebookDialog(self.master, self.data_manager, self.colors, self.on_notebook_created)
        
    def on_notebook_created(self, name):
        self.show_all_notebooks()
        # Update sidebar
        if isinstance(self.master.master, CourseMateRevampApp):
            self.master.master.sidebar.refresh_notebooks_list()
            self.master.master.sidebar.refresh_stats()

    def rename_notebook(self, notebook_name=None):
        target = notebook_name or self.selected_notebook
        if not target: return
        
        new_name = simpledialog.askstring("Rename", "Enter new name:", initialvalue=target)
        if new_name and new_name.strip() and new_name != target:
            if len(new_name.strip()) > 25:
                messagebox.showwarning("Name Too Long", "Notebook name must be 25 characters or less.")
                return
                
            if self.data_manager.rename_notebook(target, new_name.strip()):
                if self.selected_notebook == target:
                    self.selected_notebook = new_name.strip()
                    self.show_notebook(self.selected_notebook) # Refresh single view
                else:
                    self.show_all_notebooks() # Refresh grid view
                    
                # Update sidebar
                if isinstance(self.master.master, CourseMateRevampApp):
                    self.master.master.sidebar.refresh_notebooks_list()
            else:
                messagebox.showwarning("Error", "Name already exists or invalid!")

    def delete_notebook(self, notebook_name=None):
        target = notebook_name or self.selected_notebook
        if not target: return
        
        if messagebox.askyesno("Delete", f"Delete notebook '{target}' and all its notes?"):
            self.data_manager.delete_notebook(target)
            
            if self.selected_notebook == target:
                self.selected_notebook = None
                self.show_all_notebooks()
            else:
                self.show_all_notebooks()
                
            # Update sidebar
            if isinstance(self.master.master, CourseMateRevampApp):
                self.master.master.sidebar.refresh_notebooks_list()
                self.master.master.sidebar.refresh_stats()

    def delete_note(self, index):
        if not self.selected_notebook: return
        if messagebox.askyesno("Delete Note", "Are you sure you want to delete this note?"):
            self.data_manager.delete_note(self.selected_notebook, index)
            self.show_notebook(self.selected_notebook) # Refresh list
            # Update sidebar stats
            if isinstance(self.master.master, CourseMateRevampApp):
                self.master.master.sidebar.refresh_stats()

    def open_note(self, note):
        NoteWindow(self.master, note, self.colors, self.data_manager, lambda: self.show_notebook(self.selected_notebook))

class SettingsView:
    def __init__(self, master, data_manager, colors):
        self.master = master
        self.data_manager = data_manager
        self.colors = colors
        self.settings = data_manager.get_settings()
        
        self.container = ctk.CTkScrollableFrame(master, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(self.container, text="Settings", font=master.master.get_font(10, "bold"), text_color=colors['main_text']).pack(anchor="w", pady=(0, 20))
        
        self._setup_appearance_section()
        self._setup_inspiration_section()
        self._setup_templates_section()

    def _setup_appearance_section(self):
        frame = ctk.CTkFrame(self.container, fg_color=self.colors['card_bg'], corner_radius=10)
        frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(frame, text="Appearance", font=self.master.master.get_font(2, "bold"), text_color=self.colors['main_text']).pack(anchor="w", padx=20, pady=15)
        
        # Theme
        row1 = ctk.CTkFrame(frame, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(row1, text="Theme Color:", font=self.master.master.get_font(-2), text_color=self.colors['main_text']).pack(side="left")
        
        self.theme_var = ctk.StringVar(value=self.settings.get("theme", "CourseMate Theme"))
        themes = list(THEMES.keys())
        ctk.CTkOptionMenu(row1, variable=self.theme_var, values=themes, command=self.change_theme,
                          fg_color=self.colors['primary'], button_color=self.colors['primary_dark']).pack(side="right")
        
        # Font Family
        row2 = ctk.CTkFrame(frame, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(row2, text="Font Style:", font=self.master.master.get_font(-2), text_color=self.colors['main_text']).pack(side="left")
        
        self.font_var = ctk.StringVar(value=self.settings.get("font_family", "Helvetica"))
        fonts = ["Helvetica", "Times New Roman", "Courier New", "Alice", "Open Sans", "Roboto Mono"]
        ctk.CTkOptionMenu(row2, variable=self.font_var, values=fonts, command=lambda v: self.update_setting("font_family", v),
                          fg_color=self.colors['primary'], button_color=self.colors['primary_dark']).pack(side="right")

        # Font Size
        row3 = ctk.CTkFrame(frame, fg_color="transparent")
        row3.pack(fill="x", padx=20, pady=(5, 20))
        ctk.CTkLabel(row3, text="Font Size:", font=self.master.master.get_font(-2), text_color=self.colors['main_text']).pack(side="left")
        
        self.size_var = ctk.StringVar(value=self.settings.get("font_size", "Normal"))
        sizes = ["Normal", "Large"]
        ctk.CTkOptionMenu(row3, variable=self.size_var, values=sizes, command=lambda v: self.update_setting("font_size", v),
                          fg_color=self.colors['primary'], button_color=self.colors['primary_dark']).pack(side="right")

    def _setup_inspiration_section(self):
        frame = ctk.CTkFrame(self.container, fg_color=self.colors['card_bg'], corner_radius=10)
        frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(frame, text="Inspiration & Quotes", font=self.master.master.get_font(2, "bold"), text_color=self.colors['main_text']).pack(anchor="w", padx=20, pady=15)
        
        # Timer
        row1 = ctk.CTkFrame(frame, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(row1, text="Change Quote Every (seconds):", font=self.master.master.get_font(-2), text_color=self.colors['main_text']).pack(side="left")
        
        self.timer_entry = ctk.CTkEntry(row1, width=60, fg_color=self.colors['background'], text_color=self.colors['main_text'])
        self.timer_entry.insert(0, str(self.settings.get("quote_timer", 30)))
        self.timer_entry.pack(side="left", padx=10)
        
        ctk.CTkButton(row1, text="Save Timer", width=80, command=self.save_timer,
                      fg_color=self.colors['info']).pack(side="left")
        
        # Add Quote
        row2 = ctk.CTkFrame(frame, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=(15, 5))
        ctk.CTkLabel(row2, text="Add New Quote:", font=self.master.master.get_font(-2), text_color=self.colors['main_text']).pack(anchor="w")
        
        self.quote_entry = ctk.CTkEntry(row2, placeholder_text="Enter a favorite quote...", fg_color=self.colors['background'], text_color=self.colors['main_text'])
        self.quote_entry.pack(fill="x", pady=5)
        
        ctk.CTkButton(row2, text="Add Quote", command=self.add_quote,
                      fg_color=self.colors['success']).pack(anchor="e", pady=5)

    def _setup_templates_section(self):
        frame = ctk.CTkFrame(self.container, fg_color=self.colors['card_bg'], corner_radius=10)
        frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(frame, text="Custom Templates", font=self.master.master.get_font(2, "bold"), text_color=self.colors['main_text']).pack(anchor="w", padx=20, pady=15)
        
        ctk.CTkLabel(frame, text="Create your own templates for the Home screen.", font=self.master.master.get_font(-2), text_color=self.colors['secondary_text']).pack(anchor="w", padx=20)
        
        # Add Template Button
        ctk.CTkButton(frame, text="+ Create New Template", command=self.create_template,
                      fg_color=self.colors['primary'], height=35).pack(padx=20, pady=20, fill="x")

    def update_setting(self, key, value):
        self.data_manager.update_setting(key, value)
        # Apply settings immediately
        if isinstance(self.master.master.master, CourseMateRevampApp):
             self.master.master.master.apply_settings()
        elif isinstance(self.master.master, CourseMateRevampApp):
             self.master.master.apply_settings()
        else:
            messagebox.showinfo("Settings Saved", f"{key.replace('_', ' ').title()} updated! Restart app to see full changes.")

    def change_theme(self, new_theme):
        self.data_manager.update_setting("theme", new_theme)
        # Apply settings immediately
        if isinstance(self.master.master.master, CourseMateRevampApp): 
            self.master.master.master.apply_settings()
        elif isinstance(self.master.master, CourseMateRevampApp):
             self.master.master.apply_settings()
        else:
             print("Could not find App instance to apply theme")
             messagebox.showinfo("Theme Saved", "Theme saved! Restart to apply (Dynamic update failed).")

    def save_timer(self):
        try:
            val = int(self.timer_entry.get())
            if val < 5:
                messagebox.showwarning("Invalid", "Timer must be at least 5 seconds.")
                return
            self.data_manager.update_setting("quote_timer", val)
            messagebox.showinfo("Saved", "Quote timer updated.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")

    def add_quote(self):
        quote = self.quote_entry.get().strip()
        if quote:
            quotes = self.settings.get("quotes", [])
            quotes.append(quote)
            self.data_manager.update_setting("quotes", quotes)
            self.quote_entry.delete(0, "end")
            messagebox.showinfo("Success", "Quote added to your collection!")
        else:
            messagebox.showwarning("Empty", "Please enter a quote.")

    def create_template(self):
        # Simple dialog to add a template
        # Ideally this would be a full editor, but for now we'll use simple dialogs
        name = simpledialog.askstring("New Template", "Template Name:")
        if not name: return
        
        content = simpledialog.askstring("New Template", "Template Content (use \\n for new lines):")
        if not content: return
        
        # We need to add this to the HomeView TEMPLATES
        # Since TEMPLATES is a class attribute, we can modify it, but it won't persist across restarts unless we save it to JSON
        # The current DataManager doesn't have a 'templates' key.
        # We should probably add it.
        
        # For now, let's just save it to the class attribute and warn user it's temporary
        # OR better, let's add 'custom_templates' to DataManager.
        
        # Let's add it to DataManager on the fly
        custom_templates = self.settings.get("custom_templates", {})
        
        # Check for duplicates
        if name in custom_templates or name in HomeView.TEMPLATES:
            messagebox.showerror("Error", "Template name already exists!")
            return
            
        custom_templates[name] = content.replace("\\n", "\n")
        self.data_manager.update_setting("custom_templates", custom_templates)
        
        # Update HomeView
        HomeView.TEMPLATES.update(custom_templates)
        messagebox.showinfo("Success", "Template added! It will appear in the dropdown.")


if __name__ == "__main__":
    app = CourseMateRevampApp()
    app.mainloop()
