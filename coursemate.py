"""CourseMate Application Module

Core definitions for data persistence, themed UI components, note/dialog views,
and the main application shell. Comments are concise for panel review.
"""

import customtkinter as ctk
import json
import uuid
from datetime import datetime
import os
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog
import ctypes
import os

# Simple icon loading system
try:
    from PIL import Image, ImageOps
    from customtkinter import CTkImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL (Pillow) not available. Icons will not be displayed.")

def load_icon(filename, size=(20, 20)):
    """Load an icon and return a CTkImage.
    
    Simple implementation - loads the icon file as-is without tinting.
    Used for sidebar icons with pre-colored versions.
    """
    if not PIL_AVAILABLE:
        return None
    
    try:
        icon_dir = os.path.join(os.path.dirname(__file__), 'assets', 'icons')
        icon_path = os.path.join(icon_dir, filename)
        
        if not os.path.exists(icon_path):
            print(f"Icon file not found: {icon_path}")
            return None
        
        # Load and resize
        img = Image.open(icon_path).convert('RGBA')
        img = img.resize(size, Image.LANCZOS)
        
        # Create CTkImage
        ctk_img = CTkImage(light_image=img, dark_image=img, size=size)
        
        return ctk_img
    except Exception as e:
        print(f"Error loading icon {filename}: {e}")
        import traceback
        traceback.print_exc()
        return None

def load_and_tint_icon(filename, tint_color, size=(20, 20)):
    """Load and tint an icon, returning a CTkImage.
    
    Used for utility icons (refresh, edit, delete, etc.) that need dynamic coloring.
    """
    if not PIL_AVAILABLE:
        return None
    
    try:
        icon_dir = os.path.join(os.path.dirname(__file__), 'assets', 'icons')
        icon_path = os.path.join(icon_dir, filename)
        
        if not os.path.exists(icon_path):
            print(f"Icon file not found: {icon_path}")
            return None
        
        # Load and resize
        img = Image.open(icon_path).convert('RGBA')
        img = img.resize(size, Image.LANCZOS)
        
        # Tint the image
        alpha = img.split()[-1]
        gray = ImageOps.grayscale(img)
        colored = ImageOps.colorize(gray, black='#000000', white=tint_color)
        colored.putalpha(alpha)
        
        # Create CTkImage
        ctk_img = CTkImage(light_image=colored, dark_image=colored, size=size)
        
        return ctk_img
    except Exception as e:
        print(f"Error loading icon {filename}: {e}")
        import traceback
        traceback.print_exc()
        return None

import re
from tags_utils import extract_hashtags_from_text


# ------------------------
# Color utilities
# ------------------------
def darken_color(hex_color, percentage=12):
    """Darken a hex color by a given percentage.
    
    Args:
        hex_color: Hex color string (e.g., '#ffffff' or 'ffffff')
        percentage: Percentage to darken (0-100), default 12%
    
    Returns:
        Darkened hex color string with leading #
    
    Example:
        >>> darken_color('#f5f5f5', 12)
        '#d8d8d8'
    """
    try:
        # Remove # if present and ensure we have a valid hex
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return f'#{hex_color}' if not hex_color.startswith('#') else hex_color
        
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Darken by percentage (use absolute value in case negative)
        factor = 1.0 - (abs(percentage) / 100.0)
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        
        # Ensure values stay in valid range
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'
    except Exception as e:
        # On any error, return original color
        print(f"Warning: Could not darken color {hex_color}: {e}")
        return f'#{hex_color}' if not hex_color.startswith('#') else hex_color


