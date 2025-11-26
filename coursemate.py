import customtkinter as ctk
import json
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog
import re
from tags_utils import extract_hashtags_from_text


# ------------------------
# Tag utilities
# ------------------------
def _normalize_token(text: str) -> str:
    """Return a normalized token for a tag (no '#', lowercase, hyphen-joined).

    Examples:
      'Cornell Notes' -> 'cornell-notes'
      '#Main Idea & Details' -> 'main-idea-details'
    """
    if not text:
        return ""
    # Remove any non-alphanumeric characters except spaces, lowercase
    cleaned = re.sub(r'[^0-9a-zA-Z ]+', '', str(text)).strip().lower()
    if not cleaned:
        return ""
    parts = [p for p in cleaned.split() if p]
    return '-'.join(parts)


def sanitize_tags_from_text(text: str) -> list:
    """Turn a comma separated tags string into a sanitized list of tags.

    Returns canonical form including leading '#', no duplicates, order preserved.
    """
    if not text:
        return []
    pieces = [p.strip() for p in text.split(',')]
    out = []
    seen = set()
    for p in pieces:
        if not p:
            continue
        # Remove leading '#' for normalization
        bare = p.lstrip('#').strip()
        token = _normalize_token(bare)
        if not token:
            continue
        if token in seen:
            continue
        seen.add(token)
        out.append('#' + token)
    return out


# ------------------------
# Hashtag highlighting helpers
# ------------------------
def _get_underlying_text_widget(ctk_textbox):
    """Try to find the underlying tk.Text widget for a CTkTextbox.
    CTkTextbox implementations vary; try several common attribute names then fall back to the object itself.
    """
    if ctk_textbox is None:
        return None
    # Common internal attribute names used by CTkTextbox wrappers
    candidates = ['_text', 'textbox', 'text', 'text_widget', '_textbox', '_text_widget']
    for a in candidates:
        if hasattr(ctk_textbox, a):
            candidate = getattr(ctk_textbox, a)
            # Most likely candidate will be a tk.Text instance
            if isinstance(candidate, tk.Text):
                return candidate
    # If the provided object is itself a tk.Text, return it
    if isinstance(ctk_textbox, tk.Text):
        return ctk_textbox
    return None


def highlight_hashtags_in_textbox(ctk_textbox, fg_color="#4a90e2"):
    """Highlight hashtag ranges in a CTkTextbox (falls back gracefully if internals differ).

    This will add a 'hashtag' tag colored with fg_color over any '#token' occurrences.
    """
    tk_text = _get_underlying_text_widget(ctk_textbox)
    if tk_text is None:
        return
    try:
        # Remove any previous ranges for this tag and configure appearance
        try:
            tk_text.tag_remove('hashtag', '1.0', 'end')
        except Exception:
            pass
        try:
            tk_text.tag_configure('hashtag', foreground=fg_color)
        except Exception:
            pass

        content = tk_text.get('1.0', 'end-1c')
        for m in re.finditer(r"#([0-9A-Za-z_-]+)", content):
            s = m.start()
            e = m.end()
            # Convert absolute char offsets into Tk text indices (line.column)
            line = content.count('\n', 0, s) + 1
            prev_nl = content.rfind('\n', 0, s)
            col = s - (prev_nl + 1) if prev_nl != -1 else s
            start_index = f"{line}.{col}"

            line_e = content.count('\n', 0, e) + 1
            prev_nl_e = content.rfind('\n', 0, e)
            col_e = e - (prev_nl_e + 1) if prev_nl_e != -1 else e
            end_index = f"{line_e}.{col_e}"

            try:
                tk_text.tag_add('hashtag', start_index, end_index)
            except Exception:
                # Some underlying widget API might reject indexes from our calc — ignore
                pass
    except Exception:
        # Be defensive: never allow tagging to break the app
        pass

def apply_visual_formatting_to_textbox(*_args, **_kwargs):
    """Formatting system removed; legacy no-op placeholder."""
    return

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
        'secondary_text':   "#a2b6c4",
        'dropdown_bg':      '#253241',
        'dropdown_text':    '#F4F4F4',
        'button_primary':   '#334a66',
        'button_text':      '#ffffff',
        'card_border':      '#c2ccd6',
        'danger':           '#e74c3c',
        'card_hover':       '#cfd8e1'
    },
    'Light Theme': {
        'primary_dark':     '#e0e0e0',
        'primary':          '#f5f5f5',
        'accent':           '#2196f3',
        'background':       '#ffffff',
        'sidebar_button':   '#f5f5f5',
        'sidebar_hover':    '#ebebeb',
        'sidebar_text':     '#0b2740',
        'card_bg':          '#f5f5f5',
        'success':          '#4caf50',
        'info':             '#2196f3',
        'warning':          '#ffeb3b',
        'muted':            '#9e9e9e',
        'header_text':      '#0b2740',
        'main_text':        '#0b2740',
        'secondary_text':   '#6b7280',
        'dropdown_bg':      '#0b2740',
        'dropdown_text':    '#ffffff',
        'button_primary':   '#1976d2',
        'button_text':      '#ffffff',
        'card_border':      '#e0e0e0',
        'danger':           '#f44336',
        'card_hover':       '#eeeeee'
    },
    'Dark Theme': {
        'primary_dark':   '#172027', 
        'primary':        '#253244', 
        'accent':         '#3f7fbf',  
        'background':     '#0b0f12',  
        'sidebar_button': '#253244', 
        'sidebar_hover':  '#2d4358', 
        'sidebar_text':   '#ffffff',
        'card_bg':        '#1a2631',  
        'success':        '#27ae60',  
        'info':           '#3498db',  
        'warning':        '#cf6679',
        'muted':          '#9aa6b1',
        'header_text':    '#ffffff',
        'main_text':      '#e6eef6',  
        'secondary_text': '#a2b6c4',  
        'dropdown_bg':    '#253244',  
        'dropdown_text':  '#ffffff',
        'button_primary': '#3f7fbf',
        'button_text':    '#ffffff',
        'card_border':    '#2d4358',
        'danger':         '#e74c3c',
        'card_hover':     '#273544'
    },
    'Baby Pink': {
        'primary_dark':     '#f8bbd0',
        'primary':          '#fce4ec',
        'accent':           '#ec407a',
        'background':       '#fff0f5',
        'sidebar_button':   '#fce4ec',
        'sidebar_hover':    '#fad7e5',
        'sidebar_text':     '#0b2740',
        'card_bg':          '#ffebee',
        'success':          '#66bb6a',
        'info':             '#42a5f5',
        'warning':          '#ffee58',
        'muted':            '#bdbdbd',
        'header_text':      '#0b2740',
        'main_text':        '#0b2740',
        'secondary_text':   '#7b1e5f',
        'dropdown_bg':      '#0b2740',
        'dropdown_text':    '#ffffff',
        'button_primary':   '#d81b60',
        'button_text':      '#ffffff',
        'card_border':      '#f8bbd0',
        'danger':           '#ef5350',
        'card_hover':       '#ffcdd2'
    },
    'Baby Blue': {
        'primary_dark':     '#b3e5fc',
        'primary':          '#e1f5fe',
        'accent':           '#29b6f6',
        'background':       '#f0f8ff',
        'sidebar_button':   '#e1f5fe',
        'sidebar_hover':    '#cdeefc',
        'sidebar_text':     '#0b2740',
        'card_bg':          '#e3f2fd',
        'success':          '#66bb6a',
        'info':             '#29b6f6',
        'warning':          '#ffee58',
        'muted':            '#bdbdbd',
        'header_text':      '#0b2740',
        'main_text':        '#0b2740',
        'secondary_text':   '#2563a8',
        'dropdown_bg':      '#0b2740',
        'dropdown_text':    '#ffffff',
        'dp_button_color':  "#ffffff",
        'button_primary':   '#0277bd',
        'button_text':      '#ffffff',
        'card_border':      '#b3e5fc',
        'danger':           '#ef5350',
        'card_hover':       '#bbdefb'
    }
}

DEFAULT_SETTINGS = {
    "theme": "CourseMate Theme",
    "font_family": "Open Sans",
    "font_size": "Normal", # Normal, Large
    "quotes": [],
    "quote_timer": 30, # seconds
    # New template category keys (will be migrated/populated in DataManager.load_data)
    "study_templates": {},
    "additional_templates": {},
    # Legacy key retained for backward compatibility; migrated into study_templates then cleared
    "custom_templates": {}
}

# Default planner / organizational templates for the new Additional Templates category
DEFAULT_ADDITIONAL_TEMPLATES = {
    "Daily Planner": "Date: \n\nTop 3 Priorities:\n1. \n2. \n3. \n\nSchedule (Hour | Task):\n08:00 - \n09:00 - \n10:00 - \n11:00 - \n12:00 - \n13:00 - \n14:00 - \n15:00 - \n16:00 - \n17:00 - \n\nTasks:\n- [ ] \n- [ ] \n- [ ] \n\nNotes:\n- ",
    "Weekly Overview": "Week Of: \n\nGoals:\n- \n- \n- \n\nMon:\nFocus: \nTasks: - [ ] \n\nTue:\nFocus: \nTasks: - [ ] \n\nWed:\nFocus: \nTasks: - [ ] \n\nThu:\nFocus: \nTasks: - [ ] \n\nFri:\nFocus: \nTasks: - [ ] \n\nWeekend Notes:\n- ",
    "Time Block Grid": "Date: \n\n| Time | Block |\n|------|-------|\n| 08:00 | \n| 09:00 | \n| 10:00 | \n| 11:00 | \n| 12:00 | Lunch |\n| 13:00 | \n| 14:00 | \n| 15:00 | \n| 16:00 | \n| 17:00 | Wrap Up |\n\nAdjustments / Reflections:\n- ",
    "Assignment Tracker": "Course: \n\n| Assignment | Due Date | Status | Notes |\n|------------|----------|--------|-------|\n|            |          |        |       |\n|            |          |        |       |\n|            |          |        |       |\n\nUpcoming Deadlines:\n- ",
    "Habit Tracker": "Month: \nHabit: \n\n| Day | Done? | Notes |\n|-----|-------|-------|\n| 1   |       |       |\n| 2   |       |       |\n| 3   |       |       |\n| 4   |       |       |\n| 5   |       |       |\n| 6   |       |       |\n| 7   |       |       |\n| 8   |       |       |\n| 9   |       |       |\n| 10  |       |       |\n| 11  |       |       |\n| 12  |       |       |\n| 13  |       |       |\n| 14  |       |       |\n| 15  |       |       |\n| 16  |       |       |\n| 17  |       |       |\n| 18  |       |       |\n| 19  |       |       |\n| 20  |       |       |\n| 21  |       |       |\n| 22  |       |       |\n| 23  |       |       |\n| 24  |       |       |\n| 25  |       |       |\n| 26  |       |       |\n| 27  |       |       |\n| 28  |       |       |\n| 29  |       |       |\n| 30  |       |       |\n| 31  |       |       |\n\nReflection:\n- "
}

# Default built-in quotes shown initially. These will be copied into persistent
# settings on first open so the user can edit/delete them.
DEFAULT_QUOTES = [
    "The only way to do great work is to love what you do. — Steve Jobs",
    "Tell me and I forget. Teach me and I remember. Involve me and I learn. — Benjamin Franklin",
    "Practice doesn't make perfect. Practice makes permanent. — Unknown",
    "Strive for progress, not perfection. — Unknown",
    "We are what we repeatedly do. Excellence, then, is not an act, but a habit. — Aristotle"
]

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
                    courses = loaded_data.get("courses", {})
                    
                    # Migrate old data structure (name-keyed) to new (code-keyed)
                    # Check if any notebook is missing the 'name' field - indicates old format
                    needs_migration = False
                    for key, nb_data in courses.items():
                        if "name" not in nb_data:
                            needs_migration = True
                            break
                    
                    if needs_migration:
                        print("Migrating notebook data to new format...")
                        migrated_courses = {}
                        for old_key, nb_data in courses.items():
                            # Old format: key=name, data has no 'name' field, may/may not have 'code'
                            code = nb_data.get("code", old_key)  # Use old key as fallback
                            name = old_key
                            # Add name field
                            nb_data["name"] = name
                            nb_data["code"] = code
                            # Store with code as key
                            migrated_courses[code] = nb_data
                        self.data["courses"] = migrated_courses
                    else:
                        self.data["courses"] = courses
                    
                    # Ensure all notebooks have a 'name' field
                    for code, nb_data in self.data["courses"].items():
                        if "name" not in nb_data or not nb_data.get("name"):
                            nb_data["name"] = code  # Use code as fallback name
                    
                    self.data["tasks"] = loaded_data.get("tasks", [])
                    self.data["completed_tasks"] = loaded_data.get("completed_tasks", [])
                    self.data["unassigned_notes"] = loaded_data.get("unassigned_notes", [])
                    
                    # Merge settings carefully
                    saved_settings = loaded_data.get("settings", {})
                    for k, v in DEFAULT_SETTINGS.items():
                        if k not in saved_settings:
                            saved_settings[k] = v

                    # --- Template Category Migration ---
                    # If legacy custom_templates exist and study_templates not yet populated, migrate.
                    legacy = saved_settings.get("custom_templates", {}) or {}
                    if legacy and not saved_settings.get("study_templates"):
                        # Initialize study_templates with legacy content
                        saved_settings["study_templates"] = dict(legacy)
                        # Clear legacy key to reduce duplication (still kept as empty for backward compatibility)
                        saved_settings["custom_templates"] = {}

                    # Ensure keys exist even if empty
                    if "study_templates" not in saved_settings:
                        saved_settings["study_templates"] = {}
                    if "additional_templates" not in saved_settings:
                        saved_settings["additional_templates"] = {}

                    # Populate default additional templates only once (if user has none)
                    if not saved_settings["additional_templates"]:
                        saved_settings["additional_templates"] = DEFAULT_ADDITIONAL_TEMPLATES.copy()

                    # Move any weekly planning template from study to planner (one-time migration)
                    move_keys = [
                        k for k in list(saved_settings.get("study_templates", {}).keys())
                        if k.lower() in ("weekly planning", "weekly planner", "weekly overview")
                    ]
                    for k in move_keys:
                        val = saved_settings["study_templates"].pop(k)
                        # Don't overwrite if target already has it
                        if k not in saved_settings["additional_templates"]:
                            saved_settings["additional_templates"][k] = val

                    self.data["settings"] = saved_settings
                    
                    # Save migrated data
                    if needs_migration:
                        self.save_data()
                    
                    # Clean up any notebooks with empty codes
                    self._cleanup_invalid_notebooks()
                    
            except Exception as e:
                print(f"Error loading data: {e}")
                # Keep default initialized data
        else:
            self.save_data() # Create file if not exists
    
    def _cleanup_invalid_notebooks(self):
        """Remove notebooks with empty or whitespace-only codes"""
        invalid_codes = [code for code in self.data["courses"].keys() if not code or not code.strip()]
        if invalid_codes:
            print(f"Cleaning up {len(invalid_codes)} invalid notebook(s)...")
            for code in invalid_codes:
                del self.data["courses"][code]
            self.save_data()

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
        # Find notebook by name and add note
        for code, nb_data in self.data["courses"].items():
            if nb_data.get("name") == notebook_name:
                nb_data["notes"].append(note)
                self.save_data()
                break

    def add_notebook(self, name, code="", instructor=""):
        # Course code is now required and must be unique (case-insensitive)
        if not code or not code.strip():
            return False, "Course code is required."
        
        code = code.strip()
        existing_codes = [nb.get("code", "").lower() for nb in self.data["courses"].values()]
        if code.lower() in existing_codes:
            return False, "A notebook with this course code already exists."
        
        # Name can be duplicate as long as course code is unique
        self.data["courses"][name] = {
            "notes": [], 
            "tasks": [],
            "code": code,
            "instructor": instructor
        }
        self.save_data()
        return True, "Notebook created successfully."

    def rename_notebook(self, old_name, new_name):
        # Find notebook by name, update its stored name
        for code, nb_data in self.data["courses"].items():
            if nb_data.get("name") == old_name:
                nb_data["name"] = new_name
                self.save_data()
                return True
        return False

    def delete_notebook(self, name):
        # Find and delete notebook by name
        for code, nb_data in list(self.data["courses"].items()):
            if nb_data.get("name") == name:
                del self.data["courses"][code]
                self.save_data()
                return True
        return False

    def note_exists(self, notebook_name, title):
        # Check unassigned
        if notebook_name is None or notebook_name == "• Unassigned Notes" or notebook_name == "Unassigned Notes":
            notes = self.data["unassigned_notes"]
        # Check assigned notebooks (find by name)
        else:
            notes = None
            for code, nb_data in self.data["courses"].items():
                if nb_data.get("name") == notebook_name:
                    notes = nb_data["notes"]
                    break
            if notes is None:
                return False
            
        # Case-insensitive title check
        for note in notes:
            if note.get("title", "").lower() == title.lower():
                return True
        return False

    def delete_note(self, notebook_name, note_index):
        # Find notebook by name and delete note
        for code, nb_data in self.data["courses"].items():
            if nb_data.get("name") == notebook_name:
                if 0 <= note_index < len(nb_data["notes"]):
                    nb_data["notes"].pop(note_index)
                    self.save_data()
                    return True
                break
        return False

