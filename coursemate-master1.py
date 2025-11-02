"""
================================================================================
COURSEMATE - SIMPLE & COMPLETE VERSION
================================================================================

WHAT YOU GET:
✓ Dashboard with courses overview and task list
✓ Freeform text editor for quick notes
✓ 3 Technical templates (Polya, 5W1H, Concept Map)
✓ 3 Non-technical templates (Cornell, Frayer, Main Idea)
✓ JSON data storage (auto-saves everything)
✓ Simple, beginner-friendly code
✓ Organized with classes (but easy to understand!)

FILE STRUCTURE (All in ONE file for simplicity):
- CourseMateApp class → Main app
- Simple methods → Each does ONE thing
- JSON storage → Saves/loads automatically

HOW TO RUN:
1. Save this file as: coursemate.py
2. Run: python coursemate.py
3. That's it! Your data saves automatically in coursemate_data.json

LET'S BUILD IT STEP BY STEP...
================================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
from datetime import datetime
from pathlib import Path


# ============================================================================
# MAIN APPLICATION CLASS
# ============================================================================

class CourseMateApp:
    """
    The main CourseMate application.
    
    SIMPLE STRUCTURE:
    1. __init__ → Set up everything when app starts
    2. Data methods → Load/save JSON
    3. UI methods → Create the interface
    4. Action methods → What happens when buttons clicked
    """
    
    # ------------------------------------------------------------------------
    # PART 1: INITIALIZATION (Runs when app starts)
    # ------------------------------------------------------------------------
    
    def __init__(self, root):
        """Set up the app when it starts"""
        self.root = root
        self.root.title("CourseMate - think smarter, learn deeper, and solve problems better. ")
        self.root.geometry("1100x700")
        
        # DATA: Store everything here
        self.courses = {}  # Format: {"Course Name": {"notes": [], "tasks": []}}
        self.tasks = []    # Active tasks list
        self.completed_tasks = []  # Completed tasks (new!)
        
        # LOAD DATA: Get saved data from file
        self.data_file = Path("coursemate_data.json")
        self._load_data()
        
        # CREATE UI: Build the interface
        self._setup_styles()
        self._create_layout()
        self._create_sidebar()
        
        # START: Show dashboard first
        self.show_dashboard()
        
        print("✅ CourseMate started! Data auto-saves.")
    
    # ------------------------------------------------------------------------
    # PART 2: DATA STORAGE (JSON - Easy to understand!)
    # ------------------------------------------------------------------------
    
    def _load_data(self):
        """
        Load data from JSON file.
        
        JSON is just a text file that stores data like:
        {
          "courses": {"Math": {"notes": [], "tasks": []}},
          "tasks": ["Do homework", "Study"]
        }
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
        Save data to JSON file.
        Called automatically after any change!
        """
        try:
            data = {
                "courses": self.courses,
                "tasks": self.tasks,
                "completed_tasks": self.completed_tasks
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)  # Write to file
            print("💾 Data saved automatically")
        except Exception as e:
            print(f"❌ Error saving: {e}")
            messagebox.showerror("Save Error", f"Could not save data: {e}")
    
    # ------------------------------------------------------------------------
    # PART 3: UI SETUP (Create the interface)
    # ------------------------------------------------------------------------
    
    def _setup_styles(self):
        """Set up colors and styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colors
        style.configure('TFrame', background='#f5f5f5')
        style.configure('Sidebar.TFrame', background='#2c3e50')
        style.configure('Card.TFrame', background='white', relief='solid', borderwidth=1)
        
        # Buttons
        style.configure('Sidebar.TButton', background='#34495e', foreground='white',
                       borderwidth=0, font=('Helvetica', 10))
        style.map('Sidebar.TButton', background=[('active', '#546a7e')])
    
    def _create_layout(self):
        """Create main layout: sidebar on left, content on right"""
        # Sidebar (navigation)
        self.sidebar = ttk.Frame(self.root, width=220, style='Sidebar.TFrame')
        self.sidebar.pack(fill='y', side='left')
        self.sidebar.pack_propagate(False)
        
        # Main content area (where views appear)
        self.main_content = ttk.Frame(self.root, style='TFrame')
        self.main_content.pack(fill='both', expand=True, side='right')
    
    def _create_sidebar(self):
        """Create navigation sidebar"""
        # Title
        tk.Label(self.sidebar, text="CourseMate",
                font=('Helvetica', 16, 'bold'),
                bg='#2c3e50', fg='white').pack(pady=20)
        
        tk.Label(self.sidebar, text="Simple & Complete",
                font=('Helvetica', 9, 'italic'),
                bg='#2c3e50', fg='#95a5a6').pack()
        
        # Navigation section
        tk.Label(self.sidebar, text="NAVIGATION",
                font=('Helvetica', 9, 'bold'),
                bg='#2c3e50', fg='#95a5a6').pack(pady=(30, 10), padx=20, anchor='w')
        
        # Main navigation buttons
        main_nav = [
            ("📊 Dashboard", self.show_dashboard),
            ("📝 Freeform Notes", self.show_freeform),
        ]
        
        for text, command in main_nav:
            btn = ttk.Button(self.sidebar, text=text, style='Sidebar.TButton',
                           command=command)
            btn.pack(fill='x', pady=3, padx=15)
        
        # Non-Technical Templates Section
        tk.Label(self.sidebar, text="NON-TECHNICAL TEMPLATES",
                font=('Helvetica', 8, 'bold'),
                bg='#2c3e50', fg='#95a5a6').pack(pady=(15, 5), padx=20, anchor='w')
        
        non_tech_templates = [
            ("Cornell Notes", "Cornell"),
            ("Main Idea & Details", "MainIdea"),
            ("Frayer Model", "Frayer"),
        ]
        
        for text, template_key in non_tech_templates:
            btn = ttk.Button(self.sidebar, text=text, style='Sidebar.TButton',
                           command=lambda k=template_key: self.open_template(k))
            btn.pack(fill='x', pady=2, padx=15)
        
        # Technical Templates Section
        tk.Label(self.sidebar, text="TECHNICAL TEMPLATES",
                font=('Helvetica', 8, 'bold'),
                bg='#2c3e50', fg='#95a5a6').pack(pady=(15, 5), padx=20, anchor='w')
        
        tech_templates = [
            ("Polya's 4 Steps", "Polya"),
            ("5W1H Analysis", "5W1H"),
            ("Concept Map", "ConceptMap"),
        ]
        
        for text, template_key in tech_templates:
            btn = ttk.Button(self.sidebar, text=text, style='Sidebar.TButton',
                           command=lambda k=template_key: self.open_template(k))
            btn.pack(fill='x', pady=2, padx=15)
        
        # Quick Actions section
        tk.Label(self.sidebar, text="QUICK ACTIONS",
                font=('Helvetica', 9, 'bold'),
                bg='#2c3e50', fg='#95a5a6').pack(pady=(20, 10), padx=20, anchor='w')
        
        tk.Button(self.sidebar, text="+ Add Course",
                 command=self.add_course,
                 bg='#27ae60', fg='white',
                 relief='flat', font=('Helvetica', 9, 'bold')).pack(fill='x', padx=15, pady=3)
        
        tk.Button(self.sidebar, text="+ Add Task",
                 command=self.add_task,
                 bg='#3498db', fg='white',
                 relief='flat', font=('Helvetica', 9, 'bold')).pack(fill='x', padx=15, pady=3)
    
    # ------------------------------------------------------------------------
    # PART 4: COURSE MANAGEMENT
    # ------------------------------------------------------------------------
    
    def add_course(self):
        """Add a new course"""
        name = simpledialog.askstring("Add Course", "Enter course name:")
        
        if name and name.strip():
            name = name.strip()
            if name in self.courses:
                messagebox.showwarning("Exists", f"'{name}' already exists!")
                return
            
            # Create new course
            self.courses[name] = {"notes": [], "tasks": []}
            self._save_data()
            messagebox.showinfo("Success", f"Course '{name}' added!")
            self.show_dashboard()  # Refresh view
        elif name is not None:  # User clicked OK but empty
            messagebox.showwarning("Error", "Course name cannot be empty!")
    
    def delete_course(self, name):
        """Delete a course"""
        if messagebox.askyesno("Delete", f"Delete '{name}' and all its notes?"):
            del self.courses[name]
            self._save_data()
            messagebox.showinfo("Deleted", f"'{name}' deleted")
            self.show_dashboard()
    
    def view_course(self, course_name):
        """
        VIEW COURSE DETAILS
        Shows all notes for a specific course with scrollbar
        """
        self._clear_content()
        
        course = self.courses[course_name]
        
        # Header
        header_frame = ttk.Frame(self.main_content)
        header_frame.pack(fill='x', padx=30, pady=20)
        
        tk.Label(header_frame, text=f"📚 {course_name}",
                font=('Helvetica', 24, 'bold'),
                bg='#f5f5f5').pack(side='left')
        
        tk.Button(header_frame, text="← Back to Dashboard",
                 command=self.show_dashboard,
                 bg='#95a5a6', fg='white',
                 relief='flat', font=('Helvetica', 9)).pack(side='right')
        
        # Stats
        stats_frame = ttk.Frame(self.main_content, style='Card.TFrame', padding=15)
        stats_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        tk.Label(stats_frame, text=f"📝 Total Notes: {len(course['notes'])}",
                font=('Helvetica', 12), bg='white').pack(side='left', padx=10)
        tk.Label(stats_frame, text=f"📋 Total Tasks: {len(course['tasks'])}",
                font=('Helvetica', 12), bg='white').pack(side='left', padx=10)
        
        # Notes section title
        tk.Label(self.main_content, text="Notes",
                font=('Helvetica', 16, 'bold'),
                bg='#f5f5f5').pack(anchor='w', padx=30, pady=(10, 10))
        
        if not course['notes']:
            empty_card = ttk.Frame(self.main_content, style='Card.TFrame', padding=30)
            empty_card.pack(fill='x', padx=30, pady=10)
            
            tk.Label(empty_card, text="📝 No notes yet for this course",
                    font=('Helvetica', 12), bg='white',
                    fg='#95a5a6').pack()
            tk.Label(empty_card, text="Use 'Freeform Notes' or templates to add notes!",
                    font=('Helvetica', 10), bg='white',
                    fg='#95a5a6').pack(pady=5)
        else:
            # Create scrollable area for notes
            notes_container = ttk.Frame(self.main_content)
            notes_container.pack(fill='both', expand=True, padx=30, pady=(0, 20))
            
            canvas = tk.Canvas(notes_container, bg='#f5f5f5', highlightthickness=0)
            scrollbar = ttk.Scrollbar(notes_container, orient='vertical', command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind('<Configure>',
                                 lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # Mouse wheel scrolling
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
            # Display all notes in scrollable area
            for i, note in enumerate(course['notes']):
                self._display_note_card_in_frame(scrollable_frame, course_name, i, note)
    
    def _display_note_card_in_frame(self, parent_frame, course_name, note_index, note):
        """Helper: Display a single note card in a specific frame"""
        card = ttk.Frame(parent_frame, style='Card.TFrame', padding=15)
        card.pack(fill='x', pady=8, padx=5)
        
        # Note header
        header = ttk.Frame(card)
        header.pack(fill='x', pady=(0, 10))
        
        tk.Label(header, text=note.get('title', 'Untitled Note'),
                font=('Helvetica', 13, 'bold'),
                bg='white').pack(side='left')
        
        tk.Label(header, text=note.get('created', ''),
                font=('Helvetica', 9), fg='#95a5a6',
                bg='white').pack(side='left', padx=10)
        
        # Delete button
        tk.Button(header, text="🗑️ Delete",
                 command=lambda: self.delete_note(course_name, note_index),
                 fg='#e74c3c', relief='flat',
                 font=('Helvetica', 9)).pack(side='right')
        
        # Note content
        if 'template' in note:
            # Template note - show structured data
            tk.Label(card, text=f"Template: {note['template']}",
                    font=('Helvetica', 10, 'italic'),
                    fg='#3498db', bg='white').pack(anchor='w', pady=5)
            
            for field, value in note.get('data', {}).items():
                if value:  # Only show fields with content
                    field_frame = ttk.Frame(card)
                    field_frame.pack(fill='x', pady=5)
                    
                    tk.Label(field_frame, text=f"{field}:",
                            font=('Helvetica', 10, 'bold'),
                            bg='white').pack(anchor='w')
                    
                    tk.Label(field_frame, text=value,
                            font=('Helvetica', 10),
                            bg='white', wraplength=700,
                            justify='left').pack(anchor='w', padx=20)
        else:
            # Freeform note - show content
            content = note.get('content', '')
            preview = content[:200] + "..." if len(content) > 200 else content
            
            tk.Label(card, text=preview,
                    font=('Helvetica', 10),
                    bg='white', wraplength=700,
                    justify='left').pack(anchor='w', pady=5)
            
            if len(content) > 200:
                tk.Button(card, text="Read full note →",
                         command=lambda: self.view_full_note(note),
                         fg='#3498db', relief='flat',
                         font=('Helvetica', 9)).pack(anchor='w', pady=5)
    
    def delete_note(self, course_name, note_index):
        """Delete a specific note"""
        note_title = self.courses[course_name]['notes'][note_index].get('title', 'this note')
        
        if messagebox.askyesno("Delete Note", f"Delete '{note_title}'?"):
            self.courses[course_name]['notes'].pop(note_index)
            self._save_data()
            self.view_course(course_name)  # Refresh the view
    
    def view_full_note(self, note):
        """View full note content in a popup window"""
        popup = tk.Toplevel(self.root)
        popup.title(note.get('title', 'Note'))
        popup.geometry("700x500")
        
        # Title
        tk.Label(popup, text=note.get('title', 'Untitled'),
                font=('Helvetica', 16, 'bold')).pack(pady=20, padx=20)
        
        # Content in scrollable text widget
        text_frame = ttk.Frame(popup)
        text_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')
        
        text_widget = tk.Text(text_frame, wrap='word', font=('Helvetica', 11),
                             yscrollcommand=scrollbar.set)
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # Insert content
        text_widget.insert('1.0', note.get('content', ''))
        text_widget.config(state='disabled')  # Read-only
        
        # Close button
        tk.Button(popup, text="Close",
                 command=popup.destroy,
                 bg='#95a5a6', fg='white',
                 font=('Helvetica', 10),
                 relief='flat', padx=20, pady=8).pack(pady=10)
    
    def show_task_history(self):
        """
        TASK HISTORY VIEW
        Shows completed tasks with restore/delete options
        """
        self._clear_content()
        
        # Title
        tk.Label(self.main_content, text="✅ Task History",
                font=('Helvetica', 24, 'bold'),
                bg='#f5f5f5').pack(pady=20, anchor='w', padx=30)
        
        tk.Label(self.main_content, text="View and manage your completed tasks",
                font=('Helvetica', 11), fg='#7f8c8d',
                bg='#f5f5f5').pack(anchor='w', padx=30, pady=(0, 20))
        
        # Stats
        stats_frame = ttk.Frame(self.main_content, style='Card.TFrame', padding=15)
        stats_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        tk.Label(stats_frame, text=f"📋 Active Tasks: {len(self.tasks)}",
                font=('Helvetica', 12), bg='white').pack(side='left', padx=10)
        tk.Label(stats_frame, text=f"✓ Completed Tasks: {len(self.completed_tasks)}",
                font=('Helvetica', 12), bg='white').pack(side='left', padx=10)
        
        # Completed tasks list
        if not self.completed_tasks:
            empty_card = ttk.Frame(self.main_content, style='Card.TFrame', padding=30)
            empty_card.pack(fill='x', padx=30, pady=10)
            
            tk.Label(empty_card, text="✅ No completed tasks yet",
                    font=('Helvetica', 12), bg='white',
                    fg='#95a5a6').pack()
            tk.Label(empty_card, text="Complete tasks from the Dashboard to see them here!",
                    font=('Helvetica', 10), bg='white',
                    fg='#95a5a6').pack(pady=5)
        else:
            # Create scrollable area for completed tasks
            tasks_container = ttk.Frame(self.main_content)
            tasks_container.pack(fill='both', expand=True, padx=30, pady=(0, 20))
            
            canvas = tk.Canvas(tasks_container, bg='#f5f5f5', highlightthickness=0)
            scrollbar = ttk.Scrollbar(tasks_container, orient='vertical', command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind('<Configure>',
                                 lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # Mouse wheel scrolling
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
            # Display completed tasks
            for i, task_data in enumerate(self.completed_tasks):
                card = ttk.Frame(scrollable_frame, style='Card.TFrame', padding=15)
                card.pack(fill='x', pady=8, padx=5)
                
                # Task info
                info_frame = ttk.Frame(card)
                info_frame.pack(fill='x')
                
                tk.Label(info_frame, text="✓",
                        font=('Helvetica', 14, 'bold'),
                        fg='#27ae60', bg='white').pack(side='left', padx=(0, 10))
                
                task_text_frame = ttk.Frame(info_frame)
                task_text_frame.pack(side='left', fill='x', expand=True)
                
                tk.Label(task_text_frame, text=task_data['task'],
                        font=('Helvetica', 11),
                        bg='white').pack(anchor='w')
                
                tk.Label(task_text_frame, text=f"Completed: {task_data['completed_date']}",
                        font=('Helvetica', 9), fg='#95a5a6',
                        bg='white').pack(anchor='w')
                
                # Action buttons
                btn_frame = ttk.Frame(info_frame)
                btn_frame.pack(side='right')
                
                tk.Button(btn_frame, text="↶ Restore",
                         command=lambda idx=i: self._restore_and_refresh(idx),
                         bg='#3498db', fg='white',
                         relief='flat', font=('Helvetica', 9)).pack(side='left', padx=5)
                
                tk.Button(btn_frame, text="🗑️ Delete",
                         command=lambda idx=i: self._delete_completed_and_refresh(idx),
                         fg='#e74c3c',
                         relief='flat', font=('Helvetica', 9)).pack(side='left', padx=5)
        
        # Back button
        tk.Button(self.main_content, text="← Back to Dashboard",
                 command=self.show_dashboard,
                 bg='#95a5a6', fg='white',
                 relief='flat', font=('Helvetica', 10),
                 padx=15, pady=8).pack(pady=20)
    
    def _restore_task_and_refresh(self, index):
        """Restore task from dashboard and refresh"""
        self.restore_task(index)
        self.show_dashboard()
    
    def _delete_completed_from_dashboard(self, index):
        """Delete completed task from dashboard"""
        if messagebox.askyesno("Delete", "Permanently delete this completed task?"):
            self.permanently_delete_task(index)
            self.show_dashboard()
    
    # ------------------------------------------------------------------------
    # PART 5: TASK MANAGEMENT
    # ------------------------------------------------------------------------
    
    def add_task(self):
        """Add a general task"""
        task = simpledialog.askstring("Add Task", "Enter task:")
        
        if task and task.strip():
            self.tasks.append(task.strip())
            self._save_data()
            self.show_dashboard()
    
    def delete_task(self, index):
        """Mark task as complete and move to history"""
        task = self.tasks.pop(index)
        self.completed_tasks.append({
            "task": task,
            "completed_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        self._save_data()
        self.show_dashboard()
    
    def restore_task(self, index):
        """Restore a completed task back to active tasks"""
        task_data = self.completed_tasks.pop(index)
        self.tasks.append(task_data["task"])
        self._save_data()
    
    def permanently_delete_task(self, index):
        """Permanently delete a completed task"""
        self.completed_tasks.pop(index)
        self._save_data()
    
    # ------------------------------------------------------------------------
    # PART 6: VIEWS (Different screens)
    # ------------------------------------------------------------------------
    
    def _clear_content(self):
        """Helper: Clear the main content area"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """
        DASHBOARD VIEW
        Shows: Course list + Task list side by side
        """
        self._clear_content()
        
        # Title
        tk.Label(self.main_content, text="📊 Dashboard",
                font=('Helvetica', 24, 'bold'),
                bg='#f5f5f5').pack(pady=20, anchor='w', padx=30)
        
        # Container for two columns
        container = ttk.Frame(self.main_content)
        container.pack(fill='both', expand=True, padx=30, pady=10)
        
        # LEFT: Courses list
        courses_frame = ttk.Frame(container, style='Card.TFrame', padding=15)
        courses_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(courses_frame, text="📚 My Courses",
                font=('Helvetica', 14, 'bold'),
                bg='white').pack(anchor='w', pady=(0, 10))
        
        if not self.courses:
            tk.Label(courses_frame, text="No courses yet.\nClick '+ Add Course' to start!",
                    font=('Helvetica', 10), fg='#95a5a6',
                    bg='white', justify='left').pack(pady=20)
        else:
            for name, data in self.courses.items():
                course_row = ttk.Frame(courses_frame)
                course_row.pack(fill='x', pady=5)
                
                # Make course name clickable
                course_btn = tk.Button(course_row, text=f"📚 {name}",
                                      font=('Helvetica', 11, 'bold'),
                                      bg='white', fg='#2c3e50',
                                      relief='flat', anchor='w',
                                      command=lambda n=name: self.view_course(n))
                course_btn.pack(side='left', fill='x', expand=True)
                
                tk.Label(course_row, text=f"({len(data['notes'])} notes)",
                        font=('Helvetica', 9), fg='#7f8c8d',
                        bg='white').pack(side='left', padx=5)
                
                tk.Button(course_row, text="🗑️",
                         command=lambda n=name: self.delete_course(n),
                         relief='flat', bg='white',
                         font=('Helvetica', 8)).pack(side='right')
        
        # RIGHT: Tasks list (Active + Completed)
        tasks_frame = ttk.Frame(container, style='Card.TFrame', padding=15)
        tasks_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Active Tasks Section
        active_header = ttk.Frame(tasks_frame)
        active_header.pack(fill='x', pady=(0, 10))
        
        tk.Label(active_header, text="✅ Quick Tasks",
                font=('Helvetica', 14, 'bold'),
                bg='white').pack(side='left')
        
        tk.Button(active_header, text="+ Add",
                 command=self.add_task,
                 bg='#3498db', fg='white',
                 relief='flat', font=('Helvetica', 8, 'bold')).pack(side='right')
        
        # Active tasks list
        if not self.tasks:
            tk.Label(tasks_frame, text="No active tasks",
                    font=('Helvetica', 10), fg='#95a5a6',
                    bg='white').pack(pady=10)
        else:
            for i, task in enumerate(self.tasks):
                task_row = ttk.Frame(tasks_frame)
                task_row.pack(fill='x', pady=5)
                
                tk.Label(task_row, text=f"☐ {task}",
                        font=('Helvetica', 11), bg='white').pack(side='left')
                
                tk.Button(task_row, text="✓",
                         command=lambda idx=i: self.delete_task(idx),
                         relief='flat', bg='white', fg='#27ae60',
                         font=('Helvetica', 10, 'bold')).pack(side='right')
        
        # Separator
        ttk.Separator(tasks_frame, orient='horizontal').pack(fill='x', pady=15)
        
        # Completed Tasks Section
        completed_header = ttk.Frame(tasks_frame)
        completed_header.pack(fill='x', pady=(0, 10))
        
        tk.Label(completed_header, text="✓ Completed Tasks",
                font=('Helvetica', 12, 'bold'),
                fg='#27ae60', bg='white').pack(side='left')
        
        tk.Label(completed_header, text=f"({len(self.completed_tasks)})",
                font=('Helvetica', 10), fg='#95a5a6',
                bg='white').pack(side='left', padx=5)
        
        # Completed tasks list (scrollable if many)
        if not self.completed_tasks:
            tk.Label(tasks_frame, text="No completed tasks yet",
                    font=('Helvetica', 9), fg='#95a5a6',
                    bg='white', justify='left').pack(pady=10)
        else:
            # Create scrollable area for completed tasks
            completed_container = ttk.Frame(tasks_frame)
            completed_container.pack(fill='both', expand=True)
            
            # Limit height for scrollbar
            canvas_height = min(200, len(self.completed_tasks) * 40)
            
            canvas = tk.Canvas(completed_container, bg='white', 
                             height=canvas_height, highlightthickness=0)
            scrollbar = ttk.Scrollbar(completed_container, orient='vertical', 
                                     command=canvas.yview)
            scrollable_completed = ttk.Frame(canvas)
            
            scrollable_completed.bind('<Configure>',
                                     lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
            
            canvas.create_window((0, 0), window=scrollable_completed, anchor='nw')
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side='left', fill='both', expand=True)
            if len(self.completed_tasks) > 5:
                scrollbar.pack(side='right', fill='y')
            
            # Display completed tasks
            for i, task_data in enumerate(reversed(self.completed_tasks[-10:])):  # Show last 10, newest first
                task_row = ttk.Frame(scrollable_completed)
                task_row.pack(fill='x', pady=3)
                
                # Task text
                task_text_frame = ttk.Frame(task_row)
                task_text_frame.pack(side='left', fill='x', expand=True)
                
                tk.Label(task_text_frame, text=f"✓ {task_data['task']}",
                        font=('Helvetica', 9), fg='#7f8c8d',
                        bg='white').pack(anchor='w')
                
                # Action buttons
                btn_container = ttk.Frame(task_row)
                btn_container.pack(side='right')
                
                # Calculate actual index in the original list
                actual_index = len(self.completed_tasks) - 1 - i
                
                tk.Button(btn_container, text="↶",
                         command=lambda idx=actual_index: self._restore_task_and_refresh(idx),
                         relief='flat', bg='white', fg='#3498db',
                         font=('Helvetica', 9), cursor='hand2').pack(side='left', padx=2)
                
                tk.Button(btn_container, text="🗑️",
                         command=lambda idx=actual_index: self._delete_completed_from_dashboard(idx),
                         relief='flat', bg='white', fg='#e74c3c',
                         font=('Helvetica', 8), cursor='hand2').pack(side='left', padx=2)
    
    def show_freeform(self):
        """
        FREEFORM NOTES VIEW
        Simple text editor to write notes
        """
        self._clear_content()
        
        # Title
        tk.Label(self.main_content, text="📝 Freeform Notes",
                font=('Helvetica', 24, 'bold'),
                bg='#f5f5f5').pack(pady=20, anchor='w', padx=30)
        
        # Card container
        card = ttk.Frame(self.main_content, style='Card.TFrame', padding=20)
        card.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        
        # Top: Course selector + Title
        top_frame = ttk.Frame(card)
        top_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(top_frame, text="Course:", bg='white').pack(side='left', padx=5)
        
        course_var = tk.StringVar(value="Select Course")
        course_options = ["Select Course"] + list(self.courses.keys())
        course_menu = ttk.OptionMenu(top_frame, course_var, course_options[0], *course_options)
        course_menu.pack(side='left', padx=5)
        
        tk.Label(top_frame, text="Title:", bg='white').pack(side='left', padx=(20, 5))
        title_entry = tk.Entry(top_frame, width=40, font=('Helvetica', 10))
        title_entry.pack(side='left', padx=5)
        
        # Text editor
        text_widget = tk.Text(card, wrap='word', font=('Helvetica', 11),
                             undo=True, height=20)
        text_widget.pack(fill='both', expand=True, pady=10)
        
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
        
        tk.Button(card, text="💾 Save Note",
                 command=save_note,
                 bg='#27ae60', fg='white',
                 font=('Helvetica', 11, 'bold'),
                 relief='flat', padx=20, pady=10).pack(pady=10)
    
    def show_technical(self):
        """
        TECHNICAL TEMPLATES VIEW
        Shows: Polya, 5W1H, Concept Map
        """
        self._clear_content()
        
        tk.Label(self.main_content, text="💡 Technical Templates",
                font=('Helvetica', 24, 'bold'),
                bg='#f5f5f5').pack(pady=20, anchor='w', padx=30)
        
        tk.Label(self.main_content, text="Problem-solving frameworks for technical courses",
                font=('Helvetica', 11), fg='#7f8c8d',
                bg='#f5f5f5').pack(anchor='w', padx=30, pady=(0, 20))
        
        templates = [
            ("Polya's 4 Steps", "Problem-solving methodology", "Polya"),
            ("5W1H Analysis", "What, Why, When, Where, Who, How", "5W1H"),
            ("Concept Mapping", "Visual relationship builder", "ConceptMap"),
        ]
        
        for name, desc, key in templates:
            card = ttk.Frame(self.main_content, style='Card.TFrame', padding=15)
            card.pack(fill='x', pady=8, padx=30)
            
            tk.Label(card, text=name, font=('Helvetica', 13, 'bold'),
                    bg='white').pack(anchor='w')
            tk.Label(card, text=desc, font=('Helvetica', 10),
                    fg='#7f8c8d', bg='white').pack(anchor='w', pady=5)
            
            tk.Button(card, text="Use Template →",
                     command=lambda k=key: self.open_template(k),
                     bg='#3498db', fg='white',
                     relief='flat').pack(anchor='e')
    
    def show_nontechnical(self):
        """
        NON-TECHNICAL TEMPLATES VIEW
        Shows: Cornell, Frayer, Main Idea
        """
        self._clear_content()
        
        tk.Label(self.main_content, text="📖 Study Templates",
                font=('Helvetica', 24, 'bold'),
                bg='#f5f5f5').pack(pady=20, anchor='w', padx=30)
        
        tk.Label(self.main_content, text="Structured note-taking methods for general education",
                font=('Helvetica', 11), fg='#7f8c8d',
                bg='#f5f5f5').pack(anchor='w', padx=30, pady=(0, 20))
        
        templates = [
            ("Cornell Notes", "Two-column system with summary", "Cornell"),
            ("Frayer Model", "Vocabulary and concept organizer", "Frayer"),
            ("Main Idea & Details", "Topic breakdown structure", "MainIdea"),
        ]
        
        for name, desc, key in templates:
            card = ttk.Frame(self.main_content, style='Card.TFrame', padding=15)
            card.pack(fill='x', padx=30, pady=8)
            
            tk.Label(card, text=name, font=('Helvetica', 13, 'bold'),
                    bg='white').pack(anchor='w')
            tk.Label(card, text=desc, font=('Helvetica', 10),
                    fg='#7f8c8d', bg='white').pack(anchor='w', pady=5)
            
            tk.Button(card, text="Use Template →",
                     command=lambda k=key: self.open_template(k),
                     bg='#3498db', fg='white',
                     relief='flat').pack(anchor='e')
    
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
            "Polya": ["Step 1: Understand the Problem", "Step 2: Devise a Plan",
                     "Step 3: Carry out the Plan", "Step 4: Look Back/Review"],
            "5W1H": ["What is the problem?", "Why is it important?",
                    "When did it happen?", "Where is it applied?",
                    "Who is involved?", "How does it work?"],
            "ConceptMap": ["Central Concept", "Related Concept 1",
                          "Related Concept 2", "Connection/Relationship"],
            "Cornell": ["Keywords/Cues (Left Column)", "Notes (Right Column)",
                       "Summary (Bottom)"],
            "Frayer": ["Concept/Term", "Definition", "Characteristics",
                      "Examples", "Non-Examples"],
            "MainIdea": ["Main Topic", "Core Idea/Thesis",
                        "Supporting Detail 1", "Supporting Detail 2", "Supporting Detail 3"],
        }
        
        # Template display names
        TEMPLATE_NAMES = {
            "Cornell": "Cornell Notes",
            "MainIdea": "Main Idea & Details",
            "Frayer": "Frayer Model",
            "Polya": "Polya's 4 Steps",
            "5W1H": "5W1H Analysis",
            "ConceptMap": "Concept Map"
        }
        
        fields = TEMPLATES.get(template_key, [])
        template_display_name = TEMPLATE_NAMES.get(template_key, template_key)
        
        # Title
        tk.Label(self.main_content, text=f"{template_display_name}",
                font=('Helvetica', 24, 'bold'),
                bg='#f5f5f5').pack(pady=20, anchor='w', padx=30)
        
        # Course selector
        top_frame = ttk.Frame(self.main_content)
        top_frame.pack(fill='x', padx=30, pady=(0, 10))
        
        tk.Label(top_frame, text="Course:", bg='#f5f5f5').pack(side='left', padx=5)
        
        course_var = tk.StringVar(value="Select Course")
        course_options = ["Select Course"] + list(self.courses.keys())
        course_menu = ttk.OptionMenu(top_frame, course_var, course_options[0], *course_options)
        course_menu.pack(side='left', padx=5)
        
        # Scrollable form area
        canvas_frame = ttk.Frame(self.main_content)
        canvas_frame.pack(fill='both', expand=True, padx=30, pady=(0, 10))
        
        canvas = tk.Canvas(canvas_frame, bg='#f5f5f5', highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', command=canvas.yview)
        form_frame = ttk.Frame(canvas)
        
        form_frame.bind('<Configure>',
                       lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        
        canvas.create_window((0, 0), window=form_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Create form fields
        field_widgets = {}
        for field_label in fields:
            field_card = ttk.Frame(form_frame, style='Card.TFrame', padding=15)
            field_card.pack(fill='x', pady=8, padx=10)
            
            tk.Label(field_card, text=field_label,
                    font=('Helvetica', 11, 'bold'),
                    bg='white').pack(anchor='w', pady=(0, 5))
            
            widget = tk.Text(field_card, height=5, wrap='word',
                           font=('Helvetica', 10))
            widget.pack(fill='x', expand=True)
            
            field_widgets[field_label] = widget
        
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
        
        btn_frame = ttk.Frame(self.main_content)
        btn_frame.pack(fill='x', padx=30, pady=10)
        
        tk.Button(btn_frame, text="💾 Save Template",
                 command=save_template,
                 bg='#27ae60', fg='white',
                 font=('Helvetica', 11, 'bold'),
                 relief='flat', padx=20, pady=10).pack(side='left')
        
        tk.Button(btn_frame, text="← Back to Dashboard",
                 command=self.show_dashboard,
                 relief='flat', padx=15, pady=10).pack(side='left', padx=10)


# ============================================================================
# RUN THE APP
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("COURSEMATE - SIMPLE & COMPLETE")
    print("=" * 60)
    print("\n✓ Dashboard with courses and tasks")
    print("✓ Freeform notes editor")
    print("✓ 3 Technical templates")
    print("✓ 3 Study templates")
    print("✓ Auto-save to JSON")
    print("\nData saves to: coursemate_data.json")
    print("=" * 60)
    
    root = tk.Tk()
    app = CourseMateApp(root)
    root.mainloop()