# ------------------------
# Simple tooltip class for hover text
# ------------------------
class ToolTip:
    """Create a tooltip for a given widget."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip, add="+")
        self.widget.bind("<Leave>", self.hide_tooltip, add="+")
    
    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 5
        y = self.widget.winfo_rooty() + (self.widget.winfo_height() // 2)
        
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=self.text, justify='left',
                        background="#333333", foreground="#ffffff",
                        relief='solid', borderwidth=1,
                        font=("Open Sans", 10, "normal"),
                        padx=8, pady=4)
        label.pack()
    
    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


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

# ============================================================================
# CONFIGURATION & THEMES
# ============================================================================

THEMES = {
    'CourseMate Theme': {
        # Header colors
        'header_bg':        '#253241',
        'header_text':      '#F4F4F4',
        'header_subtext':   '#a2b6c4',
        # Sidebar colors
        'sidebar_bg':       '#253241',
        'sidebar_button':   '#334a66',
        'sidebar_hover':    '#405977',
        'sidebar_text':     '#F4F4F4',
        'sidebar_label':    '#a2b6c4',
        # Main content colors
        'primary':          '#334a66',
        'accent':           '#4a90e2',
        'background':       '#f4f7fb',
        'card_bg':          '#e1e7ed',
        'card_border':      '#c2ccd6',
        'card_hover':       '#cfd8e1',
        'main_text':        '#0b2740',
        'secondary_text':   '#a2b6c4',
        # UI element colors
        'dropdown_bg':      '#253241',
        'dropdown_text':    '#F4F4F4',
        'button_primary':   '#334a66',
        'button_text':      '#ffffff',
        'success':          '#27ae60',
        'info':             '#3498db',
        'warning':          '#ffe082',
        'danger':           '#e74c3c',
        'muted':            '#9aa6b1'
    },
    'Light Theme': {
        # Header colors
        'header_bg':        '#e0e0e0',
        'header_text':      '#0b2740',
        'header_subtext':   '#6b7280',
        # Sidebar colors  
        'sidebar_bg':       '#e0e0e0',
        'sidebar_button':   '#334a66',
        'sidebar_hover':    '#405977',
        'sidebar_text':     '#F4F4F4',
        'sidebar_label':    '#6b7280',
        # Main content colors
        'primary':          '#f5f5f5',
        'accent':           '#2196f3',
        'background':       '#ffffff',
        'card_bg':          '#f5f5f5',
        'card_border':      '#e0e0e0',
        'card_hover':       '#eeeeee',
        'main_text':        '#0b2740',
        'secondary_text':   '#6b7280',
        # UI element colors
        'dropdown_bg':      '#0b2740',
        'dropdown_text':    '#ffffff',
        'button_primary':   '#1976d2',
        'button_text':      '#ffffff',
        'success':          '#4caf50',
        'info':             '#2196f3',
        'warning':          '#ffeb3b',
        'danger':           '#f44336',
        'muted':            '#9e9e9e'
    },
    'Dark Theme': {
        # Header colors
        'header_bg':        '#172027',
        'header_text':      '#ffffff',
        'header_subtext':   '#a2b6c4',
        # Sidebar colors
        'sidebar_bg':       '#172027',
        'sidebar_button':   '#253244',
        'sidebar_hover':    '#2d4358',
        'sidebar_text':     '#ffffff',
        'sidebar_label':    '#a2b6c4',
        # Main content colors
        'primary':          '#253244',
        'accent':           '#3f7fbf',
        'background':       '#0b0f12',
        'card_bg':          '#1a2631',
        'card_border':      '#2d4358',
        'card_hover':       '#273544',
        'main_text':        '#e6eef6',
        'secondary_text':   '#a2b6c4',
        # UI element colors
        'dropdown_bg':      '#253244',
        'dropdown_text':    '#ffffff',
        'button_primary':   '#253244',
        'button_text':      '#ffffff',
        'success':          '#27ae60',
        'info':             '#3498db',
        'warning':          '#cf6679',
        'danger':           '#e74c3c',
        'muted':            '#9aa6b1'
    },
    'Baby Pink': {
        # Header colors
        'header_bg':        '#f8bbd0',
        'header_text':      '#0b2740',
        'header_subtext':   '#7b1e5f',
        # Sidebar colors
        'sidebar_bg':       '#f8bbd0',
        'sidebar_button':   '#d81b60',
        'sidebar_hover':    "#bd1855",
        'sidebar_text':     '#F4F4F4',
        'sidebar_label':    '#7b1e5f',
        # Main content colors
        'primary':          '#fce4ec',
        'accent':           '#ec407a',
        'background':       '#fff0f5',
        'card_bg':          "#fbe0e4",
        'card_border':      '#f8bbd0',
        'card_hover':       '#ffcdd2',
        'main_text':        '#0b2740',
        'secondary_text':   '#7b1e5f',
        # UI element colors
        'dropdown_bg':      '#0b2740',
        'dropdown_text':    '#ffffff',
        'button_primary':   '#d81b60',
        'button_text':      '#ffffff',
        'success':          '#66bb6a',
        'info':             '#42a5f5',
        'warning':          '#ffee58',
        'danger':           '#ef5350',
        'muted':            '#bdbdbd'
    },
    'Baby Blue': {
        # Header colors
        'header_bg':        '#b3e5fc',
        'header_text':      '#0b2740',
        'header_subtext':   '#2563a8',
        # Sidebar colors
        'sidebar_bg':       '#b3e5fc',
        'sidebar_button':   "#26a7e3",
        'sidebar_hover':    "#0b91cf",
        'sidebar_text':     '#F4F4F4',
        'sidebar_label':    '#2563a8',
        # Main content colors
        'primary':          '#e1f5fe',
        'accent':           '#29b6f6',
        'background':       '#f0f8ff',
        'card_bg':          "#c5e3f9",
        'card_border':      "#4babef",
        'card_hover':       '#bbdefb',
        'main_text':        '#0b2740',
        'secondary_text':   '#2563a8',
        # UI element colors
        'dropdown_bg':      '#0b2740',
        'dropdown_text':    '#ffffff',
        'button_primary':   '#0277bd',
        'button_text':      '#ffffff',
        'success':          '#66bb6a',
        'info':             '#29b6f6',
        'warning':          '#ffee58',
        'danger':           '#ef5350',
        'muted':            '#bdbdbd'
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
    "additional_templates": {}
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
    """Persistent storage layer.

    Responsibilities:
    - Load / save JSON data file
    - Migrate legacy structures to current schema
    - Provide helper methods for notebooks, notes, tasks, and settings.
    """
    def __init__(self, filepath="Coursemate_data.json"):
        self.filepath = Path(filepath)
        self.data = {
            "notebooks": {},
            "unassigned_notes": [],
            "settings": DEFAULT_SETTINGS.copy()
        }
        self.load_data()

    def load_data(self):
        def migrate_note(note, notebook_name=None):
            # Ensure notebook field
            note['notebook'] = notebook_name if notebook_name else None
            # Ensure id field
            if 'id' not in note or not note['id']:
                note['id'] = str(uuid.uuid4())
            # Standardize date fields to ISO 8601
            def to_iso(dt):
                if not dt:
                    return datetime.now().isoformat()
                try:
                    # Try ISO first
                    return datetime.fromisoformat(dt).isoformat()
                except Exception:
                    # Try known formats
                    for fmt in ["%B %d, %Y | %I:%M%p", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
                        try:
                            return datetime.strptime(dt, fmt).isoformat()
                        except Exception:
                            continue
                return datetime.now().isoformat()
            note['created'] = to_iso(note.get('created'))
            if 'modified' in note:
                note['modified'] = to_iso(note.get('modified'))
            return note

        if hasattr(self, 'filepath') and self.filepath.exists():
            try:
                with open(self.filepath, 'r') as f:
                    loaded_data = json.load(f)
                notebooks = loaded_data.get("notebooks", {})
                for code, nb_data in notebooks.items():
                    if "name" not in nb_data or not nb_data.get("name"):
                        nb_data["name"] = code
                    nb_data.pop("tasks", None)
                    nb_data.pop("completed_tasks", None)
                    notes = nb_data.get('notes', [])
                    for i, note in enumerate(notes):
                        notes[i] = migrate_note(note, nb_data['name'])
                self.data["notebooks"] = notebooks
                self.data["unassigned_notes"] = [migrate_note(n, None) for n in loaded_data.get("unassigned_notes", [])]
                saved_settings = loaded_data.get("settings", {})
                for k, v in DEFAULT_SETTINGS.items():
                    if k not in saved_settings:
                        saved_settings[k] = v
                # Remove legacy custom_templates migration (no longer needed)
                if "study_templates" not in saved_settings:
                    saved_settings["study_templates"] = {}
                if "additional_templates" not in saved_settings:
                    saved_settings["additional_templates"] = {}
                if not saved_settings["additional_templates"]:
                    saved_settings["additional_templates"] = DEFAULT_ADDITIONAL_TEMPLATES.copy()
                move_keys = [
                    k for k in list(saved_settings.get("study_templates", {}).keys())
                    if k.lower() in ("weekly planning", "weekly planner", "weekly overview")
                ]
                for k in move_keys:
                    val = saved_settings["study_templates"].pop(k)
                    if k not in saved_settings["additional_templates"]:
                        saved_settings["additional_templates"][k] = val
                self.data["settings"] = saved_settings
                self._cleanup_invalid_notebooks()
            except Exception as e:
                print(f"Error loading data: {e}")
        else:
            self.save_data()
    
    def _cleanup_invalid_notebooks(self):
        """Remove notebooks with empty or whitespace-only codes"""
        invalid_codes = [code for code in self.data["notebooks"].keys() if not code or not code.strip()]
        if invalid_codes:
            print(f"Cleaning up {len(invalid_codes)} invalid notebook(s)...")
            for code in invalid_codes:
                del self.data["notebooks"][code]
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
        return self.data["notebooks"]

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
        for code, nb_data in self.data["notebooks"].items():
            if nb_data.get("name") == notebook_name:
                nb_data["notes"].append(note)
                self.save_data()
                break

    def add_notebook(self, name, code="", instructor=""):
        # Course code is now required and must be unique (case-insensitive)
        if not code or not code.strip():
            return False, "Course code is required."
        
        code = code.strip()
        existing_codes = [nb.get("code", "").lower() for nb in self.data["notebooks"].values()]
        if code.lower() in existing_codes:
            return False, "A notebook with this course code already exists."
        
        # Name can be duplicate as long as course code is unique
        self.data["notebooks"][name] = {
            "notes": [],
            "code": code,
            "instructor": instructor
        }
        self.save_data()
        return True, "Notebook created successfully."

    def rename_notebook(self, old_name, new_name):
        # Find notebook by name, update its stored name
        for code, nb_data in self.data["notebooks"].items():
            if nb_data.get("name") == old_name:
                nb_data["name"] = new_name
                self.save_data()
                return True
        return False

    def delete_notebook(self, name):
        # Find and delete notebook by name
        for code, nb_data in list(self.data["notebooks"].items()):
            if nb_data.get("name") == name:
                del self.data["notebooks"][code]
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
            for code, nb_data in self.data["notebooks"].items():
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
        for code, nb_data in self.data["notebooks"].items():
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
    """Main application window.

    Sets up global theme, fonts, header, sidebar, and view switching.
    """
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
        self.grid_columnconfigure(0, weight=0)
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
        self.header = ctk.CTkFrame(self, fg_color=self.colors['header_bg'], corner_radius=0)
        self.header.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # Header content: centered title and full slogan
        self.header_inner = ctk.CTkFrame(self.header, fg_color=self.colors['header_bg'])
        self.header_inner.pack(fill="both", expand=True)

        self.header_title_label = ctk.CTkLabel(self.header_inner, text="CourseMate",
                 font=self.get_font(8, "bold"), text_color=self.colors['header_text'])
        self.header_title_label.pack(pady=(8, 0))

        self.header_slogan_label = ctk.CTkLabel(self.header_inner,
                 text="Stay Organized • Think Smarter • Learn Deeper • Solve Problems Better",
                 font=self.get_font(0, "bold"), text_color=self.colors['header_subtext'], wraplength=900, justify="center")
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
        self.sidebar = Sidebar(self, self.data_manager, self.colors, self.show_home, self.show_notebooks, self.show_settings, about_cb=self.show_about)
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

    def show_about(self):
        """Show the About CourseMate page."""
        self.clear_main_area()
        self.current_view = AboutView(self.main_area, self.data_manager, self.colors)

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
        """Return a font tuple applying adaptive scaling.

        OpenDyslexic renders visually larger at the same point size; apply
        a reduction factor so normal and large modes remain readable and
        avoid overflow in compact UI areas (e.g., inspiration section).
        """
        size = self.base_font_size + size_offset
        try:
            if self.font_family.lower().startswith("opendyslexic"):
                # Empirical adjustment: reduce about 15% while preserving legibility
                size = max(8, int(round(size * 0.85)))
        except Exception:
            pass
        return (self.font_family, size, weight, slant)

    def apply_settings(self):
        settings = self.data_manager.get_settings()
        
        # Update Theme
        theme_name = settings.get("theme", "CourseMate Theme")
        if theme_name in THEMES:
            self.current_theme = theme_name
            self.colors = THEMES[theme_name]
            # No icon cache to clear - icons are loaded fresh each time
        
        # Update Font
        self.font_family = settings.get("font_family", "Open Sans")
        self.font_size_mode = settings.get("font_size", "Normal")
        self.base_font_size = 14 if self.font_size_mode == "Normal" else 18
        
        # Preserve current active page before destroying sidebar
        current_active_page = self.sidebar.active_page if self.sidebar else "Home"
        
        # Update Sidebar (keep it in row 1 so header stays in row 0)
        self.sidebar.destroy()
        self.sidebar = Sidebar(self, self.data_manager, self.colors, self.show_home, self.show_notebooks, self.show_settings, about_cb=self.show_about, initial_page=current_active_page)
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        
        # Update Main Area Background
        self.main_area.configure(fg_color=self.colors['background'])

        # Update Header colors so theme changes affect it too
        try:
            # Header background
            if hasattr(self, 'header') and self.header:
                try:
                    self.header.configure(fg_color=self.colors.get('header_bg', self.colors.get('primary')))
                except Exception:
                    pass
                # Update header inner frame and labels (we store references during init)
                try:
                    if hasattr(self, 'header_inner') and self.header_inner:
                        try:
                            self.header_inner.configure(fg_color=self.colors.get('header_bg', self.colors.get('primary')))
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
    """Compact left navigation: icon-only navigation with an inspiration toggle at the bottom."""
    def __init__(self, master, data_manager, colors, home_cb, notebooks_cb, settings_cb, about_cb=None, initial_page="Home"):
        super().__init__(master, width=60, corner_radius=0, fg_color=colors['sidebar_bg'])
        self.pack_propagate(False)
        self.grid_propagate(False)

        self.colors = colors
        self.data_manager = data_manager
        self.home_cb = home_cb
        self.notebooks_cb = notebooks_cb
        self.settings_cb = settings_cb
        self.about_cb = about_cb or (lambda: None)
        self.active_page = initial_page
        self.nav_buttons = {}
        self._inspiration_overlay = None
        self._current_quote = None

        # Create top navigation icon stack
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent", width=56)
        self.nav_frame.pack(side="top", pady=(8), padx=2)
        self._create_nav_btn("Home", self._wrap_callback(self.home_cb, "Home"), icon_filename='icon_home_32_white.png', btn_width=44)
        self._create_nav_btn("Notebooks", self._wrap_callback(self.notebooks_cb, "Notebooks"), icon_filename='icon_notebook_32_white.png', btn_width=44)
        self._create_nav_btn("Settings", self._wrap_callback(self.settings_cb, "Settings"), icon_filename='icon_settings_32_white.png', btn_width=44)
        self._create_nav_btn("About", self._wrap_callback(self.about_cb, "About"), icon_filename='icon_info_32_white.png', btn_width=44)

        # Spacer to push nav icons to the top (no inspiration button)
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

    def _wrap_callback(self, callback, page_name):
        def _wrapped():
            try:
                self.set_active_page(page_name)
            except Exception:
                pass
            try:
                callback()
            except Exception:
                pass
        return _wrapped

    def _create_nav_btn(self, text, command, icon_filename=None, container=None, pack_side='top', set_active=True, btn_width=48, no_text_fallback=False):
        """Create a navigation button with icon or text fallback.
        Only uses white icons for all states.
        """
        is_active = (text == self.active_page) if set_active else False
        bg_color = self.colors.get('sidebar_button', '#334a66')
        hover_color = self.colors.get('sidebar_hover', '#405977')
        btn_state = "normal"
        img = None
        if icon_filename:
            try:
                img = load_icon(icon_filename, size=(32, 32))
            except Exception as e:
                print(f"✗ Failed to load icon for {text}: {e}")
        def on_click():
            if set_active:
                self.set_active_page(text)
            try:
                command()
            except Exception:
                pass
        if img:
            btn = ctk.CTkButton(
                container or self.nav_frame,
                text="",
                image=img,
                command=on_click,
                fg_color=bg_color,
                hover_color=hover_color,
                width=btn_width,
                height=btn_width,
                corner_radius=10,
                state=btn_state
            )
        else:
            if no_text_fallback:
                return
            print(f"  Using text fallback for {text}")
            btn = ctk.CTkButton(
                container or self.nav_frame,
                text=text,
                command=on_click,
                fg_color=bg_color,
                hover_color=hover_color,
                width=btn_width,
                height=btn_width,
                corner_radius=10,
                font=self.master.get_font(-1, "bold"),
                state=btn_state
            )
        btn.pack(side=pack_side, padx=4, pady=4)
        ToolTip(btn, text)
        self.nav_buttons[text] = {
            'button': btn,
            'icon_filename': icon_filename,
            'image': img,
            'set_active': set_active
        }

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
        # Quick access list removed in compact sidebar; keep method for compatibility
        return

    def open_notebook(self, name):
        # Switch to Notebooks view and select the notebook
        self.notebooks_cb(name)
        # Ideally, we'd pass the notebook name to the view, but we'll implement that later
        # by storing 'selected_notebook' in the app state or similar.

    
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

    def set_active_page(self, page_name):
        """Update the active page and refresh button styles."""
        if self.active_page == page_name:
            return  # Already active
        
        self.active_page = page_name
        
        # Refresh all navigation buttons
        for btn_text, btn_info in self.nav_buttons.items():
            is_active = (btn_text == page_name)
            btn = btn_info['button']
            icon_filename = btn_info['icon_filename']
            
            # Set background color based on active state
            if is_active:
                bg_color = self.colors.get('accent', '#4a90e2')
            else:
                bg_color = self.colors.get('button_primary', '#334a66')
            
            # Update button background
            btn.configure(fg_color=bg_color)
            
            # Reload and update icon if present
            if icon_filename:
                # Determine which icon file to load based on active state
                base_name = icon_filename.replace('.png', '')
                suffix = 'white'
                actual_filename = f"{base_name}_{suffix}.png"
                
                try:
                    new_img = load_icon(actual_filename, size=(24, 24))
                    if new_img:
                        btn.configure(image=new_img)
                        btn_info['image'] = new_img  # Update stored reference
                except Exception as e:
                    print(f"Failed to update icon for {btn_text}: {e}")



# Small modal dialog used for creating/editing templates
class LoadingDialog(ctk.CTkToplevel):
    """Simple loading indicator for AI operations."""
    def __init__(self, master, message="Working..."):
        super().__init__(master)
        self.title("")
        self.geometry("300x100")
        self.resizable(False, False)
        try:
            self.transient(master)
            self.overrideredirect(True)  # Remove window decorations
        except Exception:
            pass
        
        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.winfo_screenheight() // 2) - (100 // 2)
        self.geometry(f"300x100+{x}+{y}")
        
        ctk.CTkLabel(self, text=message, font=("Open Sans", 14)).pack(expand=True)
        self.update()


class TemplateDialog(ctk.CTkToplevel):
    """Modal dialog for creating or editing a user template."""
    def __init__(self, master, title_init="", structure_init="", on_save=None, is_edit=False, insert_mode=False):
        super().__init__(master)
        self.on_save = on_save
        self.is_edit = is_edit
        self.insert_mode = insert_mode  # New flag for AI result insertion
        self.title("Template Editor" if not insert_mode else "AI Result")
        self.geometry("480x400")
        self.resizable(False, False)
        try:
            self.transient(master)
            self.grab_set()
        except Exception:
            pass
        
        # Get app instance for font access
        app = self._get_app_instance(master)
        font_normal = app.get_font(-2) if app else ("Open Sans", 12)
        font_bold = app.get_font(-2, "bold") if app else ("Open Sans", 12, "bold")

        ctk.CTkLabel(self, text="Template title:", font=font_bold).pack(anchor="w", padx=16, pady=(12, 4))
        self.title_entry = ctk.CTkEntry(self, placeholder_text="Enter template title", font=font_normal,
                                         fg_color=master.colors.get('card_bg', master.colors['background']),
                                         text_color=master.colors['main_text'])
        self.title_entry.pack(fill="x", padx=16, pady=(0, 8))
        # Validation bindings for template title (single line + length)
        try:
            self.title_entry.bind("<KeyRelease>", self._validate_title_live)
            self.title_entry.bind("<Return>", self._on_title_return)
            self.title_entry.bind("<FocusOut>", self._validate_title_on_blur)
        except Exception:
            pass
        self.title_entry.insert(0, title_init)

        ctk.CTkLabel(self, text="Template structure:", font=font_bold).pack(anchor="w", padx=16, pady=(0, 4))
        self.structure_text = ctk.CTkTextbox(self, font=font_normal, height=200,
                                              fg_color=master.colors.get('background', '#ffffff'),
                                              text_color=master.colors['main_text'])
        self.structure_text.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        self.structure_text.insert("1.0", structure_init)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(0, 12))
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy).pack(side="right", padx=(8, 0))
        save_text = "Insert" if self.insert_mode else "Save"
        ctk.CTkButton(btn_frame, text=save_text, command=self._on_save).pack(side="right", padx=(0, 8))

    def _on_save(self):
        title = self.title_entry.get().strip()
        structure = self.structure_text.get("1.0", "end-1c").strip()
        if self.insert_mode:
            # For AI results, just need content to insert
            if not structure:
                messagebox.showwarning("Empty", "No content to insert.")
                return
            if self.on_save:
                try:
                    self.on_save(structure)  # Pass only content for insertion
                except Exception as e:
                    messagebox.showerror("Error", str(e))
                    return
        else:
            # Regular template save mode
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
    
    def _get_app_instance(self, widget):
        """Walk up widget hierarchy to find CourseMate app instance."""
        try:
            current = widget
            while current:
                if isinstance(current, CourseMate):
                    return current
                current = current.master if hasattr(current, 'master') else None
        except Exception:
            pass
        return None


# Small modal dialog for input (replaces simpledialog.askstring)
class InputDialog(ctk.CTkToplevel):
    """Generic single-field input dialog used in place of simpledialog.askstring."""
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
        
        # Get app instance for font access
        app = self._get_app_instance(master)
        font_normal = app.get_font(-3) if app else ("Open Sans", 11)

        ctk.CTkLabel(self, text=prompt, font=font_normal).pack(pady=(20, 10), padx=20, anchor="w")

        self.entry = ctk.CTkEntry(self, width=360,
                                   fg_color=master.colors.get('card_bg', master.colors['background']),
                                   text_color=master.colors['main_text'])
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
    
    def _get_app_instance(self, widget):
        """Walk up widget hierarchy to find CourseMate app instance."""
        try:
            current = widget
            while current:
                if isinstance(current, CourseMate):
                    return current
                current = current.master if hasattr(current, 'master') else None
        except Exception:
            pass
        return None


class HomeView:
    """Primary note authoring view.

    Provides template insertion, notebook assignment, hashtag-based tagging,
    and plain-text editing with lightweight bullet assistance.
    """
    # Removed legacy duplicate initialization block.
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
        ctk.CTkLabel(self.container, text="HOME", font=app.get_font(3, "bold"), text_color=colors['main_text']).pack(anchor="w", pady=(0, 2))
        
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
            width=180,
            font=self.app.get_font(0)
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
            width=180,
            font=self.app.get_font(0)
        )
        self.planner_template_dropdown.pack(side="left")

        # Actions row (Save only). Clear content relocated above textbox.
        self.actions_frame = ctk.CTkFrame(self.write_frame, fg_color="transparent")
        self.actions_frame.pack(fill="x", padx=20, pady=(0, 10))
        # store reference so we can enable/disable based on validation
        self.save_btn = ctk.CTkButton(self.actions_frame, text="Save Note", command=self.save_note,
              fg_color=self.colors['success'], hover_color='#219150', text_color="white", width=110,
              font=self.app.get_font(0, "bold"))
        self.save_btn.pack(side="right", pady=(2,0))
        # Title Entry
        self.title_entry = ctk.CTkEntry(self.write_frame, placeholder_text="Note Title (Required)", 
                font=self.app.get_font(0, "bold"), height=40,
                fg_color=self.colors['background'], text_color=self.colors['main_text'], border_width=0)
        self.title_entry.pack(fill="x", padx=20, pady=(0, 10))
       
        
        # Formatting toolbar removed.
        
        # Note: tags are now embedded directly in content as hashtags (e.g. #math).
        # We no longer present a separate tag entry or chips UI in the write area.
        
        # Clear Content button above textbox
        content_controls = ctk.CTkFrame(self.write_frame, fg_color="transparent")
        content_controls.pack(fill="x", padx=20, pady=(0,4))
        ctk.CTkButton(content_controls, text="Clear Content", command=self.clear_content_area,
              fg_color=self.colors['danger'], hover_color='#c0392b', text_color="white", width=120,
              font=self.app.get_font(-1, "bold")).pack(side="right")
        # Text Area with placeholder support
        self.text_area = ctk.CTkTextbox(self.write_frame, font=self.app.get_font(1),
            fg_color=self.colors['background'], text_color=self.colors['main_text'],
            wrap="word", corner_radius=10)
        self.text_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self._content_placeholder_text = (
            "Start writing your note here... Use #hashtags (e.g. #math). "
            "Type '- ' (dash-space) for bullets; continue the list."
        )
        self._placeholder_active = False
        self._init_content_placeholder()
        
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
                                                       text_color=self.colors.get('dropdown_text', 'white'), width=180,
                                                       font=self.app.get_font(0))
            self.notebook_dropdown.pack(side="left", padx=(0, 20))


    def _setup_notes_ui(self):
        # Tab Bar
        tab_frame = ctk.CTkFrame(self.notes_frame, fg_color="transparent")
        tab_frame.pack(fill="x", padx=10, pady=(18, 0))
        self.tab_var = ctk.StringVar(value="Unassigned")
        tab_names = ["Recent", "Assigned", "Unassigned"]
        for tab in tab_names:
            btn = ctk.CTkButton(tab_frame, text=tab, width=110,
                fg_color=self.colors['accent'] if tab == "Unassigned" else self.colors['card_bg'],
                text_color="white" if tab == "Unassigned" else self.colors['main_text'],
                font=self.app.get_font(0, "bold"),
                command=lambda t=tab: self._switch_tab(t))
            btn.pack(side="left", padx=(0,8))
            setattr(self, f"tab_btn_{tab}", btn)

        # Search Bar
        search_frame = ctk.CTkFrame(self.notes_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=(8, 0))
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Find by name, tags or keyword", 
                                         fg_color=self.colors['background'], text_color=self.colors['main_text'],
                                         height=30, font=self.app.get_font(0))
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.filter_notes)

        # Refresh Button
        # Try to load a tinted refresh icon from assets; fall back to emoji if unavailable
        try:
            img = load_and_tint_icon('icon_refresh_24.png', self.colors.get('accent', '#4a90e2'), size=(18, 18))
       
        except Exception:
            img = None
        if img:
            # Keep a reference to avoid GC
            self._img_refresh = img
            refresh_btn = ctk.CTkButton(search_frame, image=self._img_refresh, text="", width=30, height=30,
                fg_color=self.colors['accent'], command=self.refresh_notes_list)
        else:
            refresh_btn = ctk.CTkButton(search_frame, text="🔄", width=30, height=30,
                fg_color=self.colors['accent'], text_color="white",
                font=self.app.get_font(0, "bold"),
                command=self.refresh_notes_list)
        refresh_btn.pack(side="right", padx=(8, 0))

        # Notes List Area (will be swapped per tab)
        self.notes_list_container = ctk.CTkFrame(self.notes_frame, fg_color="transparent")
        self.notes_list_container.pack(fill="both", expand=True, padx=10, pady=(8,10))
        self.notes_list = None
        self._switch_tab("Unassigned")

    def _switch_tab(self, tab_name):
        self.tab_var.set(tab_name)
        # Update tab button colors
        for t in ["Recent", "Assigned", "Unassigned"]:
            btn = getattr(self, f"tab_btn_{t}", None)
            if btn:
                btn.configure(fg_color=self.colors['accent'] if t == tab_name else self.colors['card_bg'],
                              text_color="white" if t == tab_name else self.colors['main_text'])
        # Clear previous list
        for w in self.notes_list_container.winfo_children():
            w.destroy()
        self.notes_list = ctk.CTkScrollableFrame(self.notes_list_container, fg_color="transparent")
        self.notes_list.pack(fill="both", expand=True)
        self.refresh_notes_list()

    def filter_notes(self, event=None):
        self.refresh_notes_list()

    # NOTE: `refresh_notes_list` was previously defined twice. The canonical
    # implementation lives later in the file; the duplicate earlier version
    # has been removed to avoid accidental overrides.

    def _get_recent_notes(self, count=15):
        # Gather all notes with created date
        notes = []
        # Unassigned
        for n in self.data_manager.get_unassigned_notes():
            notes.append({**n, "_notebook": None})
        # Notebooks
        for nb_name, nb_data in self.data_manager.get_notebooks().items():
            for n in nb_data.get("notes", []):
                notes.append({**n, "_notebook": nb_data.get("name", nb_name)})
        # Sort by created date (newest first)
        def get_dt(note):
            try:
                return datetime.strptime(note.get('created', ''), "%B %d, %Y | %I:%M%p")
            except Exception:
                return datetime.min
        notes.sort(key=get_dt, reverse=True)
        return notes[:count]

    def _get_assigned_notes(self):
        notes = []
        for nb_name, nb_data in self.data_manager.get_notebooks().items():
            for n in nb_data.get("notes", []):
                notes.append({**n, "_notebook": nb_data.get("name", nb_name)})
        notes.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return notes

    def _create_note_card(self, note, tab=None):
        border_color = self.colors.get('card_border', self.colors.get('muted', '#68707a'))
        corner = 12
        card = ctk.CTkFrame(self.notes_list, fg_color=self.colors['card_bg'], corner_radius=corner, border_width=2, border_color=border_color)
        card.pack(fill="x", pady=5)
        card.bind("<Button-1>", lambda e, n=note: self.open_note_window(n))
        # Hover color change removed
        title = note.get('title', 'Untitled')
        created_str = note.get('created', '')
        try:
            created_dt = datetime.strptime(created_str, "%B %d, %Y | %I:%M%p")
            date_str = created_dt.strftime("%b %d")
        except Exception:
            date_str = created_str.split('|')[0].strip() if '|' in created_str else created_str.split(' ')[0]
        content_words = note.get('content', '').split()
        preview_text = " ".join(content_words[:3]) if content_words else ""
        lbl_title = ctk.CTkLabel(card, text=title, font=self.app.get_font(-1, "bold"), text_color=self.colors['main_text'], anchor="w")
        lbl_title.pack(fill="x", padx=10, pady=(5, 0))
        lbl_title.bind("<Button-1>", lambda e, n=note: self.open_note_window(n))
        meta_text = f"{date_str} | {preview_text}"
        if tab in ("Recent", "All"):
            nb_name = note.get('_notebook')
            if nb_name:
                meta_text += f" | 📒 {nb_name}"
        lbl_meta = ctk.CTkLabel(card, text=meta_text, font=self.app.get_font(-3), text_color=self.colors['secondary_text'], anchor="w")
        lbl_meta.pack(fill="x", padx=10, pady=(0, 5))
        lbl_meta.bind("<Button-1>", lambda e, n=note: self.open_note_window(n))
        tags = note.get('tags', [])
        if tags:
            tags_text = " ".join([f"#{t}" if not t.startswith('#') else t for t in tags])
            tag_lbl = ctk.CTkLabel(card, text=tags_text, font=self.app.get_font(-3, "italic"), text_color=self.colors['accent'], anchor="w")
            tag_lbl.pack(fill="x", padx=10, pady=(0, 5))
            tag_lbl.bind("<Button-1>", lambda e, n=note: self.open_note_window(n))
        # Add Open Note button
        ctk.CTkButton(card, text="Open Note", command=lambda n=note: self.open_note_window(n),
            fg_color=self.colors.get('button_primary', self.colors['primary']),
            text_color=self.colors.get('button_text', 'white'),
            height=25, font=self.app.get_font(-3)).pack(fill="x", padx=10, pady=(0, 8))
        
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

    def clear_content_area(self):
        """Clear only the content textbox and restore placeholder (title remains)."""
        current = self.text_area.get("1.0", "end-1c").strip()
        if not current:
            return
        if messagebox.askyesno("Clear Content", "Clear all note content? Title will remain."):
            self.text_area.delete("1.0", "end")
            self._restore_content_placeholder_if_empty()

    def clear_write_area(self):
        """Legacy full clear (title + content); retained for compatibility."""
        if not self.text_area.get("1.0", "end-1c").strip() and not self.title_entry.get().strip():
            return
        if messagebox.askyesno("Clear Note", "Are you sure you want to clear the current note (title + content)?"):
            self.title_entry.delete(0, "end")
            self.text_area.delete("1.0", "end")
            self.notebook_var.set("• Unassigned Notes")
            try:
                self.study_template_var.set("Select...")
                self.planner_template_var.set("Select...")
            except Exception:
                pass
            self._restore_content_placeholder_if_empty()
    
    # Formatting toolbar removed.
    def _on_text_area_key_release(self, event):
        """Handle key releases: auto-bullet conversion, continuation + hashtag highlight."""
        if event.keysym == "Return":
            self._handle_enter_key()
        elif event.keysym == "space":
            self._convert_dash_to_bullet()
        try:
            highlight_hashtags_in_textbox(self.text_area, self.colors.get('accent', '#4a90e2'))
        except Exception:
            pass
    
    def _convert_dash_to_bullet(self):
        """Convert '- ' to '• ' when user types dash-space."""
        try:
            cursor_pos = self.text_area.index("insert")
            line_num = int(cursor_pos.split('.')[0])
            col_num = int(cursor_pos.split('.')[1])
            
            # Get current line content up to cursor
            line_start = f"{line_num}.0"
            current_line = self.text_area.get(line_start, cursor_pos)
            
            # Check if line ends with "- " (dash + space we just typed)
            if current_line.endswith("- "):
                # Remove the "- " and insert "• "
                delete_start = f"{line_num}.{col_num - 2}"
                self.text_area.delete(delete_start, cursor_pos)
                self.text_area.insert(delete_start, "• ")
        except Exception:
            pass
    
    def _init_content_placeholder(self):
        """Insert placeholder text if empty; style with secondary color."""
        if self.text_area.get("1.0", "end-1c").strip():
            return
        if not self._placeholder_active:
            self._placeholder_active = True
            self.text_area.insert("1.0", self._content_placeholder_text)
            self.text_area.configure(text_color=self.colors.get('muted', '#9aa6b1'))
        # Event bindings (repeat binds acceptable)
        self.text_area.bind("<FocusIn>", lambda e: self._remove_content_placeholder_if_needed())
        self.text_area.bind("<KeyPress>", lambda e: self._remove_content_placeholder_if_needed())
        self.text_area.bind("<FocusOut>", lambda e: self._restore_content_placeholder_if_empty())

    def _remove_content_placeholder_if_needed(self):
        if self._placeholder_active:
            current = self.text_area.get("1.0", "end-1c")
            if current == self._content_placeholder_text:
                self.text_area.delete("1.0", "end")
            self._placeholder_active = False
            self.text_area.configure(text_color=self.colors.get('main_text', '#000000'))

    def _restore_content_placeholder_if_empty(self):
        if not self.text_area.get("1.0", "end-1c").strip():
            self._placeholder_active = False
            self._init_content_placeholder()
    
    # Removed _sync_content_model; no model exists.
    
    def _handle_enter_key(self):
        """Auto-create bullet on next line if current line has bullet and content.
        Remove empty bullet if Enter pressed on bullet-only line."""
        try:
            # Note: When this is called, cursor is already on the NEW line after Enter
            cursor_pos = self.text_area.index("insert")
            current_line_num = int(cursor_pos.split('.')[0])
            
            # The line we just left is the previous line
            prev_line_num = current_line_num - 1
            if prev_line_num > 0:
                prev_line_start = f"{prev_line_num}.0"
                prev_line_end = f"{prev_line_num}.end"
                prev_line = self.text_area.get(prev_line_start, prev_line_end)
                
                # If previous line is just "•" with nothing else, remove it and don't add new bullet
                if prev_line.strip() == "•":
                    self.text_area.delete(prev_line_start, f"{prev_line_num}.end")
                    # Also remove the newline we just created
                    self.text_area.delete(f"{prev_line_num}.end", cursor_pos)
                    return
                
                # If previous line has bullet and content, add bullet to current (new) line
                if prev_line.startswith('• ') and len(prev_line.strip()) > 1:
                    # Add bullet to current line immediately
                    self.text_area.insert(cursor_pos, "• ")
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
        """Persist the authored note.

        Extracts hashtags from content, validates duplicate titles, and stores
        into either a selected notebook or the unassigned notes collection.
        """
        title = self.title_entry.get().strip()
        raw_content = self.text_area.get("1.0", "end-1c").strip()
        content = "" if (self._placeholder_active and raw_content == self._content_placeholder_text.strip()) else raw_content
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
            "id": str(uuid.uuid4()),
            "title": title,
            "content": content,
            "tags": tags,
            "created": datetime.now().isoformat(),
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

    def refresh_notes_list(self):
        tab = self.tab_var.get()
        search_term = self.search_entry.get().lower().strip() if hasattr(self, 'search_entry') else ""

        # Ensure the scrollable `notes_list` exists. If the container was
        # replaced or destroyed, recreate it so refresh works standalone.
        if not hasattr(self, 'notes_list') or self.notes_list is None or not self.notes_list.winfo_exists():
            for w in self.notes_list_container.winfo_children():
                w.destroy()
            self.notes_list = ctk.CTkScrollableFrame(self.notes_list_container, fg_color="transparent")
            self.notes_list.pack(fill="both", expand=True)
        else:
            # Clear current view to avoid duplicates before repopulating
            for w in self.notes_list.winfo_children():
                w.destroy()

        # Gather notes for the active tab
        notes = []
        if tab == "Unassigned":
            notes = list(self.data_manager.get_unassigned_notes())
            notes.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        elif tab == "Recent":
            notes = self._get_recent_notes(15)
        elif tab == "Assigned":
            notes = self._get_assigned_notes()

        # Filter notes according to search term
        filtered_notes = []
        for note in notes:
            tags_str = " ".join(note.get('tags', [])).lower()
            if search_term:
                if search_term in note.get('title', '').lower() or \
                   search_term in note.get('content', '').lower() or \
                   search_term in tags_str:
                    filtered_notes.append(note)
            else:
                filtered_notes.append(note)

        # If no matches, show placeholder
        if not filtered_notes:
            ctk.CTkLabel(self.notes_list, text="No notes found.", font=self.app.get_font(0, "italic"), text_color=self.colors['secondary_text']).pack(pady=20)
            return

        # Create cards for filtered results
        for note in filtered_notes:
            self._create_note_card(note, tab)

    def open_note_window(self, note):
        """Open a dedicated window for viewing / editing a single note."""
        NoteWindow(self.master, note, self.colors, self.data_manager, self.refresh_notes_list)

class NoteWindow(ctk.CTkToplevel):
    """Modal editor for an individual note with word count, move/export features."""
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
        # create a stored reference to allow enabling/disabling based on validation
        self.save_btn = ctk.CTkButton(actions_frame, text="Save Changes", command=self.save_changes, fg_color=colors['success'], text_color="white", font=get_font(0))
        self.save_btn.pack(side="left", padx=(0, 10))
        
        # Export Button (use tinted icon when available)
        try:
            img = None
            for fn in ('icon_export_24.png',):
                try:
                    img = load_and_tint_icon(fn, colors.get('accent', '#4a90e2'), size=(16,16))
                    if img:
                        break
                except Exception:
                    img = None
        except Exception:
            img = None

        if img:
            self._img_export = img
            ctk.CTkButton(actions_frame, image=self._img_export, text="", command=self.export_note, fg_color=colors['info'], width=36, height=36).pack(side="left", padx=(0, 10))
        else:
            ctk.CTkButton(actions_frame, text="Export", command=self.export_note, fg_color=colors['info'], text_color="white", width=80, font=get_font(0)).pack(side="left", padx=(0, 10))

        # Copy Button (use tinted icon when available)
        try:
            img = None
            for fn in ('icon_copy_24.png',):
                try:
                    img = load_and_tint_icon(fn, colors.get('accent', '#4a90e2'), size=(16,16))
                    if img:
                        break
                except Exception:
                    img = None
        except Exception:
            img = None

        if img:
            self._img_copy = img
            ctk.CTkButton(actions_frame, image=self._img_copy, text="", command=self.copy_content, fg_color=colors['accent'], width=36, height=36).pack(side="left", padx=(0, 10))
        else:
            ctk.CTkButton(actions_frame, text="Copy", command=self.copy_content, fg_color=colors['accent'], text_color="white", width=80, font=get_font(0)).pack(side="left", padx=(0, 10))

        # Delete Button (use tinted icon when available)
        try:
            img = None
            for fn in ('icon_delete_24.png','icon_delete_48.png'):
                try:
                    img = load_and_tint_icon(fn, colors.get('danger', '#e74c3c'), size=(16,16))
                    if img:
                        break
                except Exception:
                    img = None
        except Exception:
            img = None

        if img:
            self._img_delete = img
            ctk.CTkButton(actions_frame, image=self._img_delete, text="", command=self.delete_note, fg_color=colors['danger'], width=36, height=36).pack(side="right")
        else:
            ctk.CTkButton(actions_frame, text="Delete Note", command=self.delete_note, fg_color=colors['danger'], text_color="white", width=80, font=get_font(0)).pack(side="right")
        
        # Move to Notebook
        move_frame = ctk.CTkFrame(self, fg_color="transparent")
        move_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(move_frame, text="Move to:", font=get_font(0), text_color=colors['accent']).pack(side="left", padx=(0, 5))
        
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
                       text_color=colors.get('dropdown_text', 'white'), font=get_font(0))
        self.notebook_dropdown.pack(side="left", padx=(0, 10))

        # Move Button (use tinted icon when available)
        try:
            img = None
            for fn in ('icon_move_24.png',):
                try:
                    img = load_and_tint_icon(fn, colors.get('info', '#3498db'), size=(14,14))
                    if img:
                        break
                except Exception:
                    img = None
        except Exception:
            img = None

        if img:
            self._img_move = img
            ctk.CTkButton(move_frame, image=self._img_move, text="", command=self.move_note, fg_color=colors['info'], width=36, height=36).pack(side="left")
        else:
            ctk.CTkButton(move_frame, text="Move", command=self.move_note, width=60,
                          fg_color=colors['info'], text_color="white", font=get_font(0)).pack(side="left")

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
                    # Export notebook title if available
                    notebook_title = ''
                    nb_code = self.note.get('notebook') or self.note.get('_notebook') or ''
                    if nb_code:
                        notebooks = self.data_manager.get_notebooks()
                        nb_data = notebooks.get(nb_code)
                        if nb_data:
                            notebook_title = nb_data.get('name', nb_code)
                        else:
                            notebook_title = nb_code
                    if notebook_title:
                        f.write(f"Notebook: {notebook_title}\n")
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
        
        # Update modified timestamp
        self.note['modified'] = datetime.now().strftime("%B %d, %Y | %I:%M%p")
        
        self.data_manager.save_data()
        messagebox.showinfo("Saved", "Title and content saved.", parent=self)
        if self.callback:
            self.callback()

    # NoteWindow tag-entry helpers removed — tags are extracted from content instead.

    def delete_note(self):
        if messagebox.askyesno("Delete Note", "Are you sure you want to delete this note? This cannot be undone."):
            # Prefer course code for notebook lookup
            notebook_code = self.note.get("notebook") or self.note.get("_notebook")
            deleted = False
            # Prefer unique id for note matching
            note_id = self.note.get("id")
            def note_match(a, b):
                if a.get("id") and b.get("id"):
                    return a["id"] == b["id"]
                # Fallback: match all fields
                return (
                    a.get("title") == b.get("title") and
                    a.get("content") == b.get("content") and
                    a.get("created") == b.get("created") and
                    set(a.get("tags", [])) == set(b.get("tags", []))
                )

            # Try unassigned notes
            if notebook_code is None or notebook_code == "Unassigned Notes":
                unassigned = self.data_manager.get_unassigned_notes()
                for idx, n in enumerate(unassigned):
                    if note_match(n, self.note):
                        unassigned.pop(idx)
                        deleted = True
                        break
                if deleted:
                    self.data_manager.save_data()
                    self.destroy()
                    if self.callback:
                        self.callback()
                    if isinstance(self.master.master, CourseMate):
                        self.master.master.sidebar.refresh_stats()
                    return
            else:
                # Use course code for notebook lookup
                notebooks = self.data_manager.get_notebooks()
                nb_data = notebooks.get(notebook_code)
                if nb_data:
                    notes = nb_data.get("notes", [])
                    for idx, n in enumerate(notes):
                        if note_match(n, self.note):
                            notes.pop(idx)
                            deleted = True
                            break
                    if deleted:
                        self.data_manager.save_data()
                        self.destroy()
                        if self.callback:
                            self.callback()
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
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Notebook Name (Required)", width=300, fg_color=colors['card_bg'], text_color=colors['main_text'], font=get_font(-1))
        self.name_entry.pack(pady=(0, 10))
        
        # Course Code
        ctk.CTkLabel(self, text="Course Code:", font=get_font(-1), text_color=colors['main_text']).pack(anchor="w", padx=50, pady=(5, 0))
        self.code_entry = ctk.CTkEntry(self, placeholder_text="Course Code (Required)", width=300, fg_color=colors['card_bg'], text_color=colors['main_text'], font=get_font(-1))
        self.code_entry.pack(pady=(0, 10))
        
        # Instructor
        ctk.CTkLabel(self, text="Instructor:", font=get_font(-1), text_color=colors['main_text']).pack(anchor="w", padx=50, pady=(5, 0))
        self.instructor_entry = ctk.CTkEntry(self, placeholder_text="Instructor (Optional)", width=300, fg_color=colors['card_bg'], text_color=colors['main_text'], font=get_font(-1))
        self.instructor_entry.pack(pady=(0, 10))
        
        # If editing, populate with current values
        if self.is_edit_mode:
            for code, nb_data in self.data_manager.get_notebooks().items():
                # Match by code or name for robustness
                if nb_data.get("name") == notebook_name or code == notebook_name:
                    self.name_entry.delete(0, "end")
                    self.name_entry.insert(0, nb_data.get("name", ""))
                    self.code_entry.delete(0, "end")
                    self.code_entry.insert(0, nb_data.get("code", code))
                    self.instructor_entry.delete(0, "end")
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
            notebooks = self.data_manager.get_notebooks()
            # Check if code changed and if new code already exists
            if code != self.original_code and code in notebooks:
                messagebox.showerror("Error", "A notebook with this course code already exists.")
                return
            # Get the notebook data
            nb_data = notebooks.get(self.original_code)
            if nb_data:
                nb_data["name"] = name
                nb_data["code"] = code
                nb_data["instructor"] = instructor
                # If code changed, move to new key
                if code != self.original_code:
                    notebooks[code] = nb_data
                    del notebooks[self.original_code]
                    self.original_code = code
                self.data_manager.save_data()
                messagebox.showinfo("Saved", "Notebook changes saved.", parent=self)
                if self.callback:
                    self.callback(name)
                self.destroy()
            else:
                messagebox.showerror("Error", "Notebook not found!")
        else:
            result = self.data_manager.add_notebook(name, code, instructor)
            if isinstance(result, tuple):
                success, message = result
                if success:
                    messagebox.showinfo("Saved", "Notebook created.", parent=self)
                    if self.callback:
                        self.callback(name)
                    self.destroy()
                else:
                    messagebox.showerror("Error", message)
            else:
                if result:
                    messagebox.showinfo("Saved", "Notebook created.", parent=self)
                    if self.callback:
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
        
        self.notebook_search_entry = ctk.CTkEntry(search_frame, placeholder_text="Find by name and course code", 
                                         fg_color=self.colors['background'], text_color=self.colors['main_text'],
                                         height=30, font=self.master.master.get_font(0))
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
            ctk.CTkLabel(self.grid_frame, text="No notebooks yet. Create one to get started!", font=self.get_font(0, "italic"), text_color=self.colors['secondary_text']).pack(pady=50)
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
        corner = 12
        card = ctk.CTkFrame(self.grid_frame, fg_color=self.colors['card_bg'], corner_radius=corner,
                           border_width=2, border_color=border_color)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Header with icon buttons
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))
        
        # Title on the left - always show notebook name
        display_name = data.get("name", name).strip() if data.get("name", name) else "(Unnamed)"
        display_name = self.truncate_text(display_name, 20)
        lbl_title = ctk.CTkLabel(header, text=display_name, font=self.get_font(2, "bold"), 
                                 text_color=self.colors['main_text'])
        lbl_title.pack(side="left")
        
        # Icon buttons on the right
        # Edit and Delete buttons with white icons and correct bg colors
        try:
            img_edit = load_icon('icon_edit_32_white.png', size=(24,24))
        except Exception:
            img_edit = None
        try:
            img_del = load_icon('icon_delete_32_white.png', size=(24,24))
        except Exception:
            img_del = None

        # Delete button
        ctk.CTkButton(header, image=img_del, text="", width=36, height=32,
            command=lambda n=name: self.delete_notebook(n),
            fg_color=self.colors.get('danger', '#e74c3c'), hover_color="#c0392b",
            border_width=0).pack(side="right", padx=(5, 0))
        # Edit button
        ctk.CTkButton(header, image=img_edit, text="", width=36, height=32,
            command=lambda n=name: self.rename_notebook(n),
            fg_color=self.colors.get('info', '#3498db'), hover_color=self.colors.get('accent', '#4a90e2'),
            border_width=0).pack(side="right", padx=(5, 0))
        # Hover effect for the card (subtle change using theme hover color)
        # Hover color change removed as requested
        
        # Meta (Code | Instructor)
        meta = []
        if data.get("code"):
            meta.append(data["code"])
        if data.get("instructor"):
            meta.append(data["instructor"])
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
        ctk.CTkButton(card, text="Open Notebook", command=lambda n=display_name: self.show_notebook(n),
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
        

        # Back Button with icon
        try:
            back_img = load_icon('icon_arrow_back_32_white.png', size=(24,24))
        except Exception:
            back_img = None
        ctk.CTkButton(header, image=back_img, text="", width=36, height=32, command=self.show_all_notebooks,
            fg_color=self.colors.get('sidebar_bg', 'transparent'), hover_color=self.colors.get('sidebar_hover', '#405977'), border_width=0).pack(side="left", padx=(0, 10))

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

        # Actions: Delete and Rename as icons
        try:
            del_img = load_icon('icon_delete_32_white.png', size=(24,24))
        except Exception:
            del_img = None
        try:
            edit_img = load_icon('icon_edit_32_white.png', size=(24,24))
        except Exception:
            edit_img = None
        ctk.CTkButton(header, image=del_img, text="", width=36, height=32, command=self.delete_notebook,
            fg_color=self.colors.get('danger', '#e74c3c'), hover_color="#c0392b", border_width=0).pack(side="right", padx=5)
        ctk.CTkButton(header, image=edit_img, text="", width=36, height=32, command=self.rename_notebook,
            fg_color=self.colors.get('info', '#3498db'), hover_color=self.colors.get('accent', '#4a90e2'), border_width=0).pack(side="right", padx=5)
        
        # Search Bar
        search_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        search_frame.pack(fill="x", padx=0, pady=(0, 10))
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Find by name, tag, or keyword", 
                                         fg_color=self.colors['background'], text_color=self.colors['main_text'],
                                         height=30, font=self.master.master.get_font(0))
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
        try:
            img_del = load_icon('icon_delete_32_white.png', size=(24,24))
        except Exception:
            img_del = None
        ctk.CTkButton(header, image=img_del, text="", width=36, height=32, command=lambda: self.delete_note(index),
            fg_color=self.colors.get('danger', '#e74c3c'), hover_color="#c0392b", border_width=0).pack(side="right")
        
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
        # Hover color change removed as requested

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
        
        # Main container for Settings view
        self.container = ctk.CTkScrollableFrame(master, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.container, text="SETTINGS", font=master.master.get_font(6, "bold"), text_color=self.colors['main_text']).pack(anchor="w", pady=(0, 10))

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
            width=control_width,
            font=self.master.master.get_font(0)
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
            width=control_width,
            font=self.master.master.get_font(0)
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
            width=control_width,
            font=self.master.master.get_font(0)
        )
        size_menu.grid(row=0, column=1, sticky="e", padx=(30, 0))

 

    def _setup_inspiration_section(self):
        frame = ctk.CTkFrame(self.container, fg_color=self.colors['card_bg'], corner_radius=10)
        frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(frame, text="Inspiration & Quotes", font=self.master.master.get_font(2, "bold"), text_color=self.colors['main_text']).pack(anchor="w", padx=20, pady=15)
        
        # Timer
        row1 = ctk.CTkFrame(frame, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(row1, text="Change Quote Every (seconds):", font=self.master.master.get_font(0), text_color=self.colors['main_text']).pack(side="left")
        
        self.timer_entry = ctk.CTkEntry(row1, width=60, placeholder_text="e.g. 30", fg_color=self.colors['background'], text_color=self.colors['main_text'], font=self.master.master.get_font(0))
        self.timer_entry.insert(0, str(self.settings.get("quote_timer", 30)))
        self.timer_entry.pack(side="left", padx=10)
        
        ctk.CTkButton(row1, text="Save Timer", width=80, command=self.save_timer,
                      fg_color=self.colors['info'], font=self.master.master.get_font(0)).pack(side="left")
        
        # Add Quote
        row2 = ctk.CTkFrame(frame, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=(15, 5))
        ctk.CTkLabel(row2, text="Add New Quote:", font=self.master.master.get_font(0), text_color=self.colors['main_text']).pack(anchor="w")
        
        self.quote_entry = ctk.CTkEntry(row2, placeholder_text="Enter an inspirational quote with author...", fg_color=self.colors['background'], text_color=self.colors['main_text'], font=self.master.master.get_font(0))
        self.quote_entry.pack(fill="x", pady=5)
        
        ctk.CTkButton(row2, text="Add Quote", command=self.add_quote,
                  fg_color=self.colors['success'], font=self.master.master.get_font(0)).pack(anchor="e", pady=5)

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
        self.new_template_title = ctk.CTkEntry(form, placeholder_text="e.g. My Custom Study Template", fg_color=self.colors['background'], text_color=self.colors['main_text'], font=self.master.master.get_font(0))
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
            width=120,
            font=self.master.master.get_font(0)
        )
        self.new_template_category_menu.grid(row=0, column=3, sticky="w")
        form.grid_columnconfigure(1, weight=1)

        # Content textbox (full width)
        self.new_template_text = ctk.CTkTextbox(self.templates_frame, height=120, fg_color=self.colors['background'], text_color=self.colors['main_text'])
        self.new_template_text.pack(fill="x", padx=20, pady=(0, 8))
        
        # Placeholder support for template content
        self._template_placeholder_text = "Enter template structure here...\n\nFor Study Templates (e.g., Cornell Notes, Concept Maps):\nTopic: \n\nKey Points:\n- \n- \n\nSummary:\n- \n\nFor Planner Templates (e.g., Daily/Weekly Plans):\nDate: \n\nTasks:\n- [ ] \n- [ ] \n\nNotes:\n- "
        self._template_placeholder_active = False
        self._init_template_placeholder()

        # Action buttons
        btns = ctk.CTkFrame(self.templates_frame, fg_color="transparent")
        btns.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkButton(btns, text="Clear", width=100, fg_color=self.colors['danger'], command=self.clear_new_template_inputs, font=self.master.master.get_font(0)).pack(side="left")
        ctk.CTkButton(btns, text="Add Template", width=130, fg_color=self.colors['success'], command=self.add_new_template, font=self.master.master.get_font(0)).pack(side="right")

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
                          command=lambda t=title: self.edit_template_dialog(t, "Study"),
                          font=self.master.master.get_font(-1)).pack(side="left")

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
                          command=lambda t=title: self.edit_template_dialog(t, "Planner"),
                          font=self.master.master.get_font(-1)).pack(side="left", padx=(0,8))
            ctk.CTkButton(actions, text="Delete", width=72, height=26, fg_color=self.colors['danger'],
                          command=lambda t=title: self.delete_template(t, "Planner"),
                          font=self.master.master.get_font(-1)).pack(side="left")

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
            self.preview_header.configure(fg_color=theme.get('header_bg'))
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
            ctk.CTkButton(actions, text="Edit", width=70, height=28, fg_color=self.colors['info'], command=lambda i=idx: self.edit_quote(i), font=self.master.master.get_font(-1)).pack(side="left", padx=(0,6))
            # Delete button
            ctk.CTkButton(actions, text="Delete", width=70, height=28, fg_color=self.colors['danger'], command=lambda i=idx: self.delete_quote(i), font=self.master.master.get_font(-1)).pack(side="left")

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
        raw_content = (self.new_template_text.get("1.0", "end-1c") or "").strip()
        # Exclude placeholder from content
        content = "" if (self._template_placeholder_active and raw_content == self._template_placeholder_text.strip()) else raw_content
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
            self._template_placeholder_active = False
            self._init_template_placeholder()
        except Exception:
            pass

    def _init_template_placeholder(self):
        """Insert placeholder text in template content if empty."""
        try:
            if self.new_template_text.get("1.0", "end-1c").strip():
                return
            if not self._template_placeholder_active:
                self._template_placeholder_active = True
                self.new_template_text.insert("1.0", self._template_placeholder_text)
                self.new_template_text.configure(text_color=self.colors.get('muted', '#9aa6b1'))
            # Event bindings
            self.new_template_text.bind("<FocusIn>", lambda e: self._remove_template_placeholder())
            self.new_template_text.bind("<KeyPress>", lambda e: self._remove_template_placeholder())
            self.new_template_text.bind("<FocusOut>", lambda e: self._restore_template_placeholder())
        except Exception:
            pass
    
    def _remove_template_placeholder(self):
        """Remove placeholder when user starts typing."""
        try:
            if self._template_placeholder_active:
                current = self.new_template_text.get("1.0", "end-1c")
                if current == self._template_placeholder_text:
                    self.new_template_text.delete("1.0", "end")
                self._template_placeholder_active = False
                self.new_template_text.configure(text_color=self.colors.get('main_text', '#000000'))
        except Exception:
            pass
    
    def _restore_template_placeholder(self):
        """Restore placeholder if textbox is empty."""
        try:
            if not self.new_template_text.get("1.0", "end-1c").strip():
                self._template_placeholder_active = False
                self._init_template_placeholder()
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


class AboutView:
    """Simple About page describing the app."""
    def __init__(self, master, data_manager, colors):
        self.master = master
        self.data_manager = data_manager
        self.colors = colors
        # Scrollable container
        self.container = ctk.CTkScrollableFrame(master, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        # Highlighted header
        header_frame = ctk.CTkFrame(self.container, fg_color=self.colors['accent'], corner_radius=10)
        header_frame.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(header_frame, text="About CourseMate", font=("Open Sans", 22, "bold"), text_color="#fff").pack(anchor="center", pady=12)

        info = (
            "CourseMate — Your study companion for smarter learning.\n"
            "Version: 1.0\n\n"
            "What is CourseMate?\n"
            "CourseMate helps you organize your subjects, notes, and study materials in a clean, "
            "template-based workspace. Whether you're studying technical subjects or general education, "
            "CourseMate makes it easier to learn and remember more.\n\n"
            "Why Use CourseMate?\n"
            "Because studying shouldn’t feel messy. CourseMate keeps your notes structured and easy to find, "
            "reducing clutter and helping you focus on what actually matters — understanding your lessons. "
            "Templates, hashtags, and organized notebooks help you review faster and prepare better for exams.\n\n"
            "Main Navigation Guide:\n"
            "• Home — This is where you write your notes. Choose or create a template, type freely, use "
            "hashtags for topics (e.g. #math), and assign your note to a notebook. You can clear the canvas, "
            "insert templates, and browse your notes using the Recent, Assigned, and Unassigned tabs.\n\n"
            "• Notebooks — Your subjects live here. Create notebooks for each course, add notes to them, rename "
            "subjects, and organize your content by topic. Opening a notebook shows all notes inside it.\n\n"
            "• Settings — Customize how CourseMate looks and feels. Change your theme, adjust font size, select "
            "your preferred font family, and manage template categories. Great for making the app comfortable "
            "for long study sessions.\n\n"
            "• About — You're reading this page! This section explains what CourseMate is and how to navigate "
            "the app effectively.\n\n"
            "How to Use CourseMate (Step-by-Step):\n"
            "1. Create a notebook for a subject you want to organize.\n"
            "2. Pick an existing template or create your own study or planner template.\n"
            "3. Write your note—use #hashtags to group topics and '- ' (dash + space) to create bullet points.\n"
            "4. Assign the note to a notebook or keep it in Unassigned until you're ready.\n"
            "5. Use the right-side panel in Home to review notes under Recent, Assigned, or Unassigned.\n"
            "6. Visit the Notebooks page to browse everything by subject.\n\n"
            "Features:\n"
            "- Organized notebooks for each subject\n"
            "- Fast note creation with templates\n"
            "- Hashtag-based tagging (#math, #lecture, #formula, etc.)\n"
            "- Clean, theme-based interface\n"
            "- Planner templates for daily and weekly productivity\n\n"
            "For more details, check out the project README."
        )
        ctk.CTkLabel(self.container, text=info, font=("Open Sans", 14), text_color=self.colors['main_text'], wraplength=700, justify="left").pack(anchor="w", pady=(8,0))

        # Small Close/Back button to go Home
        btn_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20,0))
        ctk.CTkButton(btn_frame, text="Back to Home", command=lambda: getattr(self.master.master, 'show_home', lambda: None)(), fg_color=self.colors.get('button_primary', self.colors['primary']), text_color=self.colors.get('button_text', 'white')).pack(side="left")


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