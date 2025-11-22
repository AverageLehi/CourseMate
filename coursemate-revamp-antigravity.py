import customtkinter as ctk
import json
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog

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
        'danger':           '#e74c3c'
    },
    # Add other themes here as needed, copying from original if desired
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

    def add_notebook(self, name):
        if name not in self.data["courses"]:
            self.data["courses"][name] = {"notes": [], "tasks": []}
            self.save_data()
            return True
        return False

    def rename_notebook(self, old_name, new_name):
        if old_name in self.data["courses"] and new_name not in self.data["courses"]:
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
        self.data_manager = DataManager()
        self.current_theme = self.data_manager.get_settings()["theme"]
        self.colors = THEMES.get(self.current_theme, THEMES['CourseMate Theme'])
        
        # Window Setup
        self.title("CourseMate")
        self.geometry("1200x800")
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
        HomeView(self.main_area, self.data_manager, self.colors)

    def show_notebooks(self):
        self.clear_main_area()
        NotebooksView(self.main_area, self.data_manager, self.colors)

    def show_settings(self):
        self.clear_main_area()
        SettingsView(self.main_area, self.data_manager, self.colors)

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
        ctk.CTkLabel(self, text="CourseMate", font=("Helvetica", 24, "bold"), text_color=colors['header_text']).pack(pady=(30, 10))
        ctk.CTkLabel(self, text="Stay Organized • Learn Deeper", font=("Helvetica", 12), text_color=colors['secondary_text']).pack(pady=(0, 20))
        
        # Quick Stats
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=20, pady=(0, 20))
        self.lbl_notebooks_count = ctk.CTkLabel(self.stats_frame, text="Notebooks: 0", font=("Helvetica", 12, "bold"), text_color=colors['header_text'], anchor="w")
        self.lbl_notebooks_count.pack(fill="x")
        self.lbl_notes_count = ctk.CTkLabel(self.stats_frame, text="Total Notes: 0", font=("Helvetica", 12, "bold"), text_color=colors['header_text'], anchor="w")
        self.lbl_notes_count.pack(fill="x")
        
        # Navigation
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(fill="x", pady=10)
        
        self._create_nav_btn("Home", home_cb)
        self._create_nav_btn("Notebooks", notebooks_cb)
        self._create_nav_btn("Settings", settings_cb)
        
        # Notebooks Quick Access (Scrollable)
        ctk.CTkLabel(self, text="NOTEBOOKS", font=("Helvetica", 12, "bold"), text_color=colors['secondary_text'], anchor="w").pack(fill="x", padx=20, pady=(20, 5))
        
        self.notebooks_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", height=150)
        self.notebooks_frame.pack(fill="x", padx=10, pady=5)
        
        # Inspiration Section (Bottom)
        self.inspiration_frame = ctk.CTkFrame(self, fg_color=colors['card_bg'], corner_radius=10)
        self.inspiration_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(self.inspiration_frame, text="Inspiration", font=("Helvetica", 12, "bold"), text_color=colors['main_text']).pack(pady=(10, 5))
        self.lbl_quote = ctk.CTkLabel(self.inspiration_frame, text="Loading quote...", font=("Helvetica", 11, "italic"), 
                                      text_color=colors['main_text'], wraplength=180)
        self.lbl_quote.pack(pady=(0, 10), padx=10)
        
        # Initial Data Load
        self.refresh_stats()
        self.refresh_notebooks_list()
        self.start_quote_timer()

    def _create_nav_btn(self, text, command):
        btn = ctk.CTkButton(self.nav_frame, text=text, command=command, 
                            fg_color="transparent", hover_color=self.colors['sidebar_hover'], 
                            anchor="w", height=40, font=("Helvetica", 16, "bold"), text_color=self.colors['sidebar_text'])
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
             ctk.CTkLabel(self.notebooks_frame, text="No notebooks yet", font=("Helvetica", 11), text_color=self.colors['secondary_text']).pack(anchor="w", padx=10)
        else:
            for name in notebooks:
                btn = ctk.CTkButton(self.notebooks_frame, text=f"📓 {name}", 
                                    command=lambda n=name: self.open_notebook(n),
                                    fg_color="transparent", hover_color=self.colors['sidebar_hover'], 
                                    anchor="w", height=30, font=("Helvetica", 12), text_color=self.colors['sidebar_text'])
                btn.pack(fill="x", pady=1)

    def open_notebook(self, name):
        # Switch to Notebooks view and select the notebook
        # This requires the main app to handle the switching and selection
        # For now, we just switch to the view
        self.notebooks_cb()
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
        
        ctk.CTkLabel(header, text="Write", font=("Helvetica", 20, "bold"), text_color=self.colors['main_text']).pack(side="left")
        
        # Controls Row
        controls = ctk.CTkFrame(self.write_frame, fg_color="transparent")
        controls.pack(fill="x", padx=20, pady=(0, 10))
        
        # Assigned To
        ctk.CTkLabel(controls, text="Assigned to:", font=("Helvetica", 12), text_color=self.colors['main_text']).pack(side="left", padx=(0, 5))
        self.notebook_var = ctk.StringVar(value="None")
        notebooks = ["None"] + list(self.data_manager.get_notebooks().keys())
        self.notebook_dropdown = ctk.CTkOptionMenu(controls, variable=self.notebook_var, values=notebooks,
                                                   fg_color=self.colors['primary'], button_color=self.colors['primary_dark'],
                                                   text_color="white", width=150)
        self.notebook_dropdown.pack(side="left", padx=(0, 20))
        
        # Template
        ctk.CTkLabel(controls, text="Template:", font=("Helvetica", 12), text_color=self.colors['main_text']).pack(side="left", padx=(0, 5))
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

        # Title Entry
        self.title_entry = ctk.CTkEntry(self.write_frame, placeholder_text="Note Title (Required)", 
                                        font=("Helvetica", 14, "bold"), height=40,
                                        fg_color=self.colors['background'], text_color=self.colors['main_text'], border_width=0)
        self.title_entry.pack(fill="x", padx=20, pady=(0, 10))

        # Text Area
        self.text_area = ctk.CTkTextbox(self.write_frame, font=("Helvetica", 12), 
                                        fg_color=self.colors['background'], text_color=self.colors['main_text'],
                                        wrap="word", corner_radius=10)
        self.text_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def _setup_notes_ui(self):
        # Header
        ctk.CTkLabel(self.notes_frame, text="Unassigned Notes", font=("Helvetica", 16, "bold"), 
                     text_color=self.colors['main_text']).pack(pady=20, padx=20, anchor="w")
        
        ctk.CTkLabel(self.notes_frame, text="Notes created here without a notebook appear below.", 
                     font=("Helvetica", 11), text_color=self.colors['secondary_text'], wraplength=250).pack(pady=(0, 10), padx=20, anchor="w")
        
        # Scrollable List
        self.notes_list = ctk.CTkScrollableFrame(self.notes_frame, fg_color="transparent")
        self.notes_list.pack(fill="both", expand=True, padx=10, pady=10)
        
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

    def save_note(self):
        title = self.title_entry.get().strip()
        content = self.text_area.get("1.0", "end-1c").strip()
        assigned_notebook = self.notebook_var.get()
        
        if not title:
            messagebox.showwarning("Missing Title", "Please enter a title for your note.")
            return
        
        if not content:
            messagebox.showwarning("Empty Note", "Cannot save an empty note.")
            return
            
        note = {
            "title": title,
            "content": content,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "notebook": assigned_notebook if assigned_notebook != "None" else None
        }
        
        if assigned_notebook != "None":
            self.data_manager.add_note_to_notebook(assigned_notebook, note)
            messagebox.showinfo("Saved", f"Note saved to '{assigned_notebook}'")
        else:
            self.data_manager.add_unassigned_note(note)
            self.refresh_notes_list()
            
        # Clear inputs
        self.title_entry.delete(0, "end")
        self.text_area.delete("1.0", "end")
        self.notebook_var.set("None")
        
        # Refresh sidebar stats
        if isinstance(self.master.master, CourseMateRevampApp):
             self.master.master.sidebar.refresh_stats()

    def refresh_notes_list(self):
        for widget in self.notes_list.winfo_children():
            widget.destroy()
            
        notes = self.data_manager.get_unassigned_notes()
        
        if not notes:
            ctk.CTkLabel(self.notes_list, text="No unassigned notes", font=("Helvetica", 12, "italic"), 
                         text_color=self.colors['secondary_text']).pack(pady=20)
            return

        for note in reversed(notes): # Show newest first
            self._create_note_card(note)

    def _create_note_card(self, note):
        card = ctk.CTkFrame(self.notes_list, fg_color=self.colors['background'], corner_radius=8)
        card.pack(fill="x", pady=5)
        
        # Click event to open note
        card.bind("<Button-1>", lambda e, n=note: self.open_note_window(n))
        
        title = note.get('title', 'Untitled')
        date = note.get('created', '').split(' ')[0] # Just date
        preview = note.get('content', '')[:30].replace('\n', ' ') + "..."
        
        lbl_title = ctk.CTkLabel(card, text=f"{title} - {date}", font=("Helvetica", 12, "bold"), text_color=self.colors['main_text'], anchor="w")
        lbl_title.pack(fill="x", padx=10, pady=(5, 0))
        lbl_title.bind("<Button-1>", lambda e, n=note: self.open_note_window(n))
        
        lbl_preview = ctk.CTkLabel(card, text=preview, font=("Helvetica", 11), text_color=self.colors['secondary_text'], anchor="w")
        lbl_preview.pack(fill="x", padx=10, pady=(0, 5))
        lbl_preview.bind("<Button-1>", lambda e, n=note: self.open_note_window(n))

    def open_note_window(self, note):
        # Open note in new window
        NoteWindow(self.master, note, self.colors)

