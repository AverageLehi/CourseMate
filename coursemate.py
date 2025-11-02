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
   
    #ito yung dalawang container columns\
    container = ttk.Frame(self.main_content)
    container.pack(fill='both', expand=True, padx=30, pady=10)

    # LEFT: Course list
    course_frame = ttk.Frame(container, style='Card.TFrame', padding=15)
    course_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
    
    tk.Label(course_frame, text="📚 My Courses",
             font=('Helvetica', 14, 'bold'),
             bg='white', justify='left').pack(pady=(0, 10))
    if not self.courses:
        tk.Label(course_frame, text="No courses yet.\nClick '+ Add Course' to start!",
                 font=('Helvetica', 10), fg='#95a5a6',
                 bg='white', justify='left').pack(pady=20)
    
    else:
        for name, data in self.courses.items():
            course_row = ttk.Frame(course_frame)
            course_row.pack(fill='x', pady=5)

            # Make course name clickable
            course_btn = tk.Button(course_row, text=f"📚 {name}",
                                   font=('Helvetics', 11, 'bold'),
                                   bg='white', fg='#2c3e50',
                                   relief='flat', anchor='w'
                                   command=lambda n=name: self.view_course(n))
            course_btn.pack(side='left', fill='x', expand=True)

            tk.Label(course_row, text=f"({len(data['note'])} notes)",
                     font=('Helvetica', 98)).pack(side='right')
            course_btn.pack(side='left', fill='x', expand=True)

            tk.Label(course_row, text=f"({len(data['notes'])} notes)"
                     font=('Helvetica', 9), fg='#7f8c8d',
                     bg='white').pack(side='left', padx=5)
            
            tk.Button(course_row, text="🗑️",
                      command=lambda n=name: self.delete_course(n),
                      relief='flat', bg='white',
                      font=('Helvetica', 8)).pack(side='right')
            
    task_frame = ttk.Frame(container, style='card.TFrame', padding=15)
    task_frame.pack(side='right',fill='both',expand=True, padx=(10, 0))

#active tasks section
active_header = ttk.Frame(container, style='Card.TFrame', padding=15)
active_header.pack(side='right', fill='both'expand=True, padx=(10, 0))

tk.Label(active_header,text="✅ Quick Tasks",
         font=('Helvetica', 14, 'bold'),
         bg='white').pack(side='left')

tk.Button(active_header,text="+ Add",
          command=self.add_task,
          bg="#3498db", fg='white',
          relief='flat', font=('Helvetica', 8, 'bold')).pack(side='right')

#Active tasks list
if not self.tasks:
    tk.Label(tasks_frame, text="No active tasks",
             font=('Helvetica', 10), fg='#95a5a6',
             bg='white').pack(padx=10)
else:
    for i, task in enumerate(self.tasks):
        task_row = ttk.Frame(tasks_frame)
        task_row.pack(fill='x', pady=5)

        tk.Label(task_row, text=f"☐ {task}",
                 font=('Helvetica', 11), bg='white').pack(side='left')
        
        tk.Button(task_row, text="✓",
                  command=lambda idx=i: self.delete_taskk(idx),
                  relief='flat', bg="white", fg='#27ae60',
                  font=('Helvetica', 10, 'bold')).pack(side='right')
        
#ito yung nagsseseparate
ttk.Separator(task_frame, orient='horizontal').pack(fill='x', pady=15)

#Completed Tasks Section
completed_header = ttk.Frame(task_frame)
completed_header.pack(fill='x', pady=(0, 10))

tk.Label(completed_header, text="✓ Completed Tasks",
         font=('Helvetica', 12, 'bold'),
         fg='#27ae60', bg='white').pack(side='left')

tk.Label(completed_header, text=f"({len(self.completed_tasks)})",
                font=('Helvetica', 10), fg='#95a5a6',
                bg='white').pack(side='left', padx=5)

#Dito makikita mga tapos na task
if not self.completed_task:
    tk.Label(tasks_frame, text="No completed task yet",
             font=('Helvetica', 9). fg='#95a5a6',
             bg='white', justify='left').pack(pady=10)
