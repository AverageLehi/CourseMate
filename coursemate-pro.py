import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
import time
import json
import os
import random
from datetime import datetime
from pathlib import Path

class CourseMateApp:
    """Enhanced CourseMate: Comprehensive Note-Taking and Study Management Tool"""
    
    TEMPLATE_FIELDS = {
        "Cornell": ["Keywords/Cues (Left Column)", "Notes (Right Column)", "Summary (Bottom)"],
        "Frayer": ["Concept/Term", "Definition (What it is)", "Characteristics (Facts)", "Examples", "Non-Examples"],
        "MainIdea": ["Main Topic", "Core Idea/Thesis", "Supporting Detail 1", "Supporting Detail 2", "Supporting Detail 3"],
        "Polya": ["Step 1: Understand the Problem", "Step 2: Devise a Plan", "Step 3: Carry out the Plan", "Step 4: Look Back/Review"],
        "5W1H": ["What is the problem/subject?", "Why is it important?", "When did it happen/occur?", "Where is it applied?", "Who is involved?", "How does it work/How to solve it?"],
        "ConceptMap": ["Central Concept", "Related Concept 1", "Related Concept 2", "Linking Words (Concept 1 to 2)"],
        "KWLH": ["K: What I KNOW", "W: What I WANT to know", "L: What I LEARNED", "H: HOW I can learn more (Application)"],
        "SQ3R": ["Survey (Title, Headings)", "Question (Convert Headings to Questions)", "Read (Active Note-taking)", "Recite (Answer Questions)", "Review (Self-Test)"],
        "Timeline": ["Starting Event/Date", "Intermediate Event/Date 1", "Intermediate Event/Date 2", "Final Event/Outcome", "Notes on Significance"],
        "Feynman": ["Concept Name", "Explain in Simple Terms", "Identify Knowledge Gaps", "Simplify and Use Analogies"],
        "TwoColumn": ["Problem/Question", "Solution/Answer"],
        "Outline": ["Topic/Chapter", "Main Point 1", "Main Point 2", "Main Point 3", "Main Point 4", "Main Point 5", "Key Takeaways"],
        "QuickReview": ["Subject/Topic", "Key Concepts (Bullet Points)", "Important Formulas/Definitions", "Practice Problems/Examples", "Things to Remember for Exam"],
    }
    
    POMODORO_MODES = {
        "Work": 25 * 60,
        "Short Break": 5 * 60,
        "Long Break": 15 * 60
    }
    
    MOTIVATIONAL_QUOTES = [
        "The mind is not a vessel to be filled, but a fire to be kindled. - Plutarch",
        "Patience, persistence and perspiration make an unbeatable combination for success. - Napoleon Hill",
        "It's not that I'm so smart, it's just that I stay with problems longer. - Albert Einstein",
        "The best way to predict the future is to create it. - Peter Drucker",
        "The difference between ordinary and extraordinary is that little extra. - Jimmy Johnson",
        "Our greatest weakness lies in giving up. The most certain way to succeed is always to try just one more time. - Thomas Edison",
        "Discipline is the bridge between goals and accomplishment. - Jim Rohn",
        "The beautiful thing about learning is that no one can take it away from you. - B.B. King",
        "Education is the passport to the future, for tomorrow belongs to those who prepare for it today. - Malcolm X",
        "Learning is not attained by chance, it must be sought for with ardor and diligence. - Abigail Adams"
    ]
    
    def __init__(self, root):
        self.root = root
        self.root.title("CourseMate - Stay Organized, Think Smarter, Learn Deeper, and Solve Problems Better")
        self.root.geometry("1200x800")
        
        # Initialize data directory
        self.data_dir = Path("coursemate_data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Core data structures
        self.courses = {}
        self.scratchpad_content = ""
        self.todo_list = []
        self.study_sessions = []
        self.pomodoro_count = 0
        
        # Pomodoro state
        self.pomodoro_running = False
        self.pomodoro_mode = "Work"
        self.pomodoro_time_left = self.POMODORO_MODES["Work"]
        self.pomodoro_timer_id = None
        self.session_start_time = None
        
        # UI state
        self.is_focus_mode = False
        
        # Widget references
        self.quote_label = None
        self.pomodoro_time_label = None
        self.pomodoro_mode_label = None
        self.todo_listbox = None
        
        # Load data
        self._load_data()
        
        # Setup UI
        self._setup_styles()
        self._setup_layout()
        self.views = {}
        self.current_view = None
        
        self._create_widgets()
        self._create_content_frames()
        
        self.show_view("Dashboard")
        
        # Background tasks
        self.root.after(100, self._rotate_quote)
        self.root.after(60000, self._auto_save)
        
        # Keyboard shortcuts
        self._setup_keyboard_shortcuts()
        
        # Window close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _load_data(self):
        """Load all application data"""
        courses_file = self.data_dir / "courses.json"
        try:
            if courses_file.exists():
                with open(courses_file, 'r') as f:
                    self.courses = json.load(f)
            else:
                self.courses = {}
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load courses: {str(e)}")
            self.courses = {}
        
        scratchpad_file = self.data_dir / "scratchpad.txt"
        try:
            if scratchpad_file.exists():
                with open(scratchpad_file, 'r') as f:
                    self.scratchpad_content = f.read()
            else:
                self.scratchpad_content = "Welcome to CourseMate Pro! Start typing your quick notes here."
        except:
            self.scratchpad_content = "Welcome to CourseMate Pro!"
        
        todo_file = self.data_dir / "todo_list.json"
        try:
            if todo_file.exists():
                with open(todo_file, 'r') as f:
                    self.todo_list = json.load(f)
            else:
                self.todo_list = []
        except:
            self.todo_list = []
        
        sessions_file = self.data_dir / "study_sessions.json"
        try:
            if sessions_file.exists():
                with open(sessions_file, 'r') as f:
                    self.study_sessions = json.load(f)
            else:
                self.study_sessions = []
        except:
            self.study_sessions = []

    def _save_courses(self):
        """Save courses to JSON"""
        try:
            courses_file = self.data_dir / "courses.json"
            with open(courses_file, 'w') as f:
                json.dump(self.courses, f, indent=2)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save courses: {str(e)}")

    def _save_todolist(self):
        """Save todo list"""
        try:
            todo_file = self.data_dir / "todo_list.json"
            with open(todo_file, 'w') as f:
                json.dump(self.todo_list, f, indent=2)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save todo list: {str(e)}")

    def _save_scratchpad(self, content=None):
        """Save scratchpad"""
        try:
            if content:
                self.scratchpad_content = content
            scratchpad_file = self.data_dir / "scratchpad.txt"
            with open(scratchpad_file, 'w') as f:
                f.write(self.scratchpad_content)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save scratchpad: {str(e)}")

    def _save_study_sessions(self):
        """Save study sessions"""
        try:
            sessions_file = self.data_dir / "study_sessions.json"
            with open(sessions_file, 'w') as f:
                json.dump(self.study_sessions, f, indent=2)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save study sessions: {str(e)}")

    def _auto_save(self):
        """Auto-save periodically"""
        self._save_courses()
        self._save_todolist()
        self._save_study_sessions()
        self.root.after(60000, self._auto_save)

    def _on_closing(self):
        """Handle application closing"""
        if self.pomodoro_running:
            if messagebox.askyesno("Exit", "Pomodoro timer is running. Exit anyway?"):
                self._save_courses()
                self._save_todolist()
                self._save_scratchpad()
                self._save_study_sessions()
                self.root.destroy()
        else:
            self._save_courses()
            self._save_todolist()
            self._save_scratchpad()
            self._save_study_sessions()
            self.root.destroy()

    def add_new_course_dialog(self):
        """Add a new course"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Course")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Course Name:", font=('Helvetica', 10, 'bold')).pack(pady=(20, 5), padx=20, anchor='w')
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(pady=5, padx=20)
        name_entry.focus()
        
        ttk.Label(dialog, text="Course Code (optional):", font=('Helvetica', 10, 'bold')).pack(pady=(10, 5), padx=20, anchor='w')
        code_entry = ttk.Entry(dialog, width=40)
        code_entry.pack(pady=5, padx=20)
        
        ttk.Label(dialog, text="Instructor (optional):", font=('Helvetica', 10, 'bold')).pack(pady=(10, 5), padx=20, anchor='w')
        instructor_entry = ttk.Entry(dialog, width=40)
        instructor_entry.pack(pady=5, padx=20)
        
        def save_course():
            name = name_entry.get().strip()
            code = code_entry.get().strip()
            instructor = instructor_entry.get().strip()
            
            if not name:
                messagebox.showwarning("Input Error", "Course name is required!", parent=dialog)
                return
            
            if name in self.courses:
                messagebox.showerror("Error", f"Course '{name}' already exists!", parent=dialog)
                return
            
            self.courses[name] = {
                "code": code,
                "instructor": instructor,
                "tasks": [],
                "notes": [],
                "created_date": datetime.now().isoformat(),
                "total_study_time": 0
            }
            
            self._save_courses()
            messagebox.showinfo("Success", f"Course '{name}' added successfully!", parent=dialog)
            dialog.destroy()
            self.show_view("Courses")
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Add Course", command=save_course).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)
        
        dialog.bind('<Return>', lambda e: save_course())
        dialog.bind('<Escape>', lambda e: dialog.destroy())

    def delete_course(self, course_name):
        """Delete a course"""
        if messagebox.askyesno("Confirm Delete", 
                              f"Delete course '{course_name}' and all its notes?\nThis cannot be undone!"):
            del self.courses[course_name]
            self._save_courses()
            messagebox.showinfo("Deleted", f"Course '{course_name}' has been deleted.")
            self.show_view("Courses")

    def export_course_notes(self, course_name):
        """Export course notes"""
        if course_name not in self.courses:
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"{course_name}_notes.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(f"CourseMate Notes Export\n")
                    f.write(f"Course: {course_name}\n")
                    f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    
                    for i, note in enumerate(self.courses[course_name]['notes'], 1):
                        f.write(f"Note {i}: {note[0]}\n")
                        f.write("-" * 60 + "\n")
                        
                        if isinstance(note[1], dict):
                            for key, value in note[1].items():
                                f.write(f"\n{key}:\n{value}\n")
                        else:
                            f.write(f"\n{note[1]}\n")
                        
                        f.write("\n" + "=" * 60 + "\n\n")
                
                messagebox.showinfo("Success", f"Notes exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export notes: {str(e)}")

    def save_template_note(self, template_key, course_var, field_inputs):
        """Save template note"""
        course = course_var.get()
        if course == "Select Course":
            messagebox.showerror("Error", "Please select a course before saving.")
            return

        note_data = {}
        all_empty = True
        
        for label, widget in field_inputs.items():
            if isinstance(widget, tk.Text):
                content = widget.get("1.0", tk.END).strip()
            else:
                content = widget.get().strip()
            
            note_data[label] = content
            if content:
                all_empty = False
        
        if all_empty:
            messagebox.showwarning("Warning", "Note is empty. Nothing saved.")
            return
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        note_title = f"{template_key} Note - {timestamp}"
        note_content = (note_title, note_data)
        
        self.courses[course]['notes'].append(note_content)
        self._save_courses()
        
        messagebox.showinfo("Note Saved", f"{template_key} note saved to {course}!")
        self.show_view("Courses")

    def save_freeform_note(self, course_var, content_widget, title_widget=None):
        """Save freeform note"""
        course = course_var.get()
        content = content_widget.get("1.0", tk.END).strip()
        
        if course == "Select Course":
            messagebox.showerror("Error", "Please select a course before saving.")
            return
        
        if not content:
            messagebox.showwarning("Warning", "Note content is empty. Nothing saved.")
            return
        
        if title_widget:
            title = title_widget.get().strip()
            if not title:
                title = f"Freeform Note - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            title = f"Freeform Note - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.courses[course]['notes'].append((title, content))
        self._save_courses()
        
        messagebox.showinfo("Saved", f"Note saved to {course}!")
        
        content_widget.delete("1.0", tk.END)
        if title_widget:
            title_widget.delete(0, tk.END)

    def view_course_notes(self, course_name):
        """View all notes for a course"""
        if course_name not in self.courses:
            return
        
        notes_window = tk.Toplevel(self.root)
        notes_window.title(f"Notes: {course_name}")
        notes_window.geometry("900x700")
        
        header = ttk.Frame(notes_window)
        header.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(header, text=f"📚 {course_name} - All Notes", 
                 font=('Helvetica', 16, 'bold')).pack(side='left')
        
        ttk.Button(header, text="Export Notes", 
                  command=lambda: self.export_course_notes(course_name)).pack(side='right', padx=5)
        
        ttk.Button(header, text="Delete Selected", 
                  command=lambda: self.delete_selected_note(course_name, notes_listbox, notes_window)).pack(side='right', padx=5)
        
        list_frame = ttk.Frame(notes_window)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        notes_listbox = tk.Listbox(list_frame, font=('Helvetica', 11), 
                                   yscrollcommand=scrollbar.set, height=15)
        notes_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=notes_listbox.yview)
        
        for note in self.courses[course_name]['notes']:
            notes_listbox.insert(tk.END, note[0])
        
        preview_frame = ttk.LabelFrame(notes_window, text="Note Preview", padding=10)
        preview_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        preview_text = tk.Text(preview_frame, wrap='word', font=('Helvetica', 10))
        preview_text.pack(fill='both', expand=True)
        
        def show_note_preview(event):
            selection = notes_listbox.curselection()
            if selection:
                idx = selection[0]
                note = self.courses[course_name]['notes'][idx]
                preview_text.delete('1.0', tk.END)
                preview_text.insert('1.0', f"{note[0]}\n{'='*60}\n\n")
                
                if isinstance(note[1], dict):
                    for key, value in note[1].items():
                        preview_text.insert(tk.END, f"{key}:\n{value}\n\n")
                else:
                    preview_text.insert(tk.END, note[1])
        
        notes_listbox.bind('<<ListboxSelect>>', show_note_preview)

    def delete_selected_note(self, course_name, listbox, window):
        """Delete selected note"""
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a note to delete.")
            return
        
        idx = selection[0]
        note_title = self.courses[course_name]['notes'][idx][0]
        
        if messagebox.askyesno("Confirm Delete", f"Delete note:\n{note_title}?"):
            del self.courses[course_name]['notes'][idx]
            self._save_courses()
            window.destroy()
            self.view_course_notes(course_name)

    def add_todo_item(self):
        """Add todo item"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Task")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Task Description:", font=('Helvetica', 10, 'bold')).pack(pady=(20, 5), padx=20, anchor='w')
        task_entry = ttk.Entry(dialog, width=40)
        task_entry.pack(pady=5, padx=20)
        task_entry.focus()
        
        ttk.Label(dialog, text="Priority:", font=('Helvetica', 10, 'bold')).pack(pady=(10, 5), padx=20, anchor='w')
        priority_var = tk.StringVar(value="Medium")
        priority_frame = ttk.Frame(dialog)
        priority_frame.pack(pady=5, padx=20, anchor='w')
        
        for priority in ["High", "Medium", "Low"]:
            ttk.Radiobutton(priority_frame, text=priority, variable=priority_var, 
                          value=priority).pack(side='left', padx=5)
        
        def save_task():
            task = task_entry.get().strip()
            if not task:
                messagebox.showwarning("Input Error", "Task description is required!", parent=dialog)
                return
            
            priority = priority_var.get()
            todo_item = {
                "task": task,
                "priority": priority,
                "completed": False,
                "created_date": datetime.now().isoformat()
            }
            
            self.todo_list.append(todo_item)
            self._save_todolist()
            messagebox.showinfo("Success", "Task added!", parent=dialog)
            dialog.destroy()
            self.show_view("ToDoList")
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Add Task", command=save_task).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)
        
        dialog.bind('<Return>', lambda e: save_task())
        dialog.bind('<Escape>', lambda e: dialog.destroy())

    def remove_todo_item(self):
        """Remove todo item"""
        if self.todo_listbox and self.todo_listbox.curselection():
            index = self.todo_listbox.curselection()[0]
            del self.todo_list[index]
            self._save_todolist()
            self.show_view("ToDoList")
        else:
            messagebox.showwarning("Selection Error", "Please select a task to remove.")

    def toggle_todo_completion(self):
        """Toggle todo completion"""
        if self.todo_listbox and self.todo_listbox.curselection():
            index = self.todo_listbox.curselection()[0]
            self.todo_list[index]['completed'] = not self.todo_list[index].get('completed', False)
            self._save_todolist()
            self.show_view("ToDoList")

    def start_pomodoro(self):
        """Start pomodoro"""
        if not self.pomodoro_running:
            self.pomodoro_running = True
            if not self.session_start_time:
                self.session_start_time = datetime.now()
            self._update_pomodoro_timer()

    def pause_pomodoro(self):
        """Pause pomodoro"""
        if self.pomodoro_running and self.pomodoro_timer_id:
            self.pomodoro_running = False
            self.root.after_cancel(self.pomodoro_timer_id)

    def reset_pomodoro(self, mode=None):
        """Reset pomodoro"""
        self.pause_pomodoro()
        if mode:
            self.pomodoro_mode = mode
            self.pomodoro_time_left = self.POMODORO_MODES[mode]
        else:
            self.pomodoro_mode = "Work"
            self.pomodoro_time_left = self.POMODORO_MODES["Work"]
        
        self.session_start_time = None
        self._update_pomodoro_display()

    def _update_pomodoro_timer(self):
        """Update pomodoro timer"""
        if self.pomodoro_running and self.pomodoro_time_left > 0:
            self.pomodoro_time_left -= 1
            self._update_pomodoro_display()
            self.pomodoro_timer_id = self.root.after(1000, self._update_pomodoro_timer)
        elif self.pomodoro_time_left <= 0:
            self.pomodoro_running = False
            
            if self.pomodoro_mode == "Work" and self.session_start_time:
                session_duration = self.POMODORO_MODES["Work"]
                self.study_sessions.append({
                    "date": datetime.now().isoformat(),
                    "duration": session_duration,
                    "mode": "Pomodoro"
                })
                self._save_study_sessions()
                self.pomodoro_count += 1
            
            messagebox.showinfo("Pomodoro", f"{self.pomodoro_mode} session complete!")
            
            if self.pomodoro_mode == "Work":
                if self.pomodoro_count % 4 == 0:
                    self.reset_pomodoro("Long Break")
                else:
                    self.reset_pomodoro("Short Break")
            else:
                self.reset_pomodoro("Work")

    def _update_pomodoro_display(self):
        """Update pomodoro display"""
        minutes = int(self.pomodoro_time_left // 60)
        seconds = int(self.pomodoro_time_left % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        if self.pomodoro_time_label:
            self.pomodoro_time_label.config(text=time_str)
        if self.pomodoro_mode_label:
            self.pomodoro_mode_label.config(text=self.pomodoro_mode)

    def search_notes(self, query):
        """Search notes"""
        if not query.strip():
            messagebox.showinfo("Search", "Please enter a search term.")
            return
        
        results = []
        query_lower = query.lower()
        
        for course_name, course_data in self.courses.items():
            for note_title, note_content in course_data['notes']:
                if query_lower in note_title.lower():
                    results.append((course_name, note_title, "Title match"))
                    continue
                
                if isinstance(note_content, dict):
                    for key, value in note_content.items():
                        if query_lower in str(value).lower():
                            results.append((course_name, note_title, f"Found in {key}"))
                            break
                else:
                    if query_lower in str(note_content).lower():
                        results.append((course_name, note_title, "Content match"))
        
        self._display_search_results(query, results)

    def _display_search_results(self, query, results):
        """Display search results"""
        results_window = tk.Toplevel(self.root)
        results_window.title(f"Search Results: '{query}'")
        results_window.geometry("700x500")
        
        ttk.Label(results_window, text=f"Search Results for: '{query}'", 
                 font=('Helvetica', 14, 'bold')).pack(padx=20, pady=10)
        
        ttk.Label(results_window, text=f"Found {len(results)} result(s)", 
                 font=('Helvetica', 10)).pack(padx=20, pady=5)
        
        list_frame = ttk.Frame(results_window)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        results_tree = ttk.Treeview(list_frame, columns=('Course', 'Note', 'Match'), 
                                   show='headings', yscrollcommand=scrollbar.set)
        results_tree.heading('Course', text='Course')
        results_tree.heading('Note', text='Note Title')
        results_tree.heading('Match', text='Match Type')
        
        results_tree.column('Course', width=150)
        results_tree.column('Note', width=300)
        results_tree.column('Match', width=150)
        
        results_tree.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=results_tree.yview)
        
        for course, note_title, match_type in results:
            results_tree.insert('', 'end', values=(course, note_title, match_type))
        
        if not results:
            ttk.Label(results_window, text="No results found.", 
                     font=('Helvetica', 10, 'italic')).pack(pady=20)

    def show_statistics(self):
        """Show statistics"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Study Statistics")
        stats_window.geometry("700x600")
        
        ttk.Label(stats_window, text="📊 Your Study Statistics", 
                 font=('Helvetica', 18, 'bold')).pack(padx=30, pady=20)
        
        stats_frame = ttk.Frame(stats_window, padding=20)
        stats_frame.pack(fill='both', expand=True)
        
        total_courses = len(self.courses)
        total_notes = sum(len(c['notes']) for c in self.courses.values())
        total_tasks = sum(len(c['tasks']) for c in self.courses.values())
        completed_tasks = sum(1 for tasks in [c['tasks'] for c in self.courses.values()] 
                            for task in tasks if isinstance(task, dict) and task.get('completed'))
        
        total_study_minutes = sum(s['duration'] for s in self.study_sessions) // 60
        total_pomodoros = self.pomodoro_count
        
        stats = [
            ("Total Courses", total_courses),
            ("Total Notes Created", total_notes),
            ("Total Tasks", total_tasks),
            ("Completed Tasks", completed_tasks),
            ("Total Study Time", f"{total_study_minutes} minutes"),
            ("Pomodoro Sessions", total_pomodoros)
        ]
        
        for label, value in stats:
            stat_row = ttk.Frame(stats_frame)
            stat_row.pack(fill='x', pady=10)
            ttk.Label(stat_row, text=f"{label}:", 
                     font=('Helvetica', 12, 'bold')).pack(side='left')
            ttk.Label(stat_row, text=str(value), 
                     font=('Helvetica', 12)).pack(side='right')
        
        ttk.Separator(stats_frame, orient='horizontal').pack(fill='x', pady=20)
        ttk.Label(stats_frame, text="Recent Study Sessions", 
                 font=('Helvetica', 12, 'bold')).pack(pady=10)
        
        recent_sessions = self.study_sessions[-10:] if self.study_sessions else []
        if recent_sessions:
            for session in reversed(recent_sessions):
                date = datetime.fromisoformat(session['date']).strftime('%Y-%m-%d %H:%M')
                duration = session['duration'] // 60
                ttk.Label(stats_frame, text=f"• {date} - {duration} min ({session['mode']})",
                         font=('Helvetica', 9)).pack(anchor='w', padx=20)
        else:
            ttk.Label(stats_frame, text="No study sessions recorded yet.",
                     font=('Helvetica', 9, 'italic')).pack(pady=10)

    def _rotate_quote(self):
        """Rotate quotes"""
        if self.quote_label:
            new_quote = random.choice(self.MOTIVATIONAL_QUOTES)
            self.quote_label.config(text=new_quote)
        self.root.after(60000, self._rotate_quote)

    def toggle_focus_mode(self, event=None):
        """Toggle focus mode"""
        self.is_focus_mode = not self.is_focus_mode
        
        if self.is_focus_mode:
            self.header_frame.pack_forget()
            self.sidebar_frame.pack_forget()
            self.root.attributes('-fullscreen', True)
            messagebox.showinfo("Focus Mode", "Focus Mode ON. Press F11 to exit.")
        else:
            self.root.attributes('-fullscreen', False)
            self.header_frame.pack(fill='x', side='top')
            self.sidebar_frame.pack(fill='y', side='left')
            self.root.geometry("1200x800")

    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<Control-s>', self._quick_save)
        self.root.bind('<Command-s>', self._quick_save)
        self.root.bind('<F11>', self.toggle_focus_mode)
        self.root.bind('<Control-f>', lambda e: self._show_search_dialog())
        self.root.bind('<Control-n>', lambda e: self.add_new_course_dialog())
        self.root.bind('<Control-q>', lambda e: self._on_closing())

    def _quick_save(self, event=None):
        """Quick save"""
        focused = self.root.focus_get()
        if isinstance(focused, tk.Text):
            content = focused.get("1.0", tk.END).strip()
            if hasattr(focused, 'scratchpad_flag'):
                self._save_scratchpad(content)
                messagebox.showinfo("Saved", "Scratchpad saved!")
        return "break"

    def _show_search_dialog(self):
        """Show search dialog"""
        query = simpledialog.askstring("Search Notes", "Enter search term:", parent=self.root)
        if query:
            self.search_notes(query)

    def _setup_styles(self):
        """Setup styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TFrame', background='#f5f5f5')
        style.configure('Sidebar.TFrame', background='#2c3e50')
        style.configure('Card.TFrame', background='white', relief='solid', borderwidth=1)
        
        style.configure('Sidebar.TButton', background='#34495e', foreground='white', 
                       borderwidth=0, font=('Helvetica', 10))
        style.map('Sidebar.TButton', background=[('active', '#546a7e')])
        
        style.configure('Course.TButton', background='#27ae60', foreground='white',
                       font=('Helvetica', 10, 'bold'))
        style.map('Course.TButton', background=[('active', '#229954')])
        
        style.configure('Pomodoro.TLabel', font=('Helvetica', 48, 'bold'), 
                       foreground='#e74c3c', background='white')
        style.configure('Mode.TLabel', font=('Helvetica', 14, 'bold'), 
                       foreground='#34495e', background='white')

    def _setup_layout(self):
        """Setup layout"""
        self.header_frame = ttk.Frame(self.root, height=60, style='Sidebar.TFrame')
        self.header_frame.pack(fill='x', side='top')
        self.header_frame.pack_propagate(False)
        
        self.sidebar_frame = ttk.Frame(self.root, width=240, style='Sidebar.TFrame')
        self.sidebar_frame.pack(fill='y', side='left')
        self.sidebar_frame.pack_propagate(False)
        
        self.main_content = ttk.Frame(self.root, style='TFrame')
        self.main_content.pack(fill='both', side='right', expand=True)

    def _create_widgets(self):
        """Create widgets"""
        # Header with tagline
        header_container = ttk.Frame(self.header_frame, style='Sidebar.TFrame')
        header_container.pack(pady=8, padx=20, side='left', fill='both', expand=True)
        
        ttk.Label(header_container, text="CourseMate",
                 font=('Helvetica', 18, 'bold'), foreground='white', 
                 background='#2c3e50').pack(anchor='w')
        
        ttk.Label(header_container, text="Stay Organized • Think Smarter • Learn Deeper • Solve Problems Better",
                 font=('Helvetica', 9), foreground='#95a5a6', 
                 background='#2c3e50').pack(anchor='w')
        
        search_btn = ttk.Button(self.header_frame, text="🔍 Search", 
                               command=self._show_search_dialog)
        search_btn.pack(side='right', padx=20)
        
        # Updated navigation order
        nav_buttons = [
            ("📊 Dashboard", "Dashboard"),
            ("📚 My Courses", "Courses"),
            ("📝 Freeform Canvas", "FreeForm"),
            ("📖 Study Templates", "NonTech"),
            ("💡 Technical Templates", "Technical"),
            ("🍅 Pomodoro Timer", "Pomodoro"),
            ("✅ To-Do List", "ToDoList"),
            ("📈 Statistics", "Statistics"),
            ("⚙️ Settings", "Settings"),
        ]
        
        ttk.Label(self.sidebar_frame, text="NAVIGATION", 
                 font=('Helvetica', 9, 'bold'), foreground='#95a5a6',
                 background='#2c3e50').pack(pady=(20, 10), padx=20, anchor='w')
        
        for text, view in nav_buttons:
            btn = ttk.Button(self.sidebar_frame, text=text, style='Sidebar.TButton',
                           command=lambda v=view: self.show_view(v))
            btn.pack(fill='x', pady=3, padx=15)
        
        ttk.Separator(self.sidebar_frame, orient='horizontal').pack(fill='x', pady=15, padx=15)
        
        ttk.Label(self.sidebar_frame, text="QUICK ACTIONS", 
                 font=('Helvetica', 9, 'bold'), foreground='#95a5a6',
                 background='#2c3e50').pack(pady=(10, 10), padx=20, anchor='w')
        
        # Enhanced quick actions
        ttk.Button(self.sidebar_frame, text="+ Add New Course", style='Course.TButton',
                  command=self.add_new_course_dialog).pack(fill='x', pady=5, padx=15)
        
        ttk.Button(self.sidebar_frame, text="+ Quick Note", style='Sidebar.TButton',
                  command=self._quick_note_dialog).pack(fill='x', pady=3, padx=15)
        
        ttk.Button(self.sidebar_frame, text="+ Add Task", style='Sidebar.TButton',
                  command=self.add_todo_item).pack(fill='x', pady=3, padx=15)
        
        ttk.Button(self.sidebar_frame, text="⏱ Start Pomodoro", style='Sidebar.TButton',
                  command=self._quick_pomodoro).pack(fill='x', pady=3, padx=15)

    def _create_content_frames(self):
        """Create content frames"""
        view_names = ["Dashboard", "Courses", "Pomodoro", "ToDoList", "FreeForm",
                     "NonTech", "Technical", "TemplateForm", "Statistics", "Settings"]
        
        for name in view_names:
            self.views[name] = ttk.Frame(self.main_content, style='TFrame')
        
        self._setup_pomodoro(self.views["Pomodoro"])
        self._setup_non_tech_templates(self.views["NonTech"])
        self._setup_technical_templates(self.views["Technical"])

    def show_view(self, view_name):
        """Switch views"""
        if view_name == "Dashboard":
            self._setup_dashboard(self.views["Dashboard"])
        elif view_name == "Courses":
            self._setup_courses_list(self.views["Courses"])
        elif view_name == "ToDoList":
            self._setup_todolist(self.views["ToDoList"])
        elif view_name == "FreeForm":
            self._setup_freeform(self.views["FreeForm"])
        elif view_name == "Pomodoro":
            self._update_pomodoro_display()
        elif view_name == "Statistics":
            self.show_statistics()
            return
        elif view_name == "Settings":
            self._setup_settings(self.views["Settings"])
        
        if self.current_view:
            self.current_view.pack_forget()
        
        new_view = self.views.get(view_name)
        if new_view:
            new_view.pack(fill='both', expand=True)
            self.current_view = new_view

    def _setup_dashboard(self, parent):
        """Setup dashboard"""
        for widget in parent.winfo_children():
            widget.destroy()
        
        ttk.Label(parent, text="Dashboard Overview", 
                 font=('Helvetica', 24, 'bold')).pack(padx=30, pady=20, anchor='nw')
        
        cards_frame = ttk.Frame(parent, style='TFrame')
        cards_frame.pack(fill='x', padx=30, pady=10)
        
        num_courses = len(self.courses)
        total_notes = sum(len(c['notes']) for c in self.courses.values())
        total_tasks = sum(len(c['tasks']) for c in self.courses.values())
        study_time = sum(s['duration'] for s in self.study_sessions) // 60
        
        self._create_stat_card(cards_frame, "Courses", num_courses, "#3498db").pack(
            side='left', padx=10, fill='x', expand=True)
        self._create_stat_card(cards_frame, "Notes", total_notes, "#2ecc71").pack(
            side='left', padx=10, fill='x', expand=True)
        self._create_stat_card(cards_frame, "Tasks", total_tasks, "#e74c3c").pack(
            side='left', padx=10, fill='x', expand=True)
        self._create_stat_card(cards_frame, "Study Time (min)", study_time, "#f39c12").pack(
            side='left', padx=10, fill='x', expand=True)
        
        bottom_frame = ttk.Frame(parent, style='TFrame')
        bottom_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        left_frame = ttk.Frame(bottom_frame, style='TFrame')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tasks_card = ttk.Frame(left_frame, style='Card.TFrame', padding=15)
        tasks_card.pack(fill='x', pady=(0, 10))
        
        ttk.Label(tasks_card, text="📋 Recent Tasks", 
                 font=('Helvetica', 12, 'bold'), background='white').pack(anchor='w')
        
        recent_tasks = [item for item in self.todo_list if not item.get('completed', False)][:5]
        if recent_tasks:
            for task in recent_tasks:
                task_text = task.get('task', task) if isinstance(task, dict) else task
                priority = task.get('priority', 'Medium') if isinstance(task, dict) else 'Medium'
                color = {'High': '#e74c3c', 'Medium': '#f39c12', 'Low': '#95a5a6'}.get(priority, '#95a5a6')
                
                task_frame = ttk.Frame(tasks_card, style='TFrame')
                task_frame.pack(fill='x', pady=3)
                
                ttk.Label(task_frame, text="•", foreground=color, 
                         background='white', font=('Helvetica', 12, 'bold')).pack(side='left')
                ttk.Label(task_frame, text=task_text[:50], 
                         background='white').pack(side='left', padx=5)
        else:
            ttk.Label(tasks_card, text="No pending tasks!", 
                     background='white', foreground='#95a5a6').pack(pady=10)
        
        quote_card = ttk.Frame(left_frame, style='Card.TFrame', padding=15)
        quote_card.pack(fill='both', expand=True)
        
        ttk.Label(quote_card, text="💡 Daily Inspiration", 
                 font=('Helvetica', 12, 'bold'), background='white').pack(anchor='w')
        
        self.quote_label = ttk.Label(quote_card, text="", wraplength=400,
                                     font=('Helvetica', 10, 'italic'),
                                     foreground='#2c3e50', background='white')
        self.quote_label.pack(fill='x', pady=10)
        self._rotate_quote()
        
        scratchpad_card = ttk.Frame(bottom_frame, style='Card.TFrame', padding=15)
        scratchpad_card.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        ttk.Label(scratchpad_card, text="📝 Quick Notes", 
                 font=('Helvetica', 12, 'bold'), background='white').pack(anchor='w')
        
        scratchpad_text = tk.Text(scratchpad_card, wrap='word', 
                                 font=('Helvetica', 10), height=20)
        scratchpad_text.pack(fill='both', expand=True, pady=10)
        scratchpad_text.insert('1.0', self.scratchpad_content)
        scratchpad_text.scratchpad_flag = True
        
        ttk.Button(scratchpad_card, text="💾 Save (Ctrl+S)",
                  command=lambda: self._save_scratchpad(
                      scratchpad_text.get("1.0", tk.END).strip())).pack()

    def _setup_courses_list(self, parent):
        """Setup courses list"""
        for widget in parent.winfo_children():
            widget.destroy()
        
        ttk.Label(parent, text="My Courses", 
                 font=('Helvetica', 24, 'bold')).pack(padx=30, pady=20, anchor='nw')
        
        if not self.courses:
            empty_frame = ttk.Frame(parent, style='Card.TFrame', padding=40)
            empty_frame.pack(fill='both', expand=True, padx=30, pady=20)
            
            ttk.Label(empty_frame, text="📚 No courses yet!", 
                     font=('Helvetica', 16), background='white').pack(pady=20)
            ttk.Label(empty_frame, text="Click '+ Add New Course' to get started",
                     font=('Helvetica', 11), background='white', 
                     foreground='#7f8c8d').pack()
            ttk.Button(empty_frame, text="Add Your First Course",
                      command=self.add_new_course_dialog).pack(pady=20)
        else:
            for name, details in self.courses.items():
                course_card = ttk.Frame(parent, style='Card.TFrame', padding=15)
                course_card.pack(fill='x', padx=30, pady=8)
                
                header_frame = ttk.Frame(course_card, style='TFrame')
                header_frame.pack(fill='x')
                
                ttk.Label(header_frame, text=name, font=('Helvetica', 14, 'bold'),
                         background='white').pack(side='left')
                
                if details.get('code'):
                    ttk.Label(header_frame, text=f"[{details['code']}]",
                             font=('Helvetica', 10), background='white',
                             foreground='#7f8c8d').pack(side='left', padx=10)
                
                info_frame = ttk.Frame(course_card, style='TFrame')
                info_frame.pack(fill='x', pady=5)
                
                ttk.Label(info_frame, text=f"📝 {len(details['notes'])} Notes",
                         background='white').pack(side='left', padx=10)
                ttk.Label(info_frame, text=f"📋 {len(details['tasks'])} Tasks",
                         background='white').pack(side='left', padx=10)
                
                if details.get('instructor'):
                    ttk.Label(info_frame, text=f"👤 {details['instructor']}",
                             background='white').pack(side='left', padx=10)
                
                actions_frame = ttk.Frame(course_card, style='TFrame')
                actions_frame.pack(fill='x', pady=5)
                
                ttk.Button(actions_frame, text="📖 View Notes",
                          command=lambda n=name: self.view_course_notes(n)).pack(side='left', padx=5)
                ttk.Button(actions_frame, text="📤 Export",
                          command=lambda n=name: self.export_course_notes(n)).pack(side='left', padx=5)
                ttk.Button(actions_frame, text="🗑️ Delete",
                          command=lambda n=name: self.delete_course(n)).pack(side='right', padx=5)

    def _setup_todolist(self, parent):
        """Setup todolist"""
        for widget in parent.winfo_children():
            widget.destroy()
        
        ttk.Label(parent, text="To-Do List", 
                 font=('Helvetica', 24, 'bold')).pack(padx=30, pady=20, anchor='nw')
        
        list_card = ttk.Frame(parent, style='Card.TFrame', padding=20)
        list_card.pack(fill='both', expand=True, padx=30, pady=10)
        
        btn_frame = ttk.Frame(list_card, style='TFrame')
        btn_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(btn_frame, text="+ Add Task", 
                  command=self.add_todo_item).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="✓ Toggle Complete",
                  command=self.toggle_todo_completion).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🗑️ Remove",
                  command=self.remove_todo_item).pack(side='left', padx=5)
        
        list_frame = ttk.Frame(list_card, style='TFrame')
        list_frame.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.todo_listbox = tk.Listbox(list_frame, font=('Helvetica', 11),
                                       yscrollcommand=scrollbar.set, height=20)
        self.todo_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.todo_listbox.yview)
        
        for item in self.todo_list:
            if isinstance(item, dict):
                task = item.get('task', '')
                priority = item.get('priority', 'Medium')
                completed = item.get('completed', False)
                prefix = "✓" if completed else "○"
                display_text = f"{prefix} [{priority}] {task}"
            else:
                display_text = f"○ {item}"
            
            self.todo_listbox.insert(tk.END, display_text)

    def _setup_freeform(self, parent):
        """Setup freeform"""
        for widget in parent.winfo_children():
            widget.destroy()
        
        ttk.Label(parent, text="Freeform Writing Canvas", 
                 font=('Helvetica', 24, 'bold')).pack(padx=30, pady=20, anchor='nw')
        
        form_card = ttk.Frame(parent, style='Card.TFrame', padding=20)
        form_card.pack(fill='both', expand=True, padx=30, pady=10)
        
        top_frame = ttk.Frame(form_card, style='TFrame')
        top_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(top_frame, text="Course:", background='white').pack(side='left', padx=5)
        
        course_var = tk.StringVar(value="Select Course")
        courses = ["Select Course"] + list(self.courses.keys())
        course_menu = ttk.OptionMenu(top_frame, course_var, courses[0], *courses)
        course_menu.pack(side='left', padx=5)
        
        ttk.Label(top_frame, text="Title:", background='white').pack(side='left', padx=(20, 5))
        title_entry = ttk.Entry(top_frame, width=40)
        title_entry.pack(side='left', padx=5)
        
        content_text = tk.Text(form_card, wrap='word', font=('Helvetica', 11),
                              undo=True, height=25)
        content_text.pack(fill='both', expand=True, pady=10)
        
        ttk.Button(form_card, text="💾 Save Note",
                  command=lambda: self.save_freeform_note(course_var, content_text, title_entry)
                  ).pack(pady=10)

    def _setup_pomodoro(self, parent):
        """Setup pomodoro"""
        for widget in parent.winfo_children():
            widget.destroy()
        
        ttk.Label(parent, text="Pomodoro Timer", 
                 font=('Helvetica', 24, 'bold')).pack(padx=30, pady=20, anchor='nw')
        
        timer_card = ttk.Frame(parent, style='Card.TFrame', padding=40)
        timer_card.pack(pady=50)
        
        self.pomodoro_mode_label = ttk.Label(timer_card, text=self.pomodoro_mode,
                                             style='Mode.TLabel', background='white')
        self.pomodoro_mode_label.pack(pady=10)
        
        self.pomodoro_time_label = ttk.Label(timer_card, text="25:00",
                                             style='Pomodoro.TLabel', background='white')
        self.pomodoro_time_label.pack(pady=20)
        
        controls = ttk.Frame(timer_card, style='TFrame')
        controls.pack(pady=20)
        
        ttk.Button(controls, text="▶ Start", 
                  command=self.start_pomodoro).pack(side='left', padx=10)
        ttk.Button(controls, text="⏸ Pause",
                  command=self.pause_pomodoro).pack(side='left', padx=10)
        ttk.Button(controls, text="⏹ Reset",
                  command=self.reset_pomodoro).pack(side='left', padx=10)
        
        modes = ttk.Frame(timer_card, style='TFrame')
        modes.pack(pady=10)
        
        ttk.Button(modes, text="Work (25m)",
                  command=lambda: self.reset_pomodoro("Work")).pack(side='left', padx=5)
        ttk.Button(modes, text="Short Break (5m)",
                  command=lambda: self.reset_pomodoro("Short Break")).pack(side='left', padx=5)
        ttk.Button(modes, text="Long Break (15m)",
                  command=lambda: self.reset_pomodoro("Long Break")).pack(side='left', padx=5)
        
        self._update_pomodoro_display()

    def _quick_note_dialog(self):
        """Quick note creation dialog"""
        if not self.courses:
            messagebox.showinfo("No Courses", "Please add a course first!")
            self.add_new_course_dialog()
            return
        
        self.show_view("FreeForm")
    
    def _quick_pomodoro(self):
        """Quick start pomodoro"""
        self.show_view("Pomodoro")
        self.start_pomodoro()

    def _setup_non_tech_templates(self, parent):
        """Setup non-tech templates with scrollbar"""
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Header
        header_frame = ttk.Frame(parent, style='TFrame')
        header_frame.pack(fill='x', padx=30, pady=20)
        
        ttk.Label(header_frame, text="Study Templates", 
                 font=('Helvetica', 24, 'bold')).pack(anchor='w')
        
        ttk.Label(header_frame, text="Structured note-taking methods for effective learning",
                 font=('Helvetica', 11), foreground='#7f8c8d').pack(anchor='w', pady=(5, 0))
        
        # Scrollable container
        canvas_frame = ttk.Frame(parent, style='TFrame')
        canvas_frame.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        
        canvas = tk.Canvas(canvas_frame, background='#f5f5f5', borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='TFrame')
        
        scrollable_frame.bind('<Configure>', 
                             lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        templates = [
            ("Cornell Notes", "Cornell", "Two-column system with cues and summary section"),
            ("Frayer Model", "Frayer", "Vocabulary and concept organizer with examples"),
            ("Main Idea & Details", "MainIdea", "Topic breakdown with supporting details"),
            ("Outline Notes", "Outline", "Structured bullet-point format for organized notes"),
            ("Quick Review Sheet", "QuickReview", "Fast review format perfect for exam preparation"),
            ("K-W-L-H Method", "KWLH", "Know, Want to know, Learned, How to learn more"),
            ("SQ3R Reading", "SQ3R", "Survey, Question, Read, Recite, Review strategy"),
            ("Timeline Mapping", "Timeline", "Chronological event tracking and analysis"),
        ]
        
        for name, key, desc in templates:
            card = ttk.Frame(scrollable_frame, style='Card.TFrame', padding=15)
            card.pack(fill='x', pady=8, padx=10)
            
            ttk.Label(card, text=name, font=('Helvetica', 13, 'bold'),
                     background='white').pack(anchor='w')
            ttk.Label(card, text=desc, font=('Helvetica', 10),
                     background='white', foreground='#7f8c8d', wraplength=700).pack(anchor='w', pady=5)
            
            ttk.Button(card, text="Use Template →",
                      command=lambda k=key: self.open_template(k)).pack(anchor='e')

    def _setup_technical_templates(self, parent):
        """Setup technical templates with scrollbar"""
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Header
        header_frame = ttk.Frame(parent, style='TFrame')
        header_frame.pack(fill='x', padx=30, pady=20)
        
        ttk.Label(header_frame, text="Technical Templates", 
                 font=('Helvetica', 24, 'bold')).pack(anchor='w')
        
        ttk.Label(header_frame, text="Problem-solving and analytical frameworks",
                 font=('Helvetica', 11), foreground='#7f8c8d').pack(anchor='w', pady=(5, 0))
        
        # Scrollable container
        canvas_frame = ttk.Frame(parent, style='TFrame')
        canvas_frame.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        
        canvas = tk.Canvas(canvas_frame, background='#f5f5f5', borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='TFrame')
        
        scrollable_frame.bind('<Configure>', 
                             lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        templates = [
            ("Polya's 4 Steps", "Polya", "Systematic problem-solving methodology"),
            ("5W1H Analysis", "5W1H", "What, Why, When, Where, Who, How framework"),
            ("Concept Mapping", "ConceptMap", "Visual relationship and connection builder"),
            ("Feynman Technique", "Feynman", "Explain concepts in simple terms to master them"),
            ("Two-Column Notes", "TwoColumn", "Problem and solution paired format"),
        ]
        
        for name, key, desc in templates:
            card = ttk.Frame(scrollable_frame, style='Card.TFrame', padding=15)
            card.pack(fill='x', pady=8, padx=10)
            
            ttk.Label(card, text=name, font=('Helvetica', 13, 'bold'),
                     background='white').pack(anchor='w')
            ttk.Label(card, text=desc, font=('Helvetica', 10),
                     background='white', foreground='#7f8c8d', wraplength=700).pack(anchor='w', pady=5)
            
            ttk.Button(card, text="Use Template →",
                      command=lambda k=key: self.open_template(k)).pack(anchor='e')

    def open_template(self, template_key):
        """Open template"""
        self._setup_template_form(self.views["TemplateForm"], template_key)
        self.show_view("TemplateForm")

    def _setup_template_form(self, parent, template_key):
        """Setup template form"""
        for widget in parent.winfo_children():
            widget.destroy()
        
        ttk.Label(parent, text=f"{template_key} Template",
                 font=('Helvetica', 24, 'bold')).pack(padx=30, pady=20, anchor='nw')
        
        top_frame = ttk.Frame(parent, style='TFrame')
        top_frame.pack(fill='x', padx=30, pady=(0, 10))
        
        ttk.Label(top_frame, text="Course:").pack(side='left', padx=5)
        
        course_var = tk.StringVar(value="Select Course")
        courses = ["Select Course"] + list(self.courses.keys())
        course_menu = ttk.OptionMenu(top_frame, course_var, courses[0], *courses)
        course_menu.pack(side='left', padx=5)
        
        ttk.Button(top_frame, text="← Back",
                  command=lambda: self.show_view("NonTech" if template_key in 
                                ["Cornell", "Frayer", "MainIdea", "KWLH", "SQ3R", "Timeline", "Outline", "QuickReview"] 
                                else "Technical")).pack(side='right', padx=5)
        
        canvas_frame = ttk.Frame(parent, style='TFrame')
        canvas_frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        canvas = tk.Canvas(canvas_frame, background='#f5f5f5', borderwidth=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', command=canvas.yview)
        form_frame = ttk.Frame(canvas, style='TFrame')
        
        form_frame.bind('<Configure>', 
                       lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        
        canvas.create_window((0, 0), window=form_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        field_inputs = {}
        fields = self.TEMPLATE_FIELDS.get(template_key, [])
        
        for field_label in fields:
            field_card = ttk.Frame(form_frame, style='Card.TFrame', padding=15)
            field_card.pack(fill='x', pady=8, padx=10)
            
            ttk.Label(field_card, text=field_label, font=('Helvetica', 11, 'bold'),
                     background='white').pack(anchor='w', pady=(0, 5))
            
            needs_text = any(keyword in field_label.lower() 
                           for keyword in ['detail', 'notes', 'summary', 'step', 
                                         'explain', 'solution', 'answer', 'point', 'concepts',
                                         'formulas', 'examples', 'takeaways', 'remember'])
            
            if needs_text or template_key in ["Polya", "5W1H", "SQ3R", "Feynman", "Outline", "QuickReview"]:
                widget = tk.Text(field_card, height=5, wrap='word', 
                               font=('Helvetica', 10))
                widget.pack(fill='x', expand=True)
            else:
                widget = ttk.Entry(field_card, font=('Helvetica', 10))
                widget.pack(fill='x', expand=True)
            
            field_inputs[field_label] = widget
        
        save_frame = ttk.Frame(parent, style='TFrame')
        save_frame.pack(fill='x', padx=30, pady=10)
        
        ttk.Button(save_frame, text="💾 Save Note",
                  command=lambda: self.save_template_note(template_key, course_var, field_inputs)
                  ).pack(side='left', padx=5)

    def _setup_settings(self, parent):
        """Setup settings"""
        for widget in parent.winfo_children():
            widget.destroy()
        
        ttk.Label(parent, text="Settings", 
                 font=('Helvetica', 24, 'bold')).pack(padx=30, pady=20, anchor='nw')
        
        focus_card = ttk.Frame(parent, style='Card.TFrame', padding=20)
        focus_card.pack(fill='x', padx=30, pady=10)
        
        ttk.Label(focus_card, text="🎯 Focus Mode", 
                 font=('Helvetica', 14, 'bold'), background='white').pack(anchor='w')
        ttk.Label(focus_card, text="Hide UI elements for distraction-free work",
                 background='white', foreground='#7f8c8d').pack(anchor='w', pady=5)
        
        status = "ON" if self.is_focus_mode else "OFF"
        ttk.Button(focus_card, text=f"Toggle Focus Mode (Currently: {status})",
                  command=self.toggle_focus_mode).pack(anchor='w', pady=10)
        
        ttk.Label(focus_card, text="Tip: Press F11 to quickly toggle",
                 font=('Helvetica', 9), background='white', 
                 foreground='#95a5a6').pack(anchor='w')
        
        data_card = ttk.Frame(parent, style='Card.TFrame', padding=20)
        data_card.pack(fill='x', padx=30, pady=10)
        
        ttk.Label(data_card, text="💾 Data Management", 
                 font=('Helvetica', 14, 'bold'), background='white').pack(anchor='w')
        ttk.Label(data_card, text="Backup and manage your study data",
                 background='white', foreground='#7f8c8d').pack(anchor='w', pady=5)
        
        ttk.Button(data_card, text="📦 Export All Data",
                  command=self._export_all_data).pack(anchor='w', pady=5)
        ttk.Button(data_card, text="📂 Open Data Folder",
                  command=self._open_data_folder).pack(anchor='w', pady=5)
        
        shortcuts_card = ttk.Frame(parent, style='Card.TFrame', padding=20)
        shortcuts_card.pack(fill='x', padx=30, pady=10)
        
        ttk.Label(shortcuts_card, text="⌨️ Keyboard Shortcuts", 
                 font=('Helvetica', 14, 'bold'), background='white').pack(anchor='w')
        
        shortcuts = [
            ("Ctrl+S", "Quick save"),
            ("Ctrl+F", "Search notes"),
            ("Ctrl+N", "Add new course"),
            ("F11", "Toggle focus mode"),
            ("Ctrl+Q", "Quit application")
        ]
        
        for key, action in shortcuts:
            shortcut_frame = ttk.Frame(shortcuts_card, style='TFrame')
            shortcut_frame.pack(fill='x', pady=3)
            
            ttk.Label(shortcut_frame, text=key, font=('Courier', 10, 'bold'),
                     background='white', foreground='#3498db').pack(side='left', padx=10)
            ttk.Label(shortcut_frame, text=action, background='white').pack(side='left')
        
        about_card = ttk.Frame(parent, style='Card.TFrame', padding=20)
        about_card.pack(fill='x', padx=30, pady=10)
        
        ttk.Label(about_card, text="ℹ️ About CourseMate Pro", 
                 font=('Helvetica', 14, 'bold'), background='white').pack(anchor='w')
        ttk.Label(about_card, text="Enhanced study and note-taking tool\nVersion 2.0",
                 background='white', foreground='#7f8c8d').pack(anchor='w', pady=5)

    def _export_all_data(self):
        """Export all data"""
        try:
            import shutil
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = filedialog.asksaveasfilename(
                defaultextension=".zip",
                filetypes=[("ZIP files", "*.zip")],
                initialfile=f"coursemate_backup_{timestamp}.zip"
            )
            
            if filename:
                base_name = filename.replace('.zip', '')
                shutil.make_archive(base_name, 'zip', self.data_dir)
                messagebox.showinfo("Success", f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")

    def _open_data_folder(self):
        """Open data folder"""
        try:
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(self.data_dir)
            elif platform.system() == 'Darwin':
                subprocess.Popen(['open', self.data_dir])
            else:
                subprocess.Popen(['xdg-open', self.data_dir])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {str(e)}")

    def _create_stat_card(self, parent, label, value, color):
        """Create stat card"""
        card = ttk.Frame(parent, style='Card.TFrame', padding=15)
        
        ttk.Label(card, text=str(value), font=('Helvetica', 28, 'bold'),
                 foreground=color, background='white').pack()
        ttk.Label(card, text=label, font=('Helvetica', 11),
                 foreground='#7f8c8d', background='white').pack()
        
        return card


if __name__ == "__main__":
    root = tk.Tk()
    app = CourseMateApp(root)
    root.mainloop()