# ============================================================================
# MAIN APPLICATION
# ============================================================================

class CourseMate(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Data Setup
        # Data Setup
        self.data_manager = DataManager()
        self.load_custom_fonts()
        
        # ...existing initialization continues (no app-level tag UI here)
        
        self.current_theme = self.data_manager.get_settings()["theme"]
        self.colors = THEMES.get(self.current_theme, THEMES['CourseMate Theme'])
        
        # Font State
        self.font_family = self.data_manager.get_settings().get("font_family", "Open Sans")
        self.font_size_mode = self.data_manager.get_settings().get("font_size", "Normal")
        self.base_font_size = 14 if self.font_size_mode == "Normal" else 18
        
        # Window Setup
        self.title("CourseMate: Template-Based Note-Taking & Study Aid For Students")
        self.geometry("1400x800")
        self.minsize(1400, 800)
        ctk.set_appearance_mode("System")

        # --- Window Icon ---
        # Attempt to load an application icon from assets/icons.
        # Prefer .ico on Windows (taskbar/alt-tab), but fall back to PNG if present.
        try:
            icon_dir = os.path.join(os.path.dirname(__file__), "assets", "icons")
            candidates = ["app.ico", "icon.ico", "app.png", "icon.png"]
            for ico_name in candidates:
                ico_path = os.path.join(icon_dir, ico_name)
                if os.path.exists(ico_path):
                    try:
                        if ico_path.lower().endswith('.ico'):
                            # iconbitmap is the most reliable on Windows for titlebar/taskbar icons
                            try:
                                self.iconbitmap(ico_path)
                            except Exception:
                                # Fallback to PhotoImage if iconbitmap fails for any reason
                                try:
                                    img = tk.PhotoImage(file=ico_path)
                                    # Set as default icon for all toplevels and keep a reference
                                    try:
                                        self.iconphoto(True, img)
                                    except Exception:
                                        self.iconphoto(False, img)
                                    self._icon_image = img
                                except Exception:
                                    print(f"Failed to load icon (ico fallback): {ico_path}")
                        else:
                            # Use PhotoImage for PNGs (keep a reference to avoid GC)
                            try:
                                img = tk.PhotoImage(file=ico_path)
                                # Use True so it applies to all toplevel windows
                                try:
                                    self.iconphoto(True, img)
                                except Exception:
                                    self.iconphoto(False, img)
                                self._icon_image = img
                            except Exception:
                                print(f"Failed to load icon (png): {ico_path}")
                    except Exception as e:
                        # Ignore icon loading problems; non-fatal but log for debugging
                        print(f"Icon load error: {e}")
                    break
        except Exception as e:
            print(f"Icon setup unexpected error: {e}")

        # Start maximized on Windows after initial layout completes and provide fullscreen toggle (F11) + Escape to exit
        def _maximize_after_startup():
            try:
                self.state('zoomed')  # maximizes window (works well on Windows)
            except Exception:
                pass

        # Schedule maximize shortly after init so later layout changes won't override it
        self.after(150, _maximize_after_startup)

        # Fullscreen toggle state
        self._is_fullscreen = False

        def _toggle_fullscreen(event=None):
            try:
                self._is_fullscreen = not self._is_fullscreen
                self.attributes('-fullscreen', self._is_fullscreen)
            except Exception:
                pass

        # F11 toggles fullscreen, Escape exits fullscreen
        self.bind('<F11>', _toggle_fullscreen)
        self.bind('<Escape>', lambda e: (self.attributes('-fullscreen', False), setattr(self, '_is_fullscreen', False)))
        
        # Layout Setup
        self.grid_columnconfigure(1, weight=1)
        # Reserve row 0 for a header and make the main content row (1) expandable
        self.grid_rowconfigure(1, weight=1)
        
        self.sidebar = None
        self.main_area = None
        
        self._init_ui()
        #Deafult view
        # self.show_settings()
        self.show_home() 


    def _init_ui(self):
        # Header (top, spans sidebar + main area)
        self.header = ctk.CTkFrame(self, fg_color=self.colors['primary_dark'], corner_radius=0)
        self.header.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # Header content: centered title and full slogan
        self.header_inner = ctk.CTkFrame(self.header, fg_color=self.colors['primary_dark'])
        self.header_inner.pack(fill="both", expand=True)

        self.header_title_label = ctk.CTkLabel(self.header_inner, text="CourseMate",
                 font=self.get_font(8, "bold"), text_color=self.colors['header_text'])
        self.header_title_label.pack(pady=(8, 0))

        self.header_slogan_label = ctk.CTkLabel(self.header_inner,
                 text="Stay Organized • Think Smarter • Learn Deeper • Solve Problems Better",
                 font=self.get_font(0, "bold"), text_color=self.colors['secondary_text'], wraplength=900, justify="center")
        self.header_slogan_label.pack(pady=(0, 8))

        # Header overlay quick-stats (top-left) - placed so it doesn't affect header layout
        self.header_stats_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        # place overlay at small offset from top-left
        self.header_stats_frame.place(x=8, y=8)

        self.header_lbl_notebooks_count = ctk.CTkLabel(self.header_stats_frame, text="Notebooks: 0",
                                   font=self.get_font(-2, "bold"), text_color=self.colors['header_text'])
        self.header_lbl_notebooks_count.pack(anchor="w", padx=(10, 0))

        self.header_lbl_notes_count = ctk.CTkLabel(self.header_stats_frame, text="Total Notes: 0",
                               font=self.get_font(-2, "bold"), text_color=self.colors['header_text'])
        self.header_lbl_notes_count.pack(anchor="w", padx=(10, 0))

        # Sidebar
        self.sidebar = Sidebar(self, self.data_manager, self.colors, self.show_home, self.show_notebooks, self.show_settings)
        self.sidebar.grid(row=1, column=0, sticky="nsew")

        # Main Content Area
        self.main_area = ctk.CTkFrame(self, fg_color=self.colors['background'], corner_radius=0)
        self.main_area.grid(row=1, column=1, sticky="nsew")

    def clear_main_area(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()

    def show_home(self):
        self.clear_main_area()
        self.current_view = HomeView(self.main_area, self.data_manager, self.colors, app=self)

    def show_notebooks(self, notebook_name=None):
        self.clear_main_area()
        self.current_view = NotebooksView(self.main_area, self.data_manager, self.colors, notebook_name, app=self)

    def show_settings(self):
        self.clear_main_area()
        self.current_view = SettingsView(self.main_area, self.data_manager, self.colors)

    def load_custom_fonts(self):
        # Load fonts from assets/fonts
        font_dir = os.path.join(os.path.dirname(__file__), "assets", "fonts")
        if not os.path.exists(font_dir):
            return

        # Platform-specific font loading
        import platform
        system = platform.system()
        
        if system == "Windows":
            try:
                gdi32 = ctypes.windll.gdi32
                for font_file in os.listdir(font_dir):
                    if font_file.lower().endswith((".ttf", ".otf")):
                        font_path = os.path.join(font_dir, font_file)
                        ret = gdi32.AddFontResourceExW(font_path, 0x10, 0) # FR_PRIVATE = 0x10
                        if ret == 0:
                            print(f"Failed to load font: {font_file}")
                        else:
                            print(f"Loaded font: {font_file}")
            except Exception as e:
                print(f"Font loading error: {e}")
        else:
            # On Linux/Mac, fonts need to be installed system-wide or tkinter uses system fonts
            print(f"Custom font loading not implemented for {system}. Using system fonts.")

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
        self.font_family = settings.get("font_family", "Open Sans")
        self.font_size_mode = settings.get("font_size", "Normal")
        self.base_font_size = 14 if self.font_size_mode == "Normal" else 18
        
        # Update Sidebar (keep it in row 1 so header stays in row 0)
        self.sidebar.destroy()
        self.sidebar = Sidebar(self, self.data_manager, self.colors, self.show_home, self.show_notebooks, self.show_settings)
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        
        # Update Main Area Background
        self.main_area.configure(fg_color=self.colors['background'])

        # Update Header colors so theme changes affect it too
        try:
            # Header background
            if hasattr(self, 'header') and self.header:
                try:
                    self.header.configure(fg_color=self.colors.get('primary_dark', self.colors.get('primary')))
                except Exception:
                    pass
                # Update header inner frame and labels (we store references during init)
                try:
                    if hasattr(self, 'header_inner') and self.header_inner:
                        try:
                            self.header_inner.configure(fg_color=self.colors.get('primary_dark', self.colors.get('primary')))
                        except Exception:
                            pass
                    if hasattr(self, 'header_title_label') and self.header_title_label:
                        try:
                            self.header_title_label.configure(text_color=self.colors.get('header_text'))
                        except Exception:
                            pass
                        try:
                            self.header_title_label.configure(font=self.get_font(8, "bold"))
                        except Exception:
                            pass
                    if hasattr(self, 'header_slogan_label') and self.header_slogan_label:
                        try:
                            self.header_slogan_label.configure(text_color=self.colors.get('secondary_text'))
                        except Exception:
                            pass
                        try:
                            self.header_slogan_label.configure(font=self.get_font(0, "bold"))
                        except Exception:
                            pass
                except Exception:
                    pass

                # Update header stats labels (if present)
                if hasattr(self, 'header_lbl_notebooks_count'):
                    try:
                        self.header_lbl_notebooks_count.configure(text_color=self.colors.get('header_text'))
                        self.header_lbl_notebooks_count.configure(font=self.get_font(-2, "bold"))
                    except Exception:
                        pass
                if hasattr(self, 'header_lbl_notes_count'):
                    try:
                        self.header_lbl_notes_count.configure(text_color=self.colors.get('header_text'))
                        self.header_lbl_notes_count.configure(font=self.get_font(-2, "bold"))
                    except Exception:
                        pass
        except Exception:
            pass
        
        self._update_header_fonts()
        self._update_header_stat_fonts()
        self._update_header_inspiration_controls()

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

    def _update_header_fonts(self):
        try:
            if hasattr(self, 'header_title_label') and self.header_title_label:
                self.header_title_label.configure(font=self.get_font(8, "bold"))
            if hasattr(self, 'header_slogan_label') and self.header_slogan_label:
                self.header_slogan_label.configure(font=self.get_font(0, "bold"))
        except Exception:
            pass

    def _update_header_stat_fonts(self):
        try:
            if hasattr(self, 'header_lbl_notebooks_count') and self.header_lbl_notebooks_count:
                self.header_lbl_notebooks_count.configure(font=self.get_font(-2, "bold"))
            if hasattr(self, 'header_lbl_notes_count') and self.header_lbl_notes_count:
                self.header_lbl_notes_count.configure(font=self.get_font(-2, "bold"))
        except Exception:
            pass

    def _update_header_inspiration_controls(self):
        try:
            if hasattr(self, 'inspire_label') and self.inspire_label:
                self.inspire_label.configure(font=self.get_font(2, "bold"))
        except Exception:
            pass


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
        
        # (Title moved to top header) — keep sidebar compact without duplicate title

        # Quick stats moved to top header overlay to avoid duplicate title and keep layout clean

        # Navigation (compact)
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(fill="x", pady=3)

        self._create_nav_btn("Home", home_cb)
        self._create_nav_btn("Notebooks", notebooks_cb)
        self._create_nav_btn("Settings", settings_cb)

        # Notebooks Quick Access (Scrollable with collapsible header)
        self.notebooks_visible = True
        self._nb_icon_open = "▼"
        self._nb_icon_closed = "▶"
        
        self.notebooks_header = ctk.CTkFrame(self, fg_color="transparent")
        self.notebooks_header.pack(fill="x", padx=8, pady=(6, 3))
        
        self.notebooks_label = ctk.CTkLabel(self.notebooks_header, text="NOTEBOOKS", 
                                           font=master.get_font(-2, "bold"), 
                                           text_color=colors['secondary_text'], 
                                           anchor="w")
        self.notebooks_label.pack(side="left", padx=2)
        
        self.notebooks_toggle_btn = ctk.CTkButton(
            self.notebooks_header,
            text=self._nb_icon_open,
            command=self.toggle_notebooks,
            fg_color="transparent",
            hover_color=self.colors.get('sidebar_hover'),
            width=20,
            height=20,
            text_color=self.colors.get('sidebar_text', 'white'),
            font=master.get_font(-2)
        )
        self.notebooks_toggle_btn.pack(side="right", padx=2)

        # Container to maintain size when notebooks are toggled
        self.notebooks_container = ctk.CTkFrame(self, fg_color="transparent")
        self.notebooks_container.pack(fill="both", expand=True, padx=8, pady=3)
        
        self.notebooks_frame = ctk.CTkScrollableFrame(self.notebooks_container, fg_color="transparent", height=200)
        self.notebooks_frame.pack(fill="both", expand=True)

        # Inspiration Section (collapsible)
        self.inspiration_visible = True
        self._insp_icon_open = "▼"
        self._insp_icon_closed = "▶"
        
        self.inspiration_header = ctk.CTkFrame(self, fg_color="transparent")
        self.inspiration_header.pack(side="bottom", fill="x", padx=8, pady=(3, 10))

        # Label on the left, toggle button on the right
        self.inspire_label = ctk.CTkLabel(
            self.inspiration_header,
            text="INSPIRATION",
            text_color=colors['secondary_text'],
            font=master.get_font(-2, "bold"),
            anchor="w"
        )
        self.inspire_label.pack(side="left", padx=2)
        
        self.inspire_toggle_btn = ctk.CTkButton(
            self.inspiration_header,
            text=self._insp_icon_open,
            command=self.toggle_inspiration,
            fg_color="transparent",
            hover_color=self.colors.get('sidebar_hover'),
            width=20,
            height=20,
            text_color=self.colors.get('sidebar_text', 'white'),
            font=master.get_font(-2)
        )
        self.inspire_toggle_btn.pack(side="right", padx=2)

        self.inspiration_frame = ctk.CTkFrame(self, fg_color=colors['card_bg'], corner_radius=10)
        try:
            screen_h = self.winfo_toplevel().winfo_screenheight()
        except Exception:
            screen_h = 900
        if screen_h < 850:
            self.inspiration_visible = True
        if self.inspiration_visible:
            self.inspiration_frame.pack(side="bottom", fill="x", padx=8, pady=3)

        ctk.CTkLabel(self.inspiration_frame, text="Inspiration", font=master.get_font(0, "bold"), text_color=colors['main_text']).pack(pady=3)
        # Make the sidebar quote slightly larger for readability
        self.lbl_quote = ctk.CTkLabel(self.inspiration_frame, text="Loading quote...", font=master.get_font(0, "italic"), 
                          text_color=colors['main_text'], wraplength=180)
        self.lbl_quote.pack(pady=(0, 6), padx=8)
        
        # Ensure inspiration is visible on startup so user doesn't have to click
        try:
            if not screen_h < 850:
                # Only pack if not already visible
                if not getattr(self.inspiration_frame, 'winfo_ismapped', lambda: False)():
                    self.inspiration_frame.pack(side="bottom", fill="x", padx=8, pady=3)
                self.inspiration_visible = True
        except Exception:
            pass

        # Initial Data Load
        self.refresh_stats()
        self.refresh_notebooks_list()
        self.start_quote_timer()

    def _create_nav_btn(self, text, command):
        # Use a distinct button background so these look like buttons (not labels)
        # Center the nav buttons with a fixed width so they appear compact and centered
        # Make nav buttons expand to the sidebar width and keep their text centered
        btn = ctk.CTkButton(self.nav_frame, text=text, command=command,
                    fg_color=self.colors.get('sidebar_button', self.colors['primary']), hover_color=self.colors['sidebar_hover'],
                    height=36, font=self.master.get_font(2, "bold"), text_color=self.colors.get('sidebar_text', 'white'))
        # Pack with no horizontal padding so the button spans the sidebar edge-to-edge
        btn.pack(padx=10, pady=3, fill="x")

    def refresh_stats(self):
        notebooks = self.data_manager.get_notebooks()
        total_notes = sum(len(nb.get('notes', [])) for nb in notebooks.values()) + len(self.data_manager.get_unassigned_notes())

        # Update header overlay labels if present (overlay lives on the App instance)
        app = getattr(self, 'master', None)
        if app and hasattr(app, 'header_lbl_notebooks_count'):
            try:
                app.header_lbl_notebooks_count.configure(text=f"Notebooks: {len(notebooks)}")
            except Exception:
                pass
        if app and hasattr(app, 'header_lbl_notes_count'):
            try:
                app.header_lbl_notes_count.configure(text=f"Total Notes: {total_notes}")
            except Exception:
                pass

    def refresh_notebooks_list(self):
        # Clear existing
        for widget in self.notebooks_frame.winfo_children():
            widget.destroy()
            
        notebooks = self.data_manager.get_notebooks()
        if not notebooks:
             ctk.CTkLabel(self.notebooks_frame, text="No notebooks yet", font=self.master.get_font(-1), text_color=self.colors['secondary_text']).pack(anchor="w", padx=8, pady=3)
        else:
            for code, nb_data in notebooks.items():
                name = nb_data.get("name", code)
                course_code = nb_data.get("code", "")
                
                if course_code:
                    # If code exists, show "CODE | Name..."
                    # Truncate name more aggressively to fit
                    display_name = f"{course_code} | {self.master.truncate_text(name, 15)}"
                else:
                    display_name = self.master.truncate_text(name)
                
                item_bg = self.colors.get('sidebar_button', self.colors['primary'])
                hover_bg = self.colors.get('sidebar_hover', item_bg)

                row = ctk.CTkFrame(
                    self.notebooks_frame,
                    fg_color=item_bg,
                    corner_radius=8
                )
                row.pack(fill="x", padx=4, pady=2)
                row.configure(cursor="hand2")

                label = ctk.CTkLabel(
                    row,
                    text=f"📓 {display_name}",
                    font=self.master.get_font(0),
                    text_color=self.colors.get('sidebar_text', 'white'),
                    anchor="w"
                )
                label.pack(fill="x", padx=12, pady=6)
                label.configure(cursor="hand2")

                def _open_notebook(event=None, notebook=name):
                    self.open_notebook(notebook)

                def _on_enter(event=None, frame=row, color=hover_bg):
                    frame.configure(fg_color=color)

                def _on_leave(event=None, frame=row, color=item_bg):
                    frame.configure(fg_color=color)

                row.bind("<Button-1>", _open_notebook)
                label.bind("<Button-1>", _open_notebook)
                row.bind("<Enter>", _on_enter)
                row.bind("<Leave>", _on_leave)
                label.bind("<Enter>", _on_enter)
                label.bind("<Leave>", _on_leave)

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

    def toggle_inspiration(self):
        """Show/hide the inspiration card. Useful on short screens."""
        if getattr(self, 'inspiration_visible', True):
            try:
                self.inspiration_frame.pack_forget()
            except Exception:
                pass
            self.inspiration_visible = False
        else:
            try:
                self.inspiration_frame.pack(side="bottom", fill="x", padx=8, pady=3)
            except Exception:
                pass
            self.inspiration_visible = True
        # Update toggle button icon
        icon = self._insp_icon_open if self.inspiration_visible else self._insp_icon_closed
        self.inspire_toggle_btn.configure(text=icon)
    
    def toggle_notebooks(self):
        """Show/hide the notebooks list."""
        if getattr(self, 'notebooks_visible', True):
            try:
                self.notebooks_frame.pack_forget()
            except Exception:
                pass
            self.notebooks_visible = False
        else:
            try:
                self.notebooks_frame.pack(fill="both", expand=True)
            except Exception:
                pass
            self.notebooks_visible = True
        # Update toggle button icon
        icon = self._nb_icon_open if self.notebooks_visible else self._nb_icon_closed
        self.notebooks_toggle_btn.configure(text=icon)




# Small modal dialog used for creating/editing templates
class TemplateDialog(ctk.CTkToplevel):
    def __init__(self, master, title_init="", structure_init="", on_save=None, is_edit=False):
        super().__init__(master)
        self.on_save = on_save
        self.is_edit = is_edit
        self.title("Template Editor")
        self.geometry("480x400")
        self.resizable(False, False)
        try:
            self.transient(master)
            self.grab_set()
        except Exception:
            pass

        ctk.CTkLabel(self, text="Template title:", font=("Open Sans", 12, "bold")).pack(anchor="w", padx=16, pady=(12, 4))
        self.title_entry = ctk.CTkEntry(self, placeholder_text="Enter template title", font=("Open Sans", 12))
        self.title_entry.pack(fill="x", padx=16, pady=(0, 8))
        self.title_entry.insert(0, title_init)

        ctk.CTkLabel(self, text="Template structure:", font=("Open Sans", 12, "bold")).pack(anchor="w", padx=16, pady=(0, 4))
        self.structure_text = ctk.CTkTextbox(self, font=("Open Sans", 12), height=200)
        self.structure_text.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        self.structure_text.insert("1.0", structure_init)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(0, 12))
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy).pack(side="right", padx=(8, 0))
        ctk.CTkButton(btn_frame, text="Save", command=self._on_save).pack(side="right", padx=(0, 8))

    def _on_save(self):
        title = self.title_entry.get().strip()
        structure = self.structure_text.get("1.0", "end-1c").strip()
        if not title or not structure:
            messagebox.showwarning("Invalid", "Both title and structure are required.")
            return
        if self.on_save:
            try:
                self.on_save(title, structure)
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return
        self.destroy()


