# CourseMate Application Flowchart

## Simple One-Page Flowchart

```
┌─────────────────┐
│   Start App     │
│ (CourseMate())  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐     ┌─────────────────┐
│ Load Data       │────▶│ Initialize UI   │
│ (DataManager)   │     │ (Sidebar, Main) │
└─────────┬───────┘     └─────────┬───────┘
          │                       │
          ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│ Show Home View  │◄────┤   User Actions   │
│ (Default)       │     │                  │
└─────────┬───────┘     └─────────┬───────┘
          │                       │
          ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│   Home View     │     │   Navigation    │
│                 │     │                 │
│ • Write Notes (hashtags inline)   │     │ • Home Button   │
│ • Select Template│     │ • Notebooks     │
│ • Assign to NB   │     │ • Settings      │
│ • View Notes     │     │                 │
└─────────┬───────┘     └─────────┬───────┘
          │                       │
          ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│ Notebooks View  │     │ Settings View   │
│                 │     │                 │
│ • Grid of NBs   │     │ • Theme Select  │
│ • Create NB     │     │ • Font Settings │
│ • View NB Notes │     │ • Quotes Mgmt   │
│ • Edit/Delete   │     │ • Templates     │
└─────────┬───────┘     └─────────┬───────┘
          │                       │
          ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│   Note Window   │     │   Dialogs       │
│                 │     │                 │
│ • View Note     │     │ • Input Dialog  │
│ • Edit Content  │     │ • Template Dialog│
│ • Move Note     │     │ • Create NB     │
│ • Delete Note   │     │                 │
└─────────┬───────┘     └─────────┬───────┘
          │                       │
          ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│   Data Manager  │     │   Save/Load     │
│                 │     │                 │
│ • Add Note      │     │ • JSON File     │
│ • Update NB     │     │ • Auto-save     │
│ • Delete Items  │     │ • Load on Start │
│ • Settings      │     │                 │
└─────────┬───────┘     └─────────┬───────┘
          │                       │
          ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│   Theme System  │     │   Templates     │
│                 │     │                 │
│ • Color Schemes │     │ • Predefined    │
│ • Dynamic Apply │     │ • Custom Create │
│ • Font Loading  │     │ • Insert into   │
│                 │     │   Notes         │
└─────────────────┘     └─────────────────┘
```

## Flowchart Explanation

### Main Flow:
1. **App Start** → Load data → Initialize UI → Show Home View
2. **User Navigation** → Switch between Home, Notebooks, Settings views
3. **Home View** → Write notes, select templates, assign to notebooks
4. **Notebooks View** → Manage notebooks and their notes
5. **Settings View** → Customize appearance, manage quotes/templates
6. **Data Operations** → All changes saved to JSON file automatically

### Key Components:
- **DataManager**: Central hub for all data operations
- **Views**: Different screens (Home, Notebooks, Settings)
- **Dialogs**: Popups for input, creation, editing
- **Theme System**: Dynamic color/font changes
- **Template System**: Predefined note structures

### Data Flow:
User Action → UI Component → DataManager → JSON File → UI Update

This flowchart shows the high-level architecture and user interaction flow of the CourseMate application.

## Flowchart updates for mock defense (Nov 26, 2025)

I've expanded the flowchart to include important decision points and added a short legend listing the standard shapes we used so the reviewers understand the diagram semantics.

Shapes Legend (use these in the updated diagram):
- Terminator / Start-End (rounded rectangle) — marks application start and graceful shutdown
- Process (rectangle) — standard operation or step (e.g., Initialize UI, Save Data)
- Decision (diamond) — branching logic (e.g., "search term present?", "note saved successfully?")
- Input/Output (parallelogram) — user input elements such as forms / file dialogs
- Document (rectangle with wavy base) — saved outputs like exported .txt files
- Data / Storage (cylinder) — persistent storage (the JSON file or database)

Example places to use shapes in the diagram (mapping):
- Start App — Terminator
- Load Data — Process
- Initialize UI — Process
- User Input (Write note, Search, Tag input) — Input/Output
- Search term present? — Decision
    - Yes → Filter notes (Process)
    - No → Show all notes (Process)
- Save Changes → Process → Decision "Write success?" → Yes → UI refresh; No → Show error dialog (Document)
- Export Note → Process → Document (exported file)
- DataManager writes to JSON — Data Storage (cylinder)

Updated flow (ASCII + shapes hint):

Start (Terminator rounded) -> Load Data (Process) -> Initialize UI (Process)
    |
    -> Home View (Process) -> Write Note (I/O) -> Save (Process) -> DataManager -> JSON file (Data)
        |
        -> Decision: Note saved? (Decision diamond) — Yes: Refresh UI (Process) — No: Show error (Document)

Search Flow:
User enters search (I/O) -> Decision: search term present? (diamond)
    - Yes -> Filter notes (Process) -> Show filtered list
    - No -> Show all notes (Process)

Notes/Notebooks UI flows and shapes are now aligned with the new edits:
- All cards use consistent borders and corner radii (visual consistency) — illustrated with Process boxes in the visual diagram.

If you want, I can render a simple PNG export of the flowchart or produce a draw.io / mermaid diagram with exact coordinates and shape types for your presentation. Which format do you prefer for the mock defense: PNG or Mermaid (text diagram)?

Note on tags (UI update):
- Tag sanitization is preserved, but the UX rose to a simpler model: hashtags are typed inline inside notes and are highlighted as you type. On save, the app extracts, normalizes, and persists hashtags into the note's tag list.
    Draw the flow as: Content (user types note with #hashtags) -> Process (extract & sanitize tags) -> DataManager save.