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
│ • Write Notes   │     │ • Home Button   │
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