# Small modal dialog for input (replaces simpledialog.askstring)
class InputDialog(ctk.CTkToplevel):
    def __init__(self, master, title, prompt, initialvalue=""):
        super().__init__(master)
        self.title(title)
        self.geometry("400x150")
        self.resizable(False, False)
        try:
            self.transient(master)
            self.grab_set()
        except Exception:
            pass

        self.result = None

        ctk.CTkLabel(self, text=prompt, font=("Open Sans", 11)).pack(pady=(20, 10), padx=20, anchor="w")

        self.entry = ctk.CTkEntry(self, width=360)
        self.entry.pack(padx=20, pady=(0, 20))
        self.entry.insert(0, initialvalue)
        self.entry.focus()

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkButton(btn_frame, text="OK", width=80, command=self._on_ok).pack(side="right", padx=(6, 0))
        ctk.CTkButton(btn_frame, text="Cancel", width=80, command=self.destroy).pack(side="right")

        self.entry.bind("<Return>", lambda e: self._on_ok())
        self.bind("<Escape>", lambda e: self.destroy())

    def _on_ok(self):
        self.result = self.entry.get().strip()
        self.destroy()


class HomeView:
    TEMPLATES = {
        "Cornell Notes": "Title: \n\nQuestion/Keyword\n-\n-\n\nNotes\n-\n-\n\nSummary\n-\n_",
        "Main Idea & Details": "Main Idea: ___\n\nDetail 1:\n-\n\nDetail 2:\n-\n\nDetail 3:\n-\n\nSummary:\n-",
        "Modified Frayer Model": "Definition:\n-\n\nCharacteristics:\n-\n\nExamples:\n-\n\nNon-Examples:\n-",
        "Polya's 4 Steps": "1. Understand the Problem:\n-\n\n2. Devise a Plan:\n-\n\n3. Carry Out the Plan:\n-\n\n4. Look Back:\n-",
        "5W1H": "Who:\n-\n\nWhat:\n-\n\nWhen:\n-\n\nWhere:\n-\n\nWhy:\n-\n\nHow:\n-",
        "Concept Map": "Central Concept:\n-\n\nRelated Concept 1:\n-\n\nRelated Concept 2:\n-\n\nConnections:\n-"
    }

    def __init__(self, master, data_manager, colors, app):
        self.master = master
        self.data_manager = data_manager
        self.colors = colors
        self.app = app
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
    # ...existing HomeView methods go here...