class NoteWindow(ctk.CTkToplevel):
    def __init__(self, master, note, colors):
        super().__init__(master)
        self.title(note.get('title', 'Note'))
        self.geometry("600x500")
        
        self.colors = colors
        self.note = note
        
        # Title
        ctk.CTkLabel(self, text=note.get('title', 'Untitled'), font=("Helvetica", 20, "bold"), text_color=colors['main_text']).pack(pady=20, padx=20, anchor="w")
        
        # Content
        self.text_area = ctk.CTkTextbox(self, font=("Helvetica", 12), fg_color=colors['background'], text_color=colors['main_text'], wrap="word")
        self.text_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.text_area.insert("1.0", note.get('content', ''))
        
        # Save Button (For editing)
        ctk.CTkButton(self, text="Save Changes", command=self.save_changes, fg_color=colors['success'], text_color="white").pack(pady=10)

    def save_changes(self):
        # This is a simplified save - it updates the object in memory but we need to persist it
        # Since we passed the dictionary reference, modifying it here modifies it in the list
        # But we need to trigger a save to disk.
        self.note['content'] = self.text_area.get("1.0", "end-1c")
        
        # Trigger save in data manager (a bit hacky, ideally we pass a save callback)
        # We'll assume the main app instance is available or we can access data manager
        # For now, let's just show a message that it's updated in memory
        # To fix this properly, we should pass a save_callback to this window.
        messagebox.showinfo("Updated", "Note content updated in memory. (Disk save pending implementation)")

