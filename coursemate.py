import tkinter as tk
from tkinter import ttk
import json
from datetime import datetime
from pathlib import Path


class CourseMateApp:
    #Part 1: Initialization
    def __init__(self, root):
        self.root = root
        self.root.title("CourseMate - think smarter, learn deeper, and solve problems better.")
        self.root.geometry("1100x700")


        #Data: Store everything here
        self.courses = {}
        self.tasks = []
        self.completed_tasks = []


        #Load data: Get saved data from file
        self.data_file = Path("coursemate_data.json")
        self._load_data()


        #Create UI: Build interface
        self._setup_styles()
        self._create_layout()
        self._create_sidebar()


        #Start: Show dashboard first
        self.show_dashboard()


   
    #Part 2: Data Storage (JSON)
    def _load_data(self):
        """
        Load data from JSON file.


        JSON is just a text file thats stores data like:
        {
            "courses": {"Math": {"notes": [], "tasks": []}},
            "tasks": ["Do Homework", "Study"]
        }
        """
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.courses = data.get("courses", {})
                    self.tasks = data.get("tasks", [])
                    self.completed_tasks = data.get("completed_tasks", [])
                print(f"📁 Loaded {len(self.courses)} courses")
            else:
                print("📁 No saved data, starting fresh.")
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            self.courses = {}
            self.tasks = []
    def _save_data(self):
        """
        Save data to JSON file.
        Called automatically on change!
        """
        try:
            data = {
                "courses": self.courses,
                "tasks": self.tasks,
                "completed_tasks": self.completed_tasks
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2) #write to file
            print("💾 Data saved automatically.")
        except Exception as e:
            print(f"❌ Error saving: {e}")
            tk.messagebox.showerror("Save Error", f"Could not save data: {e}")
   


   
    #Part 3: UI Setup
    def _setup_styles(self):
        """Set up colors and styling"""
        style = ttk.Style()
        style.theme_use('clam')


        #colors
        style.configure('TFrame', background= '#f5f5f5')
        style.configure('TLabel', background= '#2c3e50')
        style.configure('TButton', background= 'white', relief= 'solid', borderwidth= 1)


        #Buttons
        style.configure('Sidebar.TButton', background= '#34495e', foreground= 'white',
                        borderwidth=0, font=('Helvetica', 10))
        style.map('Sidebar.TButton', background=[('active', '#546a7e')])


    def _create_layout(self):
        """Create main Layout: sidebar on left, content on right"""


        # Sidebar (navigation)
        self.sidebar = ttk.Frame(self.root, width=220, style='Sidebar.TFrame')
        self.sidebar.pack(fill='y', side='left')
        self.sidebar.pack_propagate(False)


        # Main content area
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
                 bg='#2c3e50', fg='#95a5a6').pack(pady=(30,10), padx=20, anchor='w')
       
        # Main Navigation Button
        main_nav = [
            ("📊 Dashboard", self.show_dashboard),
            ("📝 Freeform Courses", self.show_freeform),
        ]


        for text, command in main_nav:
            btn = ttk.Button(self.sidebar, text=text, style='Sidebar.TButton', command=command)
            btn.pack(fill='x', pady=3, padx=15)


        # Non-Technical Template Section
        tk.Label(self.sidebar, text="NON-TECHNICAL TEMPLATES",
                 font=('Helvetica', 8, 'bold'),
                 bg='#2c3e50', fg='#95a5a6').pack(pady=(15,5), padx=20, anchor='w')
       
        non_tech_templates = [
            ("Cornell Notes", "Cornell"),
            ("Main Idea & Details", "Mainidea"),
            ("Frayer Model", "Frayer"),
        ]


        for text, template_key in non_tech_templates:
            btn = ttk.Button(self.sidebar, text=text, style='Sidebar.TButton',
                             command=lambda key=template_key: self.open_template(key))
            btn.pack(fill='x', pady=2, padx=15)


        # Technical Template Sectiong
        tk.Label(self.sidebar, text="TECHNICAL TEMPLATES",
                 font=('Helvetica', 8, 'bold'),
                    bg='#2c3e50', fg='#95a5a6').pack(pady=(15,5), padx=20, anchor='w')
       
        tech_templates = [
            ("Polya's 4 steps", "Polya"),
            ("5W1H Analysis", "5W1H"),
            ("Concept Map", "ConceptMap"),
        ]


        for text, template_key in tech_templates:
            btn = ttk.Button(self.sidebar, text=text, style='Sidebar.TButton',
                             command=lambda key=template_key: self.open_template(key))
            btn.pack(fill='x', pady=2, padx=15)


        # Quick Action Section
        tk.Label(self.sidebar, text="QUICK ACTIONS",
                 font=('Helvetica', 9, 'bold'),
                 bg='#2c3e50', fg='#95a5a6').pack(pady=(20,10), padx=20, anchor='w')
       
        tk.Button(self.sidebar, text="➕ Add Course",
                  command=self.add_course,
                  bg='#27ae60', fg='white',
                  relief='flat', font=('Helvetica', 9, 'bold')).pack(fill='x', padx=15, pady=3)


        tk.Button(self.sidebar, text="➕ Add Task",
                  command=self.add_task,
                  bg='#3498db', fg='white',
                  relief='flat', font=('Helvetica', 9, 'bold')).pack(fill='x', padx=15, pady=3)






    #Part 4:Course Management
    def add_course(self):
        pass
    def delete_course(self, name):
        pass
    def view_course(self, course_name):
        pass
    def _display_note_card_in_frame(self, parent_frame, course_name, note_index, note):
        pass
    def delete_note(self, course_name, note_index):
        pass
    def view_full_note(self, note):
        pass
    def show_task_history(self):
        pass
    def _restore_task_and_refresh(self, index):
        pass
    def _delete_completed_from_dashboard(self, index):
        pass


    #Part 5: Task Management
    def add_task(self):
        pass
    def delete_task(self, indeX):
        pass
    def restore_task(self, index):
        pass
    def permanently_delete_task(self, index):
        pass


    #Part 6: Views
    def _clear_content(self):
        """Helper: Clear the main content area"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
       
    def show_dashboard(self):
        """
        DASHBOARD VIEW
        Shows: Course list + Task list side by side]
        """
        self._clear_content(self):
    #Title
    tk.Label(self.main_content, text="📊 Dashboard",
             font=('Helvetica', 24, 'bold')
             bg='#f5f5f5').pack(pady=20, anchor='w', padx=30)
   
    #ito yung dalawang container columns
   
    #Con
   
    def show_freeform(self):
        pass
    def show_technical(self):
        pass
    def show_nontechnical(self):
        pass


    #Part 7: Template
    def open_template(self, template_key):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = CourseMateApp(root)
    root.mainloop()