# TemplateDialog will be defined after HomeView methods to avoid interrupting the class body
    TEMPLATES = {
        "Cornell Notes": "Title: \n\nQuestion/Keyword\n-\n-\n\nNotes\n-\n-\n\nSummary\n-\n_",
        "Main Idea & Details": "Main Idea: ___\n\nDetail 1:\n-\n\nDetail 2:\n-\n\nDetail 3:\n-\n\nSummary:\n-",
        "Modified Frayer Model": "Definition:\n-\n\nCharacteristics:\n-\n\nExamples:\n-\n\nNon-Examples:\n-",
        "Polya's 4 Steps": "1. Understand the Problem:\n-\n\n2. Devise a Plan:\n-\n\n3. Carry Out the Plan:\n-\n\n4. Look Back:\n-",
        "5W1H": "Who:\n-\n\nWhat:\n-\n\nWhen:\n-\n\nWhere:\n-\n\nWhy:\n-\n\nHow:\n-",
        "Concept Map": "Central Concept:\n-\n\nRelated Concept 1:\n-\n\nRelated Concept 2:\n-\n\nConnections:\n-"
    }

    def __init__(self, master, data_manager, colors, app):
        self.master = master
        self.data_manager = data_manager
        self.colors = colors
        self.app = app
        
        # Load categorized templates from settings
        settings = data_manager.get_settings()
        study_saved = settings.get("study_templates", {}) or {}
        additional_saved = settings.get("additional_templates", {}) or {}
        # Merge built-in study templates with any saved ones (saved can override built-in by title)
        self.study_templates = {**self.TEMPLATES, **study_saved}
        self.additional_templates = dict(additional_saved)
        # Active category tracking
        self.active_category = "Study"
        self.current_templates = self.study_templates
        
        # Main container
        self.container = ctk.CTkFrame(master, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Page Title
        ctk.CTkLabel(self.container, text="HOME", font=app.get_font(6, "bold"), text_color=colors['main_text']).pack(anchor="w", pady=(0, 10))
        
        # Content container with two columns
        content_container = ctk.CTkFrame(self.container, fg_color="transparent")
        content_container.pack(fill="both", expand=True)
        
        # Left Column: Write Frame (70% width)
        self.write_frame = ctk.CTkFrame(content_container, fg_color=colors['card_bg'], corner_radius=15)
        self.write_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Right Column: Notes List (30% width)
        self.notes_frame = ctk.CTkFrame(content_container, fg_color=colors['card_bg'], corner_radius=15, width=300)
        self.notes_frame.pack(side="right", fill="y", padx=(10, 0))
        
        self._setup_write_ui()
        self._setup_notes_ui()

    def _setup_write_ui(self):
        # Header
        header = ctk.CTkFrame(self.write_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(header, text="Write", font=self.app.get_font(6, "bold"), text_color=self.colors['main_text']).pack(side="left")
        # Controls Row
        self.controls_frame = ctk.CTkFrame(self.write_frame, fg_color="transparent")
        self.controls_frame.pack(fill="x", padx=20, pady=(0, 4))
        controls = self.controls_frame
        # Assign to
        ctk.CTkLabel(controls, text="Assign to:", font=self.app.get_font(0), text_color=self.colors['main_text']).pack(side="left", padx=(0, 5))
        self.notebook_var = ctk.StringVar(value="• Unassigned Notes")
        self.update_notebook_dropdown()
        # Template Category Switch
        templates_frame = ctk.CTkFrame(controls, fg_color="transparent")
        templates_frame.pack(side="left", padx=(0,10))
        # Study templates dropdown
        ctk.CTkLabel(templates_frame, text="Study:", font=self.app.get_font(0), text_color=self.colors['main_text']).pack(side="left", padx=(0,5))
        self.study_template_var = ctk.StringVar(value="Select...")
        self.study_template_dropdown = ctk.CTkOptionMenu(
            templates_frame,
            variable=self.study_template_var,
            values=["Select..."] + list(self.study_templates.keys()),
            command=self.insert_study_template,
            fg_color=self.colors.get('dropdown_bg', self.colors['main_text']),
            button_color=self.colors.get('accent'),
            text_color=self.colors.get('dropdown_text', 'white'),
            width=180
        )
        self.study_template_dropdown.pack(side="left")
        # Planner (additional) templates dropdown
        ctk.CTkLabel(templates_frame, text="Planner:", font=self.app.get_font(0), text_color=self.colors['main_text']).pack(side="left", padx=(8,5))
        self.planner_template_var = ctk.StringVar(value="Select...")
        self.planner_template_dropdown = ctk.CTkOptionMenu(
            templates_frame,
            variable=self.planner_template_var,
            values=["Select..."] + list(self.additional_templates.keys()),
            command=self.insert_planner_template,
            fg_color=self.colors.get('dropdown_bg', self.colors['main_text']),
            button_color=self.colors.get('accent'),
            text_color=self.colors.get('dropdown_text', 'white'),
            width=180
        )
        self.planner_template_dropdown.pack(side="left")

        # Second row for action buttons to reduce crowding
        self.actions_frame = ctk.CTkFrame(self.write_frame, fg_color="transparent")
        self.actions_frame.pack(fill="x", padx=20, pady=(0, 10))
        # Clear on the left (west), Save on the right (east)
        ctk.CTkButton(self.actions_frame, text="Clear", command=self.clear_write_area,
                  fg_color=self.colors['danger'], hover_color='#c0392b', text_color="white", width=90).pack(side="left", pady=(2,0))
        ctk.CTkButton(self.actions_frame, text="Save Note", command=self.save_note,
                  fg_color=self.colors['success'], hover_color='#219150', text_color="white", width=110).pack(side="right", pady=(2,0))
        # Title Entry
        self.title_entry = ctk.CTkEntry(self.write_frame, placeholder_text="Note Title (Required)", 
                font=self.app.get_font(0, "bold"), height=40,
                fg_color=self.colors['background'], text_color=self.colors['main_text'], border_width=0)
        self.title_entry.pack(fill="x", padx=20, pady=(0, 10))
        
        # Formatting toolbar removed.
        
        # Note: tags are now embedded directly in content as hashtags (e.g. #math).
        # We no longer present a separate tag entry or chips UI in the write area.
        
        # Text Area
        self.text_area = ctk.CTkTextbox(self.write_frame, font=self.app.get_font(0), 
                fg_color=self.colors['background'], text_color=self.colors['main_text'],
                wrap="word", corner_radius=10)
        self.text_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Formatting model removed; plain text only.
        
        # Highlight hashtags as user types and handle formatting
        try:
            self.text_area.bind("<KeyRelease>", lambda e: self._on_text_area_key_release(e))
            # ensure any initial content is highlighted
            highlight_hashtags_in_textbox(self.text_area, self.colors.get('accent', '#4a90e2'))
        except Exception:
            pass
    def update_notebook_dropdown(self):
        # Add bullets to notebook names and truncate
        self.notebook_map = {} # Map display name -> full name
        notebook_list = []
        
        for code, nb_data in self.data_manager.get_notebooks().items():
            name = nb_data.get("name", code)
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
                                                       fg_color=self.colors.get('dropdown_bg', self.colors['main_text']), button_color=self.colors.get('accent'),
                                                       text_color=self.colors.get('dropdown_text', 'white'), width=180)
            self.notebook_dropdown.pack(side="left", padx=(0, 20))

    def _setup_notes_ui(self):
        # Header
        ctk.CTkLabel(self.notes_frame, text="Unassigned Notes", font=self.app.get_font(2, "bold"), 
                 text_color=self.colors['main_text']).pack(pady=(20, 10), padx=20, anchor="w")
        
        # Search Bar
        search_frame = ctk.CTkFrame(self.notes_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Filter unassigned notes...", 
                                         fg_color=self.colors['background'], text_color=self.colors['main_text'],
                                         height=30)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.filter_notes)
        
        # Filter Emoji
        # ctk.CTkLabel(search_frame, text="🔍", font=self.app.get_font(0), text_color=self.colors['secondary_text']).pack(side="right", padx=(5, 0))
        
        # Scrollable List
        self.notes_list = ctk.CTkScrollableFrame(self.notes_frame, fg_color="transparent")
        self.notes_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.refresh_notes_list()
        
    def filter_notes(self, event=None):
        self.refresh_notes_list()

    def _insert_template_from(self, templates_dict, selected_name, var_to_reset):
        if selected_name in templates_dict:
            content = templates_dict[selected_name]
            current_text = self.text_area.get("1.0", "end-1c")
            if len(current_text.strip()) > 0:
                self.text_area.insert("end", "\n\n" + content)
            else:
                self.text_area.insert("1.0", content)
            # Add a tag corresponding to the template so users can see which template was used
            try:
                # normalize template name into a tag-friendly token (alphanumeric + hyphens)
                raw = str(selected_name or "").strip()
                # collapse whitespace and remove punctuation, then join words with single hyphens
                token_base = re.sub(r'[^0-9a-zA-Z ]+', '', raw).strip().lower()
                token = '-'.join(token_base.split())
                if token:
                    new_tag = f"#{token}"
                    # Ensure we don't duplicate tags already in content — check existing content hashtags
                    current_text = self.text_area.get("1.0", "end-1c")
                    existing = extract_hashtags_from_text(current_text)
                    seen = {t.lstrip('#') for t in existing}
                    if token not in seen:
                        # Append the new tag to the end of the content so it's stored in-text
                        if current_text.strip():
                            self.text_area.insert("end", " \n" + new_tag)
                        else:
                            self.text_area.insert("1.0", new_tag)
            except Exception:
                pass
        # Reset the invoking dropdown regardless
        try:
            var_to_reset.set("Select...")
        except Exception:
            pass

    def insert_study_template(self, template_name):
        self._insert_template_from(self.study_templates, template_name, self.study_template_var)

    def insert_planner_template(self, template_name):
        self._insert_template_from(self.additional_templates, template_name, self.planner_template_var)

    def handle_notebook_selection(self, selection):
        if selection == "+ Create new notebook...":
            # Open dialog
            EditNotebookDialog(self.master, self.data_manager, self.colors, self.on_notebook_created)
            # Reset dropdown temporarily until created or cancelled
            self.notebook_var.set("• Unassigned Notes")

    def on_notebook_created(self, new_notebook_name):
        self.update_notebook_dropdown()
        # Find the display name for this new notebook
        display_name = f"• {self.master.master.truncate_text(new_notebook_name)}"
        self.notebook_var.set(display_name)
        # Also refresh sidebar
        if isinstance(self.master.master, CourseMate):
             self.master.master.sidebar.refresh_notebooks_list()
             self.master.master.sidebar.refresh_stats()

    def clear_write_area(self):
        if not self.text_area.get("1.0", "end-1c").strip() and not self.title_entry.get().strip():
            return # Already empty
            
        if messagebox.askyesno("Clear Note", "Are you sure you want to clear the current note?"):
            self.title_entry.delete(0, "end")
            self.text_area.delete("1.0", "end")
            self.notebook_var.set("• Unassigned Notes")
            # Reset both template dropdowns
            try:
                self.study_template_var.set("Select...")
                self.planner_template_var.set("Select...")
            except Exception:
                pass
    
    # Formatting toolbar removed.
    def _on_text_area_key_release(self, event):
        """Handle key releases: auto-bullet + hashtag highlight."""
        if event.keysym == "Return":
            self._handle_enter_key()
        try:
            highlight_hashtags_in_textbox(self.text_area, self.colors.get('accent', '#4a90e2'))
        except Exception:
            pass
    
    # Removed _sync_content_model; no model exists.
    
    def _handle_enter_key(self):
        """Auto-create bullet on next line if current line has bullet and content."""
        try:
            text_content = self.text_area.get("1.0", "end-1c")
            cursor_pos = self.text_area.index("insert")
            line_num = int(cursor_pos.split('.')[0])
            col_num = int(cursor_pos.split('.')[1])
            
            # Get current line content
            line_start = f"{line_num}.0"
            line_end = f"{line_num}.end"
            current_line = self.text_area.get(line_start, line_end)
            
            # Check if current line starts with bullet and has content after bullet
            if current_line.startswith('• ') and len(current_line.strip()) > 2:
                # Schedule bullet addition on next line
                self.after(10, lambda: self._add_bullet_to_next_line(line_num + 1))
        except Exception:
            pass
    
    def _add_bullet_to_next_line(self, line_num):
        """Add bullet to the specified line if it's empty."""
        try:
            line_start = f"{line_num}.0"
            line_end = f"{line_num}.end"
            line_content = self.text_area.get(line_start, line_end)
            
            if line_content.strip() == "":
                self.text_area.insert(line_start, "• ")
        except Exception:
            pass
    
    def _get_text_selection_or_cursor(self):
        """Get selected text and indices, or current cursor position."""
        try:
            sel_first = self.text_area.index("sel.first")
            sel_last = self.text_area.index("sel.last")
            return sel_first, sel_last, True
        except tk.TclError:
            # No selection, use cursor position
            cursor = self.text_area.index("insert")
            return cursor, cursor, False
    
    # Removed _apply_formatting and inline formatting logic.
    
    # Formatting button handlers removed.

    def save_note(self):
        title = self.title_entry.get().strip()
        content = self.text_area.get("1.0", "end-1c").strip()
        assigned_notebook = self.notebook_var.get()
        
        # Extract tags from content (hashtags written in the text area)
        tags = extract_hashtags_from_text(content)
        
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
            "tags": tags,
            "created": datetime.now().strftime("%B %d, %Y | %I:%M%p"),
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
        # text-based tags are extracted from content, so we don't keep a separate tags entry here
            # clear any previous chips (safe no-op if chips removed later)
        try:
            chip_frame = getattr(self, 'tags_chip_frame', None)
            if chip_frame is not None:
                for w in chip_frame.winfo_children():
                    w.destroy()
        except Exception:
            # Some older states may not have tags_chip_frame yet — ignore
            pass
        self.text_area.delete("1.0", "end")
        self.notebook_var.set("• Unassigned Notes")
        # we no longer maintain a separate tags chip UI (tags embedded in content)

    # Tags are now embedded in content; write-area tag helpers removed.

    def refresh_notes_list(self):
        for widget in self.notes_list.winfo_children():
            widget.destroy()
            
        notes = self.data_manager.get_unassigned_notes()
        search_term = self.search_entry.get().lower().strip() if hasattr(self, 'search_entry') else ""
        
        if not notes:
            ctk.CTkLabel(self.notes_list, text="No unassigned notes", font=self.app.get_font(-1, "italic"), 
                         text_color=self.colors['secondary_text']).pack(pady=20)
            return

        # Filter and Sort (Newest first)
        filtered_notes = []
        for note in reversed(notes):
            if search_term:
                tags_str = " ".join(note.get('tags', [])).lower()
                if search_term in note.get('title', '').lower() or \
                   search_term in note.get('content', '').lower() or \
                   search_term in tags_str:
                    filtered_notes.append(note)
            else:
                filtered_notes.append(note)
                
        if not filtered_notes and search_term:
             ctk.CTkLabel(self.notes_list, text="No matches found", font=self.app.get_font(0, "italic"), 
                         text_color=self.colors['secondary_text']).pack(pady=20)
             return

        for note in filtered_notes:
            self._create_note_card(note)

    def _create_note_card(self, note):
        border_color = self.colors.get('card_border', self.colors.get('muted', '#68707a'))
        corner = 12
        card = ctk.CTkFrame(self.notes_list, fg_color=self.colors['card_bg'], corner_radius=corner, border_width=2, border_color=border_color)
        card.pack(fill="x", pady=5)
        
        # Click event to open note
        card.bind("<Button-1>", lambda e, n=note: self.open_note_window(n))
        try:
            card.bind("<Enter>", lambda e: card.configure(fg_color=self.colors.get('card_hover', card.cget('fg_color'))))
            card.bind("<Leave>", lambda e: card.configure(fg_color=self.colors.get('card_bg', card.cget('fg_color'))))
        except Exception:
            pass
        
        title = note.get('title', 'Untitled')
        
        # Date formatting: "Nov 23"
        created_str = note.get('created', '')
        try:
            # Try new format first
            created_dt = datetime.strptime(created_str, "%B %d, %Y | %I:%M%p")
            date_str = created_dt.strftime("%b %d")
        except ValueError:
            try:
                # Try old format
                created_dt = datetime.strptime(created_str, "%Y-%m-%d %H:%M")
                date_str = created_dt.strftime("%b %d")
            except ValueError:
                # Fallback
                date_str = created_str.split('|')[0].strip() if '|' in created_str else created_str.split(' ')[0]
            
        # Preview: First 3 words
        content_words = note.get('content', '').split()
        preview_text = " ".join(content_words[:3]) if content_words else ""
        
        # Row 1: Title
        lbl_title = ctk.CTkLabel(card, text=title, font=self.app.get_font(-1, "bold"), text_color=self.colors['main_text'], anchor="w")
        lbl_title.pack(fill="x", padx=10, pady=(5, 0))
        lbl_title.bind("<Button-1>", lambda e, n=note: self.open_note_window(n))
        
        # Row 2: Date | Preview
        meta_text = f"{date_str} | {preview_text}"
        lbl_meta = ctk.CTkLabel(card, text=meta_text, font=self.app.get_font(-3), text_color=self.colors['secondary_text'], anchor="w")
        lbl_meta.pack(fill="x", padx=10, pady=(0, 5))
        lbl_meta.bind("<Button-1>", lambda e, n=note: self.open_note_window(n))
        
        # Row 3: Tags
        tags = note.get('tags', [])
        if tags:
            tags_text = " ".join([f"#{t}" if not t.startswith('#') else t for t in tags])
            lbl_tags = ctk.CTkLabel(card, text=tags_text, font=self.app.get_font(-3, "italic"), text_color=self.colors['accent'], anchor="w")
            lbl_tags.pack(fill="x", padx=10, pady=(0, 5))
            lbl_tags.bind("<Button-1>", lambda e, n=note: self.open_note_window(n))

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
        get_font = master.master.get_font if hasattr(master.master, 'get_font') else lambda s=0, w="normal": ("Open Sans", 14+s, w)
        
        # Editable title
        initial_title = note.get('title', '').strip() or 'Untitled'
        self.title_var = tk.StringVar(value=initial_title)
        
        # Title Label
        ctk.CTkLabel(self, text="Title", font=get_font(0, "bold"), text_color=colors['main_text']).pack(anchor="w", padx=20, pady=(10, 0))

        self.title_entry = ctk.CTkEntry(
            self,
            textvariable=self.title_var,
            placeholder_text="Note Title",
            font=get_font(2, "bold"),
            fg_color=colors.get('card_bg', colors['background']),
            text_color=colors['main_text'],
            border_width=1,
            border_color=colors.get('card_border', colors.get('muted', '#68707a'))
        )
        self.title_entry.pack(fill="x", padx=20, pady=(5, 10))
        
        # Tagging is now handled inline — hashtags are discovered in the content itself.
        
        # Content
        # Content Label
        ctk.CTkLabel(self, text="Content", font=get_font(0, "bold"), text_color=colors['main_text']).pack(anchor="w", padx=20, pady=(0, 0))

        self.text_area = ctk.CTkTextbox(self, font=get_font(0), fg_color=colors['background'], text_color=colors['main_text'], wrap="word")
        self.text_area.pack(fill="both", expand=True, padx=20, pady=(5, 0))
        
        # Insert raw content directly (no formatting model)
        initial_content = note.get('content', '')
        self.text_area.insert("1.0", initial_content)
        try:
            def on_key_release(e):
                self.update_word_count()
                highlight_hashtags_in_textbox(self.text_area, self.colors.get('accent', '#4a90e2'))
            self.text_area.bind("<KeyRelease>", on_key_release)
            highlight_hashtags_in_textbox(self.text_area, self.colors.get('accent', '#4a90e2'))
        except Exception:
            try:
                self.text_area.bind("<KeyRelease>", self.update_word_count)
            except Exception:
                pass

        # Word Count Label
        self.word_count_label = ctk.CTkLabel(self, text="Word Count: 0", font=get_font(-2), text_color=colors['secondary_text'])
        self.word_count_label.pack(anchor="e", padx=20, pady=(0, 10))
        self.after(100, self.update_word_count) # Initial count
        
        # Date Info Frame
        date_frame = ctk.CTkFrame(self, fg_color="transparent")
        date_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Created On
        created_text = note.get('created', '')
        try:
             dt = datetime.strptime(created_text, "%Y-%m-%d %H:%M")
             created_text = dt.strftime("%B %d, %Y | %I:%M%p")
        except ValueError:
             pass
        
        ctk.CTkLabel(date_frame, text=f"Created on: {created_text}", font=get_font(-3), text_color=colors['secondary_text']).pack(anchor="w")
        
        # Modified On
        modified_text = note.get('modified', '')
        if modified_text:
            ctk.CTkLabel(date_frame, text=f"Last edited on: {modified_text}", font=get_font(-3), text_color=colors['secondary_text']).pack(anchor="w")
        
        # Actions Frame
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Save Button
        ctk.CTkButton(actions_frame, text="Save Changes", command=self.save_changes, fg_color=colors['success'], text_color="white").pack(side="left", padx=(0, 10))
        
        # Export Button
        ctk.CTkButton(actions_frame, text="Export", command=self.export_note, fg_color=colors['info'], text_color="white", width=80).pack(side="left", padx=(0, 10))

        # Copy Button
        ctk.CTkButton(actions_frame, text="Copy", command=self.copy_content, fg_color=colors['accent'], text_color="white", width=80).pack(side="left", padx=(0, 10))

        # Delete Button
        ctk.CTkButton(actions_frame, text="Delete Note", command=self.delete_note, fg_color=colors['danger'], text_color="white").pack(side="right")
        
        # Move to Notebook
        move_frame = ctk.CTkFrame(self, fg_color="transparent")
        move_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(move_frame, text="Move to:", font=get_font(-2), text_color=colors['main_text']).pack(side="left", padx=(0, 5))
        
        self.notebook_var = ctk.StringVar(value="Select Notebook...")
        
        self.notebook_map = {}
        notebook_list = []
        for code, nb_data in self.data_manager.get_notebooks().items():
            name = nb_data.get("name", code)
            display_name = master.master.truncate_text(name)
            notebook_list.append(display_name)
            self.notebook_map[display_name] = name
            
        # Include an option to move the note to Unassigned Notes
        notebooks = ["• Unassigned Notes"] + notebook_list
        if not notebook_list:
            # If there are no notebooks, allow the user to select 'No Notebooks'
            notebooks = ["• Unassigned Notes", "No Notebooks"]
        # Map the unassigned display to a sentinel value (None)
        self.notebook_map["• Unassigned Notes"] = None
            
        self.notebook_dropdown = ctk.CTkOptionMenu(move_frame, variable=self.notebook_var, values=notebooks,
                       fg_color=colors.get('dropdown_bg', colors['main_text']), button_color=colors.get('accent'),
                       text_color=colors.get('dropdown_text', 'white'))
        self.notebook_dropdown.pack(side="left", padx=(0, 10))

        # Move Button
        ctk.CTkButton(move_frame, text="Move", command=self.move_note, width=60,
                      fg_color=colors['info'], text_color="white").pack(side="left")

    def update_word_count(self, event=None):
        text = self.text_area.get("1.0", "end-1c")
        words = text.split()
        self.word_count_label.configure(text=f"Word Count: {len(words)}")

    def copy_content(self):
        content = self.text_area.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(content)
        messagebox.showinfo("Copied", "Note content copied to clipboard.")

    def export_note(self):
        initial_file = f"{self.title_var.get()}.txt"
        # Sanitize filename
        initial_file = "".join(c for c in initial_file if c.isalnum() or c in (' ', '.', '_', '-')).strip()
        
        file_path = tk.filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=initial_file,
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Title: {self.title_var.get()}\n")
                    # Export tags derived from content (keep consistent with save behavior)
                    exported_tags = extract_hashtags_from_text(self.text_area.get("1.0", "end-1c"))
                    f.write(f"Tags: {', '.join(exported_tags)}\n")
                    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                    f.write("-" * 40 + "\n\n")
                    f.write(self.text_area.get("1.0", "end-1c"))
                messagebox.showinfo("Exported", "Note exported successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export note: {e}")


    def save_changes(self):
        # Get content with markers (like bullets are saved)
        new_content = self.text_area.get("1.0", "end-1c")
        
        # Extract tags from the content text (hashtags embedded in content)
        try:
            parsed_tags = extract_hashtags_from_text(new_content)
            self.note['tags'] = parsed_tags
        except Exception:
            self.note['tags'] = []

        new_title = self.title_var.get().strip() if hasattr(self, 'title_var') else self.note.get('title', '')
        if not new_title:
            new_title = 'Untitled'
        self.note['title'] = new_title
        try:
            self.title(new_title)
        except Exception:
            pass
        if hasattr(self, 'title_var'):
            self.title_var.set(new_title)
        
        # Save content with markers
        self.note['content'] = new_content
        self.content_model.set_text(new_content)
        
        # Update modified timestamp
        self.note['modified'] = datetime.now().strftime("%B %d, %Y | %I:%M%p")
        
        self.data_manager.save_data()
        messagebox.showinfo("Saved", "Title and content saved.")
        if self.callback:
            self.callback()

    # NoteWindow tag-entry helpers removed — tags are extracted from content instead.

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
                if isinstance(self.master.master, CourseMate):
                     self.master.master.sidebar.refresh_stats()
                return

            # If not in unassigned, check all notebooks
            for code, notebook_data in self.data_manager.get_notebooks().items():
                if self.note in notebook_data.get("notes", []):
                    notebook_data["notes"].remove(self.note)
                    self.data_manager.save_data()
                    self.destroy()
                    if self.callback:
                        self.callback()
                    # Refresh sidebar stats
                    if isinstance(self.master.master, CourseMate):
                         self.master.master.sidebar.refresh_stats()
                    return
            
            messagebox.showerror("Error", "Could not find note to delete.")

    def move_note(self):
        # Move note to selected notebook (from the dropdown created in __init__)
        target_display = self.notebook_var.get()
        if not target_display or target_display in ("Select Notebook...", "No Notebooks"):
            messagebox.showwarning("No Target", "Please select a target notebook to move this note.")
            return

        # Resolve the mapping; notebook_map maps display names to actual notebook
        # names, and maps '• Unassigned Notes' to None.
        target_notebook = self.notebook_map.get(target_display, target_display)

        # Confirm action text for unassigned target
        confirm_target = "Unassigned Notes" if target_notebook is None else target_notebook
        if messagebox.askyesno("Move Note", f"Move this note to '{confirm_target}'?"):
            # If target is Unassigned (None), remove from any notebook and add to unassigned
            if target_notebook is None:
                # If already unassigned, nothing to do
                unassigned = self.data_manager.get_unassigned_notes()
                if self.note in unassigned:
                    messagebox.showinfo("No-op", "Note is already in Unassigned Notes.")
                    return

                # Remove from assigned notebook if present
                removed = False
                for code, notebook_data in self.data_manager.get_notebooks().items():
                    if self.note in notebook_data.get("notes", []):
                        notebook_data["notes"].remove(self.note)
                        removed = True
                        break

                # Add to unassigned and save
                self.data_manager.add_unassigned_note(self.note)
                # If we removed from a notebook we already modified data in-memory; save
                if not removed:
                    # If it wasn't found in notebooks, ensure data is saved
                    self.data_manager.save_data()

                self.destroy()
                if self.callback:
                    self.callback()

                # Refresh sidebar and main view
                if isinstance(self.master.master, CourseMate):
                    try:
                        self.master.master.sidebar.refresh_stats()
                        self.master.master.sidebar.refresh_notebooks_list()
                    except Exception:
                        pass
                return

            # Otherwise, move to a named notebook
            # Remove from unassigned if present
            unassigned = self.data_manager.get_unassigned_notes()
            if self.note in unassigned:
                unassigned.remove(self.note)
                self.data_manager.add_note_to_notebook(target_notebook, self.note)
                self.data_manager.save_data()
                self.destroy()
                if self.callback:
                    self.callback()
                if isinstance(self.master.master, CourseMate):
                    try:
                        self.master.master.sidebar.refresh_stats()
                        self.master.master.sidebar.refresh_notebooks_list()
                    except Exception:
                        pass
                return

            # If not in unassigned, search notebooks to find and move
            for code, notebook_data in self.data_manager.get_notebooks().items():
                if self.note in notebook_data.get("notes", []):
                    notebook_data["notes"].remove(self.note)
                    self.data_manager.add_note_to_notebook(target_notebook, self.note)
                    self.data_manager.save_data()
                    self.destroy()
                    if self.callback:
                        self.callback()
                    if isinstance(self.master.master, CourseMate):
                        try:
                            self.master.master.sidebar.refresh_stats()
                            self.master.master.sidebar.refresh_notebooks_list()
                        except Exception:
                            pass
                    return

            messagebox.showerror("Error", "Could not move note.")

