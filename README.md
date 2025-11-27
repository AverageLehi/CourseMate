# 📚 CourseMate: A Smart Note-Taking & Study Aid for Students

### Project Team
* Lehi Ontoria Gomez
* James Decano Sarmiento
* Janry Landingin Malong
* Erl John Guiller Carino Ygay

---

## 💡 Project Overview

**CourseMate** is a lightweight, student-centered application designed to help learners organize their academic materials and apply proven learning strategies. By integrating flexible, evidence-based [...]

---

## ✨ Features

* **Course Management:** Keep your educational materials neatly organized by creating dedicated folders for each course or module. Add tasks, assignments, and readings, and track their completion stat[...]
* **Note-taking Module:** Write, edit, and organize notes under each course. The application supports various templates to guide your note-taking process.
* **Templates for Non-Technical Courses:**
    * **Cornell Notes:** A powerful method for active review and retention.
    * **Main Idea & Supporting Details:** Quickly grasp core concepts by separating the main point from its supporting evidence.
    * **Frayer Model:** Master new vocabulary by exploring definitions, characteristics, examples, and non-examples.
* **Templates for Technical Courses:**
    * **Polya's Four Steps:** A structured method to systematically tackle and solve complex problems.
    * **Concept Mapping:** Visually connect ideas to build a deeper understanding of any topic.
    * **5W1H Strategy:** Instantly get a complete overview of a topic by answering six essential questions.
* **Lightweight Data Storage:** The system uses simple CSV and text files for structured records and notes, making the application highly portable and easy to back up.
* **Update — Data Storage Format:** Moving forward, CourseMate will use JSON files for data saving and file storage instead of CSV. The original CSV/text description on the previous line is retained for context and backward-compatibility notes.

---

## 🎯 Project Objectives

Our core objectives for CourseMate are to:

* Provide an easy-to-use platform for organizing notes and tasks.
* Support non-technical courses with structured study aids.
* Support technical courses with effective problem-solving tools.
* Encourage the adoption of evidence-based learning strategies.
* Keep the system lightweight, portable, and accessible.

---

## 🛠️ How It Works

CourseMate addresses the common student struggle of staying organized while applying effective study techniques. It combines a simple file management system with integrated learning templates, guiding[...]

---

## 🚀 Getting Started

**Prerequisites:**
* Python 3.x

**Usage:**
1.  Clone the repository:
    `git clone [https://github.com/AverageLehi/CourseMate.git]`
2.  Navigate to the project directory:
    `cd coursemate`
3.  Run the application:
    `python coursemate.py`

### Optional: Offline AI Features (Local LLM via Ollama)

CourseMate can generate study/planner templates, summarize notes, extract tags, and answer questions using a local Large Language Model (LLM)—no cloud required.

1. Install Ollama (Windows/macOS/Linux): https://ollama.com
2. Pull a model (example): `ollama pull llama3`
3. (Optional) Pull additional models (e.g. `ollama pull mistral`, `ollama pull phi3`)
4. Start Ollama (service usually autostarts after install). Default host: `http://localhost:11434`
5. Launch CourseMate. AI actions appear in Home view and AI template generation + model selection appear in Settings.
6. Change active model in Settings (Model dropdown). The app persists your choice in settings (`ai_model`).

If the AI buttons warn that the service is unavailable, ensure Ollama is running and at least one model is pulled.

Environment overrides:
`OLLAMA_HOST` to change host (default `http://localhost:11434`).
`OLLAMA_MODEL` to set initial model (overridden when selecting in-app).

No data is sent to external servers; all inference is local.

---

## 🧑‍💻 Contributing

We welcome contributions from the community! If you'd like to improve CourseMate, please check the issues, fork the repository, and submit a pull request.

---

## 📄 License

This project is licensed under the MIT License.

---

*For inquiries, please contact the project group members listed above.*
