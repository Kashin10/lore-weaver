# ⚔ LoreWeaver

> **AI-powered video game narrative & character generator** — built with Flask, Python, and Google Gemini AI.

LoreWeaver lets you craft rich, deeply detailed game stories and characters by filling in a set of creative specifications. The AI takes care of the rest — world building, plot structure, character arcs, backstories, and more.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey?style=flat-square&logo=flask)
![Gemini](https://img.shields.io/badge/Gemini-AI-orange?style=flat-square&logo=google)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## ✨ Features

- **4-Step Narrative Wizard** — specify genre, tone, world type, plot structure, protagonist archetype, magic system, tech level, and more
- **AI Narrative Generation** — Gemini AI writes a full narrative with world building, conflict, themes, and a 4-act plot
- **AI Character Generation** — generate a cast of 3–8 deep characters tailored to your story, each with backstory, arc, abilities, flaws, and quotes
- **Full Editing** — customize every field of your narrative and characters after generation
- **Manual Character Creation** — add your own characters from scratch with a color-picker avatar
- **Project Dashboard** — manage multiple game projects at once
- **Fallback Mode** — works without an API key using rich built-in demo content

---

## 🖥 Preview

| Dashboard | Narrative Wizard | Character Profile |
|-----------|-----------------|-------------------|
| Browse and manage all your game projects | Fill in 30+ creative specs across 4 steps | Deep character cards with backstory, quotes, and arc |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- pip

### 1. Clone the repository

```bash
git clone https://github.com/Kashin10/lore-weaver.git
cd lore-weaver
```

### 2. Create a virtual environment (recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your environment file

Create a `.env` file in the root of the project:

```bash
# Windows
copy NUL .env

# macOS / Linux
touch .env
```

Open `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

> **Don't have a key?** Get one free at [Google AI Studio](https://aistudio.google.com/app/apikey).  
> The app works without a key too — it falls back to built-in demo content.

### 5. Run the app

```bash
python app.py
```

Then open your browser and go to:

```
http://127.0.0.1:5000
```

---

## 📁 Project Structure

```
lore-weaver/
├── app.py                        # Flask app, routes, AI service
├── requirements.txt              # Python dependencies
├── .env                          # Your API key (not committed)
├── .gitignore
├── static/
│   ├── css/
│   │   └── style.css             # Full design system (dark glassmorphism)
│   └── js/
│       └── main.js               # Animations and interactivity
└── templates/
    ├── base.html                 # Base layout (navbar, orbs, footer)
    ├── index.html                # Dashboard
    ├── create_project.html       # New project form
    ├── create_narrative.html     # 4-step narrative specification wizard
    ├── view_narrative.html       # Narrative viewer
    ├── edit_narrative.html       # Narrative editor
    ├── characters.html           # Character gallery + AI generator
    ├── character_detail.html     # Full character profile
    ├── edit_character.html       # Character editor
    ├── add_character.html        # Manual character creation
    └── settings.html             # API key configuration
```

---

## ⚙ Configuration

| Setting | Description |
|---|---|
| `GEMINI_API_KEY` | Your Google Gemini API key. Optional — app uses fallback content without it. |

You can also configure the key through the in-app **Settings (⚙)** page at `http://127.0.0.1:5000/settings`.

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, Flask-SQLAlchemy |
| Database | SQLite (auto-created on first run) |
| AI | Google Gemini 1.5 Flash |
| Frontend | Vanilla HTML, CSS, JavaScript |
| Fonts | Google Fonts — Outfit, Playfair Display |

---

## 📖 Usage Guide

1. **Create a Project** — give it a title and pick a genre
2. **Fill the Narrative Wizard** — go through 4 steps specifying your world, tone, plot, characters, and any extra notes
3. **Generate** — the AI crafts your full narrative
4. **Generate Characters** — from the Characters page, choose how many and let AI build your cast
5. **Customize** — edit any narrative section or character field to your liking
6. **Add Characters** — manually create additional characters as needed

---

## 📄 License

MIT — feel free to use, modify, and build on this.
