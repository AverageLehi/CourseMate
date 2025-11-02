"""
================================================================================
COURSEMATE - EASIEST VERSION (CSV + TXT FILES)
================================================================================
A simple note-taking and study tool using CSV and TXT files.

FEATURES:
- Dashboard with courses
- Freeform notes
- 6 study templates
- Course tasks and quick tasks
- Auto-saves to CSV and TXT files

TO RUN: python coursemate.py

Data Files Created:
- courses.csv       -> Stores course names
- notes.csv         -> Stores all notes
- tasks.csv         -> Stores tasks (course tasks + quick tasks)

Simple and easy to understand!
================================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import csv
import os
from datetime import datetime


class CourseMateApp:
    """Main application - everything in one simple class"""
    
    def __init__(self, root):
        """Setup when app starts"""
        self.root = root
        self.root.title("CourseMate - Simple CSV Version")
        self.root.geometry("1100x700")
        
        # Our data (stored in memory while app runs)
        self.courses = []          # List of course names
        self.notes = []            # List of all notes
        self.tasks = []            # List of all tasks
        
        # Load data from files
        self.load_all_data()
        
        # Create the interface
        self.create_interface()
        
        # Show dashboard
        self.show_dashboard()
        
        print("✅ CourseMate started! Using CSV files.")
    
    # ========================================
    # PART 1: LOADING DATA (FROM FILES)
    # ========================================
    
    def load_all_data(self):
        """Load all data from CSV files"""
        self.load_courses()
        self.load_notes()
        self.load_tasks()
    
    def load_courses(self):
        """Load courses from courses.csv"""
        try:
            if os.path.exists('courses.csv'):
                with open('courses.csv', 'r') as f:
                    reader = csv.reader(f)
                    next(reader, None)  # Skip header
                    self.courses = [row[0] for row in reader if row]
                print(f"📁 Loaded {len(self.courses)} courses")
            else:
                self.courses = []
                print("📁 No courses file found")
        except:
            self.courses = []
            print("⚠️ Error loading courses")
    
    def load_notes(self):
        """Load notes from notes.csv"""
        try:
            if os.path.exists('notes.csv'):
                with open('notes.csv', 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.notes = list(reader)
                print(f"📝 Loaded {len(self.notes)} notes")
            else:
                self.notes = []
                print("📝 No notes file found")
        except:
            self.notes = []
            print("⚠️ Error loading notes")
    
    def load_tasks(self):
        """Load tasks from tasks.csv"""
        try:
            if os.path.exists('tasks.csv'):
                with open('tasks.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    self.tasks = list(reader)
                print(f"✅ Loaded {len(self.tasks)} tasks")
            else:
                self.tasks = []
                print("✅ No tasks file found")
        except:
            self.tasks = []
            print("⚠️ Error loading tasks")
    
    # ========================================
    # PART 2: SAVING DATA (TO FILES)
    # ========================================
    
    def save_courses(self):
        """Save courses to courses.csv"""
        try:
            with open('courses.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Course Name'])  # Header
                for course in self.courses:
                    writer.writerow([course])
            print("💾 Courses saved")
        except Exception as e:
            print(f"❌ Error saving courses: {e}")
    
    def save_notes(self):
        """Save notes to notes.csv"""
        try:
            with open('notes.csv', 'w', newline='', encoding='utf-8') as f:
                if self.notes:
                    # Get all possible fields
                    fieldnames = ['course', 'title', 'content', 'template', 'created']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.notes)
            print("💾 Notes saved")
        except Exception as e:
            print(f"❌ Error saving notes: {e}")
    
    def save_tasks(self):
        """Save tasks to tasks.csv"""
        try:
            with open('tasks.csv', 'w', newline='') as f:
                fieldnames = ['task', 'course', 'type']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.tasks)
            print("💾 Tasks saved")
        except Exception as e:
            print(f"❌ Error saving tasks: {e}")
    
    # ========================================
    # PART 3: USER INTERFACE
    # ========================================
    
    def create_interface(self):
        """Create the user interface"""
        # Styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f5f5f5')
        style.configure('Sidebar.TFrame', background='#2c3e50')
        style.configure('Card.TFrame', background='white', relief='solid', borderwidth=1)
        style.configure('Sidebar.TButton', background='#34495e', foreground='white',
                       borderwidth=0, font=('Helvetica', 10))
        style.map('Sidebar.TButton', background=[('active', '#546a7e')])
        
        # Left sidebar
        self.sidebar = ttk.Frame(self.root, width=220, style='Sidebar.TFrame')
        self.sidebar.pack(fill='y', side='left')
        self.sidebar.pack_propagate(False)
        
        # Right content area
        self.content = ttk.Frame(self.root, style='TFrame')
        self.content.pack(fill='both', expand=True, side='right')
        
        # Create sidebar menu
        self.create_sidebar()
    
    def create_sidebar(self):
        """Create navigation menu"""
        # Title
        tk.Label(self.sidebar, text="CourseMate",
                font=('Helvetica', 16, 'bold'),
                bg='#2c3e50', fg='white').pack(pady=20)
        
        tk.Label(self.sidebar, text="CSV Version",
                font=('Helvetica', 9, 'italic'),
                bg='#2c3e50', fg='#95a5a6').pack()
        
        # Navigation
        tk.Label(self.sidebar, text="NAVIGATION",
                font=('Helvetica', 9, 'bold'),
                bg='#2c3e50', fg='#95a5a6').pack(pady=(20, 10), padx=20, anchor='w')
        
        ttk.Button(self.sidebar, text="📊 Dashboard",
                  command=self.show_dashboard,
                  style='Sidebar.TButton').pack(fill='x', pady=3, padx=15)
        
        ttk.Button(self.sidebar, text="📝 Freeform Notes",
                  command=self.show_freeform,
                  style='Sidebar.TButton').pack(fill='x', pady=3, padx=15)
        
        # Templates
        tk.Label(self.sidebar, text="NON-TECHNICAL",
                font=('Helvetica', 8, 'bold'),
                bg='#2c3e50', fg='#95a5a6').pack(pady=(15, 5), padx=20, anchor='w')
        
        for text, key in [("Cornell Notes", "Cornell"),
                         ("Main Idea", "MainIdea"),
                         ("Frayer Model", "Frayer")]:
            ttk.Button(self.sidebar, text=text,
                      command=lambda k=key: self.open_template(k),
                      style='Sidebar.TButton').pack(fill='x', pady=2, padx=15)
        
        tk.Label(self.sidebar, text="TECHNICAL",
                font=('Helvetica', 8, 'bold'),
                bg='#2c3e50', fg='#95a5a6').pack(pady=(15, 5), padx=20, anchor='w')
        
        for text, key in [("Polya's 4 Steps", "Polya"),
                         ("5W1H", "5W1H"),
                         ("Concept Map", "ConceptMap")]:
            ttk.Button(self.sidebar, text=text,
                      command=lambda k=key: self.open_template(k),
                      style='Sidebar.TButton').pack(fill='x', pady=2, padx=15)
        
        # Quick Actions
        tk.Label(self.sidebar, text="QUICK ACTIONS",
                font=('Helvetica', 9, 'bold'),
                bg='#2c3e50', fg='#95a5a6').pack(pady=(20, 10), padx=20, anchor='w')
        
        tk.Button(self.sidebar, text="+ Add Course",
                 command=self.add_course,
                 bg='#27ae60', fg='white',
                 relief='flat', font=('Helvetica', 9, 'bold')).pack(fill='x', padx=15, pady=3)
    
    # ========================================
    # PART 4: COURSES
    # ========================================
    
    def add_course(self):
        """Add a new course"""
        name = simpledialog.askstring("Add Course", "Enter course name:")
        
        if name and name.strip():
            name = name.strip()
            if name in self.courses:
                messagebox.showwarning("Exists", f"'{name}' already exists!")
                return
            
            self.courses.append(name)
            self.save_courses()
            messagebox.showinfo("Success", f"Course '{name}' added!")
            self.show_dashboard()
    
    def delete_course(self, name):
        """Delete a course"""
        if messagebox.askyesno("Delete", f"Delete '{name}'?"):
            self.courses.remove(name)
            self.save_courses()
            # Also delete related notes and tasks
            self.notes = [n for n in self.notes if n.get('course') != name]
            self.tasks = [t for t in self.tasks if t.get('course') != name]
            self.save_notes()
            self.save_tasks()
            self.show_dashboard()
    
    def view_course(self, name):
        """View a course details"""
        self.clear_content()
        
        # Header
        header = ttk.Frame(self.content)
        header.pack(fill='x', padx=30, pady=20)
        
        tk.Label(header, text=f"📚 {name}",
                font=('Helvetica', 24, 'bold'),
                bg='#f5f5f5').pack(side='left')
        
        tk.Button(header, text="← Back",
                 command=self.show_dashboard,
                 bg='#95a5a6', fg='white',
                 relief='flat').pack(side='right')
        
        # Get course data
        course_notes = [n for n in self.notes if n.get('course') == name]
        course_tasks = [t for t in self.tasks if t.get('course') == name]
        
        # Stats
        stats = ttk.Frame(self.content, style='Card.TFrame', padding=15)
        stats.pack(fill='x', padx=30, pady=(0, 20))
        
        tk.Label(stats, text=f"📝 {len(course_notes)} Notes",
                font=('Helvetica', 12), bg='white').pack(side='left', padx=10)
        tk.Label(stats, text=f"📋 {len(course_tasks)} Tasks",
                font=('Helvetica', 12), bg='white').pack(side='left', padx=10)
        
        # Notes
        tk.Label(self.content, text="Notes",
                font=('Helvetica', 16, 'bold'),
                bg='#f5f5f5').pack(anchor='w', padx=30, pady=10)
        
        if not course_notes:
            empty = ttk.Frame(self.content, style='Card.TFrame', padding=30)
            empty.pack(fill='x', padx=30, pady=10)
            tk.Label(empty, text="No notes yet",
                    font=('Helvetica', 11), fg='#95a5a6',
                    bg='white').pack()
        else:
            for note in course_notes:
                self.show_note_card(note)
        
        # Tasks
        tk.Label(self.content, text="Tasks",
                font=('Helvetica', 16, 'bold'),
                bg='#f5f5f5').pack(anchor='w', padx=30, pady=(20, 10))
        
        tasks_card = ttk.Frame(self.content, style='Card.TFrame', padding=15)
        tasks_card.pack(fill='x', padx=30, pady=10)
        
        tk.Button(tasks_card, text="+ Add Task",
                 command=lambda: self.add_task(name),
                 bg='#3498db', fg='white',
                 relief='flat', font=('Helvetica', 9, 'bold')).pack(anchor='w', pady=(0, 10))
        
        if not course_tasks:
            tk.Label(tasks_card, text="No tasks",
                    font=('Helvetica', 10), fg='#95a5a6',
                    bg='white').pack(pady=10)
        else:
            for task in course_tasks:
                row = ttk.Frame(tasks_card)
                row.pack(fill='x', pady=3)
                
                tk.Label(row, text=f"☐ {task['task']}",
                        font=('Helvetica', 11), bg='white').pack(side='left')
                
                tk.Button(row, text="✓",
                         command=lambda t=task: self.complete_task(t),
                         relief='flat', bg='white', fg='#27ae60',
                         font=('Helvetica', 10, 'bold')).pack(side='right')
    
    def show_note_card(self, note):
        """Display a note card"""
        card = ttk.Frame(self.content, style='Card.TFrame', padding=15)
        card.pack(fill='x', padx=30, pady=8)
        
        # Header
        header = ttk.Frame(card)
        header.pack(fill='x', pady=(0, 10))
        
        tk.Label(header, text=note.get('title', 'Untitled'),
                font=('Helvetica', 13, 'bold'),
                bg='white').pack(side='left')
        
        tk.Button(header, text="🗑️",
                 command=lambda: self.delete_note(note),
                 fg='#e74c3c', relief='flat').pack(side='right')
        
        # Content
        if note.get('template'):
            tk.Label(card, text=f"Template: {note['template']}",
                    font=('Helvetica', 10, 'italic'),
                    fg='#3498db', bg='white').pack(anchor='w', pady=5)
        
        content = note.get('content', '')
        if content:
            preview = content[:200] + "..." if len(content) > 200 else content
            tk.Label(card, text=preview,
                    font=('Helvetica', 10),
                    bg='white', wraplength=700).pack(anchor='w', pady=5)
    
    def delete_note(self, note):
        """Delete a note"""
        if messagebox.askyesno("Delete", "Delete this note?"):
            self.notes.remove(note)
            self.save_notes()
            self.view_course(note['course'])
    
    # ========================================
    # PART 5: TASKS
    # ========================================
    
    def add_task(self, course):
        """Add a task to a course"""
        task = simpledialog.askstring("Add Task", f"Task for {course}:")
        
        if task and task.strip():
            self.tasks.append({
                'task': task.strip(),
                'course': course,
                'type': 'course'
            })
            self.save_tasks()
            self.view_course(course)
    
    def add_quick_task(self):
        """Add a general quick task"""
        task = simpledialog.askstring("Quick Task", "Enter task:")
        
        if task and task.strip():
            self.tasks.append({
                'task': task.strip(),
                'course': '',
                'type': 'quick'
            })
            self.save_tasks()
            self.show_dashboard()
    
    def complete_task(self, task):
        """Complete a task (removes it)"""
        self.tasks.remove(task)
        self.save_tasks()
        if task.get('course'):
            self.view_course(task['course'])
        else:
            self.show_dashboard()
    
    # ========================================
    # PART 6: VIEWS (SCREENS)
    # ========================================
    
    def clear_content(self):
        """Clear the main area"""
        for widget in self.content.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Show main dashboard"""
        self.clear_content()
        
        tk.Label(self.content, text="📊 Dashboard",
                font=('Helvetica', 24, 'bold'),
                bg='#f5f5f5').pack(pady=20, anchor='w', padx=30)
        
        container = ttk.Frame(self.content)
        container.pack(fill='both', expand=True, padx=30, pady=10)
        
        # Courses
        courses_frame = ttk.Frame(container, style='Card.TFrame', padding=15)
        courses_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(courses_frame, text="📚 My Courses",
                font=('Helvetica', 14, 'bold'),
                bg='white').pack(anchor='w', pady=(0, 10))
        
        if not self.courses:
            tk.Label(courses_frame, text="No courses.\nClick '+ Add Course'",
                    font=('Helvetica', 10), fg='#95a5a6',
                    bg='white').pack(pady=20)
        else:
            for name in self.courses:
                row = ttk.Frame(courses_frame)
                row.pack(fill='x', pady=5)
                
                # Count notes and tasks
                notes_count = len([n for n in self.notes if n.get('course') == name])
                tasks_count = len([t for t in self.tasks if t.get('course') == name])
                
                btn = tk.Button(row, text=f"📚 {name}",
                              font=('Helvetica', 11, 'bold'),
                              bg='white', fg='#2c3e50',
                              relief='flat', anchor='w',
                              command=lambda n=name: self.view_course(n))
                btn.pack(side='left', fill='x', expand=True)
                
                tk.Label(row, text=f"({notes_count} notes, {tasks_count} tasks)",
                        font=('Helvetica', 9), fg='#7f8c8d',
                        bg='white').pack(side='left', padx=5)
                
                tk.Button(row, text="🗑️",
                         command=lambda n=name: self.delete_course(n),
                         relief='flat', bg='white').pack(side='right')
        
        # Quick Tasks
        tasks_frame = ttk.Frame(container, style='Card.TFrame', padding=15)
        tasks_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        header = ttk.Frame(tasks_frame)
        header.pack(fill='x', pady=(0, 10))
        
        tk.Label(header, text="✅ Quick Tasks",
                font=('Helvetica', 14, 'bold'),
                bg='white').pack(side='left')
        
        tk.Button(header, text="+ Add",
                 command=self.add_quick_task,
                 bg='#3498db', fg='white',
                 relief='flat', font=('Helvetica', 8, 'bold')).pack(side='right')
        
        quick_tasks = [t for t in self.tasks if t.get('type') == 'quick']
        
        if not quick_tasks:
            tk.Label(tasks_frame, text="No quick tasks",
                    font=('Helvetica', 10), fg='#95a5a6',
                    bg='white').pack(pady=10)
        else:
            for task in quick_tasks:
                row = ttk.Frame(tasks_frame)
                row.pack(fill='x', pady=5)
                
                tk.Label(row, text=f"☐ {task['task']}",
                        font=('Helvetica', 11), bg='white').pack(side='left')
                
                tk.Button(row, text="✓",
                         command=lambda t=task: self.complete_task(t),
                         relief='flat', bg='white', fg='#27ae60',
                         font=('Helvetica', 10, 'bold')).pack(side='right')
    
    def show_freeform(self):
        """Show freeform notes editor"""
        self.clear_content()
        
        tk.Label(self.content, text="📝 Freeform Notes",
                font=('Helvetica', 24, 'bold'),
                bg='#f5f5f5').pack(pady=20, anchor='w', padx=30)
        
        card = ttk.Frame(self.content, style='Card.TFrame', padding=20)
        card.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        
        # Course and title
        top = ttk.Frame(card)
        top.pack(fill='x', pady=(0, 10))
        
        tk.Label(top, text="Course:", bg='white').pack(side='left', padx=5)
        
        course_var = tk.StringVar(value="Select Course")
        courses = ["Select Course"] + self.courses
        ttk.OptionMenu(top, course_var, courses[0], *courses).pack(side='left', padx=5)
        
        tk.Label(top, text="Title:", bg='white').pack(side='left', padx=(20, 5))
        title_entry = tk.Entry(top, width=40)
        title_entry.pack(side='left', padx=5)
        
        # Text editor
        text_widget = tk.Text(card, wrap='word', font=('Helvetica', 11), height=20)
        text_widget.pack(fill='both', expand=True, pady=10)
        
        # Save button
        def save_note():
            course = course_var.get()
            title = title_entry.get().strip()
            content = text_widget.get("1.0", tk.END).strip()
            
            if course == "Select Course":
                messagebox.showwarning("Error", "Select a course!")
                return
            
            if not content:
                messagebox.showwarning("Error", "Note is empty!")
                return
            
            if not title:
                title = f"Note - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            self.notes.append({
                'course': course,
                'title': title,
                'content': content,
                'template': '',
                'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            self.save_notes()
            messagebox.showinfo("Saved", f"Note saved to {course}!")
            text_widget.delete("1.0", tk.END)
            title_entry.delete(0, tk.END)
        
        tk.Button(card, text="💾 Save Note",
                 command=save_note,
                 bg='#27ae60', fg='white',
                 font=('Helvetica', 11, 'bold'),
                 relief='flat', padx=20, pady=10).pack(pady=10)
    
    def open_template(self, template_key):
        """Open template form"""
        self.clear_content()
        
        # Template data
        templates = {
            "Cornell": ["Keywords", "Notes", "Summary"],
            "MainIdea": ["Main Topic", "Core Idea", "Detail 1", "Detail 2"],
            "Frayer": ["Concept", "Definition", "Examples", "Non-Examples"],
            "Polya": ["Understand", "Plan", "Execute", "Review"],
            "5W1H": ["What?", "Why?", "When?", "Where?", "Who?", "How?"],
            "ConceptMap": ["Central", "Related 1", "Related 2", "Connection"]
        }
        
        names = {
            "Cornell": "Cornell Notes",
            "MainIdea": "Main Idea",
            "Frayer": "Frayer Model",
            "Polya": "Polya's 4 Steps",
            "5W1H": "5W1H Analysis",
            "ConceptMap": "Concept Map"
        }
        
        fields = templates.get(template_key, [])
        name = names.get(template_key, template_key)
        
        tk.Label(self.content, text=name,
                font=('Helvetica', 24, 'bold'),
                bg='#f5f5f5').pack(pady=20, anchor='w', padx=30)
        
        # Course selector
        top = ttk.Frame(self.content)
        top.pack(fill='x', padx=30, pady=(0, 10))
        
        tk.Label(top, text="Course:", bg='#f5f5f5').pack(side='left', padx=5)
        
        course_var = tk.StringVar(value="Select Course")
        courses = ["Select Course"] + self.courses
        ttk.OptionMenu(top, course_var, courses[0], *courses).pack(side='left', padx=5)
        
        # Fields
        field_widgets = {}
        for field in fields:
            card = ttk.Frame(self.content, style='Card.TFrame', padding=15)
            card.pack(fill='x', padx=30, pady=5)
            
            tk.Label(card, text=field,
                    font=('Helvetica', 11, 'bold'),
                    bg='white').pack(anchor='w', pady=(0, 5))
            
            widget = tk.Text(card, height=3, wrap='word')
            widget.pack(fill='x')
            
            field_widgets[field] = widget
        
        # Save button
        def save_template():
            course = course_var.get()
            if course == "Select Course":
                messagebox.showwarning("Error", "Select a course!")
                return
            
            # Collect data
            all_content = []
            for field, widget in field_widgets.items():
                content = widget.get("1.0", tk.END).strip()
                if content:
                    all_content.append(f"{field}: {content}")
            
            if not all_content:
                messagebox.showwarning("Error", "Template is empty!")
                return
            
            combined_content = "\n\n".join(all_content)
            
            self.notes.append({
                'course': course,
                'title': f"{name} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                'content': combined_content,
                'template': template_key,
                'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            self.save_notes()
            messagebox.showinfo("Saved", f"{name} saved!")
            self.show_dashboard()
        
        btn_frame = ttk.Frame(self.content)
        btn_frame.pack(fill='x', padx=30, pady=20)
        
        tk.Button(btn_frame, text="💾 Save",
                 command=save_template,
                 bg='#27ae60', fg='white',
                 font=('Helvetica', 11, 'bold'),
                 relief='flat', padx=20, pady=10).pack(side='left')
        
        tk.Button(btn_frame, text="← Back",
                 command=self.show_dashboard,
                 relief='flat', padx=15, pady=10).pack(side='left', padx=10)


# ============================================================================
# RUN THE APP
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("COURSEMATE - CSV VERSION")
    print("=" * 60)
    print("\nUsing simple CSV files:")
    print("  📁 courses.csv  - Stores courses")
    print("  📝 notes.csv    - Stores all notes")
    print("  ✅ tasks.csv    - Stores tasks")
    print("\nEasy to understand and view in Excel!")
    print("=" * 60)
    
    root = tk.Tk()
    app = CourseMateApp(root)
    root.mainloop()