class EditNotebookDialog(ctk.CTkToplevel):
    def __init__(self, master, data_manager, colors, callback, notebook_name=None):
        super().__init__(master)
        self.is_edit_mode = notebook_name is not None
        self.original_notebook_name = notebook_name
        self.title("Edit Notebook" if self.is_edit_mode else "Create New Notebook")
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
        get_font = master.master.get_font if hasattr(master.master, 'get_font') else lambda s=0, w="normal": ("Open Sans", 14+s, w)
        
        title_text = "Edit Notebook" if self.is_edit_mode else "New Notebook"
        ctk.CTkLabel(self, text=title_text, font=get_font(4, "bold"), text_color=colors['main_text']).pack(pady=20)
        
        # Notebook Name
        ctk.CTkLabel(self, text="Notebook Name:", font=get_font(-1), text_color=colors['main_text']).pack(anchor="w", padx=50, pady=(5, 0))
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Notebook Name (Required)", width=300, fg_color=colors['card_bg'], text_color=colors['main_text'])
        self.name_entry.pack(pady=(0, 10))
        
        # Course Code
        ctk.CTkLabel(self, text="Course Code:", font=get_font(-1), text_color=colors['main_text']).pack(anchor="w", padx=50, pady=(5, 0))
        self.code_entry = ctk.CTkEntry(self, placeholder_text="Course Code (Required)", width=300, fg_color=colors['card_bg'], text_color=colors['main_text'])
        self.code_entry.pack(pady=(0, 10))
        
        # Instructor
        ctk.CTkLabel(self, text="Instructor:", font=get_font(-1), text_color=colors['main_text']).pack(anchor="w", padx=50, pady=(5, 0))
        self.instructor_entry = ctk.CTkEntry(self, placeholder_text="Instructor (Optional)", width=300, fg_color=colors['card_bg'], text_color=colors['main_text'])
        self.instructor_entry.pack(pady=(0, 10))
        
        # If editing, populate with current values
        if self.is_edit_mode:
            for code, nb_data in self.data_manager.get_notebooks().items():
                if nb_data.get("name") == notebook_name:
                    self.name_entry.insert(0, nb_data.get("name", ""))
                    self.code_entry.insert(0, nb_data.get("code", ""))
                    self.instructor_entry.insert(0, nb_data.get("instructor", ""))
                    self.original_code = code
                    break
        
        button_text = "Save Changes" if self.is_edit_mode else "Create Notebook"
        ctk.CTkButton(self, text=button_text, command=self.create, fg_color=colors['success'], text_color="white").pack(pady=20)
        
        # Bind Enter key only to window (not individual entries to avoid double-trigger)
        self.bind("<Return>", lambda e: self.create())
        
        # Ensure focus lands on name entry after window is ready
        self.after(100, self.name_entry.focus)
        
    def create(self):
        name = self.name_entry.get().strip()
        code = self.code_entry.get().strip()
        instructor = self.instructor_entry.get().strip()
        
        if not name:
            messagebox.showwarning("Required", "Notebook name is required.")
            return
        
        if not code:
            messagebox.showwarning("Required", "Course code is required.")
            return
            
        if len(name) > 25:
            messagebox.showwarning("Name Too Long", "Notebook name must be 25 characters or less.")
            return
        
        if len(code) > 15:
            messagebox.showwarning("Code Too Long", "Course code must be 15 characters or less.")
            return
        
        if self.is_edit_mode:
            # Update existing notebook
            notebooks = self.data_manager.get_notebooks()
            
            # Check if code changed and if new code already exists
            if code != self.original_code and code in notebooks:
                messagebox.showerror("Error", "A notebook with this course code already exists.")
                return
            
            # Get the notebook data
            if self.original_code in notebooks:
                nb_data = notebooks[self.original_code]
                
                # Update fields
                nb_data["name"] = name
                nb_data["code"] = code
                nb_data["instructor"] = instructor
                
                # If code changed, move to new key
                if code != self.original_code:
                    notebooks[code] = nb_data
                    del notebooks[self.original_code]
                
                self.data_manager.save_data()
                self.callback(name)
                self.destroy()
            else:
                messagebox.showerror("Error", "Notebook not found!")
        else:
            # Create new notebook
            result = self.data_manager.add_notebook(name, code, instructor)
            if isinstance(result, tuple):
                success, message = result
                if success:
                    self.callback(name)
                    self.destroy()
                else:
                    messagebox.showerror("Error", message)
            else:
                # Legacy compatibility
                if result:
                    self.callback(name)
                    self.destroy()
                else:
                    messagebox.showerror("Error", "Could not create notebook!")