else:
    completed_container = ttk.Frame(tasks_frame)
    completed_container.pack(fill='both', expand=True)

    #Ito yung naglilimit sa scrollbar
    canvas_height = min (200, len(self.completed_task) *40)

    canvas = ttk.Scrollbar(completed_container, bg='white',
                           height=canvas_height, highlightthickness=0)
    scrollbar = ttk.Scrollbar(completed_container, orient='vertical',
                              command=canvas.yview)
    scrollable_completed = ttk.Frame(canvas)
    scrollable_completed.bind('<configure>',
                              lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
    
    canvas.create_window((0, 0), window+scrollable_completed,anchor='nw')
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side='left', fill='both', expand=True)
    if len(self.completed_tasks) > 5:
        scrollbar.pack(side='right', fill='y')

    for i, task_data in enumerate(reversed(self.completed_tasks.completed_tasks[-10:])):
        task_row = ttk.Frame(scrollable_completed)
        task_row.pack(fill='x',pady=3)

        #Task text
        task_text_frame = ttk.Frame(task_row)
        task_text_frame.pack(side='left',fill='x',expand=True)

        tk.Label(task_text_frame, text=f"✓ {task_data['task']}",
                        font=('Helvetica', 9), fg='#7f8c8d',
                    bg='white').pack(anchor='w')
        

        #mga active buttons
        btn_container=ttk.Frame(task_row)
        btn_container.pack(side='right')

        #Calculate actual index in the original list

        actual_index=len(self.completed_tasks) - 1 - i
        tk.Button(btn_container, text="↶",
                  command=lambda idx=actual_index: self._restore_task_and_refresh(idx),
                  relief='flat', bg='white', fg='#3498db',
                         font=('Helvetica', 9), cursor='hand2').pack(side='left', padx=2)
        
        tk.Button(btn_container, text="🗑️",
                  command=lambda idx=actual_index: self._delete_completed_from_dashboard(idx),
                  relief='flat', bg='white', fg='#3498db',
                  font=('Helvetica', 9), cursor='hand2').pack(side='left', padx=2)
                            
    
    def show_freeform(self):
        """
        FREEFORM NOTES VIEW
        Simple text editor to write notes
        """
        self._clear_content()

        #Title
        tk.Label(self.main_content, text="📝 Freeform Notes",
                font=('Helvetica', 24, 'bold'),
                bg='#f5f5f5').pack(pady=20, anchor='w', padx=30)
        
        #Dito yung card container
        card = ttk.Frame(self.main_content, style='Card.Tframe', padding=20)
        card.pack(fill='both', expand=True,padx=30, pady=(0, 20))

        #dito mo iseselect yung course mo kasama nung title

        top_frame =ttk.Frame(card)
        top_frame.pack(fill='x', padx=(0, 10))

        tk.Label(top_frame, text="course:", bg='white').pack(side='left')

        course_var = tk.StringVar(value="Select Course")
        course_options = ["Select Course"] + list(self.course.keys())
        course_menu = ttk.OptionMenu(top_frame, course_var course_options)
        course_menu.pack(side='left', padx=5)

        #editor text
        text_widget = tk.Text(card, wrap='word', font=('Helvetica', 11),
                              undo=True, height=20)
        text_widget.pack(fill='both',expand=True,pady=10)

        #save button
        def save_note():
            course = course_var.get()
            title = title_entry.get().strip()
            content = text_widget.get("1.0", tk.END).strip()

            if course == "Select Course":
                messsagebox.showwarning("Error", "PLEASE SELECT A COURSE!")
                return
            
            if not content:
                messagebox.showwarning("Error", "NOTE IS EMPTY!")
                return
            
            if not title:
                title=f"Note - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            #save notes
            note = {
                "title": title,
                "content": content,
                "created": datetime.now().strftime('%Y-%m-%d %H:%M')
            }
            self.course[course]["note"].append(note)
            self._save_data()

            messagebox.showinfo(:"saved"f"Note saved to {course}!")
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
        Shows:Polya, 5W1H, Concept Map
        """
        self._clear_content()

        tk.Label(self.main_content, text="💡 Technical Templates",
                 font=('Helvetica', 24, 'bold'),
                bg='#f5f5f5').pack(pady=20, anchor='w', padx=30)
        tk.Label(self.main_content, text="Problem-solving frameworks for technical courses",
                 font=('Helvetica', 11), fg='#7f8c8d',
                 bg='#f5f5f5').pack(anchor='w', padx=30, pady=(0,20))
        
        templates = [
            ("Polya's 4 Steps", "Problem-Solving methodology","polya"),
            ("5WH1H Analysis", "What, Why, When, Where, Who, How", "5W1H"),
            ("Concept Mapping", "Visual relationship builder", "ConceptMap"),

        ]

        for name, desc,key in templates:
            card = ttk.Frame(self.main_content,style='Card.Tframe',padding=15)
            card.pack(fill='x', padx=30, pady=8)
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
                 font=('Helvetica', 11),fg='#7f8c8d',
                 bg='#f5f5f5').pack(anchor='w', padx=30, pady=(0, 20))
        
        templates = [
            ("Cornell Notes", "Two-Column system with summary", "Cornell"),
             ("Frayer Model", "Vocabulary and concept organizer", "Frayer"),
            ("Main Idea & Details", "Topic breakdown structure", "MainIdea"),

        ]

        for name, desc, key in templates:
            card = ttk.Frame(self.main_content, style='Card.TFrame', padding=15)
            card.pack(fill='x',pady=8)

            tk.Label(card, text=name, font=('Helvetica', 13, 'bold'),
                     bg='white').pack(anchor='w')
            tk.Label(card, text=desc, font=('Helvetica', 10),
                    fg='#7f8c8d', bg='white').pack(anchor='w', pady=5)
            tk.Button(card, text="Use Template →",
                     command=lambda k=key: self.open_template(k),
                     bg='#3498db', fg='white',
                     relief='flat').pack(anchor='e')


    #Part 7: Template
    def open_template(self, template_key):
        """
        Open a template form
        Shows fields to fill out based on template type
        """
        self._clear_content()

        #Definition nung template
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

        #Ito yung display name 
        TEMPLATES_NAMES = {
            "Cornell": "Cornell Notes",
            "MainIdea": "Main Idea and Details",
            "Frayer": "Frayer Model",
            "Polya": "Polya's 4 Steps",
            "5W1H": "5W1H Analysis",
            "ConceptMap": "Concept Mapping"
        }

        fields = TEMPLATES.get(template_key, [])
        template_display_name = TEMPLATES_NAMES.get(template_display_name)

        #Title
        tk.Label(self,main_content, text=f"{template_display_name}",
                 font=('Helvetica', 24, 'bold'),
                 bg='#f5f5f5').pack(pady=20, anchor='w',padx=30)
        
        #Dito selector
        top_frame = ttk.Frame(self.main_content)
        top_frame.pack(fill='x', padx=30, pady=(0, 10))

        tk.Label(top_frame, text="Course", bg='#f5f5f5').pack(side='left',padx=5)
        course_var = tk.StringVar(value="Select Course")
        course_option = ["Select Course"] + list(self.course.key())
        course_menu = ttk.OptionMenu(top_frame, course_var, course_option[0], *course_option)
        course_menu.pack(side='left',padx=5)

        #Scrollable form area
        canvas_frame = ttk.Frame(self.main_content)
        canvas_frame.pack(fill='both', expand=True, padx=30, pady=(0, 10))
        canvas = tk.Canvas(canvas_frame, bg='#f5f5f5', highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', command=canvas.yview)
        form_frame = ttk.Frame(canvas)
        form_frame.bind('<Configure>',
                        lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        
        canvas.pack(side='left',fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        #Create form fields
        field_widget = {}
        for field_label in fields:
            field_card = ttk.Frame(form_frame,style='Card.TFrame',padding=15)
            field_card.pack(fill='x', pady=8, padx=10)

            tk.Label(field_card,text=field_label,
                     font=('Helvetica', 11, 'bold'),
                     bg='white').pack(anchor='w', pady=(0, 5))
            
            #save note
            note = {
                "title": f"{template_key} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "template": template_key
                "data": note_data
                "created": datetime.now().strftim('%Y-%m-%d %H:%M:%S')

            }
            self.courses[course]["notes"].append(note)
            self._save_data()

            messagebox.showinfo("saved", f"{template_key} template saved to {course}!")
            self.show_dashboard()

    btn_frame = ttk.Frame(self.main_content)
    btn_frame.pack(fill='x', padx=30, pady=10)
    tk.Button(btn_frame, text="💾 Save Template",
              command=save_template,
              bg='#27ae60', fg='white',
              font=('Helvetica', 11, 'bold'),
              relief='flat', padx=20, pady=10).pack(side='left')
    tk.Button(btn_frame, text="← Back to Dashboard",
              command =self.show_dashboard,
              relief='flat', padx=15, pady=10).pack(side='left', padx=10)





if __name__ == "__main__":
    root = tk.Tk()
    app = CourseMateApp(root)
    root.mainloop()

