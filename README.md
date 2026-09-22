# Tikkit — AI-Driven Gamified To-Do List
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-41CD52?style=flat&logo=qt&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white)
![Local LLM](https://img.shields.io/badge/AI-Qwen2.5-purple?style=flat)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![Tikkit Demo](./assets/demo.gif)

A desktop to-do list app built with PyQt6 that pairs real task management with a local, offline AI model. Every task you add is scored for difficulty by a small local LLM, which sets its cash reward and — optionally — breaks it into subtasks. Completing tasks earns in-app currency that's spent on furniture and clothing to decorate an isometric room and dress up your avatar.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Prerequisites and Dependencies](#prerequisites-and-dependencies)
- [Installation and Environment Configuration](#installation-and-environment-configuration)
- [Usage](#usage)
- [Testing and Deployment Protocols](#testing-and-deployment-protocols)

## Architecture Overview

The app is a single-process PyQt6 desktop application (`main.py`) that switches between pages with a `QStackedWidget`, backed by a local SQLite database and a local LLM for task scoring.

*Data flow: Task Entry UI → Local LLM (difficulty + subtask split) → SQLite (`appdata/app_data`) → Task Handler → Room / Store UI → Reward granted on completion*

### UI Layer (PyQt6)
- `main.py` — app entry point; owns the `MainWindow`, wires every page together via Qt signals, and drives login/logout, page navigation, and save-on-close
- `login_page.py` — username/password login and registration form
- `home_page.py` — `RoomScene`, the main hub: an isometric room view (`Camera` / `QGraphicsScene`) for placed furniture, a collapsible side panel of task cards, and a bottom panel linking to the two stores
- `task_page.py` — `TaskEntryWidget`, the task creation form (description, optional split into subtasks, optional deadline with calendar/time pickers)
- `clothing_store.py` / `furniture_store.py` — `ClothingView` / `FurnitureView`, the two in-game shops used to spend earned currency
- `store_utils.py` — shared `GameData` state container and `UniversalStyles` theme/stylesheet generator (`default_theme`) reused across every page

### AI Engine (`task_handler.py`)
- Runs a quantized **Qwen2.5-0.5B-Instruct** model fully offline via `llama-cpp-python`
- `get_task_diff()` — rates a new task's difficulty from 0–100; the task's cash reward is `difficulty × 10`
- `get_subtask_list()` — when "Split Task" is enabled, asks the model for 2–5 short (≤4 word) subtask steps and parses them out with a regex splitter
- Both calls run synchronously when a task is submitted, inside `TaskSpecifications.__init__` in `task_page.py`

### Data Layer (`data_manager.py`)
- `DatabaseManager` — raw SQLite queries (users, task/subtask state, furniture and clothing inventory, placed furniture, equipped clothes)
- `UserManager` — validation and business logic on top of it: registration rules, login, and save/load of a user's full game state (money, furniture, clothes)
- All persistence goes through a single SQLite file at `appdata/app_data`

### Reward Loop
- Checking off a task (or, for a divided task, every one of its subtasks) grants its reward exactly once — a `grant_status` flag on each task prevents double payouts
- Earned money is spent in the Clothing or Furniture store; furniture placement (`x`, `y`, `z`, and a rotation `angle_index`) and equipped clothing slots (`Head`, `Torso`, `Legs`, `Feet`) are saved back to the database on logout or app close

## Prerequisites and Dependencies

### Runtime
- Python 3.10+ (required by PyQt6)

### Libraries
- **PyQt6** — GUI framework for every page and widget
- **llama-cpp-python** — loads and runs the local GGUF model used by the AI engine
- **numpy** — used to rescale the model's raw difficulty score
- **sqlite3** — Python standard library, no install needed

> No `requirements.txt` is included in the repo, so these need to be installed manually.

### Model File
- A GGUF build of **Qwen2.5-0.5B-Instruct**, expected at the exact relative path `qwen2.5-0.5b-instruct-q4_k_m.gguf` from wherever `main.py` is run — this filename is hardcoded in `task_handler.py`'s `AIEngine`

### Art Assets
- `home_page.py` loads furniture/room sprites from an `assets/` folder at the project root, matching any PNG whose filename contains the item's name (case-insensitive); items that face multiple directions (e.g. `Wall1`) need one image per rotation, sorted alphabetically to line up with each piece's `angle_index`
- `clock_icon.png` and `calendar_icon.png` (already in the repo root) are used by the task entry page's time/date buttons

## Installation and Environment Configuration

1. **Clone the repository**

   ```bash
   git clone https://github.com/omar-daoud-rbtxs/ai-driven-todo.git
   cd ai-driven-todo
   ```

2. **Install dependencies**

   ```bash
   pip install PyQt6 llama-cpp-python numpy
   ```

3. **Add the local AI model**

   Download a Qwen2.5-0.5B-Instruct GGUF quantization (e.g. `qwen2.5-0.5b-instruct-q4_k_m.gguf`) and place it in the project root so it matches the `model_path` in `task_handler.py`.

4. **Add room, furniture, and clothing sprites**

   Populate an `assets/` folder at the project root with the PNGs the room view expects (see [Art Assets](#art-assets) above). A new account's default room layout references `Floor Blank`, `Wall1`, and `Wall2`.

5. **Run the app**

   ```bash
   python main.py
   ```

## Usage

1. **Register or log in** — new accounts start with $300 and an empty default room shell.
2. **Add a task** — from the room view, click **Add Task**. Type a description, and optionally:
   - toggle **Split Task** and drag the slider (2–5) to have the AI break it into that many subtasks
   - toggle **Set Deadline** to attach a due date and time via the calendar/clock popups

   Submitting sends the task to the local model, which rates its difficulty (and drafts subtasks, if requested) before it's saved to your task list.
3. **Complete tasks** — check items off in the side panel. A divided task pays out only once every one of its subtasks is checked.
4. **Spend your earnings** — from the room view's bottom panel, open the **Clothing Store** or **Furniture Store** to buy and equip outfits or place furniture in your room. Layouts and equipped items are saved automatically on logout or when the app closes.

## Testing and Deployment Protocols

### AI Model Verification

`task_handler.py` instantiates the AI engine (`ai_engine = AIEngine()`) at import time, so a missing or misnamed model file will fail on startup, before the login window even opens. Confirm `qwen2.5-0.5b-instruct-q4_k_m.gguf` is present in the working directory and loads without error before relying on task entry.

### Database Schema Reference

| Table | Key columns |
|---|---|
| `users` | `uuid` (PK), `username`, `password`, `logged_status`, `money` |
| `inventory` | `uuid`, `item_name`, `item_type` (`'furn'` or `'clothe'`), `quantity` |
| `placed_furniture` | `uuid`, `name`, `angle_index`, `x`, `y`, `z` |
| `equipped_clothes` | `uuid`, `Head`, `Torso`, `Legs`, `Feet` |
| `tasks` | `taskid` (PK), `uuid`, `name`, `subdivisions`, `deadline`, `date_due`, `time_due`, `reward`, `status`, `grant_status` |
| `subtasks` | `subtask_id` (PK), `parent_id` (→ `tasks.taskid`), `subtask_order`, `name`, `status` |

### Asset Path Verification

Before first run, confirm:
- `assets/` exists at the project root with sprites for every piece in the default room layout (`Floor Blank`, `Wall1`, `Wall2`) plus any store items
- `clock_icon.png` and `calendar_icon.png` are present at the project root

### First-Run Checklist

- [ ] `appdata/app_data` exists with the schema above
- [ ] `qwen2.5-0.5b-instruct-q4_k_m.gguf` is present and loads successfully
- [ ] `assets/` is populated with the sprites the default room and stores reference

## License

Distributed under the **GPL-3.0** license — see [`LICENSE`](./LICENSE) for details.