class NotebooksView:
    def __init__(self, master, data_manager, colors, initial_notebook=None, app=None):
        self.master = master
        self.data_manager = data_manager
        self.colors = colors
        self.app = app or getattr(master, "master", None)
        self.selected_notebook = None  # Initialize selected_notebook attribute
        
        self.container = ctk.CTkFrame(master, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Check if initial_notebook name exists in any notebook
        notebook_found = False
        if initial_notebook:
            for code, nb_data in self.data_manager.get_notebooks().items():
                if nb_data.get("name") == initial_notebook:
                    notebook_found = True
                    break
        
        if notebook_found:
            self.show_notebook(initial_notebook)
        else:
            self.show_all_notebooks()

    def get_font(self, size_offset=0, weight="normal", slant="roman"):
        if self.app and hasattr(self.app, "get_font"):
            return self.app.get_font(size_offset, weight, slant)
        base_size = getattr(self.app, "base_font_size", 14) if self.app else 14
        family = getattr(self.app, "font_family", "Open Sans") if self.app else "Open Sans"
        return (family, base_size + size_offset, weight, slant)

    def truncate_text(self, text, limit=25):
        if self.app and hasattr(self.app, "truncate_text"):
            return self.app.truncate_text(text, limit)
        if len(text) <= limit:
            return text
        return text[:max(limit - 3, 0)] + "..."

    def show_all_notebooks(self):
        # Clear container
        for widget in self.container.winfo_children():
            widget.destroy()
            
        # Header
        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="YOUR NOTEBOOKS", font=self.get_font(6, "bold"), text_color=self.colors['main_text']).pack(side="left")
        ctk.CTkButton(header, text="+ Create Notebook", command=self.add_notebook, fg_color=self.colors['success'], text_color="white").pack(side="right")
        
        # Search Bar for Notebooks
        search_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        search_frame.pack(fill="x", padx=0, pady=(0, 10))
        
        self.notebook_search_entry = ctk.CTkEntry(search_frame, placeholder_text="Filter notebooks...", 
                                         fg_color=self.colors['background'], text_color=self.colors['main_text'],
                                         height=30)
        self.notebook_search_entry.pack(side="left", fill="x", expand=True)
        self.notebook_search_entry.bind("<KeyRelease>", self.filter_notebooks)
        
        # Grid Container
        self.grid_frame = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True)
        
        self.refresh_notebooks_grid()

    def filter_notebooks(self, event=None):
        self.refresh_notebooks_grid()

    def refresh_notebooks_grid(self):
        # Clear grid frame
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        # Grid Layout Logic
        notebooks = self.data_manager.get_notebooks()
        if not notebooks:
            ctk.CTkLabel(self.grid_frame, text="No notebooks yet. Create one to get started!", font=self.get_font(0), text_color=self.colors['secondary_text']).pack(pady=50)
            return

        search_term = self.notebook_search_entry.get().lower().strip() if hasattr(self, 'notebook_search_entry') else ""

        # Filter notebooks
        filtered_notebooks = {}
        for code, data in notebooks.items():
            name = data.get("name", code)
            if search_term:
                if search_term in name.lower() or search_term in str(data.get("code", "")).lower():
                    filtered_notebooks[code] = data
            else:
                filtered_notebooks[code] = data

        if not filtered_notebooks and search_term:
             ctk.CTkLabel(self.grid_frame, text="No matching notebooks found", font=self.get_font(0, "italic"), 
                         text_color=self.colors['secondary_text']).pack(pady=50)
             return

        # Configure grid columns
        columns = 3
        for i in range(columns):
            self.grid_frame.grid_columnconfigure(i, weight=1)

        for i, (code, data) in enumerate(filtered_notebooks.items()):
            name = data.get("name", code)
            row = i // columns
            col = i % columns
            self._create_notebook_card(name, data, row, col)

    def _create_notebook_card(self, name, data, row, col):
        # Card Frame with border
        border_color = self.colors.get('card_border', self.colors.get('muted', '#68707a'))
        # Use a consistent corner radius across cards
        corner = 12
        card = ctk.CTkFrame(self.grid_frame, fg_color=self.colors['card_bg'], corner_radius=corner,
                           border_width=2, border_color=border_color)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Header with icon buttons
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))
        
        # Title on the left - handle empty names
        display_name = name.strip() if name else "(Unnamed)"
        display_name = self.truncate_text(display_name, 20)
        lbl_title = ctk.CTkLabel(header, text=display_name, font=self.get_font(2, "bold"), 
                                 text_color=self.colors['main_text'])
        lbl_title.pack(side="left")
        
        # Icon buttons on the right
        # Delete button (trash icon) with border
        ctk.CTkButton(header, text="🗑️", width=30, height=25, 
                     command=lambda n=name: self.delete_notebook(n),
                     fg_color="transparent", hover_color=self.colors['danger'], 
                     text_color=self.colors['danger'],
                     border_width=1, border_color=self.colors.get('muted', '#9e9e9e'),
                     font=self.get_font(-2)).pack(side="right", padx=(5, 0))
        
        # Edit button (pen icon) with border
        ctk.CTkButton(header, text="✏️", width=30, height=25, 
                     command=lambda n=name: self.rename_notebook(n),
                     fg_color="transparent", hover_color=self.colors['info'], 
                     text_color=self.colors['info'],
                     border_width=1, border_color=self.colors.get('muted', '#9e9e9e'),
                     font=self.get_font(-2)).pack(side="right", padx=(5, 0))
        # Hover effect for the card (subtle change using theme hover color)
        try:
            card.bind("<Enter>", lambda e: card.configure(fg_color=self.colors.get('card_hover', card.cget('fg_color'))))
            card.bind("<Leave>", lambda e: card.configure(fg_color=self.colors.get('card_bg', card.cget('fg_color'))))
        except Exception:
            pass
        
        # Meta (Code | Instructor)
        meta = []
        if data.get("code"): meta.append(data["code"])
        if data.get("instructor"): meta.append(data["instructor"])
        meta_text = " • ".join(meta) if meta else "No details"
        
        lbl_meta = ctk.CTkLabel(card, text=meta_text, font=self.get_font(-2), 
                               text_color=self.colors['secondary_text'])
        lbl_meta.pack(padx=15, pady=(0, 8), anchor="w")
        
        # Stats (Note Count)
        note_count = len(data.get("notes", []))
        lbl_count = ctk.CTkLabel(card, text=f"{note_count} Notes", font=self.get_font(-2, "bold"), 
                                text_color=self.colors['accent'])
        lbl_count.pack(padx=15, pady=(0, 10), anchor="w")

        # Open Notebook Button at bottom
        ctk.CTkButton(card, text="Open Notebook", command=lambda n=name: self.show_notebook(n),
                     fg_color=self.colors.get('button_primary', self.colors['primary']), 
                     text_color=self.colors.get('button_text', 'white'),
                     height=30, font=self.get_font(-2)).pack(fill="x", padx=15, pady=(0, 15))

    def show_notebook(self, name):
        self.selected_notebook = name
        
        # Find notebook data
        notebook_data = None
        for code, nb_data in self.data_manager.get_notebooks().items():
            if nb_data.get("name") == name:
                notebook_data = nb_data
                break

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
        ctk.CTkLabel(header, text=name, font=self.get_font(6, "bold"), text_color=self.colors['main_text']).pack(side="left")
        
        # Meta Info (Code | Instructor)
        if notebook_data:
            meta_parts = []
            if notebook_data.get("code"): meta_parts.append(notebook_data["code"])
            if notebook_data.get("instructor"): meta_parts.append(notebook_data["instructor"])
            
            if meta_parts:
                meta_text = " | ".join(meta_parts)
                ctk.CTkLabel(header, text=meta_text, font=self.get_font(-2), text_color=self.colors['secondary_text']).pack(side="left", padx=(15, 0), pady=(5, 0))

        # Actions
        ctk.CTkButton(header, text="Delete", width=80, command=self.delete_notebook,
                      fg_color=self.colors['danger'], text_color="white").pack(side="right", padx=5)
        ctk.CTkButton(header, text="Rename", width=80, command=self.rename_notebook,
                      fg_color=self.colors['info'], text_color="white").pack(side="right", padx=5)
        
        # Search Bar
        search_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        search_frame.pack(fill="x", padx=0, pady=(0, 10))
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Filter notes...", 
                                         fg_color=self.colors['background'], text_color=self.colors['main_text'],
                                         height=30)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.filter_notes)
               
        # Notes List
        self.notes_area = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        self.notes_area.pack(fill="both", expand=True)
        
        self.refresh_notebook_notes()

    def filter_notes(self, event=None):
        self.refresh_notebook_notes()

    def refresh_notebook_notes(self):
        # Clear notes area
        for widget in self.notes_area.winfo_children():
            widget.destroy()
            
        name = self.selected_notebook
        notebook_data = None
        for code, nb_data in self.data_manager.get_notebooks().items():
            if nb_data.get("name") == name:
                notebook_data = nb_data
                break
        
        notes = notebook_data.get('notes', []) if notebook_data else []
        
        search_term = self.search_entry.get().lower().strip() if hasattr(self, 'search_entry') else ""
        
        if not notes:
            ctk.CTkLabel(self.notes_area, text="No notes in this notebook", font=self.get_font(-2, "italic"), text_color=self.colors['secondary_text']).pack(pady=50)
            return

        match_found = False
        for i, note in enumerate(notes):
            if search_term:
                tags_str = " ".join(note.get('tags', [])).lower()
                if search_term not in note.get('title', '').lower() and \
                   search_term not in note.get('content', '').lower() and \
                   search_term not in tags_str:
                    continue
            
            match_found = True
            self._create_note_item(note, i)
            
        if not match_found and search_term:
             ctk.CTkLabel(self.notes_area, text="No matches found", font=self.get_font(0, "italic"), 
                         text_color=self.colors['secondary_text']).pack(pady=20)

    def _create_note_item(self, note, index):
        border_color = self.colors.get('card_border', self.colors.get('muted', '#68707a'))
        card = ctk.CTkFrame(
            self.notes_area,
            fg_color=self.colors['card_bg'],
            corner_radius=12,
            border_width=2,
            border_color=border_color
        )
        card.pack(fill="x", padx=10, pady=6)
        
        # Header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(header, text=note.get('title', 'Untitled'), font=self.get_font(0, "bold"), text_color=self.colors['main_text']).pack(side="left")
        
        # Format date for display
        created_text = note.get('created', '')
        try:
             # Try to reformat if it matches the old format
             dt = datetime.strptime(created_text, "%Y-%m-%d %H:%M")
             created_text = dt.strftime("%B %d, %Y | %I:%M%p")
        except ValueError:
             pass # Already in new format or unknown
             
        date_display = f"Created on: {created_text}"
        
        # Check for modified date
        modified_text = note.get('modified', '')
        if modified_text:
            date_display += f"  •  Last edited on: {modified_text}"
             
        ctk.CTkLabel(header, text=date_display, font=self.get_font(-3), text_color=self.colors['secondary_text']).pack(side="left", padx=10)
        
        # Delete Note Button
        ctk.CTkButton(header, text="🗑️", width=30, height=25, command=lambda: self.delete_note(index),
                      fg_color="transparent", hover_color=self.colors['danger'], text_color=self.colors['danger'],
                      border_width=1, border_color=self.colors.get('muted', '#9e9e9e'),
                      font=self.get_font(-2)).pack(side="right")
        
        # Preview
        preview = note.get('content', '')[:100].replace('\n', ' ') + "..."
        ctk.CTkLabel(card, text=preview, font=self.get_font(-1), text_color=self.colors['main_text'], anchor="w").pack(fill="x", padx=15, pady=(0, 5))
        
        # Tags
        tags = note.get('tags', [])
        if tags:
            tags_text = " ".join([f"#{t}" if not t.startswith('#') else t for t in tags])
            ctk.CTkLabel(card, text=tags_text, font=self.get_font(-3, "italic"), text_color=self.colors['accent'], anchor="w").pack(fill="x", padx=15, pady=(0, 5))
        
        # Open Button
        ctk.CTkButton(card, text="Open Note", command=lambda: self.open_note(note),
                  fg_color=self.colors.get('button_primary', self.colors['primary']), 
                  text_color=self.colors.get('button_text', 'white'),
                  height=25, font=self.get_font(-3)).pack(fill="x", padx=15, pady=(0, 10))
        try:
            card.bind("<Enter>", lambda e: card.configure(fg_color=self.colors.get('card_hover', card.cget('fg_color'))))
            card.bind("<Leave>", lambda e: card.configure(fg_color=self.colors.get('card_bg', card.cget('fg_color'))))
        except Exception:
            pass

    def add_notebook(self):
        # Open dialog
        EditNotebookDialog(self.master, self.data_manager, self.colors, self.on_notebook_created)
        
    def on_notebook_created(self, name):
        self.show_all_notebooks()
        # Update sidebar
        if isinstance(self.app, CourseMate):
            self.app.sidebar.refresh_notebooks_list()
            self.app.sidebar.refresh_stats()

    def rename_notebook(self, notebook_name=None):
        target = notebook_name or self.selected_notebook
        if not target: return
        
        # Open edit dialog with current notebook data
        EditNotebookDialog(self.master, self.data_manager, self.colors, 
                          lambda new_name: self.on_notebook_edited(target, new_name), 
                          notebook_name=target)
    
    def on_notebook_edited(self, old_name, new_name):
        # Refresh view
        if self.selected_notebook == old_name:
            self.selected_notebook = new_name
            self.show_notebook(self.selected_notebook)
        else:
            self.show_all_notebooks()
        
        # Update sidebar
        if isinstance(self.app, CourseMate):
            self.app.sidebar.refresh_notebooks_list()
            self.app.sidebar.refresh_stats()

    def delete_notebook(self, notebook_name=None):
        target = notebook_name or self.selected_notebook
        if target is None: return
        
        # Handle empty or blank names gracefully
        display_name = target if target.strip() else "(Unnamed Notebook)"
        
        if messagebox.askyesno("Delete", f"Delete notebook '{display_name}' and all its notes?"):
            self.data_manager.delete_notebook(target)
            # If possible, ask the app to re-create the Notebooks view so
            # the top-level `current_view` is updated and the main area is
            # fully refreshed. Fall back to instance-level refresh if the
            # App instance cannot be found.
            app = self.app or getattr(self.master, 'master', None)
            if isinstance(app, CourseMate):
                try:
                    app.show_notebooks()
                except Exception:
                    # Fall back to internal refresh
                    self.selected_notebook = None
                    self.show_all_notebooks()
            else:
                # No app reference; refresh this view instance
                self.selected_notebook = None
                self.show_all_notebooks()

            # Update sidebar list and stats to reflect deletion
            if isinstance(self.app, CourseMate):
                try:
                    self.app.sidebar.refresh_notebooks_list()
                    self.app.sidebar.refresh_stats()
                except Exception:
                    pass

    def delete_note(self, index):
        if not self.selected_notebook: return
        if messagebox.askyesno("Delete Note", "Are you sure you want to delete this note?"):
            self.data_manager.delete_note(self.selected_notebook, index)
            self.refresh_notebook_notes() # Refresh list keeping filter state
            # Update sidebar stats
            if isinstance(self.app, CourseMate):
                self.app.sidebar.refresh_stats()

    def open_note(self, note):
        NoteWindow(self.master, note, self.colors, self.data_manager, lambda: self.show_notebook(self.selected_notebook))

