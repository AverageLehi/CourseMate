import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
from datetime import datetime
from pathlib import Path
import customtkinter as ctk

# ============================================================================
# MAIN APPLICATION CLASS
# ============================================================================

class CourseMateApp:
    """
    Main CourseMate application class.
    
    Structure:
    1. __init__ - Initializes the app and sets up everything when it starts.
    2. Data methods - Load and save data using JSON files.
    3. UI methods - Build the user interface (windows, buttons, etc.).
    4. Action methods - Define what happens when you click buttons or interact with the app.
    """
   
    # ------------------------------------------------------------------------
    # Theme definitions (class attribute): multiple named palettes
    # You can add more palettes here; keys must match usages below.
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

        'Slate Gray': {
            'primary_dark':     '#2b3438',
            'primary':          '#3b4a4f',
            'accent':           '#2aa198',
            'background':       '#f7f7f7',
            'sidebar_button':   '#3b4a4f',
            'sidebar_hover':    '#4a5a5f',
            'sidebar_text':     '#F4F4F4',
            'card_bg':          '#e1e7ed',
            'success':          '#27ae60',
            'info':             '#3498db',
            'warning':          '#ffe082',
            'muted':            '#99a1a4',
            'header_text':      '#F4F4F4',
            'main_text':        '#132028',
            'secondary_text':   '#97a0a3', 
            'danger':           '#e74c3c'
        },
        'Warm Charcoal': {
            'primary_dark':     '#2e3336',
            'primary':          '#3b4044',
            'accent':           '#22a155',
            'background':       '#f6f6f6',
            'sidebar_button':   '#3b4044',
            'sidebar_hover':    '#495052',
            'sidebar_text':     "#FFFFFF",
            'card_bg':          '#e1e7ed',
            'success':          '#27ae60',
            'info':             '#3498db',
            'warning':          '#ffe082',
            'muted':            '#a0a6a8',
            'header_text':      '#F4F4F4',
            'main_text':        '#0b2427',
            'secondary_text':   '#8f9698', 
            'danger':           '#e74c3c'
        },
        'Soft Pink': {
            'primary_dark':   '#CC6F95',
            'primary':        '#FF9BBE',
            'accent':         '#FFB4CD',
            'background':     '#F8F8F8',
            'sidebar_button': '#FF9BBE',
            'sidebar_hover':  '#E887AB',
            'sidebar_text':   "#FCE8F1",
            'card_bg':        '#FFFFFF',
            'success':        '#7ACDA0',
            'info':           '#A0D4FF',
            'warning':        '#FFD28B',
            'muted':          "#FFBBD3",
            'header_text':    '#FFFFFF',
            'main_text':      '#1A1A1A',
            'secondary_text': "#FFF4F8",
            'danger':         '#E57373',
        },
        'Baby Blue': {
            'primary_dark':   '#6FAFE0',
            'primary':        '#90C9FF',
            'accent':         '#A8D7FF',
            'background':     '#F8F8F8',
            'sidebar_button': '#90C9FF',
            'sidebar_hover':  '#7AB7EE',
            'sidebar_text':   '#FFFFFF',
            'card_bg':        '#FFFFFF',
            'success':        '#7ACDA0',
            'info':           '#90C9FF',
            'warning':        '#FFD28B',
            'muted':          "#C0DEFA",
            'header_text':    '#FFFFFF',
            'main_text':      '#1A1A1A',
            'secondary_text': '#555555',
            'danger':         '#E57373',
        },
    }

    # Default class-level COLORS (initially use one theme)
    COLORS = THEMES['CourseMate Theme']

    # ------------------------------------------------------------------------
    # PART 1: INITIALIZATION (Runs when app starts)
    # ------------------------------------------------------------------------
   
    def __init__(self, root):
        """
        Set up the app when it starts.
        This method creates the main window, loads data, and builds the interface.
        """
        self.root = root
        self.root.title("CourseMate - Smart Note-Taking & Study Aid For Students")
        self.root.geometry("1100x700")
        self.root.minsize(1000, 800)
        
        # Set default appearance mode
        ctk.set_appearance_mode("System")
        
        # Theme state (instance-level). Start with the class default.
        self.theme_name = 'CourseMate Theme'
        self.colors = CourseMateApp.COLORS.copy()
        # Width used by sidebar buttons and the header stats card so they align
        self.sidebar_button_width = 180
       
        # DATA: Store everything here
        self.courses = {}  # Format: {"Course Name": {"notes": [], "tasks": []}}
        self.tasks = []    # Active tasks list
        self.completed_tasks = []  # Completed tasks
       
        # LOAD DATA: Get saved data from file
        self.data_file = Path("Coursemate_data.json")
        self._load_data()
       
        # CREATE UI: Build the interface
        self._setup_styles()
        self._create_layout()
        self._create_widgets()
       
        # START: Show dashboard first
        self.show_dashboard()
       
        print("✅ CourseMate started! Data auto-saves.")
   
    # ------------------------------------------------------------------------
    # PART 2: DATA STORAGE (JSON - Easy to understand!)
    # ------------------------------------------------------------------------
   
    def _load_data(self):
        """
        Load data from a JSON file.
        This reads saved courses and tasks from disk so you don't lose your progress.
        """
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    data = json.load(f)  # Read the file
                    self.courses = data.get("courses", {})
                    self.tasks = data.get("tasks", [])
                    self.completed_tasks = data.get("completed_tasks", [])
                print(f"📁 Loaded {len(self.courses)} courses")
            else:
                print("📁 No saved data, starting fresh")
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            self.courses = {}
            self.tasks = []
   
    def _save_data(self):
        """
        Save data to a JSON file.
        This is called automatically whenever you make changes, so your work is always saved.
        """
        try:
            data = {
                "courses": self.courses,
                "tasks": self.tasks,
                "completed_tasks": self.completed_tasks
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)  # Write  to file
            print("💾 Data saved automatically")
        except Exception as e:
            print(f"❌ Error saving: {e}")
            messagebox.showerror("Save Error", f"Could not save data: {e}")
   
    # ------------------------------------------------------------------------
    # PART 3: UI SETUP (Create the interface)
    # ------------------------------------------------------------------------
   
    def _setup_styles(self):
        """
        Set up colors and styling for the app.
        Mostly handled by CustomTkinter now, but we keep this for legacy support
        or specific ttk widgets if needed.
        """
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure generic ttk styles if any remain
        style.configure('TFrame', background=self.colors['background'])
   
    def _create_layout(self):
        """
        Create the main layout of the app.
        Adds the header at the top, sidebar on the left, and main content area on the right.
        """
        self.header_frame = ctk.CTkFrame(self.root, height=110, corner_radius=0, fg_color=self.colors['primary_dark'])
        self.header_frame.pack(fill='x', side='top')
        self.header_frame.pack_propagate(False)
        
        # Sidebar (navigation)
        self.sidebar_frame = ctk.CTkFrame(self.root, width=220, corner_radius=0, fg_color=self.colors['primary_dark'])
        self.sidebar_frame.pack(fill='y', side='left')
        self.sidebar_frame.pack_propagate(False)
       
        # Main content area (where views appear)
        self.main_content = ctk.CTkFrame(self.root, corner_radius=0, fg_color=self.colors['background'])
        self.main_content.pack(fill='both', expand=True, side='right')

    def _create_widgets(self):
        """
        Create all widgets (buttons, labels, frames) for the app.
        This method builds the sidebar, header, navigation, and other UI elements.
        """

        # Header container frame
        self.header_container = ctk.CTkFrame(self.header_frame, fg_color=self.colors['primary_dark'], corner_radius=0)
        self.header_container.pack(fill='both', expand=True)

        # Title and slogan (centered, stacked)
        title_frame = ctk.CTkFrame(self.header_container, fg_color=self.colors['primary_dark'], corner_radius=0)
        title_frame.pack(fill='x', expand=True)
        
        ctk.CTkLabel(title_frame, text="CourseMate",
            font=('Helvetica', 26, 'bold'),
            text_color=self.colors['header_text']).pack(pady=(10,0), anchor='center')
            
        ctk.CTkLabel(title_frame, text="Stay Organized • Think Smarter • Learn Deeper • Solve Problems Better",
            font=('Helvetica', 12),
            text_color=self.colors['secondary_text']).pack(pady=(0,10), anchor='center')

        # NOTE: header keeps title and slogan only. Stats are shown in the sidebar.
        # Ensure stats are shown on startup (sidebar widgets created below)
        # (the actual labels are created in the sidebar area)
        
       
        # Header overlay: small stats + theme name placed over the title so the
        # centered title/slogan remain unchanged. Use a rounded CTkFrame.
        # To avoid the window's default (white) background showing through the
        # rounded corners, create a square "holder" with the same card color
        # behind the rounded frame. The holder provides a consistent background
        # so rounded corners blend seamlessly.
        overlay_color = self.colors.get('card_bg')

        # Holder behind the rounded overlay (square, no border)
        overlay_holder = ctk.CTkFrame(self.header_container,
                          fg_color=self.colors['primary_dark'],
                          corner_radius=0,
                          border_width=0,
                          width=self.sidebar_button_width,
                          height=90)
        # absolute placement so it doesn't affect packing of the centered title
        overlay_holder.place(x=20, y=10)

        # The actual rounded overlay sits inside the holder. Because the holder
        # uses the same `card_bg`, any transparent rounded corners will reveal
        # the same color instead of the white window background.
        header_overlay = ctk.CTkFrame(overlay_holder,
                          fg_color=overlay_color,
                          corner_radius=15,
                          border_width=2.5,
                          border_color=self.colors.get('muted'))
        header_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        # left column: numeric stats (stacked vertically)
        stats_col = ctk.CTkFrame(header_overlay, fg_color="transparent")
        stats_col.pack(side='left', anchor='n', padx=8, pady=6)

        # Use darker text on the light overlay so it remains readable
        stat_fg = self.colors.get('primary_dark', '#222222')

        self.stat_courses = ctk.CTkLabel(stats_col, text="", font=('Helvetica', 10, 'bold'), text_color=stat_fg, anchor="w")
        self.stat_courses.pack(anchor='w')
        self.stat_active_tasks = ctk.CTkLabel(stats_col, text="", font=('Helvetica', 10, 'bold'), text_color=stat_fg, anchor="w")
        self.stat_active_tasks.pack(anchor='w')
        self.stat_completed = ctk.CTkLabel(stats_col, text="", font=('Helvetica', 10, 'bold'), text_color=stat_fg, anchor="w")
        self.stat_completed.pack(anchor='w')

        # Theme shown as a quick stat (same format as other stats)
        self.stat_theme = ctk.CTkLabel(stats_col, text=f"Theme: {self.theme_name}", font=('Helvetica', 10, 'bold'), text_color=stat_fg, anchor="w")
        self.stat_theme.pack(anchor='w')

        # Ensure stats are shown on startup (populates text and swatch)
        self._update_stats()

        # Navigation section on sidebar
        ctk.CTkLabel(self.sidebar_frame, text="NAVIGATION",
            font=('Helvetica', 11, 'bold'),
            text_color=self.colors['sidebar_text'], anchor="w").pack(pady=(20,5), padx=20, anchor='w')

        main_nav = [
            ("Dashboard", self.show_dashboard),
            ("Freeform Notes", self.show_freeform),
            ("Task History", self.show_task_history) 
        ]

        for text, command in main_nav:
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                command=command,
                fg_color=self.colors['sidebar_button'],
                hover_color=self.colors['sidebar_hover'],
                text_color=self.colors['sidebar_text'],
                corner_radius=20,
                border_width=0,
                width=self.sidebar_button_width,
                height=35,
                font=("Helvetica", 13, "bold"),
                anchor="w"
            )
            btn.pack(pady=3, padx=20)
       
        # Non-Technical Templates Section
        ctk.CTkLabel(self.sidebar_frame, text="NON-TECHNICAL TEMPLATES",
            font=('Helvetica', 11, 'bold'),
            text_color=self.colors['sidebar_text'], anchor="w").pack(pady=(20,5), padx=20, anchor='w')
       
        non_tech_templates = [
            ("Cornell Notes", "Cornell"),
            ("Main Idea & Details", "MainIdea"),
            ("Modified Frayer Model", "Frayer"),
        ]
       
        for text, template_key in non_tech_templates:
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                command=lambda k=template_key: self.open_template(k),
                fg_color=self.colors['sidebar_button'],
                hover_color=self.colors['sidebar_hover'],
                text_color=self.colors['sidebar_text'],
                corner_radius=20,
                border_width=0,
                width=self.sidebar_button_width,
                height=35,
                font=("Helvetica", 13, "bold"),
                anchor="w"
            )
            btn.pack(pady=3, padx=20)
       
        # Technical Templates Section
        ctk.CTkLabel(self.sidebar_frame, text="TECHNICAL TEMPLATES",
            font=('Helvetica', 11, 'bold'),
            text_color=self.colors['sidebar_text'], anchor="w").pack(pady=(20,5), padx=20, anchor='w')

        tech_templates = [
            ("Polya's 4 Steps", "Polya"),
            ("5W1H Analysis", "5W1H"),
            ("Concept Map", "ConceptMap"),
        ]
        for text, template_key in tech_templates:
            btn = ctk.CTkButton(
                    self.sidebar_frame,
                    text=text,
                    command=lambda k=template_key: self.open_template(k),
                    fg_color=self.colors['sidebar_button'],
                    hover_color=self.colors['sidebar_hover'],
                    text_color=self.colors['sidebar_text'],
                    corner_radius=20,
                    border_width=0,
                    width=self.sidebar_button_width,
                    height=35,
                    font=("Helvetica", 13, "bold"),
                    anchor="w"
            )
            btn.pack(pady=3, padx=20)

        # Quick Actions section (placed after template lists)
        ctk.CTkLabel(self.sidebar_frame, text="QUICK ACTIONS",
            font=('Helvetica', 11, 'bold'),
            text_color=self.colors['sidebar_text'], anchor="w").pack(pady=(20,5), padx=20, anchor='w')

        # Theme selector button
        ctk.CTkButton(self.sidebar_frame, text="🎨 Themes",
            command=self.show_theme_selector,
            fg_color=self.colors['primary'], 
            text_color=self.colors['sidebar_text'],
            hover_color=self.colors['sidebar_hover'],
            corner_radius=20,
            width=self.sidebar_button_width,
            height=35,
            font=('Helvetica', 13, 'bold'),
            anchor="w").pack(padx=20, pady=3)

        ctk.CTkButton(self.sidebar_frame, text="+ Add Course",
            command=self.add_course,
            fg_color=self.colors['success'], 
            text_color=self.colors['sidebar_text'],
            hover_color='#219150',
            corner_radius=20,
            width=self.sidebar_button_width,
            height=35,
            font=('Helvetica', 13, 'bold'),
            anchor="w").pack(padx=20, pady=3)

        ctk.CTkButton(self.sidebar_frame, text="+ Add To-Do",
            command=self.quick_add_task,
            fg_color=self.colors['info'], 
            text_color=self.colors['sidebar_text'],
            hover_color='#2980b9',
            corner_radius=20,
            width=self.sidebar_button_width,
            height=35,
            font=('Helvetica', 13, 'bold'),
            anchor="w").pack(padx=20, pady=3)
   
    def _update_stats(self):
        """
        Update the quick stats display in the header.
        Shows the number of courses, active tasks, and completed tasks.
        """
        self.stat_courses.configure(text=f"Courses: {len(self.courses)}")
        self.stat_active_tasks.configure(text=f"Active Tasks: {len(self.tasks)}")
        self.stat_completed.configure(text=f"Completed Tasks: {len(self.completed_tasks)}")
        # Update theme display (if present)
        if hasattr(self, 'stat_theme'):
            try:
                self.stat_theme.configure(text=f"Theme: {self.theme_name}")
            except Exception:
                pass
   
    # ------------------------------------------------------------------------
    # PART 4: COURSE MANAGEMENT
    # ------------------------------------------------------------------------
   
    def add_course(self):
        """
        Add a new course to your list.
        Prompts the user for a course name and saves it if valid.
        """
        name = simpledialog.askstring("Add Course", "Enter course name:")
       
        if name and name.strip():
            name = name.strip()
            if name in self.courses:
                messagebox.showwarning("Exists", f"'{name}' already exists!")
                return
           
            # Create new course
            self.courses[name] = {"notes": [], "tasks": []}
            self._save_data()
            self._update_stats()
            messagebox.showinfo("Success", f"Course '{name}' added!")
            self.show_dashboard()  # Refresh view
        elif name is not None:  # User clicked OK but empty
            messagebox.showwarning("Error", "Course name cannot be empty!")
   
    def delete_course(self, name):
        """
        Delete a course and all its notes and tasks.
        Asks for confirmation before deleting.
        """
        if messagebox.askyesno("Delete", f"Delete '{name}' and all its notes?"):
            del self.courses[name]
            self._save_data()
            messagebox.showinfo("Deleted", f"'{name}' deleted")
            self.show_dashboard()
   
    def view_course(self, course_name):
        """
        View details for a specific course.
        Shows all notes and tasks for the selected course, with scrolling if needed.
        """
        self._clear_content()
       
        course = self.courses[course_name]
       
        # Header
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill='x', padx=30, pady=20)
       
        ctk.CTkLabel(header_frame, text=f"📚 {course_name}",
            font=('Helvetica', 26, 'bold'),
            text_color=self.colors['main_text']).pack(side='left')
       
        ctk.CTkButton(header_frame, text="← Back to Dashboard",
             command=self.show_dashboard,
             fg_color=self.colors['muted'], text_color=self.colors['header_text'],
             hover_color=self.colors['secondary_text'],
             corner_radius=8, height=30,
             font=('Helvetica', 12)).pack(side='right')
       
        # Stats
        stats_frame = ctk.CTkFrame(self.main_content, fg_color=self.colors['card_bg'], corner_radius=10, border_width=1, border_color=self.colors['muted'])
        stats_frame.pack(fill='x', padx=30, pady=(0, 20))
       
        ctk.CTkLabel(stats_frame, text=f"📝 Total Notes: {len(course['notes'])}",
            font=('Helvetica', 14), text_color=self.colors['main_text']).pack(side='left', padx=20, pady=10)
        ctk.CTkLabel(stats_frame, text=f"📋 Total Tasks: {len(course['tasks'])}",
            font=('Helvetica', 14), text_color=self.colors['main_text']).pack(side='left', padx=20, pady=10)
       
        # Notes section title
        ctk.CTkLabel(self.main_content, text="Notes",
            font=('Helvetica', 20, 'bold'),
            text_color=self.colors['main_text']).pack(anchor='w', padx=30, pady=(10, 10))
       
        if not course['notes']:
            empty_card = ctk.CTkFrame(self.main_content, fg_color=self.colors['card_bg'], corner_radius=10)
            empty_card.pack(fill='x', padx=30, pady=10)
            ctk.CTkLabel(empty_card, text="📝 No notes yet for this course",
                    font=('Helvetica', 14), text_color=self.colors['muted']).pack(pady=(20,5))
            ctk.CTkLabel(empty_card, text="Use 'Freeform Notes' or templates to add notes!",
                    font=('Helvetica', 12), text_color=self.colors['muted']).pack(pady=(0,20))
        else:
            # Create scrollable area for notes using CTkScrollableFrame
            # This replaces the complex Canvas+Scrollbar setup
            notes_container = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent")
            notes_container.pack(fill='both', expand=True, padx=30, pady=(0, 20))
           
            # Display all notes in scrollable area
            for i, note in enumerate(course['notes']):
                self._display_note_card_in_frame(notes_container, course_name, i, note)
   
    def _display_note_card_in_frame(self, parent_frame, course_name, note_index, note):
        """
        Display a single note card in a given frame.
        Used to show each note in the course details view.
        """
        card = ctk.CTkFrame(parent_frame, fg_color=self.colors['card_bg'], corner_radius=10, border_width=1, border_color=self.colors['muted'])
        card.pack(fill='x', pady=8, padx=5)
       
        # Note header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill='x', pady=(10, 10), padx=15)
       
        ctk.CTkLabel(header, text=note.get('title', 'Untitled Note'),
            font=('Helvetica', 16, 'bold'),
            text_color=self.colors['main_text']).pack(side='left')
       
        ctk.CTkLabel(header, text=note.get('created', ''),
            font=('Helvetica', 11), text_color=self.colors['muted']).pack(side='left', padx=15)
       
        # Delete button
        ctk.CTkButton(header, text="🗑️ Delete",
             command=lambda: self.delete_note(course_name, note_index),
             fg_color=self.colors['danger'], hover_color='#c0392b',
             text_color='white',
             width=80, height=28,
             font=('Helvetica', 11)).pack(side='right')
       
        # Note content
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill='x', padx=15, pady=(0, 15))

        if 'template' in note:
            # Template note - show structured data
                ctk.CTkLabel(content_frame, text=f"Template: {note['template']}",
                    font=('Helvetica', 11, 'italic'),
                    text_color=self.colors['info']).pack(anchor='w', pady=5)
           
        for field, value in note.get('data', {}).items():
            if value:  # Only show fields with content
                field_row = ctk.CTkFrame(content_frame, fg_color="transparent")
                field_row.pack(fill='x', pady=2)
                
                ctk.CTkLabel(field_row, text=f"{field}:",
                    font=('Helvetica', 11, 'bold'),
                    text_color=self.colors['main_text']).pack(anchor='w')
            
                ctk.CTkLabel(field_row, text=value,
                    font=('Helvetica', 11),
                    text_color=self.colors['main_text'], wraplength=650,
                    justify='left').pack(anchor='w', padx=10)
        else:
            # Freeform note - show content
            content = note.get('content', '')
            preview = content[:200] + "..." if len(content) > 200 else content
           
            ctk.CTkLabel(content_frame, text=preview,
                font=('Helvetica', 11),
                text_color=self.colors['main_text'], wraplength=650,
                justify='left').pack(anchor='w', pady=5)
           
            if len(content) > 200:
                ctk.CTkButton(content_frame, text="Read full note →",
                         command=lambda: self.view_full_note(note),
                         fg_color="transparent", hover_color=self.colors['card_bg'],
                         text_color=self.colors['info'], 
                         anchor="w",
                         font=('Helvetica', 11, 'bold')).pack(anchor='w', pady=5)
   
    def delete_note(self, course_name, note_index):
        """
        Delete a specific note from a course.
        Asks for confirmation before deleting.
        """
        note_title = self.courses[course_name]['notes'][note_index].get('title', 'this note')
       
        if messagebox.askyesno("Delete Note", f"Delete '{note_title}'?"):
            self.courses[course_name]['notes'].pop(note_index)
            self._save_data()
            self.view_course(course_name)  # Refresh the view
   
    def view_full_note(self, note):
        """
        Show the full content of a note in a popup window.
        Useful for reading long notes.
        """
        popup = ctk.CTkToplevel(self.root)
        popup.title(note.get('title', 'Note'))
        popup.geometry("700x500")
       
        # Title
        ctk.CTkLabel(popup, text=note.get('title', 'Untitled'),
                font=('Helvetica', 20, 'bold'),
                text_color=self.colors['main_text']).pack(pady=20, padx=20)
       
        # Content in scrollable text widget
        text_widget = ctk.CTkTextbox(popup, wrap='word', font=('Helvetica', 12),
                                     fg_color=self.colors['background'],
                                     text_color=self.colors['main_text'])
        text_widget.pack(fill='both', expand=True, padx=20, pady=(0, 20))
       
        # Insert content
        text_widget.insert('1.0', note.get('content', ''))
        text_widget.configure(state='disabled')  # Read-only
       
        # Close button
        ctk.CTkButton(popup, text="Close",
             command=popup.destroy,
             fg_color=self.colors['muted'], text_color=self.colors['header_text'],
             font=('Helvetica', 12),
             corner_radius=8, width=100).pack(pady=10)
   
    def show_task_history(self):
        """
        Show the history of completed tasks.
        Lets you restore or permanently delete completed tasks.
        """
        self._clear_content()
       
        # Title
        ctk.CTkLabel(self.main_content, text="✅ Task History",
            font=('Helvetica', 26, 'bold'),
            text_color=self.colors['main_text']).pack(pady=(20,5), anchor='w', padx=30)
       
        ctk.CTkLabel(self.main_content, text="View and manage your completed tasks",
            font=('Helvetica', 12), text_color=self.colors['secondary_text']).pack(anchor='w', padx=30, pady=(0, 20))
       
        # Stats
        stats_frame = ctk.CTkFrame(self.main_content, fg_color=self.colors['card_bg'], corner_radius=10, border_width=1, border_color=self.colors['muted'])
        stats_frame.pack(fill='x', padx=30, pady=(0, 20))
       
        ctk.CTkLabel(stats_frame, text=f"📋 Active Tasks: {len(self.tasks)}",
            font=('Helvetica', 14), text_color=self.colors['main_text']).pack(side='left', padx=20, pady=10)
        ctk.CTkLabel(stats_frame, text=f"✓ Completed Tasks: {len(self.completed_tasks)}",
            font=('Helvetica', 14), text_color=self.colors['main_text']).pack(side='left', padx=20, pady=10)
       
        # Completed tasks list
        if not self.completed_tasks:
            empty_card = ctk.CTkFrame(self.main_content, fg_color=self.colors['card_bg'], corner_radius=10)
            empty_card.pack(fill='x', padx=30, pady=10)
            ctk.CTkLabel(empty_card, text="✅ No completed tasks yet",
                font=('Helvetica', 14), text_color=self.colors['muted']).pack(pady=(20,5))
            ctk.CTkLabel(empty_card, text="Complete tasks from the Dashboard to see them here!",
                font=('Helvetica', 12), text_color=self.colors['muted']).pack(pady=(0,20))
        else:
            # Create scrollable area for completed tasks
            tasks_container = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent")
            tasks_container.pack(fill='both', expand=True, padx=30, pady=(0, 20))
           
            # Display completed tasks
            for i, task_data in enumerate(self.completed_tasks):
                card = ctk.CTkFrame(tasks_container, fg_color=self.colors['card_bg'], corner_radius=10, border_width=1, border_color=self.colors['muted'])
                card.pack(fill='x', pady=8, padx=5)
               
                # Task info
                info_frame = ctk.CTkFrame(card, fg_color="transparent")
                info_frame.pack(fill='x', padx=15, pady=10)
               
                ctk.CTkLabel(info_frame, text="✓",
                    font=('Helvetica', 18, 'bold'),
                    text_color=self.colors['success']).pack(side='left', padx=(0, 15))
               
                task_text_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
                task_text_frame.pack(side='left', fill='x', expand=True)
               
                ctk.CTkLabel(task_text_frame, text=task_data['task'],
                    font=('Helvetica', 14),
                    text_color=self.colors['main_text']).pack(anchor='w')
               
                ctk.CTkLabel(task_text_frame, text=f"Completed: {task_data['completed_date']}",
                    font=('Helvetica', 11), text_color=self.colors['muted']).pack(anchor='w')
               
                # Action buttons
                btn_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
                btn_frame.pack(side='right')
               
                ctk.CTkButton(btn_frame, text="↶ Restore",
                         command=lambda idx=i: self._restore_task_and_refresh(idx),
                         fg_color=self.colors['info'], hover_color='#2980b9',
                         text_color='white',
                         width=80, height=30,
                         font=('Helvetica', 11)).pack(side='left', padx=5)
               
                ctk.CTkButton(btn_frame, text="🗑️ Delete",
                         command=lambda idx=i: self._delete_completed_task(idx),
                         fg_color=self.colors['danger'], hover_color='#c0392b',
                         text_color='white',
                         width=80, height=30,
                         font=('Helvetica', 11)).pack(side='left', padx=5)
       
        # Back button
        ctk.CTkButton(self.main_content, text="← Back to Dashboard",
             command=self.show_dashboard,
             fg_color=self.colors['muted'], text_color=self.colors['header_text'],
             hover_color=self.colors['secondary_text'],
             corner_radius=8, height=30,
             font=('Helvetica', 12)).pack(pady=20)
   
    def _restore_task_and_refresh(self, index):
        """
        Restore a completed task from history and refresh the view.
        """
        self.restore_task(index)
        self.show_task_history()
   
    def _delete_completed_task(self, index):
        """
        Permanently delete a completed task from history.
        """
        if messagebox.askyesno("Delete", "Permanently delete this completed task?"):
            self.permanently_delete_task(index)
            self.show_task_history()
   
    # ------------------------------------------------------------------------
    # PART 5: TASK MANAGEMENT
    # ------------------------------------------------------------------------
   
    def quick_add_task(self):
        """
        Quickly add a new task from the sidebar using a dialog box.
        """
        task = simpledialog.askstring("Add To-Do", "Enter task:")
       
        if task and task.strip():
            self.tasks.append(task.strip())
            self._save_data()
            self._update_stats()
            messagebox.showinfo("Success", "To-Do added!")
            self.show_dashboard()
        elif task is not None:
            messagebox.showwarning("Error", "Task cannot be empty!")
   
    def delete_task(self, index):
        """
        Mark a task as complete and move it to the history.
        """
        task = self.tasks.pop(index)
        self.completed_tasks.append({
            "task": task,
            "completed_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        self._save_data()
        self._update_stats()
        self.show_dashboard()
   
    def restore_task(self, index):
        """
        Restore a completed task back to the active tasks list.
        """
        task_data = self.completed_tasks.pop(index)
        self.tasks.append(task_data["task"])
        self._save_data()
        self._update_stats()
   
    def permanently_delete_task(self, index):
        """
        Permanently delete a completed task from the history.
        """
        self.completed_tasks.pop(index)
        self._save_data()
        self._update_stats()
   
    # ------------------------------------------------------------------------
    # PART 6: VIEWS (Different screens)
    # ------------------------------------------------------------------------
   
    def _clear_content(self):
        """
        Clear the main content area before showing a new view.
        Removes all widgets from the main content frame.
        """
        for widget in self.main_content.winfo_children():
            widget.destroy()
   
    def show_dashboard(self):
        """
        DASHBOARD VIEW
        Shows: Course list + Task list side by side
        """
        self._clear_content()
       
        # Title
        ctk.CTkLabel(self.main_content, text="Dashboard",
            font=('Helvetica', 26, 'bold'),
            text_color=self.colors['main_text']).pack(pady=(20,5), anchor='w', padx=30)
       
        # Container for two columns
        # Container for two columns (dashboard)
        dashboard_container = ctk.CTkFrame(
            self.main_content,
            fg_color=self.colors['background'],
            corner_radius=15,
            border_width=0
        )
        dashboard_container.pack(fill="both", expand=True, padx=30, pady=10)

        # LEFT: Courses list (course management frame)
        courses_frame = ctk.CTkFrame(
            dashboard_container,
            fg_color=self.colors.get('card_bg'),
            corner_radius=15,
            border_width=2.5,
            border_color=self.colors.get('muted')
        )
        courses_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

        ctk.CTkLabel(courses_frame, text="My Courses",
            font=("Helvetica", 24, "bold"),
            text_color=self.colors['main_text']).pack(anchor="w", pady=(10, 10), padx=(10))

        if not self.courses:
            ctk.CTkLabel(courses_frame, text="No courses yet.\nClick '+ Add Course' to start!",
                font=("Helvetica", 12),
                text_color="#95a5a6",
                justify="left").pack(pady=20)
        else:
            for name, data in self.courses.items():
                course_row = ctk.CTkFrame(courses_frame, fg_color=self.colors['background'], corner_radius=10, border_width=0, width=350)
                course_row.pack(fill="x", pady=5, padx=15)
                # Make course name clickable
                course_btn = ctk.CTkButton(course_row, text=f"📚 {name}",
                                font=("Helvetica", 16, "bold"),
                                fg_color=self.colors['sidebar_button'], bg_color=self.colors['background'],
                                hover_color=self.colors['sidebar_hover'], text_color=self.colors['sidebar_text'],
                                corner_radius=15, border_width=0,
                                width=220, height=40,
                                command=lambda n=name: self.view_course(n),
                                anchor="w")
                course_btn.pack(side="left", padx=(0, 10))
                ctk.CTkLabel(course_row, text=f"({len(data['notes'])} notes)",
                    font=("Helvetica", 13), text_color="#7f8c8d", anchor="w").pack(side="left", padx=10)
                ctk.CTkButton(course_row, text="🗑️ Delete Course",
                    command=lambda n=name: self.delete_course(n),
                    fg_color=self.colors.get('danger', '#e74c3c'), text_color="white",
                    bg_color=self.colors.get('card_bg'),
                    font=("Helvetica", 14, "bold"), width=60, height=40).pack(side="right", padx=(10,0))
       
        # RIGHT: Tasks list (Active + Completed) - use CTk to match My Courses styling
        tasks_frame = ctk.CTkFrame(
            dashboard_container,
            fg_color=self.colors.get('card_bg'),
            corner_radius=15,
            border_width=2.5,
            border_color=self.colors.get('muted')
        )
        tasks_frame.pack(side='right', fill='both', expand=True, padx=(10, 0), pady=10)

        # To-Do List
        ctk.CTkLabel(tasks_frame, text="To-Do List",
                 font=("Helvetica", 24, "bold"),
                 text_color=self.colors['main_text']).pack(anchor='w', pady=(10, 10), padx=(10))

        # Input row: Entry + Add button
        input_row = ctk.CTkFrame(tasks_frame, fg_color=self.colors.get('card_bg'), corner_radius=0, border_width=0)
        input_row.pack(fill='x', pady=(0, 10), padx=(6,6))

        task_entry = ctk.CTkEntry(input_row, font=('Helvetica', 10))
        task_entry.pack(side='left', fill='x', expand=True, padx=(0, 8))

        def add_task_with_validation():
            """Add task with error handling"""
            task = task_entry.get().strip()
            if not task:
                messagebox.showwarning("Error", "Task cannot be empty!")
                return
            if task.isdigit():
                messagebox.showwarning("Error", "Numbers only are not allowed!")
                return
            self.tasks.append(task)
            self._save_data()
            task_entry.delete(0, tk.END)
            self.show_dashboard()

        ctk.CTkButton(input_row, text="+ Add",
                      command=add_task_with_validation,
                      fg_color=self.colors['primary_dark'],
                      text_color=self.colors['sidebar_text'],
                      corner_radius=8).pack(side='right')

        # Task list card (separate container with minimum height)
        tasks_list_card = ctk.CTkFrame(tasks_frame,
                                       fg_color=self.colors.get('card_bg'),
                                       corner_radius=10,
                                       border_width=0)
        tasks_list_card.pack(fill='both', expand=True, pady=(0, 0), padx=6)

        # Active tasks list
        if not self.tasks:
            ctk.CTkLabel(tasks_list_card, text="No active tasks",
                         font=('Helvetica', 10), text_color=self.colors['muted']).pack(pady=20)
        else:
            for i, task in enumerate(self.tasks):
                task_row = ctk.CTkFrame(tasks_list_card, fg_color=self.colors.get('card_bg'), corner_radius=6, border_width=0)
                task_row.pack(fill='x', pady=6, padx=6)

                ctk.CTkLabel(task_row, text=f"☐ {task}",
                             font=('Helvetica', 11), text_color=self.colors['main_text']).pack(side='left', fill='x', expand=True, padx=(8,0))

                ctk.CTkButton(task_row, text="✓",
                              width=36, height=28,
                              command=lambda idx=i: self.delete_task(idx),
                              fg_color=self.colors['success'],
                              text_color='white',
                              corner_radius=8).pack(side='right', padx=(6,6))
   
    def show_freeform(self):
        """
        FREEFORM NOTES VIEW
        Simple text editor to write notes
        """
        self._clear_content()
       
        # Title
        ctk.CTkLabel(self.main_content, text="📝 Freeforms Notes",
                font=('Helvetica', 26, 'bold'),
                text_color=self.colors['main_text']).pack(pady=(20,5), anchor='w', padx=30)
       
        # Card container
        card = ctk.CTkFrame(self.main_content, fg_color=self.colors['card_bg'], corner_radius=10, border_width=1, border_color=self.colors['muted'])
        card.pack(fill='both', expand=True, padx=30, pady=(0, 20))
       
        # Top: Course selector + Title
        top_frame = ctk.CTkFrame(card, fg_color="transparent")
        top_frame.pack(fill='x', pady=(20, 10), padx=20)
       
        ctk.CTkLabel(top_frame, text="Course:", text_color=self.colors['main_text']).pack(side='left', padx=5)
       
        course_var = ctk.StringVar(value="Select Course")
        course_options = ["Select Course"] + list(self.courses.keys())
        
        course_menu = ctk.CTkOptionMenu(top_frame, variable=course_var, values=course_options,
                                        fg_color=self.colors['sidebar_button'],
                                        button_color=self.colors['sidebar_hover'],
                                        text_color=self.colors['sidebar_text'])
        course_menu.pack(side='left', padx=5)
       
        ctk.CTkLabel(top_frame, text="Title:", text_color=self.colors['main_text']).pack(side='left', padx=(20, 5))
        title_entry = ctk.CTkEntry(top_frame, width=300, font=('Helvetica', 12))
        title_entry.pack(side='left', padx=5)
       
        # Text editor
        text_widget = ctk.CTkTextbox(card, wrap='word', font=('Helvetica', 12),
                                     fg_color=self.colors['background'],
                                     text_color=self.colors['main_text'])
        text_widget.pack(fill='both', expand=True, pady=10, padx=20)
       
        # Save button
        def save_note():
            course = course_var.get()
            title = title_entry.get().strip()
            content = text_widget.get("1.0", tk.END).strip()
           
            if course == "Select Course":
                messagebox.showwarning("Error", "Please select a course!")
                return
           
            if not content:
                messagebox.showwarning("Error", "Note is empty!")
                return
           
            if not title:
                title = f"Note - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
           
            # Save note
            note = {
                "title": title,
                "content": content,
                "created": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.courses[course]["notes"].append(note)
            self._save_data()
           
            messagebox.showinfo("Saved", f"Note saved to {course}!")
            text_widget.delete("1.0", tk.END)
            title_entry.delete(0, tk.END)
       
        ctk.CTkButton(card, text="💾 Save Note",
                 command=save_note,
                 fg_color=self.colors['success'], hover_color='#219150',
                 text_color='white',
                 font=('Helvetica', 12, 'bold'),
                 corner_radius=8, height=40).pack(pady=20)

    def show_theme_selector(self):
        """
        Open a small dialog that lists available themes.
        Selecting a theme applies it immediately.
        """
        dlg = ctk.CTkToplevel(self.root)
        dlg.title("Select Theme")
        dlg.geometry("320x400")
        dlg.transient(self.root)
        dlg.grab_set()

        ctk.CTkLabel(dlg, text="Choose a theme:", font=('Helvetica', 14, 'bold'), text_color=self.colors['main_text']).pack(pady=(20, 10))

        scroll_frame = ctk.CTkScrollableFrame(dlg, fg_color="transparent")
        scroll_frame.pack(fill='both', expand=True, padx=10, pady=10)

        for name, pal in CourseMateApp.THEMES.items():
            # sample button shows the primary_dark color
            btn = ctk.CTkButton(scroll_frame, text=name,
                            command=lambda n=name, d=dlg: self.apply_theme(n, d),
                            fg_color=pal.get('primary_dark', '#333'), 
                            text_color='white',
                            hover_color=pal.get('primary', '#555'),
                            height=40,
                            corner_radius=20,
                            font=('Helvetica', 12, 'bold'))
            btn.pack(fill='x', padx=10, pady=5)

    def apply_theme(self, name, dialog=None):
        """Apply theme by name and rebuild UI styles/widgets."""
        if name not in CourseMateApp.THEMES:
            return
        self.theme_name = name
        self.colors = CourseMateApp.THEMES[name].copy()
        # update class-level COLORS so other instances (if any) follow
        CourseMateApp.COLORS = self.colors
        # reapply styles and rebuild widgets to pick up new colors
        self._setup_styles()
        self._rebuild_ui()
        if dialog:
            try:
                dialog.destroy()
            except Exception:
                pass

    def _rebuild_ui(self):
        """Clear header and sidebar content and re-create widgets."""
        # Clear sidebar and header frames so widgets recreated cleanly
        for w in list(self.header_frame.winfo_children()):
            w.destroy()
        for w in list(self.sidebar_frame.winfo_children()):
            w.destroy()
        # Recreate widgets and refresh current view
        self._create_widgets()
        # Refresh the main content to reflect current view
        self.show_dashboard()
   
    
    # ------------------------------------------------------------------------
    # PART 7: TEMPLATE SYSTEM
    # ------------------------------------------------------------------------
   
    def open_template(self, template_key):
        """
        Open a template form
        Shows fields to fill out based on template type
        """
        self._clear_content()
       
        # Template definitions
        TEMPLATES = {
            "Cornell": ["Keywords/Cues (Left Column)", "Notes (Right Column)",
                       "Summary (Bottom)"],
            "Frayer": ["Concept/Term", "Definition", "Characteristics",
                      "Examples", "Non-Examples"],
            "MainIdea": ["Main Topic", "Core Idea/Thesis",
                        "Supporting Detail 1", "Supporting Detail 2", "Supporting Detail 3"],
            "Polya": ["Step 1: Understand the Problem", "Step 2: Devise a Plan",
                     "Step 3: Carry out the Plan", "Step 4: Look Back/Review"],
            "5W1H": ["What is the problem?", "Why is it important?",
                    "When did it happen?", "Where is it applied?",
                    "Who is involved?", "How does it work?"],
            "ConceptMap": ["Central Concept", "Related Concept 1",
                          "Related Concept 2", "Connection/Relationship"]
           
        }
       
        # Template display names
        TEMPLATE_NAMES = {
            "Cornell": "Cornell Notes",
            "MainIdea": "Main Idea & Details",
            "Frayer": "Modified Frayer Model",
            "Polya": "Polya's 4 Steps",
            "5W1H": "5W1H Analysis",
            "ConceptMap": "Concept Map"
        }
       
        fields = TEMPLATES.get(template_key, [])
        template_display_name = TEMPLATE_NAMES.get(template_key, template_key)
       
        # Title
        ctk.CTkLabel(self.main_content, text=f"{template_display_name}",
                font=('Helvetica', 26, 'bold'),
                text_color=self.colors['main_text']).pack(pady=(20,5), anchor='w', padx=30)
       
        # Course selector
        top_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        top_frame.pack(fill='x', padx=30, pady=(0, 10))
       
        ctk.CTkLabel(top_frame, text="Course:", text_color=self.colors['main_text']).pack(side='left', padx=5)
       
        course_var = ctk.StringVar(value="Select Course")
        course_options = ["Select Course"] + list(self.courses.keys())
        course_menu = ctk.CTkOptionMenu(top_frame, variable=course_var, values=course_options,
                                        fg_color=self.colors['sidebar_button'],
                                        button_color=self.colors['sidebar_hover'],
                                        text_color=self.colors['sidebar_text'])
        course_menu.pack(side='left', padx=5)
       
        # Scrollable form area
        form_frame = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent")
        form_frame.pack(fill='both', expand=True, padx=30, pady=(0, 10))
       
        # Create form fields
        field_widgets = {}

        # --- NON-TECHNICAL TEMPLATES ---

        if template_key == "Cornell":
        # --- Tagline ---
            tagline_label = ctk.CTkLabel(
                form_frame,
                text="🧠 Think clearly, write wisely.",
                font=('Helvetica', 12, 'italic'),
                text_color=self.colors['muted']
            )
            tagline_label.pack(anchor='center', pady=(0, 10))
   
        if template_key == "Cornell":
            # --- Title / Topic and Date (Top Section) ---
            top_section = ctk.CTkFrame(form_frame, fg_color=self.colors['card_bg'], corner_radius=10, border_width=1, border_color=self.colors['muted'])
            top_section.pack(fill='x', pady=8, padx=20)

            title_row = ctk.CTkFrame(top_section, fg_color="transparent")
            title_row.pack(fill='x', padx=15, pady=15)
            
            ctk.CTkLabel(title_row, text="Title / Topic:", font=('Helvetica', 12, 'bold'), text_color=self.colors['main_text']).pack(side='left')
            title_entry = ctk.CTkEntry(title_row, font=('Helvetica', 12))
            title_entry.pack(side='left', fill='x', expand=True, padx=(8, 20))
            field_widgets["Title / Topic"] = title_entry

            ctk.CTkLabel(title_row, text="Date:", font=('Helvetica', 12, 'bold'), text_color=self.colors['main_text']).pack(side='left')
            date_entry = ctk.CTkEntry(title_row, font=('Helvetica', 12), width=120)
            date_entry.pack(side='left')
            field_widgets["Date"] = date_entry

            # --- Middle Section: Questions (left) & Notes (right) ---
            middle_section = ctk.CTkFrame(form_frame, fg_color="transparent")
            middle_section.pack(fill='both', expand=True, pady=10, padx=20)

            # Left card - Questions / Cues
            questions_card = ctk.CTkFrame(middle_section, fg_color=self.colors['card_bg'], corner_radius=10, border_width=1, border_color=self.colors['muted'])
            questions_card.pack(side='left', fill='both', expand=True, padx=(0, 5))
            ctk.CTkLabel(questions_card, text="Questions / Cues", font=('Helvetica', 12, 'bold'), text_color=self.colors['main_text']).pack(anchor='w', pady=(10, 8), padx=15)
            questions_text = ctk.CTkTextbox(questions_card, height=300, wrap='word', font=('Helvetica', 12), fg_color=self.colors['background'], text_color=self.colors['main_text'])
            questions_text.pack(fill='both', expand=True, padx=15, pady=(0,15))
            field_widgets["Questions / Cues"] = questions_text

            # Right card - Notes
            notes_card = ctk.CTkFrame(middle_section, fg_color=self.colors['card_bg'], corner_radius=10, border_width=1, border_color=self.colors['muted'])
            notes_card.pack(side='left', fill='both', expand=True, padx=(5, 0))
            ctk.CTkLabel(notes_card, text="Notes", font=('Helvetica', 12, 'bold'), text_color=self.colors['main_text']).pack(anchor='w', pady=(10, 8), padx=15)
            notes_text = ctk.CTkTextbox(notes_card, height=300, wrap='word', font=('Helvetica', 12), fg_color=self.colors['background'], text_color=self.colors['main_text'])
            notes_text.pack(fill='both', expand=True, padx=15, pady=(0,15))
            field_widgets["Notes"] = notes_text

            # --- Bottom Section: Summary ---
            summary_section = ctk.CTkFrame(form_frame, fg_color=self.colors['card_bg'], corner_radius=10, border_width=1, border_color=self.colors['muted'])
            summary_section.pack(fill='x', pady=12, padx=20)
            ctk.CTkLabel(summary_section, text="Summary", font=('Helvetica', 12, 'bold'), text_color=self.colors['main_text']).pack(anchor='w', pady=(10, 6), padx=15)
            summary_text = ctk.CTkTextbox(summary_section, height=100, wrap='word', font=('Helvetica', 12), fg_color=self.colors['background'], text_color=self.colors['main_text'])
            summary_text.pack(fill='x', padx=15, pady=(0,15))
            field_widgets["Summary"] = summary_text

        # --- FRAYER MODEL TEMPLATE ---
        elif template_key == "Frayer":
           # --- Tagline ---
            tagline_label = ctk.CTkLabel(
                form_frame,
                text="📘 Defining concepts, expanding understanding.",
                font=('Helvetica', 12, 'italic'),
                text_color=self.colors['muted']
            )
            tagline_label.pack(anchor='center', pady=(0, 10))

             # --- Concept / Term Section ---
            concept_section = ctk.CTkFrame(form_frame, fg_color=self.colors['card_bg'], corner_radius=10, border_width=1, border_color=self.colors['muted'])
            concept_section.pack(fill='x', pady=8, padx=20)
            ctk.CTkLabel(concept_section, text="Concept / Term", font=('Helvetica', 12, 'bold'), text_color=self.colors['main_text']).pack(anchor='w', padx=15, pady=(10,0))
            concept_entry = ctk.CTkEntry(concept_section, font=('Helvetica', 12))
            concept_entry.pack(fill='x', expand=True, pady=(5, 15), padx=15)
            field_widgets["Concept / Term"] = concept_entry

            # --- 2x2 Grid for Definition / Characteristics / Examples / Importance ---
            grid_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            grid_frame.pack(fill='both', expand=True, pady=10, padx=20)

            # Top row
            top_row = ctk.CTkFrame(grid_frame, fg_color="transparent")
            top_row.pack(fill='both', expand=True)
           
            definition_card = ctk.CTkFrame(top_row, fg_color=self.colors['card_bg'], corner_radius=10, border_width=1, border_color=self.colors['muted'])
            definition_card.pack(side='left', fill='both', expand=True, padx=(0, 5))
            ctk.CTkLabel(definition_card, text="Definition", font=('Helvetica', 12, 'bold'), text_color=self.colors['main_text']).pack(anchor='w', pady=(10, 8), padx=15)
            definition_text = ctk.CTkTextbox(definition_card, height=150, wrap='word', font=('Helvetica', 12), fg_color=self.colors['background'], text_color=self.colors['main_text'])
            definition_text.pack(fill='both', expand=True, padx=15, pady=(0,15))
            field_widgets["Definition"] = definition_text

            characteristics_card = ctk.CTkFrame(top_row, fg_color=self.colors['card_bg'], corner_radius=10, border_width=1, border_color=self.colors['muted'])
            characteristics_card.pack(side='left', fill='both', expand=True, padx=(5, 0))
            ctk.CTkLabel(characteristics_card, text="Characteristics", font=('Helvetica', 12, 'bold'), text_color=self.colors['main_text']).pack(anchor='w', pady=(10, 8), padx=15)
            characteristics_text = ctk.CTkTextbox(characteristics_card, height=150, wrap='word', font=('Helvetica', 12), fg_color=self.colors['background'], text_color=self.colors['main_text'])
            characteristics_text.pack(fill='both', expand=True, padx=15, pady=(0,15))
            field_widgets["Characteristics"] = characteristics_text

            # Bottom row
            bottom_row = ctk.CTkFrame(grid_frame, fg_color="transparent")
            bottom_row.pack(fill='both', expand=True, pady=(10, 0))

            examples_card = ctk.CTkFrame(bottom_row, fg_color=self.colors['card_bg'], corner_radius=10, border_width=1, border_color=self.colors['muted'])
            examples_card.pack(side='left', fill='both', expand=True, padx=(0, 5))
            ctk.CTkLabel(examples_card, text="Examples", font=('Helvetica', 12, 'bold'), text_color=self.colors['main_text']).pack(anchor='w', pady=(10, 8), padx=15)
            examples_text = ctk.CTkTextbox(examples_card, height=150, wrap='word', font=('Helvetica', 12), fg_color=self.colors['background'], text_color=self.colors['main_text'])
            examples_text.pack(fill='both', expand=True, padx=15, pady=(0,15))
            field_widgets["Examples"] = examples_text

            importance_card = ctk.CTkFrame(bottom_row, fg_color=self.colors['card_bg'], corner_radius=10, border_width=1, border_color=self.colors['muted'])
            importance_card.pack(side='left', fill='both', expand=True, padx=(5, 0))
            ctk.CTkLabel(importance_card, text="Importance", font=('Helvetica', 12, 'bold'), text_color=self.colors['main_text']).pack(anchor='w', pady=(10, 8), padx=15)
            importance_text = ctk.CTkTextbox(importance_card, height=150, wrap='word', font=('Helvetica', 12), fg_color=self.colors['background'], text_color=self.colors['main_text'])
            importance_text.pack(fill='both', expand=True, padx=15, pady=(0,15))
            field_widgets["Importance"] = importance_text

        # --- TECHNICAL TEMPLATES ---

        elif template_key == "Polya":

            # --- Tagline ---
            tagline_label = ctk.CTkLabel(
                form_frame,
                text="⚙️ Problem-solving methodology",
                font=('Helvetica', 12, 'italic'),
                text_color=self.colors['muted']
            )
            tagline_label.pack(anchor='center', pady=(0, 10))

            # --- Main 2x2 Grid ---
            grid_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            grid_frame.pack(fill='both', expand=True, pady=10, padx=20)

            # --- TOP ROW (Step 1 & Step 2) ---
            top_row = ctk.CTkFrame(grid_frame, fg_color="transparent")
            top_row.pack(fill='both', expand=True)

            # Step 1
            step1_card = ctk.CTkFrame(top_row, fg_color=self.colors['card_bg'], corner_radius=10, border_width=1, border_color=self.colors['muted'])
            step1_card.pack(side='left', fill='both', expand=True, padx=(0, 5))

            ctk.CTkLabel(
                step1_card,
                text="1. Understanding the problem",
                font=('Helvetica', 12, 'bold'),
                text_color=self.colors['main_text']
            ).pack(anchor='w', pady=(10, 8), padx=15)

            step1_text = ctk.CTkTextbox(
                step1_card,
                height=150,
                wrap='word',
                font=('Helvetica', 12),
                fg_color=self.colors['background'],
                text_color=self.colors['main_text']
            )
            step1_text.pack(fill='both', expand=True, padx=15, pady=(0,15))
            field_widgets["Step 1"] = step1_text

            # Step 2
            step2_card = ctk.CTkFrame(top_row, fg_color=self.colors['card_bg'], corner_radius=10, border_width=1, border_color=self.colors['muted'])
            step2_card.pack(side='left', fill='both', expand=True, padx=(5, 0))

            ctk.CTkLabel(
                step2_card,
                text="2. Devise a plan",
                font=('Helvetica', 12, 'bold'),
                text_color=self.colors['main_text']
            ).pack(anchor='w', pady=(10, 8), padx=15)

            step2_text = ctk.CTkTextbox(
                step2_card,
                height=150,
                wrap='word',
                font=('Helvetica', 12),
                fg_color=self.colors['background'],
                text_color=self.colors['main_text']
            )
            step2_text.pack(fill='both', expand=True, padx=15, pady=(0,15))
            field_widgets["Step 2"] = step2_text

            # --- BOTTOM ROW (Step 3 & Step 4) ---
            bottom_row = ctk.CTkFrame(grid_frame, fg_color="transparent")
            bottom_row.pack(fill='both', expand=True, pady=(10, 0))

            # Step 3
            step3_card = ctk.CTkFrame(bottom_row, fg_color=self.colors['card_bg'], corner_radius=10, border_width=1, border_color=self.colors['muted'])
            step3_card.pack(side='left', fill='both', expand=True, padx=(0, 5))

            ctk.CTkLabel(
                step3_card,
                text="3. Carry out the plan",
                font=('Helvetica', 12, 'bold'),
                text_color=self.colors['main_text']
            ).pack(anchor='w', pady=(10, 8), padx=15)

            step3_text = ctk.CTkTextbox(
                step3_card,
                height=150,
                wrap='word',
                font=('Helvetica', 12),
                fg_color=self.colors['background'],
                text_color=self.colors['main_text']
            )
            step3_text.pack(fill='both', expand=True, padx=15, pady=(0,15))
            field_widgets["Step 3"] = step3_text

            # Step 4
            step4_card = ctk.CTkFrame(bottom_row, fg_color=self.colors['card_bg'], corner_radius=10, border_width=1, border_color=self.colors['muted'])
            step4_card.pack(side='left', fill='both', expand=True, padx=(5, 0))

            ctk.CTkLabel(
                step4_card,
                text="4. Look back",
                font=('Helvetica', 12, 'bold'),
                text_color=self.colors['main_text']
            ).pack(anchor='w', pady=(10, 8), padx=15)

            step4_text = ctk.CTkTextbox(
                step4_card,
                height=150,
                wrap='word',
                font=('Helvetica', 12),
                fg_color=self.colors['background'],
                text_color=self.colors['main_text']
            )
            step4_text.pack(fill='both', expand=True, padx=15, pady=(0,15))
            field_widgets["Step 4"] = step4_text

        # Fallback for other templates (MainIdea, 5W1H, ConceptMap) - Generic Form
        elif template_key not in ["Cornell", "Frayer", "Polya"]:
             # Generic list of fields
            for field in fields:
                field_card = ctk.CTkFrame(form_frame, fg_color=self.colors['card_bg'], corner_radius=10, border_width=1, border_color=self.colors['muted'])
                field_card.pack(fill='x', pady=5, padx=20)
                
                ctk.CTkLabel(field_card, text=field, font=('Helvetica', 12, 'bold'), text_color=self.colors['main_text']).pack(anchor='w', pady=(10, 5), padx=15)
                
                # Use Entry for short fields, Textbox for long ones
                if "Detail" in field or "Idea" in field or "Summary" in field or "Step" in field:
                     entry = ctk.CTkTextbox(field_card, height=80, wrap='word', font=('Helvetica', 12), fg_color=self.colors['background'], text_color=self.colors['main_text'])
                     entry.pack(fill='x', padx=15, pady=(0,15))
                else:
                     entry = ctk.CTkEntry(field_card, font=('Helvetica', 12))
                     entry.pack(fill='x', padx=15, pady=(0,15))
                
                field_widgets[field] = entry

    
        # Save button
        def save_template():
            course = course_var.get()
            if course == "Select Course":
                messagebox.showwarning("Error", "Please select a course!")
                return
           
            # Collect field data
            note_data = {}
            all_empty = True
            for label, widget in field_widgets.items():
            # Detetct if widget is Entry or Text
                if isinstance(widget, ctk.CTkEntry):
                    content = widget.get().strip()
                else:
                    content = widget.get("1.0", tk.END).strip()

                note_data[label] = content
                if content:
                    all_empty = False
           
            if all_empty:
                messagebox.showwarning("Error", "Template is empty!")
                return
           
            # Save note
            note = {
                "title": f"{template_key} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "template": template_key,
                "data": note_data,
                "created": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.courses[course]["notes"].append(note)
            self._save_data()
           
            messagebox.showinfo("Saved", f"{template_key} template saved to {course}!")
            self.show_dashboard()
       
        btn_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        btn_frame.place(relx=1.0, y=20, anchor='ne')
       
        ctk.CTkButton(btn_frame, text="💾 Save Template",
                 command=save_template,
                 fg_color=self.colors['success'], hover_color='#219150',
                 text_color='white',
                 font=('Helvetica', 12, 'bold'),
                 corner_radius=8, height=40).pack(side='right', padx=10)
       
        ctk.CTkButton(btn_frame, text="← Back to Dashboard",
                 command=self.show_dashboard,
                 fg_color=self.colors['muted'], text_color=self.colors['header_text'],
                 hover_color=self.colors['secondary_text'],
                 corner_radius=8, height=40,
                 font=('Helvetica', 12)).pack(side='right', padx=5)








# ============================================================================
# RUN THE APP
# ============================================================================




if __name__ == "__main__":
    # print("=" * 60)
    # print("COURSEMATE - SIMPLE & COMPLETE")
    # print("=" * 60)
    # print("\n✓ Dashboard with courses and tasks")
    # print("✓ Freeform notes editor")
    # print("✓ 3 Technical templates")
    # print("✓ 3 Study templates")
    # print("✓ Auto-save to JSON")
    # print("\nData saves to: coursemate_data.json")
    # print("=" * 60)
   
    root = ctk.CTk()
    app = CourseMateApp(root)
    root.mainloop()





