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
        'secondary_text':   "#a2b6c4",
        'dropdown_bg':      '#253241',
        'dropdown_text':    '#F4F4F4', 
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
        'card_bg':        '#11161a',  
        'success':        '#27ae60',  
        'info':           '#3498db',  
        'warning':        '#cf6679',
        'muted':          '#9aa6b1',
        'header_text':    '#ffffff',
        'main_text':      '#e6eef6',  
        'secondary_text': '#a2b6c4',  
        'dropdown_bg':    '#253244',  
        'dropdown_text':  '#ffffff',
        'danger':         '#e74c3c',
        'card_hover':     '#243442'
    },
    'Baby Pink': {
        'primary_dark':     '#f8bbd0',
        'primary':          '#fce4ec',
        'accent':           '#ec407a',
        'background':       '#fff0f5',
        'sidebar_button':   '#fce4ec',
        'sidebar_hover':    '#f8bbd0',
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
        'danger':           '#ef5350',
        'card_hover':       '#bbdefb'
    }
}

DEFAULT_SETTINGS = {
    "theme": "CourseMate Theme",
    "font_family": "Open Sans",
    "font_size": "Normal", # Normal, Large
    "quotes": [],
    "quote_timer": 30 # seconds
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

class CourseMate(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Data Setup
        # Data Setup
        self.data_manager = DataManager()
        self.load_custom_fonts()
        
        self.current_theme = self.data_manager.get_settings()["theme"]
        self.colors = THEMES.get(self.current_theme, THEMES['CourseMate Theme'])
        
        # Font State
        self.font_family = self.data_manager.get_settings().get("font_family", "Open Sans")
        self.font_size_mode = self.data_manager.get_settings().get("font_size", "Normal")
        self.base_font_size = 14 if self.font_size_mode == "Normal" else 18
        
        # Window Setup
        self.title("CourseMate: A Smart Note-Taking & Study Aid For Students")
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
        self.show_home() # Default view

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
        self.header_lbl_notebooks_count.pack(anchor="w", padx=(5, 0))

        self.header_lbl_notes_count = ctk.CTkLabel(self.header_stats_frame, text="Total Notes: 0",
                               font=self.get_font(-2, "bold"), text_color=self.colors['header_text'])
        self.header_lbl_notes_count.pack(anchor="w", padx=(5, 0))

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
                    if hasattr(self, 'header_slogan_label') and self.header_slogan_label:
                        try:
                            self.header_slogan_label.configure(text_color=self.colors.get('secondary_text'))
                        except Exception:
                            pass
                except Exception:
                    pass

                # Update header stats labels (if present)
                if hasattr(self, 'header_lbl_notebooks_count'):
                    try:
                        self.header_lbl_notebooks_count.configure(text_color=self.colors.get('header_text'))
                    except Exception:
                        pass
                if hasattr(self, 'header_lbl_notes_count'):
                    try:
                        self.header_lbl_notes_count.configure(text_color=self.colors.get('header_text'))
                    except Exception:
                        pass
        except Exception:
            pass
        
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
        
        # (Title moved to top header) — keep sidebar compact without duplicate title

        # Quick stats moved to top header overlay to avoid duplicate title and keep layout clean

        # Navigation (compact)
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(fill="x", pady=3)

        self._create_nav_btn("Home", home_cb)
        self._create_nav_btn("Notebooks", notebooks_cb)
        self._create_nav_btn("Settings", settings_cb)

        # Notebooks Quick Access (Scrollable)
        ctk.CTkLabel(self, text="NOTEBOOKS", font=master.get_font(-2, "bold"), text_color=colors['secondary_text'], anchor="w").pack(fill="x", padx=10, pady=(6, 3))

        self.notebooks_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", height=150)
        self.notebooks_frame.pack(fill="x", padx=8, pady=3)

        # Inspiration Section (collapsible)
        self.inspiration_visible = True
        self.inspiration_header = ctk.CTkFrame(self, fg_color="transparent")
        self.inspiration_header.pack(side="bottom", fill="x", padx=8, pady=(3, 10))

        # Make the inspiration header button match nav buttons and center it
        self.inspire_label = ctk.CTkButton(
            self.inspiration_header,
            text="Inspiration",
            command=self.toggle_inspiration,
            fg_color=self.colors.get('sidebar_button', self.colors.get('primary')),
            hover_color=self.colors.get('sidebar_hover'),
            height=36,
            text_color=self.colors.get('sidebar_text', 'white'),
            font=master.get_font(2, "bold")
        )
        # Fill horizontally so the button stretches across the sidebar
        self.inspire_label.pack(padx=2, pady=3, fill="x")

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
            for name in notebooks:
                display_name = self.master.truncate_text(name)
                btn = ctk.CTkButton(self.notebooks_frame, text=f"📓 {display_name}", 
                                    command=lambda n=name: self.open_notebook(n),
                                    fg_color=self.colors.get('sidebar_button', self.colors['primary']), hover_color=self.colors['sidebar_hover'], 
                                    anchor="w", height=30, font=self.master.get_font(0), text_color=self.colors.get('sidebar_text', 'white'))
                btn.pack(fill="x", pady=2, padx=4)

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
        self.title_entry = ctk.CTkEntry(self, font=("Open Sans", 12))
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
        ctk.CTkLabel(header, text="Write", font=self.app.get_font(6, "bold"), text_color=self.colors['main_text']).pack(side="left")
        # Controls Row
        self.controls_frame = ctk.CTkFrame(self.write_frame, fg_color="transparent")
        self.controls_frame.pack(fill="x", padx=20, pady=(0, 10))
        controls = self.controls_frame
        # Assign to
        ctk.CTkLabel(controls, text="Assign to:", font=self.app.get_font(0), text_color=self.colors['main_text']).pack(side="left", padx=(0, 5))
        self.notebook_var = ctk.StringVar(value="• Unassigned Notes")
        self.update_notebook_dropdown()
        # Template
        ctk.CTkLabel(controls, text="Template:", font=self.app.get_font(0), text_color=self.colors['main_text']).pack(side="left", padx=(0, 5))
        self.template_var = ctk.StringVar(value="Select...")
        templates = ["Select..."] + list(self.TEMPLATES.keys())
        self.template_dropdown = ctk.CTkOptionMenu(controls, variable=self.template_var, values=templates,
                       command=self.insert_template,
                       fg_color=self.colors.get('dropdown_bg', self.colors['main_text']), button_color=self.colors.get('primary'),
                       text_color=self.colors.get('dropdown_text', 'white'), width=150)
        self.template_dropdown.pack(side="left")
        # Save Button
        ctk.CTkButton(controls, text="Save Note", command=self.save_note,
                      fg_color=self.colors['success'], hover_color='#219150', text_color="white", width=100).pack(side="right")
        # Clear Button
        ctk.CTkButton(controls, text="Clear", command=self.clear_write_area,
                      fg_color=self.colors['danger'], hover_color='#c0392b', text_color="white", width=80).pack(side="right", padx=(0, 10))
        # Title Entry
        self.title_entry = ctk.CTkEntry(self.write_frame, placeholder_text="Note Title (Required)", 
                font=self.app.get_font(0, "bold"), height=40,
                fg_color=self.colors['background'], text_color=self.colors['main_text'], border_width=0)
        self.title_entry.pack(fill="x", padx=20, pady=(0, 10))
        # Text Area
        self.text_area = ctk.CTkTextbox(self.write_frame, font=self.app.get_font(0), 
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
                                                       fg_color=self.colors.get('dropdown_bg', self.colors['main_text']), button_color=self.colors.get('primary'),
                                                       text_color=self.colors.get('dropdown_text', 'white'), width=180)
            self.notebook_dropdown.pack(side="left", padx=(0, 20))

    def _setup_notes_ui(self):
        # Header
        ctk.CTkLabel(self.notes_frame, text="Unassigned Notes", font=self.app.get_font(2, "bold"), 
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
        ctk.CTkLabel(search_frame, text="🔍", font=self.app.get_font(0), text_color=self.colors['secondary_text']).pack(side="right", padx=(5, 0))
        
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
        if isinstance(self.master.master, CourseMate):
             self.master.master.sidebar.refresh_stats()

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
                if search_term in note.get('title', '').lower() or search_term in note.get('content', '').lower():
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
        lbl_title = ctk.CTkLabel(card, text=title, font=self.app.get_font(-1, "bold"), text_color=self.colors['main_text'], anchor="w")
        lbl_title.pack(fill="x", padx=10, pady=(5, 0))
        lbl_title.bind("<Button-1>", lambda e, n=note: self.open_note_window(n))
        
        # Row 2: Date | Preview
        meta_text = f"{date_str} | {preview_text}"
        lbl_meta = ctk.CTkLabel(card, text=meta_text, font=self.app.get_font(-3), text_color=self.colors['secondary_text'], anchor="w")
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
        get_font = master.master.get_font if hasattr(master.master, 'get_font') else lambda s=0, w="normal": ("Open Sans", 14+s, w)
        
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
            
        # Include an option to move the note to Unassigned Notes
        notebooks = ["• Unassigned Notes"] + notebook_list
        if not notebook_list:
            # If there are no notebooks, allow the user to select 'No Notebooks'
            notebooks = ["• Unassigned Notes", "No Notebooks"]
        # Map the unassigned display to a sentinel value (None)
        self.notebook_map["• Unassigned Notes"] = None
            
        self.notebook_dropdown = ctk.CTkOptionMenu(move_frame, variable=self.notebook_var, values=notebooks,
                       fg_color=colors.get('dropdown_bg', colors['main_text']), button_color=colors.get('primary'),
                       text_color=colors.get('dropdown_text', 'white'))
        self.notebook_dropdown.pack(side="left", padx=(0, 10))

        # Move Button
        ctk.CTkButton(move_frame, text="Move", command=self.move_note, width=60,
                      fg_color=colors['info'], text_color="white").pack(side="left")

    def rename_note(self):
        # Use a CustomTkinter modal dialog instead of tkinter.simpledialog
        dlg = InputDialog(self, "Rename Note", "Enter new title:", initialvalue=self.note.get('title', ''))
        self.wait_window(dlg)
        new_title = dlg.result
        if new_title and new_title.strip():
            self.note['title'] = new_title.strip()
            # Update window title
            try:
                self.title(self.note['title'])
            except Exception:
                pass

            # Update stored title label if present
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
                if isinstance(self.master.master, CourseMate):
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
                for notebook_name, notebook_data in self.data_manager.get_notebooks().items():
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
            for notebook_name, notebook_data in self.data_manager.get_notebooks().items():
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
        get_font = master.master.get_font if hasattr(master.master, 'get_font') else lambda s=0, w="normal": ("Open Sans", 14+s, w)
        
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
    def __init__(self, master, data_manager, colors, initial_notebook=None, app=None):
        self.master = master
        self.data_manager = data_manager
        self.colors = colors
        self.app = app or getattr(master, "master", None)
        
        self.container = ctk.CTkFrame(master, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        if initial_notebook and initial_notebook in self.data_manager.get_notebooks():
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
        ctk.CTkLabel(header, text="Your Notebooks", font=self.get_font(6, "bold"), text_color=self.colors['main_text']).pack(side="left")
        ctk.CTkButton(header, text="+ Create Notebook", command=self.add_notebook, fg_color=self.colors['success'], text_color="white").pack(side="right")
        
        # Grid Container
        self.grid_frame = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True)
        
        # Grid Layout Logic
        notebooks = self.data_manager.get_notebooks()
        if not notebooks:
            ctk.CTkLabel(self.grid_frame, text="No notebooks yet. Create one to get started!", font=self.get_font(0), text_color=self.colors['secondary_text']).pack(pady=50)
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
        display_name = self.truncate_text(name, 20)
        lbl_title = ctk.CTkLabel(card, text=display_name, font=self.get_font(2, "bold"), text_color=self.colors['main_text'])
        lbl_title.pack(padx=15, pady=(15, 5), anchor="w")
        lbl_title.bind("<Button-1>", lambda e, n=name: self.show_notebook(n))
        
        # Meta (Code | Instructor)
        meta = []
        if data.get("code"): meta.append(data["code"])
        if data.get("instructor"): meta.append(data["instructor"])
        meta_text = " • ".join(meta) if meta else "No details"
        
        lbl_meta = ctk.CTkLabel(card, text=meta_text, font=self.get_font(-2), text_color=self.colors['secondary_text'])
        lbl_meta.pack(padx=15, pady=(0, 10), anchor="w")
        lbl_meta.bind("<Button-1>", lambda e, n=name: self.show_notebook(n))
        
        # Stats (Note Count)
        note_count = len(data.get("notes", []))
        lbl_count = ctk.CTkLabel(card, text=f"{note_count} Notes", font=self.get_font(-2, "bold"), text_color=self.colors['accent'])
        lbl_count.pack(padx=15, pady=(0, 15), anchor="w")
        lbl_count.bind("<Button-1>", lambda e, n=name: self.show_notebook(n))

        # Actions Row
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(actions_frame, text="Rename", width=60, height=25, 
              command=lambda n=name: self.rename_notebook(n),
              fg_color=self.colors['info'], font=self.get_font(-3)).pack(side="left", padx=(0, 5), expand=True, fill="x")
                      
        ctk.CTkButton(actions_frame, text="Delete", width=60, height=25, 
              command=lambda n=name: self.delete_notebook(n),
              fg_color=self.colors['danger'], font=self.get_font(-3)).pack(side="right", padx=(5, 0), expand=True, fill="x")

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
        ctk.CTkLabel(header, text=name, font=self.get_font(6, "bold"), text_color=self.colors['main_text']).pack(side="left")
        
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
            ctk.CTkLabel(self.notes_area, text="No notes in this notebook", font=self.get_font(-2, "italic"), text_color=self.colors['secondary_text']).pack(pady=50)
        else:
            for i, note in enumerate(notes):
                self._create_note_item(note, i)

    def _create_note_item(self, note, index):
        card = ctk.CTkFrame(self.notes_area, fg_color=self.colors['card_bg'], corner_radius=10)
        card.pack(fill="x", pady=5)
        
        # Header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(header, text=note.get('title', 'Untitled'), font=self.get_font(0, "bold"), text_color=self.colors['main_text']).pack(side="left")
        ctk.CTkLabel(header, text=note.get('created', ''), font=self.get_font(-3), text_color=self.colors['secondary_text']).pack(side="left", padx=10)
        
        # Delete Note Button
        ctk.CTkButton(header, text="🗑️", width=30, height=20, command=lambda: self.delete_note(index),
                      fg_color="transparent", hover_color=self.colors['danger'], text_color=self.colors['danger']).pack(side="right")
        
        # Preview
        preview = note.get('content', '')[:100].replace('\n', ' ') + "..."
        ctk.CTkLabel(card, text=preview, font=self.get_font(-2), text_color=self.colors['main_text'], anchor="w").pack(fill="x", padx=15, pady=(0, 10))
        
        # Open Button
        ctk.CTkButton(card, text="Open Note", command=lambda: self.open_note(note),
                  fg_color=self.colors['primary'], height=25, font=self.get_font(-3)).pack(fill="x", padx=15, pady=(0, 10))

    def add_notebook(self):
        # Open dialog
        CreateNotebookDialog(self.master, self.data_manager, self.colors, self.on_notebook_created)
        
    def on_notebook_created(self, name):
        self.show_all_notebooks()
        # Update sidebar
        if isinstance(self.app, CourseMate):
            self.app.sidebar.refresh_notebooks_list()
            self.app.sidebar.refresh_stats()

    def rename_notebook(self, notebook_name=None):
        target = notebook_name or self.selected_notebook
        if not target: return
        
        dlg = InputDialog(self.master, "Rename", "Enter new name:", initialvalue=target)
        self.master.wait_window(dlg)
        new_name = dlg.result
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
                if isinstance(self.app, CourseMate):
                    self.app.sidebar.refresh_notebooks_list()
            else:
                messagebox.showwarning("Error", "Name already exists or invalid!")

    def delete_notebook(self, notebook_name=None):
        target = notebook_name or self.selected_notebook
        if not target: return
        
        if messagebox.askyesno("Delete", f"Delete notebook '{target}' and all its notes?"):
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
            self.show_notebook(self.selected_notebook) # Refresh list
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
        # Initialize TEMPLATES with default templates
        self.TEMPLATES = {
            "Cornell Notes": "Title: \n\nQuestion/Keyword\n-\n-\n\nNotes\n-\n-\n\nSummary\n-\n_",
            "Main Idea & Details": "Main Idea: ___\n\nDetail 1:\n-\n\nDetail 2:\n-\n\nDetail 3:\n-\n\nSummary:\n-",
            "Modified Frayer Model": "Definition:\n-\n\nCharacteristics:\n-\n\nExamples:\n-\n\nNon-Examples:\n-",
            "Polya's 4 Steps": "1. Understand the Problem:\n-\n\n2. Devise a Plan:\n-\n\n3. Carry Out the Plan:\n-\n\n4. Look Back:\n-",
            "5W1H": "Who:\n-\n\nWhat:\n-\n\nWhen:\n-\n\nWhere:\n-\n\nWhy:\n-\n\nHow:\n-",
            "Concept Map": "Central Concept:\n-\n\nRelated Concept 1:\n-\n\nRelated Concept 2:\n-\n\nConnections:\n-"
        }
        # Load custom templates
        custom_templates = self.settings.get("custom_templates", {})
        self.TEMPLATES.update(custom_templates)
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
        
        ctk.CTkLabel(self.container, text="Settings", font=master.master.get_font(10, "bold"), text_color=colors['main_text']).pack(anchor="w", pady=(0, 20))
        
        self.templates_frame = None
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
        ctk.CTkLabel(row1, text="Theme Color:", font=self.master.master.get_font(0), text_color=self.colors['main_text']).pack(side="left")
        
        self.theme_var = ctk.StringVar(value=self.settings.get("theme", "CourseMate Theme"))
        themes = list(THEMES.keys())
        # OptionMenu now previews theme on selection; use Apply to save
        ctk.CTkOptionMenu(row1, variable=self.theme_var, values=themes, command=self.preview_theme,
              fg_color=self.colors.get('dropdown_bg', self.colors['main_text']), button_color=self.colors.get('primary'), text_color=self.colors.get('dropdown_text', 'white')).pack(side="right")
        ctk.CTkButton(row1, text="Apply", width=80, command=lambda: self.change_theme(self.theme_var.get()),
                  fg_color=self.colors['info']).pack(side="right", padx=(8,8))
        
        # Font Family
        row2 = ctk.CTkFrame(frame, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(row2, text="Font Style:", font=self.master.master.get_font(0), text_color=self.colors['main_text']).pack(side="left")
        
        self.font_var = ctk.StringVar(value=self.settings.get("font_family", "Open Sans"))
        fonts = [ "Alice", "Courier New", "OpenDyslexic", "Open Sans"]
        ctk.CTkOptionMenu(row2, variable=self.font_var, values=fonts, command=lambda v: self.update_setting("font_family", v),
              fg_color=self.colors.get('dropdown_bg', self.colors['main_text']), button_color=self.colors.get('primary'), text_color=self.colors.get('dropdown_text', 'white')).pack(side="right")

        # Font Size
        row3 = ctk.CTkFrame(frame, fg_color="transparent")
        row3.pack(fill="x", padx=20, pady=(5, 20))
        ctk.CTkLabel(row3, text="Font Size:", font=self.master.master.get_font(0), text_color=self.colors['main_text']).pack(side="left")
        
        self.size_var = ctk.StringVar(value=self.settings.get("font_size", "Normal"))
        sizes = ["Normal", "Large"]
        ctk.CTkOptionMenu(row3, variable=self.size_var, values=sizes, command=lambda v: self.update_setting("font_size", v),
              fg_color=self.colors.get('dropdown_bg', self.colors['main_text']), button_color=self.colors.get('primary'), text_color=self.colors.get('dropdown_text', 'white')).pack(side="right")

        # Live Theme Preview
        preview_container = ctk.CTkFrame(frame, fg_color="transparent")
        preview_container.pack(fill="x", padx=20, pady=(8, 12))

        self.preview_header = ctk.CTkFrame(preview_container, fg_color=self.colors['primary_dark'], corner_radius=6)
        self.preview_header.pack(fill="x")
        self.preview_header_label = ctk.CTkLabel(self.preview_header, text="Header Preview", font=self.master.master.get_font(-1, "bold"), text_color=self.colors['header_text'])
        self.preview_header_label.pack(expand=True)

        sample_row = ctk.CTkFrame(preview_container, fg_color="transparent")
        sample_row.pack(fill="x", pady=(8,0))

        self.preview_sidebar = ctk.CTkFrame(sample_row, fg_color=self.colors['primary'], width=120, height=80, corner_radius=6)
        self.preview_sidebar.pack(side="left", padx=(0,8))
        self.preview_sidebar_label = ctk.CTkLabel(self.preview_sidebar, text="Sidebar", font=self.master.master.get_font(-2), text_color=self.colors['sidebar_text'])
        self.preview_sidebar_label.pack(expand=True)

        self.preview_main = ctk.CTkFrame(sample_row, fg_color=self.colors['background'], corner_radius=6)
        self.preview_main.pack(fill="x", expand=True)
        self.preview_main_label = ctk.CTkLabel(self.preview_main, text="Main Area", font=self.master.master.get_font(-2), text_color=self.colors['main_text'])
        self.preview_main_label.pack(padx=8, pady=8, anchor="w")

        # Add additional sample controls to the preview so users can see how
        # dropdowns, entries and buttons will look in the selected theme.
        sample_controls = ctk.CTkFrame(self.preview_main, fg_color="transparent")
        sample_controls.pack(fill="x", padx=8, pady=(6, 10))

        # Sample label
        self.preview_sample_label = ctk.CTkLabel(sample_controls, text="Sample Label:", font=self.master.master.get_font(-3), text_color=self.colors['secondary_text'])
        self.preview_sample_label.pack(side="left", padx=(0, 8))

        # Sample dropdown
        self.preview_sample_var = ctk.StringVar(value="Option 1")
        self.preview_sample_dropdown = ctk.CTkOptionMenu(sample_controls, variable=self.preview_sample_var, values=["Option 1", "Option 2"], width=140,
                     fg_color=self.colors.get('dropdown_bg', self.colors['main_text']), button_color=self.colors.get('primary'),
                     text_color=self.colors.get('dropdown_text', 'white'))
        self.preview_sample_dropdown.pack(side="left", padx=(0, 8))

        # Sample entry
        self.preview_sample_entry = ctk.CTkEntry(sample_controls, placeholder_text="Type...", width=180,
                             fg_color=self.colors.get('card_bg'), text_color=self.colors.get('main_text'))
        self.preview_sample_entry.pack(side="left", padx=(0, 8))

        # Sample action buttons
        btns = ctk.CTkFrame(self.preview_main, fg_color="transparent")
        btns.pack(fill="x", padx=8, pady=(0, 8))
        self.preview_sample_primary = ctk.CTkButton(btns, text="Primary", width=100, fg_color=self.colors.get('accent'), text_color="white")
        self.preview_sample_primary.pack(side="left", padx=(0, 8))
        self.preview_sample_secondary = ctk.CTkButton(btns, text="Secondary", width=100, fg_color=self.colors.get('card_bg'), text_color=self.colors.get('main_text'))
        self.preview_sample_secondary.pack(side="left")

        # Initialize preview with current theme selection
        try:
            self.preview_theme(self.theme_var.get())
        except Exception:
            pass

    def _setup_inspiration_section(self):
        frame = ctk.CTkFrame(self.container, fg_color=self.colors['card_bg'], corner_radius=10)
        frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(frame, text="Inspiration & Quotes", font=self.master.master.get_font(2, "bold"), text_color=self.colors['main_text']).pack(anchor="w", padx=20, pady=15)
        
        # Timer
        row1 = ctk.CTkFrame(frame, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(row1, text="Change Quote Every (seconds):", font=self.master.master.get_font(0), text_color=self.colors['main_text']).pack(side="left")
        
        self.timer_entry = ctk.CTkEntry(row1, width=60, fg_color=self.colors['background'], text_color=self.colors['main_text'])
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
        ctk.CTkLabel(self.templates_frame, text="View, create, edit, or delete templates for notes.", font=self.master.master.get_font(0), text_color=self.colors['secondary_text']).pack(anchor="w", padx=20)

        # Add Template Button
        ctk.CTkButton(self.templates_frame, text="+ Create New Template", command=self.create_template,
                      fg_color=self.colors['primary'], height=35).pack(padx=20, pady=10, fill="x")

        # Scrollable list of templates
        template_list_frame = ctk.CTkScrollableFrame(self.templates_frame, fg_color="transparent", height=220)
        template_list_frame.pack(fill="x", padx=20, pady=(0, 10))

        # Get all templates (default + custom)
        all_templates = list(self.TEMPLATES.items())
        custom_templates = self.settings.get("custom_templates", {})

        for title, structure in all_templates:
            row = ctk.CTkFrame(template_list_frame, fg_color=self.colors['card_bg'], corner_radius=6)
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=title, font=self.master.master.get_font(0, "bold"), text_color=self.colors['main_text'], width=180, anchor="w").pack(side="left", padx=(8, 8))

            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.pack(side="right", padx=8)

            # Edit button
            ctk.CTkButton(actions, text="Edit", width=70, height=28, fg_color=self.colors['info'],
                          command=lambda t=title: self.edit_template_dialog(t)).pack(side="left", padx=(0,6))

            # Only allow delete for custom templates
            if title in custom_templates:
                ctk.CTkButton(actions, text="Delete", width=70, height=28, fg_color=self.colors['danger'],
                              command=lambda t=title: self.delete_template(t)).pack(side="left")

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
                self.preview_sample_dropdown.configure(fg_color=theme.get('dropdown_bg'), text_color=theme.get('dropdown_text'), button_color=theme.get('primary'))
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

    def create_template(self):
        def on_save(title, structure):
            custom_templates = self.settings.get("custom_templates", {})
            # Check for duplicates
            if title in self.TEMPLATES:
                messagebox.showerror("Error", "Template name already exists!")
                return
            custom_templates[title] = structure
            self.data_manager.update_setting("custom_templates", custom_templates)
            self.TEMPLATES.update(custom_templates)
            messagebox.showinfo("Success", "Template added! It will appear in the dropdown.")
            self._setup_templates_section() # Refresh list
        TemplateDialog(self.master, on_save=on_save)
    def edit_template_dialog(self, template_title):
        structure = self.TEMPLATES.get(template_title, "")
        is_custom = template_title in self.settings.get("custom_templates", {})
        def on_save(new_title, new_structure):
            custom_templates = self.settings.get("custom_templates", {})
            # If title changed, handle renaming
            if new_title != template_title:
                if new_title in self.TEMPLATES:
                    messagebox.showerror("Error", "Template name already exists!")
                    return
                # Remove old
                if is_custom:
                    custom_templates.pop(template_title, None)
            custom_templates[new_title] = new_structure
            self.data_manager.update_setting("custom_templates", custom_templates)
            self.TEMPLATES.update(custom_templates)
            messagebox.showinfo("Success", "Template updated!")
            self._setup_templates_section() # Refresh list
        TemplateDialog(self.master, title_init=template_title, structure_init=structure, on_save=on_save, is_edit=True)

    def delete_template(self, template_title):
        if not messagebox.askyesno("Delete Template", f"Delete template '{template_title}'? This cannot be undone."):
            return
        custom_templates = self.settings.get("custom_templates", {})
        if template_title in custom_templates:
            custom_templates.pop(template_title)
            self.data_manager.update_setting("custom_templates", custom_templates)
            # Remove from TEMPLATES
            self.TEMPLATES.pop(template_title, None)
            messagebox.showinfo("Deleted", "Template deleted.")
            self._setup_templates_section() # Refresh list


if __name__ == "__main__":
    app = CourseMate()
    app.mainloop()