class SettingsView:
    def __init__(self, master, data_manager, colors):
        self.master = master
        self.data_manager = data_manager
        self.colors = colors
        self.settings = data_manager.get_settings()
        # Built-in study templates (read-only defaults)
        self.builtin_study_templates = {
            "Cornell Notes": "Title: \n\nQuestion/Keyword\n-\n-\n\nNotes\n-\n-\n\nSummary\n-\n_",
            "Main Idea & Details": "Main Idea: ___\n\nDetail 1:\n-\n\nDetail 2:\n-\n\nDetail 3:\n-\n\nSummary:\n-",
            "Modified Frayer Model": "Definition:\n-\n\nCharacteristics:\n-\n\nExamples:\n-\n\nNon-Examples:\n-",
            "Polya's 4 Steps": "1. Understand the Problem:\n-\n\n2. Devise a Plan:\n-\n\n3. Carry Out the Plan:\n-\n\n4. Look Back:\n-",
            "5W1H": "Who:\n-\n\nWhat:\n-\n\nWhen:\n-\n\nWhere:\n-\n\nWhy:\n-\n\nHow:\n-",
            "Concept Map": "Central Concept:\n-\n\nRelated Concept 1:\n-\n\nRelated Concept 2:\n-\n\nConnections:\n-"
        }
        # User-managed categories
        self.study_templates = dict(self.settings.get("study_templates", {}))
        self.planner_templates = dict(self.settings.get("additional_templates", {}))
        # Ensure default built-in quotes are present in persistent settings
        # Merge defaults with any user-saved quotes so both appear in Settings
        try:
            existing = list(self.settings.get("quotes", []))
            merged = existing.copy()
            for dq in DEFAULT_QUOTES:
                # Add default quote only if it's not already present
                if dq not in merged:
                    merged.append(dq)
            if merged != existing:
                self.data_manager.update_setting("quotes", merged)
                # Refresh local view of settings
                self.settings = self.data_manager.get_settings()
        except Exception:
            pass
        
        self.container = ctk.CTkScrollableFrame(master, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(self.container, text="SETTINGS", font=master.master.get_font(6, "bold"), text_color=colors['main_text']).pack(anchor="w", pady=(0, 10))
        
        self.templates_frame = None
        self._setup_appearance_section()
        self._setup_inspiration_section()
        self._setup_templates_section()

    def _setup_appearance_section(self):
        frame = ctk.CTkFrame(self.container, fg_color=self.colors['card_bg'], corner_radius=10)
        frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(frame, text="Appearance", font=self.master.master.get_font(2, "bold"), text_color=self.colors['main_text']).pack(anchor="w", padx=20, pady=15)
        
        # Shared layout settings for appearance rows (label + control)
        control_width = 200

        # Theme
        row1 = ctk.CTkFrame(frame, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=5)
        row1.grid_columnconfigure(0, weight=0)
        row1.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(row1, text="Theme Color:", font=self.master.master.get_font(0), text_color=self.colors['main_text']).grid(row=0, column=0, sticky="w")

        self.theme_var = ctk.StringVar(value=self.settings.get("theme", "CourseMate Theme"))
        themes = list(THEMES.keys())
        theme_menu = ctk.CTkOptionMenu(
            row1,
            variable=self.theme_var,
            values=themes,
            command=self.change_theme,
            fg_color=self.colors.get('dropdown_bg', self.colors['main_text']),
            button_color=self.colors.get('accent'),
            text_color=self.colors.get('dropdown_text', 'white'),
            width=control_width
        )
        theme_menu.grid(row=0, column=1, sticky="e", padx=(30, 0))
        
        # Font Family
        row2 = ctk.CTkFrame(frame, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=5)
        row2.grid_columnconfigure(0, weight=0)
        row2.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(row2, text="Font Style:", font=self.master.master.get_font(0), text_color=self.colors['main_text']).grid(row=0, column=0, sticky="w")
        
        self.font_var = ctk.StringVar(value=self.settings.get("font_family", "Open Sans"))
        fonts = [ "Alice", "Courier New", "OpenDyslexic", "Open Sans"]
        font_menu = ctk.CTkOptionMenu(
            row2,
            variable=self.font_var,
            values=fonts,
            command=lambda v: self.update_setting("font_family", v),
            fg_color=self.colors.get('dropdown_bg', self.colors['main_text']),
            button_color=self.colors.get('accent'),
            text_color=self.colors.get('dropdown_text', 'white'),
            width=control_width
        )
        font_menu.grid(row=0, column=1, sticky="e", padx=(30, 0))
        # Font Size
        row3 = ctk.CTkFrame(frame, fg_color="transparent")
        row3.pack(fill="x", padx=20, pady=(5, 20))
        row3.grid_columnconfigure(0, weight=0)
        row3.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(row3, text="Font Size:", font=self.master.master.get_font(0), text_color=self.colors['main_text']).grid(row=0, column=0, sticky="w")
        
        self.size_var = ctk.StringVar(value=self.settings.get("font_size", "Normal"))
        sizes = ["Normal", "Large"]
        size_menu = ctk.CTkOptionMenu(
            row3,
            variable=self.size_var,
            values=sizes,
            command=lambda v: self.update_setting("font_size", v),
            fg_color=self.colors.get('dropdown_bg', self.colors['main_text']),
            button_color=self.colors.get('accent'),
            text_color=self.colors.get('dropdown_text', 'white'),
            width=control_width
        )
        size_menu.grid(row=0, column=1, sticky="e", padx=(30, 0))

        # # Live Theme Preview
        # preview_container = ctk.CTkFrame(frame, fg_color="transparent")
        # preview_container.pack(fill="x", padx=20, pady=(8, 12))

        # self.preview_header = ctk.CTkFrame(preview_container, fg_color=self.colors['primary_dark'], corner_radius=6)
        # self.preview_header.pack(fill="x")
        # self.preview_header_label = ctk.CTkLabel(self.preview_header, text="Header Preview", font=self.master.master.get_font(-1, "bold"), text_color=self.colors['header_text'])
        # self.preview_header_label.pack(expand=True)

        # sample_row = ctk.CTkFrame(preview_container, fg_color="transparent")
        # sample_row.pack(fill="x", pady=(8,0))

        # self.preview_sidebar = ctk.CTkFrame(sample_row, fg_color=self.colors['primary'], width=120, height=80, corner_radius=6)
        # self.preview_sidebar.pack(side="left", padx=(0,8))
        # self.preview_sidebar_label = ctk.CTkLabel(self.preview_sidebar, text="Sidebar", font=self.master.master.get_font(-2), text_color=self.colors['sidebar_text'])
        # self.preview_sidebar_label.pack(expand=True)

        # self.preview_main = ctk.CTkFrame(sample_row, fg_color=self.colors['background'], corner_radius=6)
        # self.preview_main.pack(fill="x", expand=True)
        # self.preview_main_label = ctk.CTkLabel(self.preview_main, text="Main Area", font=self.master.master.get_font(-2), text_color=self.colors['main_text'])
        # self.preview_main_label.pack(padx=8, pady=8, anchor="w")

        # # Add additional sample controls to the preview so users can see how
        # # dropdowns, entries and buttons will look in the selected theme.
        # sample_controls = ctk.CTkFrame(self.preview_main, fg_color="transparent")
        # sample_controls.pack(fill="x", padx=8, pady=(6, 10))

        # # Sample label
        # self.preview_sample_label = ctk.CTkLabel(sample_controls, text="Sample Label:", font=self.master.master.get_font(-3), text_color=self.colors['secondary_text'])
        # self.preview_sample_label.pack(side="left", padx=(0, 8))

        # # Sample dropdown
        # self.preview_sample_var = ctk.StringVar(value="Option 1")
        # self.preview_sample_dropdown = ctk.CTkOptionMenu(sample_controls, variable=self.preview_sample_var, values=["Option 1", "Option 2"], width=140,
        #              fg_color=self.colors.get('dropdown_bg', self.colors['main_text']), button_color=self.colors.get('primary'),
        #              text_color=self.colors.get('dropdown_text', 'white'))
        # self.preview_sample_dropdown.pack(side="left", padx=(0, 8))

        # # Sample entry
        # self.preview_sample_entry = ctk.CTkEntry(sample_controls, placeholder_text="Type...", width=180,
        #                      fg_color=self.colors.get('card_bg'), text_color=self.colors.get('main_text'))
        # self.preview_sample_entry.pack(side="left", padx=(0, 8))

        # # Sample action buttons
        # btns = ctk.CTkFrame(self.preview_main, fg_color="transparent")
        # btns.pack(fill="x", padx=8, pady=(0, 8))
        # self.preview_sample_primary = ctk.CTkButton(btns, text="Primary", width=100, fg_color=self.colors.get('accent'), text_color="white")
        # self.preview_sample_primary.pack(side="left", padx=(0, 8))
        # self.preview_sample_secondary = ctk.CTkButton(btns, text="Secondary", width=100, fg_color=self.colors.get('card_bg'), text_color=self.colors.get('main_text'))
        # self.preview_sample_secondary.pack(side="left")

        # # Initialize preview with current theme selection
        # try:
        #     self.preview_theme(self.theme_var.get())
        # except Exception:
        #     pass

    def _setup_inspiration_section(self):
        frame = ctk.CTkFrame(self.container, fg_color=self.colors['card_bg'], corner_radius=10)
        frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(frame, text="Inspiration & Quotes", font=self.master.master.get_font(2, "bold"), text_color=self.colors['main_text']).pack(anchor="w", padx=20, pady=15)
        
        # Timer
        row1 = ctk.CTkFrame(frame, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(row1, text="Change Quote Every (seconds):", font=self.master.master.get_font(0), text_color=self.colors['main_text']).pack(side="left")
        
        self.timer_entry = ctk.CTkEntry(row1, width=60, placeholder_text="30", fg_color=self.colors['background'], text_color=self.colors['main_text'])
        self.timer_entry.insert(0, str(self.settings.get("quote_timer", 30)))
        self.timer_entry.pack(side="left", padx=10)
        
        ctk.CTkButton(row1, text="Save Timer", width=80, command=self.save_timer,
                      fg_color=self.colors['info']).pack(side="left")
        
        # Add Quote
        row2 = ctk.CTkFrame(frame, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=(15, 5))
        ctk.CTkLabel(row2, text="Add New Quote:", font=self.master.master.get_font(0), text_color=self.colors['main_text']).pack(anchor="w")
        
        self.quote_entry = ctk.CTkEntry(row2, placeholder_text="Enter a favorite quote...", fg_color=self.colors['background'], text_color=self.colors['main_text'])
        self.quote_entry.pack(fill="x", pady=5)
        
        ctk.CTkButton(row2, text="Add Quote", command=self.add_quote,
                  fg_color=self.colors['success']).pack(anchor="e", pady=5)

        # Quotes display area (shows all saved quotes, default + user-added)
        self.quotes_display_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.quotes_display_frame.pack(fill="both", expand=False, padx=20, pady=(8, 12))

        # Use a scrollable frame in case there are many quotes
        self.quotes_list = ctk.CTkScrollableFrame(self.quotes_display_frame, fg_color="transparent", height=120)
        self.quotes_list.pack(fill="both", expand=True)

        # Populate the quotes list from settings
        self.refresh_quotes_list()

    def _setup_templates_section(self):
        if self.templates_frame is not None:
            self.templates_frame.destroy()
        self.templates_frame = ctk.CTkFrame(self.container, fg_color=self.colors['card_bg'], corner_radius=10)
        self.templates_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(self.templates_frame, text="Templates", font=self.master.master.get_font(2, "bold"), text_color=self.colors['main_text']).pack(anchor="w", padx=20, pady=15)
        ctk.CTkLabel(
            self.templates_frame,
            text="View and manage your templates. Study templates are note-taking patterns; Planner templates help organize time and tasks.",
            font=self.master.master.get_font(-2),
            text_color=self.colors['main_text'],
            wraplength=560,
            anchor="w",
            justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 10))

        # --- Separator line ---
        separator = ctk.CTkFrame(self.templates_frame, fg_color=self.colors.get('card_border', self.colors['secondary_text']), height=1)
        separator.pack(fill="x", padx=20, pady=(0, 15))

        # --- Create Custom Template Section ---
        ctk.CTkLabel(self.templates_frame, text="Create Custom Template", font=self.master.master.get_font(1, "bold"), text_color=self.colors['main_text']).pack(anchor="w", padx=20, pady=(0, 8))
        
        form = ctk.CTkFrame(self.templates_frame, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=(0, 6))

        ctk.CTkLabel(form, text="Title", font=self.master.master.get_font(0), text_color=self.colors['main_text']).grid(row=0, column=0, sticky="w", padx=(0,8), pady=(0,6))
        self.new_template_title = ctk.CTkEntry(form, placeholder_text="Template Title", fg_color=self.colors['background'], text_color=self.colors['main_text'])
        self.new_template_title.grid(row=0, column=1, sticky="ew", pady=(0,6))

        ctk.CTkLabel(form, text="Category", font=self.master.master.get_font(0), text_color=self.colors['main_text']).grid(row=0, column=2, sticky="w", padx=(16,8))
        self.new_template_category = ctk.StringVar(value="Study")
        self.new_template_category_menu = ctk.CTkOptionMenu(
            form,
            variable=self.new_template_category,
            values=["Study", "Planner"],
            fg_color=self.colors.get('dropdown_bg', self.colors['main_text']),
            button_color=self.colors.get('accent'),
            text_color=self.colors.get('dropdown_text', 'white'),
            width=120
        )
        self.new_template_category_menu.grid(row=0, column=3, sticky="w")
        form.grid_columnconfigure(1, weight=1)

        # Content textbox (full width)
        self.new_template_text = ctk.CTkTextbox(self.templates_frame, height=120, fg_color=self.colors['background'], text_color=self.colors['main_text'])
        self.new_template_text.pack(fill="x", padx=20, pady=(0, 8))

        # Action buttons
        btns = ctk.CTkFrame(self.templates_frame, fg_color="transparent")
        btns.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkButton(btns, text="Clear", width=100, fg_color=self.colors['danger'], command=self.clear_new_template_inputs).pack(side="left")
        ctk.CTkButton(btns, text="Add Template", width=130, fg_color=self.colors['success'], command=self.add_new_template).pack(side="right")

        # --- Separator line ---
        separator2 = ctk.CTkFrame(self.templates_frame, fg_color=self.colors.get('card_border', self.colors['secondary_text']), height=1)
        separator2.pack(fill="x", padx=20, pady=(0, 15))

        # --- Two-Column Layout for Template Lists ---
        columns_container = ctk.CTkFrame(self.templates_frame, fg_color="transparent")
        columns_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Left Column: Study Templates
        study_column = ctk.CTkFrame(columns_container, fg_color="transparent")
        study_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(study_column, text="Study Templates", font=self.master.master.get_font(1, "bold"), text_color=self.colors['main_text']).pack(anchor="w", pady=(0, 6))
        
        study_list = ctk.CTkScrollableFrame(study_column, fg_color="transparent", height=240)
        study_list.pack(fill="both", expand=True)
        
        study_combined = {**self.builtin_study_templates}
        for k, v in self.study_templates.items():
            study_combined[k] = v
        for title in study_combined.keys():
            is_custom = title in self.study_templates
            row = ctk.CTkFrame(study_list, fg_color="transparent", height=32)
            row.pack(fill="x", pady=3)
            try:
                row.pack_propagate(False)
            except Exception:
                pass
            ctk.CTkLabel(row, text=title, font=self.master.master.get_font(-1, "bold"), text_color=self.colors['main_text'], width=200, anchor="w").pack(side="left", padx=(8, 8))
            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.pack(side="right", padx=12, pady=2)
            ctk.CTkButton(actions, text="Edit", width=72, height=26, fg_color=self.colors['info'],
                          command=lambda t=title: self.edit_template_dialog(t, "Study")).pack(side="left")

        # Right Column: Planner Templates
        planner_column = ctk.CTkFrame(columns_container, fg_color="transparent")
        planner_column.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(planner_column, text="Planner Templates", font=self.master.master.get_font(1, "bold"), text_color=self.colors['main_text']).pack(anchor="w", pady=(0, 6))
        
        planner_list = ctk.CTkScrollableFrame(planner_column, fg_color="transparent", height=240)
        planner_list.pack(fill="both", expand=True)
        
        for title in self.planner_templates.keys():
            row = ctk.CTkFrame(planner_list, fg_color=self.colors['card_bg'], corner_radius=6, height=36)
            row.pack(fill="x", pady=4)
            try:
                row.pack_propagate(False)
            except Exception:
                pass
            ctk.CTkLabel(row, text=title, font=self.master.master.get_font(0, "bold"), text_color=self.colors['main_text'], width=200, anchor="w").pack(side="left", padx=(8, 8))
            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.pack(side="right", padx=12, pady=4)
            ctk.CTkButton(actions, text="Edit", width=72, height=26, fg_color=self.colors['info'],
                          command=lambda t=title: self.edit_template_dialog(t, "Planner")).pack(side="left", padx=(0,8))
            ctk.CTkButton(actions, text="Delete", width=72, height=26, fg_color=self.colors['danger'],
                          command=lambda t=title: self.delete_template(t, "Planner")).pack(side="left")

    def update_setting(self, key, value):
        self.data_manager.update_setting(key, value)
        # Apply settings immediately
        if isinstance(self.master.master.master, CourseMate):
             self.master.master.master.apply_settings()
        elif isinstance(self.master.master, CourseMate):
             self.master.master.apply_settings()
        else:
            messagebox.showinfo("Settings Saved", f"{key.replace('_', ' ').title()} updated! Restart app to see full changes.")

    def change_theme(self, new_theme):
        self.data_manager.update_setting("theme", new_theme)
        # Apply settings immediately
        if isinstance(self.master.master.master, CourseMate): 
            self.master.master.master.apply_settings()
        elif isinstance(self.master.master, CourseMate):
             self.master.master.apply_settings()
        else:
             print("Could not find App instance to apply theme")
             messagebox.showinfo("Theme Saved", "Theme saved! Restart to apply (Dynamic update failed).")

    def preview_theme(self, theme_name):
        """Update the small preview UI to show the selected theme without saving."""
        theme = THEMES.get(theme_name, THEMES['CourseMate Theme'])
        try:
            # Header
            self.preview_header.configure(fg_color=theme.get('primary_dark'))
            self.preview_header_label.configure(text_color=theme.get('header_text'))
            # Sidebar
            self.preview_sidebar.configure(fg_color=theme.get('primary'))
            self.preview_sidebar_label.configure(text_color=theme.get('sidebar_text'))
            # Main
            self.preview_main.configure(fg_color=theme.get('background'))
            self.preview_main_label.configure(text_color=theme.get('main_text'))
            # Sample controls (if created)
            try:
                self.preview_sample_label.configure(text_color=theme.get('secondary_text'))
            except Exception:
                pass
            try:
                self.preview_sample_dropdown.configure(fg_color=theme.get('dropdown_bg'), text_color=theme.get('dropdown_text'), button_color=theme.get('accent'))
            except Exception:
                pass
            try:
                self.preview_sample_entry.configure(fg_color=theme.get('card_bg'), text_color=theme.get('main_text'))
            except Exception:
                pass
            try:
                self.preview_sample_primary.configure(fg_color=theme.get('accent'), text_color="white")
            except Exception:
                pass
            try:
                self.preview_sample_secondary.configure(fg_color=theme.get('card_bg'), text_color=theme.get('main_text'))
            except Exception:
                pass
        except Exception:
            pass

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
            # Read current quotes from persistent settings and append
            quotes = self.data_manager.get_settings().get("quotes", [])
            quotes.append(quote)
            self.data_manager.update_setting("quotes", quotes)
            # Clear entry and refresh display
            self.quote_entry.delete(0, "end")
            messagebox.showinfo("Success", "Quote added to your collection!")
            # Refresh the displayed list so the user sees the new quote immediately
            try:
                self.refresh_quotes_list()
            except Exception:
                pass
        else:
            messagebox.showwarning("Empty", "Please enter a quote.")

    def refresh_quotes_list(self):
        """Refresh the quotes shown in Settings (default + added)."""
        # Clear existing widgets
        try:
            for w in self.quotes_list.winfo_children():
                w.destroy()
        except Exception:
            return

        quotes = self.data_manager.get_settings().get("quotes", [])
        if not quotes:
            ctk.CTkLabel(self.quotes_list, text="No saved quotes.", font=self.master.master.get_font(0, "italic"), text_color=self.colors['secondary_text']).pack(pady=8)
            return
        for idx, q in enumerate(quotes):
            # Each quote gets a framed row with the quote text and action buttons
            row = ctk.CTkFrame(self.quotes_list, fg_color=self.colors['card_bg'], corner_radius=6)
            row.pack(fill="x", pady=4, padx=4)
            # Use a larger font for quotes in the settings list for readability
            ctk.CTkLabel(row, text=f'"{q}"', font=self.master.master.get_font(0), text_color=self.colors['main_text'], wraplength=520, anchor="w", justify="left").pack(fill="x", padx=8, pady=6, side="left", expand=True)

            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.pack(side="right", padx=8, pady=6)

            # Edit button
            ctk.CTkButton(actions, text="Edit", width=70, height=28, fg_color=self.colors['info'], command=lambda i=idx: self.edit_quote(i)).pack(side="left", padx=(0,6))
            # Delete button
            ctk.CTkButton(actions, text="Delete", width=70, height=28, fg_color=self.colors['danger'], command=lambda i=idx: self.delete_quote(i)).pack(side="left")

    def edit_quote(self, index):
        """Edit an existing quote by index."""
        quotes = self.data_manager.get_settings().get("quotes", [])
        if index < 0 or index >= len(quotes):
            return
        current = quotes[index]
        dlg = InputDialog(self.master, "Edit Quote", "Modify quote:", initialvalue=current)
        self.master.wait_window(dlg)
        new_val = dlg.result
        if new_val is None:
            return
        new_val = new_val.strip()
        if not new_val:
            messagebox.showwarning("Invalid", "Quote cannot be empty.")
            return
        quotes[index] = new_val
        self.data_manager.update_setting("quotes", quotes)
        self.refresh_quotes_list()

    def delete_quote(self, index):
        """Delete quote at index after confirmation."""
        quotes = self.data_manager.get_settings().get("quotes", [])
        if index < 0 or index >= len(quotes):
            return
        if messagebox.askyesno("Delete Quote", "Delete this quote? This cannot be undone."):
            try:
                quotes.pop(index)
                self.data_manager.update_setting("quotes", quotes)
                self.refresh_quotes_list()
            except Exception:
                messagebox.showerror("Error", "Could not delete quote.")

    def add_new_template(self):
        title = (self.new_template_title.get() or "").strip()
        content = (self.new_template_text.get("1.0", "end-1c") or "").strip()
        category = self.new_template_category.get()
        if not title or not content:
            messagebox.showwarning("Invalid", "Please enter both a title and content.")
            return
        # Duplicate checks within category; study also checks against built-in
        if category == "Study":
            if title in self.builtin_study_templates or title in self.study_templates:
                messagebox.showerror("Duplicate", "A Study template with this title already exists.")
                return
            self.study_templates[title] = content
            self.data_manager.update_setting("study_templates", self.study_templates)
        else:
            if title in self.planner_templates:
                messagebox.showerror("Duplicate", "A Planner template with this title already exists.")
                return
            self.planner_templates[title] = content
            self.data_manager.update_setting("additional_templates", self.planner_templates)
        self.settings = self.data_manager.get_settings()
        messagebox.showinfo("Success", "Template added.")
        self.clear_new_template_inputs()
        self._setup_templates_section()

    def clear_new_template_inputs(self):
        try:
            self.new_template_title.delete(0, "end")
            self.new_template_text.delete("1.0", "end")
            self.new_template_category.set("Study")
        except Exception:
            pass

    def edit_template_dialog(self, template_title, category):
        if category == "Study":
            structure = self.study_templates.get(template_title, self.builtin_study_templates.get(template_title, ""))
        else:
            structure = self.planner_templates.get(template_title, "")
        def on_save(new_title, new_structure):
            new_title = new_title.strip()
            new_structure = new_structure.strip()
            if not new_title or not new_structure:
                messagebox.showwarning("Invalid", "Both title and structure are required.")
                return
            if category == "Study":
                # Check duplicates (including built-in)
                if new_title != template_title and (new_title in self.builtin_study_templates or new_title in self.study_templates):
                    messagebox.showerror("Duplicate", "A Study template with this title already exists.")
                    return
                # Apply rename/update
                if new_title != template_title:
                    self.study_templates.pop(template_title, None)
                self.study_templates[new_title] = new_structure
                self.data_manager.update_setting("study_templates", self.study_templates)
            else:
                if new_title != template_title and new_title in self.planner_templates:
                    messagebox.showerror("Duplicate", "A Planner template with this title already exists.")
                    return
                if new_title != template_title:
                    self.planner_templates.pop(template_title, None)
                self.planner_templates[new_title] = new_structure
                self.data_manager.update_setting("additional_templates", self.planner_templates)
            self.settings = self.data_manager.get_settings()
            messagebox.showinfo("Success", "Template updated!")
            self._setup_templates_section()
        TemplateDialog(self.master, title_init=template_title, structure_init=structure, on_save=on_save, is_edit=True)

    def delete_template(self, template_title, category):
        if not messagebox.askyesno("Delete Template", f"Delete template '{template_title}'? This cannot be undone."):
            return
        if category == "Study":
            if template_title in self.study_templates:
                self.study_templates.pop(template_title, None)
                self.data_manager.update_setting("study_templates", self.study_templates)
        else:
            if template_title in self.planner_templates:
                self.planner_templates.pop(template_title, None)
                self.data_manager.update_setting("additional_templates", self.planner_templates)
        self.settings = self.data_manager.get_settings()
        messagebox.showinfo("Deleted", "Template deleted.")
        self._setup_templates_section()


class SearchView:
    def __init__(self, master, data_manager, colors, query, app):
        self.master = master
        self.data_manager = data_manager
        self.colors = colors
        self.query = query.lower()
        self.app = app
        self.results = []
        
        # Main container
        self.container = ctk.CTkFrame(master, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Page Title
        ctk.CTkLabel(self.container, text="Search Results", font=app.get_font(6, "bold"), 
                    text_color=colors['main_text']).pack(anchor="w", pady=(0, 10))
        
        # Search query display
        query_frame = ctk.CTkFrame(self.container, fg_color=colors['card_bg'], corner_radius=10)
        query_frame.pack(fill="x", pady=(0, 10))
        
        query_text = f"Searching for: \"{query}\""
        ctk.CTkLabel(query_frame, text=query_text, font=app.get_font(1, "bold"), 
                    text_color=colors['main_text']).pack(anchor="w", padx=20, pady=15)
        
        # Perform search
        self._perform_search()
        
        # Results count
        count_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        count_frame.pack(fill="x", pady=(0, 10))
        
        count_text = f"Found {len(self.results)} result(s)"
        ctk.CTkLabel(count_frame, text=count_text, font=app.get_font(0, "bold"), 
                    text_color=colors['secondary_text']).pack(anchor="w")
        
        # Results list
        if self.results:
            results_frame = ctk.CTkScrollableFrame(self.container, fg_color=colors['card_bg'], corner_radius=10)
            results_frame.pack(fill="both", expand=True)
            
            for result in self.results:
                self._create_result_item(results_frame, result)
        else:
            # No results message
            empty_frame = ctk.CTkFrame(self.container, fg_color=colors['card_bg'], corner_radius=10)
            empty_frame.pack(fill="both", expand=True)
            
            ctk.CTkLabel(empty_frame, text="No notes found matching your search.", 
                        font=app.get_font(1), text_color=colors['secondary_text']).pack(pady=50)
    
    def _perform_search(self):
        """Search across all notebooks and unassigned notes"""
        self.results = []
        
        # Search in all notebooks
        notebooks = self.data_manager.get_notebooks()
        for notebook_name, notebook_data in notebooks.items():
            notes = notebook_data.get("notes", [])
            for note in notes:
                title = note.get("title", "").lower()
                content = note.get("content", "").lower()
                tags_str = " ".join(note.get('tags', [])).lower()
                
                if self.query in title or self.query in content or self.query in tags_str:
                    self.results.append({
                        "title": note.get("title", "Untitled"),
                        "content": note.get("content", ""),
                        "notebook": notebook_name,
                        "note_data": note,
                        "location": f"Notebook: {notebook_name}"
                    })
        
        # Search in unassigned notes
        unassigned = self.data_manager.data.get("unassigned_notes", [])
        for note in unassigned:
            title = note.get("title", "").lower()
            content = note.get("content", "").lower()
            tags_str = " ".join(note.get('tags', [])).lower()
            
            if self.query in title or self.query in content or self.query in tags_str:
                self.results.append({
                    "title": note.get("title", "Untitled"),
                    "content": note.get("content", ""),
                    "notebook": None,
                    "note_data": note,
                    "location": "Unassigned Notes"
                })
    
    def _create_result_item(self, parent, result):
        """Create a clickable result item card"""
        item_frame = ctk.CTkFrame(parent, fg_color=self.colors['background'], corner_radius=8)
        item_frame.pack(fill="x", padx=10, pady=5)
        
        # Make the frame clickable
        item_frame.bind("<Button-1>", lambda e: self._open_note(result))
        item_frame.configure(cursor="hand2")
        
        # Content frame
        content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=10)
        content_frame.bind("<Button-1>", lambda e: self._open_note(result))
        
        # Title
        title_label = ctk.CTkLabel(content_frame, text=result["title"], 
                                   font=self.app.get_font(1, "bold"),
                                   text_color=self.colors['main_text'], anchor="w")
        title_label.pack(anchor="w")
        title_label.bind("<Button-1>", lambda e: self._open_note(result))
        
        # Location
        location_label = ctk.CTkLabel(content_frame, text=result["location"], 
                                      font=self.app.get_font(-1),
                                      text_color=self.colors['secondary_text'], anchor="w")
        location_label.pack(anchor="w", pady=(2, 0))
        location_label.bind("<Button-1>", lambda e: self._open_note(result))
        
        # Preview (first 150 characters)
        preview = result["content"][:150]
        if len(result["content"]) > 150:
            preview += "..."
        
        if preview:
            preview_label = ctk.CTkLabel(content_frame, text=preview, 
                                        font=self.app.get_font(-1),
                                        text_color=self.colors['text'], anchor="w",
                                        wraplength=700, justify="left")
            preview_label.pack(anchor="w", pady=(5, 0))
            preview_label.bind("<Button-1>", lambda e: self._open_note(result))
    
    def _open_note(self, result):
        """Open the note in NoteWindow"""
        note_data = result["note_data"]
        notebook_name = result["notebook"]
        
        # Create NoteWindow to view/edit the note
        NoteWindow(self.master, self.data_manager, self.colors, note_data, 
                  notebook_name=notebook_name, app=self.app)


if __name__ == "__main__":
    app = CourseMate()
    app.mainloop()