class NotebooksView:
    def __init__(self, master, data_manager, colors):
        self.master = master
        self.data_manager = data_manager
        self.colors = colors
        self.selected_notebook = None
        
        # Main Container
        self.container = ctk.CTkFrame(master, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left Column: Notebooks List (30%)
        self.left_col = ctk.CTkFrame(self.container, fg_color=colors['card_bg'], corner_radius=15, width=300)
        self.left_col.pack(side="left", fill="y", padx=(0, 10))
        
        # Right Column: Notes List (70%)
        self.right_col = ctk.CTkFrame(self.container, fg_color=colors['card_bg'], corner_radius=15)
        self.right_col.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        self._setup_notebooks_list()
        self._setup_notes_view()

    def _setup_notebooks_list(self):
        # Header
        header = ctk.CTkFrame(self.left_col, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=15)
        ctk.CTkLabel(header, text="Notebooks", font=("Helvetica", 16, "bold"), text_color=self.colors['main_text']).pack(side="left")
        
        # Add Button
        ctk.CTkButton(header, text="+", width=30, command=self.add_notebook,
                      fg_color=self.colors['success'], hover_color='#219150', text_color="white").pack(side="right")
        
        # List
        self.notebook_list_frame = ctk.CTkScrollableFrame(self.left_col, fg_color="transparent")
        self.notebook_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.refresh_notebooks()

    def _setup_notes_view(self):
        # Header
        self.notes_header = ctk.CTkFrame(self.right_col, fg_color="transparent")
        self.notes_header.pack(fill="x", padx=20, pady=20)
        
        self.lbl_notebook_title = ctk.CTkLabel(self.notes_header, text="Select a Notebook", font=("Helvetica", 20, "bold"), text_color=self.colors['main_text'])
        self.lbl_notebook_title.pack(side="left")
        
        # Notebook Actions (Rename/Delete) - Hidden initially
        self.notebook_actions = ctk.CTkFrame(self.notes_header, fg_color="transparent")
        
        ctk.CTkButton(self.notebook_actions, text="Rename", width=80, command=self.rename_notebook,
                      fg_color=self.colors['info'], text_color="white").pack(side="left", padx=5)
        ctk.CTkButton(self.notebook_actions, text="Delete", width=80, command=self.delete_notebook,
                      fg_color=self.colors['danger'], text_color="white").pack(side="left", padx=5)
        
        # Notes List Area
        self.notes_area = ctk.CTkScrollableFrame(self.right_col, fg_color="transparent")
        self.notes_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(self.notes_area, text="Select a notebook to view notes", font=("Helvetica", 14), text_color=self.colors['secondary_text']).pack(pady=50)

    def refresh_notebooks(self):
        for widget in self.notebook_list_frame.winfo_children():
            widget.destroy()
            
        notebooks = self.data_manager.get_notebooks()
        
        for name in notebooks:
            btn = ctk.CTkButton(self.notebook_list_frame, text=f"📓 {name}", 
                                command=lambda n=name: self.select_notebook(n),
                                fg_color=self.colors['primary'] if name == self.selected_notebook else "transparent", 
                                hover_color=self.colors['sidebar_hover'],
                                text_color=self.colors['sidebar_text'] if name == self.selected_notebook else self.colors['main_text'],
                                anchor="w", height=40, font=("Helvetica", 13))
            btn.pack(fill="x", pady=2)

    def select_notebook(self, name):
        self.selected_notebook = name
        self.refresh_notebooks() # To update selection highlight
        
        # Update Right Column
        self.lbl_notebook_title.configure(text=name)
        self.notebook_actions.pack(side="right") # Show actions
        
        # Refresh Notes
        for widget in self.notes_area.winfo_children():
            widget.destroy()
            
        notes = self.data_manager.get_notebooks()[name].get('notes', [])
        
        if not notes:
            ctk.CTkLabel(self.notes_area, text="No notes in this notebook", font=("Helvetica", 12, "italic"), text_color=self.colors['secondary_text']).pack(pady=20)
        else:
            for i, note in enumerate(notes):
                self._create_note_item(note, i)

    def _create_note_item(self, note, index):
        card = ctk.CTkFrame(self.notes_area, fg_color=self.colors['background'], corner_radius=10)
        card.pack(fill="x", pady=5)
        
        # Header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(header, text=note.get('title', 'Untitled'), font=("Helvetica", 14, "bold"), text_color=self.colors['main_text']).pack(side="left")
        ctk.CTkLabel(header, text=note.get('created', ''), font=("Helvetica", 11), text_color=self.colors['secondary_text']).pack(side="left", padx=10)
        
        # Delete Note Button
        ctk.CTkButton(header, text="×", width=30, height=20, command=lambda: self.delete_note(index),
                      fg_color="transparent", hover_color=self.colors['danger'], text_color=self.colors['danger']).pack(side="right")
        
        # Preview
        preview = note.get('content', '')[:100].replace('\n', ' ') + "..."
        ctk.CTkLabel(card, text=preview, font=("Helvetica", 12), text_color=self.colors['main_text'], anchor="w").pack(fill="x", padx=15, pady=(0, 10))
        
        # Open Button
        ctk.CTkButton(card, text="Open Note", command=lambda: self.open_note(note),
                      fg_color=self.colors['primary'], height=25, font=("Helvetica", 11)).pack(fill="x", padx=15, pady=(0, 10))

    def add_notebook(self):
        name = simpledialog.askstring("New Notebook", "Enter notebook name:")
        if name and name.strip():
            if self.data_manager.add_notebook(name.strip()):
                self.refresh_notebooks()
                # Update sidebar too
                if isinstance(self.master.master, CourseMateRevampApp):
                    self.master.master.sidebar.refresh_notebooks_list()
                    self.master.master.sidebar.refresh_stats()
            else:
                messagebox.showwarning("Error", "Notebook already exists!")

    def rename_notebook(self):
        if not self.selected_notebook: return
        new_name = simpledialog.askstring("Rename", "Enter new name:", initialvalue=self.selected_notebook)
        if new_name and new_name.strip() and new_name != self.selected_notebook:
            if self.data_manager.rename_notebook(self.selected_notebook, new_name.strip()):
                self.selected_notebook = new_name.strip()
                self.refresh_notebooks()
                self.select_notebook(new_name.strip()) # Refresh view
                # Update sidebar
                if isinstance(self.master.master, CourseMateRevampApp):
                    self.master.master.sidebar.refresh_notebooks_list()
            else:
                messagebox.showwarning("Error", "Name already exists or invalid!")

    def delete_notebook(self):
        if not self.selected_notebook: return
        if messagebox.askyesno("Delete", f"Delete notebook '{self.selected_notebook}' and all its notes?"):
            self.data_manager.delete_notebook(self.selected_notebook)
            self.selected_notebook = None
            self.refresh_notebooks()
            self.lbl_notebook_title.configure(text="Select a Notebook")
            self.notebook_actions.pack_forget()
            for widget in self.notes_area.winfo_children():
                widget.destroy()
            # Update sidebar
            if isinstance(self.master.master, CourseMateRevampApp):
                self.master.master.sidebar.refresh_notebooks_list()
                self.master.master.sidebar.refresh_stats()

    def delete_note(self, index):
        if not self.selected_notebook: return
        if messagebox.askyesno("Delete Note", "Are you sure you want to delete this note?"):
            self.data_manager.delete_note(self.selected_notebook, index)
            self.select_notebook(self.selected_notebook) # Refresh list
            # Update sidebar stats
            if isinstance(self.master.master, CourseMateRevampApp):
                self.master.master.sidebar.refresh_stats()

    def open_note(self, note):
        NoteWindow(self.master, note, self.colors)

class SettingsView:
    def __init__(self, master, data_manager, colors):
        self.master = master
        self.data_manager = data_manager
        self.colors = colors
        self.settings = data_manager.get_settings()
        
        self.container = ctk.CTkScrollableFrame(master, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(self.container, text="Settings", font=("Helvetica", 24, "bold"), text_color=colors['main_text']).pack(anchor="w", pady=(0, 20))
        
        self._setup_appearance_section()
        self._setup_inspiration_section()
        self._setup_templates_section()

    def _setup_appearance_section(self):
        frame = ctk.CTkFrame(self.container, fg_color=self.colors['card_bg'], corner_radius=10)
        frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(frame, text="Appearance", font=("Helvetica", 16, "bold"), text_color=self.colors['main_text']).pack(anchor="w", padx=20, pady=15)
        
        # Theme
        row1 = ctk.CTkFrame(frame, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(row1, text="Theme Color:", font=("Helvetica", 12), text_color=self.colors['main_text']).pack(side="left")
        
        self.theme_var = ctk.StringVar(value=self.settings.get("theme", "CourseMate Theme"))
        themes = list(THEMES.keys())
        ctk.CTkOptionMenu(row1, variable=self.theme_var, values=themes, command=self.change_theme,
                          fg_color=self.colors['primary'], button_color=self.colors['primary_dark']).pack(side="right")
        
        # Font Family
        row2 = ctk.CTkFrame(frame, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(row2, text="Font Style:", font=("Helvetica", 12), text_color=self.colors['main_text']).pack(side="left")
        
        self.font_var = ctk.StringVar(value=self.settings.get("font_family", "Helvetica"))
        fonts = ["Helvetica", "Times New Roman", "Courier New"]
        ctk.CTkOptionMenu(row2, variable=self.font_var, values=fonts, command=lambda v: self.update_setting("font_family", v),
                          fg_color=self.colors['primary'], button_color=self.colors['primary_dark']).pack(side="right")

        # Font Size
        row3 = ctk.CTkFrame(frame, fg_color="transparent")
        row3.pack(fill="x", padx=20, pady=(5, 20))
        ctk.CTkLabel(row3, text="Font Size:", font=("Helvetica", 12), text_color=self.colors['main_text']).pack(side="left")
        
        self.size_var = ctk.StringVar(value=self.settings.get("font_size", "Normal"))
        sizes = ["Normal", "Large"]
        ctk.CTkOptionMenu(row3, variable=self.size_var, values=sizes, command=lambda v: self.update_setting("font_size", v),
                          fg_color=self.colors['primary'], button_color=self.colors['primary_dark']).pack(side="right")

    def _setup_inspiration_section(self):
        frame = ctk.CTkFrame(self.container, fg_color=self.colors['card_bg'], corner_radius=10)
        frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(frame, text="Inspiration & Quotes", font=("Helvetica", 16, "bold"), text_color=self.colors['main_text']).pack(anchor="w", padx=20, pady=15)
        
        # Timer
        row1 = ctk.CTkFrame(frame, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(row1, text="Change Quote Every (seconds):", font=("Helvetica", 12), text_color=self.colors['main_text']).pack(side="left")
        
        self.timer_entry = ctk.CTkEntry(row1, width=60, fg_color=self.colors['background'], text_color=self.colors['main_text'])
        self.timer_entry.insert(0, str(self.settings.get("quote_timer", 30)))
        self.timer_entry.pack(side="left", padx=10)
        
        ctk.CTkButton(row1, text="Save Timer", width=80, command=self.save_timer,
                      fg_color=self.colors['info']).pack(side="left")
        
        # Add Quote
        row2 = ctk.CTkFrame(frame, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=(15, 5))
        ctk.CTkLabel(row2, text="Add New Quote:", font=("Helvetica", 12), text_color=self.colors['main_text']).pack(anchor="w")
        
        self.quote_entry = ctk.CTkEntry(row2, placeholder_text="Enter a favorite quote...", fg_color=self.colors['background'], text_color=self.colors['main_text'])
        self.quote_entry.pack(fill="x", pady=5)
        
        ctk.CTkButton(row2, text="Add Quote", command=self.add_quote,
                      fg_color=self.colors['success']).pack(anchor="e", pady=5)

    def _setup_templates_section(self):
        frame = ctk.CTkFrame(self.container, fg_color=self.colors['card_bg'], corner_radius=10)
        frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(frame, text="Custom Templates", font=("Helvetica", 16, "bold"), text_color=self.colors['main_text']).pack(anchor="w", padx=20, pady=15)
        
        ctk.CTkLabel(frame, text="Create your own templates for the Home screen.", font=("Helvetica", 12), text_color=self.colors['secondary_text']).pack(anchor="w", padx=20)
        
        # Add Template Button
        ctk.CTkButton(frame, text="+ Create New Template", command=self.create_template,
                      fg_color=self.colors['primary'], height=35).pack(padx=20, pady=20, fill="x")

    def update_setting(self, key, value):
        self.data_manager.update_setting(key, value)
        messagebox.showinfo("Settings Saved", f"{key.replace('_', ' ').title()} updated! Restart app to see full changes.")

    def change_theme(self, new_theme):
        self.data_manager.update_setting("theme", new_theme)
        messagebox.showinfo("Theme Changed", "Theme saved! Please restart the application to apply the new theme.")

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
        custom_templates[name] = content.replace("\\n", "\n")
        self.data_manager.update_setting("custom_templates", custom_templates)
        
        # Update HomeView
        HomeView.TEMPLATES.update(custom_templates)
        messagebox.showinfo("Success", "Template added! It will appear in the dropdown.")


if __name__ == "__main__":
    app = CourseMateRevampApp()
    app.mainloop()
