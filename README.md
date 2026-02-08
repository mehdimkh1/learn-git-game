# ⚔️ The Git Quest

**An interactive terminal game that teaches Git by making you DO it.**

No slides. No videos. No walls of text. You learn Git by typing real commands in a guided adventure with XP, achievements, and boss fights.

![Python](https://img.shields.io/badge/Python-3.7+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

---

## 🎮 What Is This?

The Git Quest is a **CLI game** that teaches you Git from zero to professional. Instead of reading documentation, you play through 8 levels — typing real Git commands while the game validates your work, awards XP, and tracks achievements.

**Perfect for:**
- Complete beginners who've never used Git
- Developers who know the basics but want to learn team workflows
- Anyone who learns better by doing than reading

## 🏆 Features

- **8 Levels** covering beginner → professional Git workflows
- **25+ hands-on labs** with real Git commands
- **3800 XP** to earn across all levels
- **12 Achievements** to unlock
- **Save/Resume system** — pick up where you left off
- **Level Select menu** — replay any level
- **Zero dependencies** — just Python 3.7+ and Git
- **Real-world team workflows** used at actual companies

## 📋 Level Overview

| Level | Name | What You Learn | XP |
|-------|------|---------------|-----|
| 1 | **The Awakening** | `init`, `add`, `commit`, `status`, `diff`, `log` | 100 |
| 2 | **First Blood** | `restore`, `amend`, `reset`, `.gitignore` | 200 |
| 3 | **The Multiverse** | Branches, merging, **merge conflict boss fight** | 400 |
| 4 | **The Cloud Kingdom** | GitHub, `push`, `pull`, `clone`, remotes | 300 |
| 5 | **The Final Boss** | `stash`, `reflog`, recovery, aliases | 500 |
| 6 | **The Guild** | Feature branches, teammates, `blame`, `cherry-pick` | 600 |
| 7 | **The War Room** | Squash merge, `bisect`, diff review, PR workflow | 500 |
| 8 | **The Throne Room** | Tags, semver, hotfix workflow, sprint simulation | 700 |

### 🏢 Real-World Team Skills (Levels 6-8)

These levels teach the workflows actually used at companies:

- **Feature branch naming** — `feature/`, `bugfix/`, `hotfix/` conventions
- **Conventional commits** — `feat:`, `fix:`, `docs:` message format
- **Simulating teammates** — what happens when coworkers push to main
- **Squash merging** — cleaning up messy commits before merge
- **Git bisect** — binary search to find bug-introducing commits
- **Git blame** — finding who wrote what line
- **Cherry-pick** — taking one commit from another branch
- **Semantic versioning** — `v1.0.0` → `v1.1.0` → `v2.0.0`
- **Hotfix workflow** — emergency production fixes
- **Complete sprint simulation** — the full professional cycle

## 🚀 Quick Start

### Prerequisites

- **Python 3.7+** — [Download](https://www.python.org/downloads/)
- **Git** — [Download](https://git-scm.com/downloads)

### Run

```bash
# Clone the repo
git clone https://github.com/mehdimkh1/learn-git-game.git
cd learn-git-game

# Play!
python git-quest.py
```

That's it. No pip install. No setup. No dependencies.

## 🎯 How It Works

1. The game shows you a concept with a story
2. It tells you what command to type
3. You type the command
4. The game runs real Git operations and validates your work
5. You earn XP and unlock achievements
6. Difficulty increases as you progress — less hand-holding over time

```
  ╔══════════════════════════════════════════════════╗
  ║                                                  ║
  ║     ⚔️   T H E   G I T   Q U E S T   ⚔️          ║
  ║                                                  ║
  ║     1.  🆕  New Game                               ║
  ║     2.  ▶️   Continue (Level 3)                     ║
  ║     3.  🗺️   Level Select                          ║
  ║     4.  📊  Progress                               ║
  ║     5.  ❌  Quit                                   ║
  ║                                                  ║
  ╚══════════════════════════════════════════════════╝
```

## 🏅 Achievements

| Achievement | How to Unlock |
|------------|---------------|
| First Commit | Make your first commit |
| Time Traveler | Explore git log |
| Conflict Resolver | Defeat the merge conflict boss |
| Branch Master | Master branching and merging |
| Cloud Warrior | Push to GitHub |
| Rescue Ranger | Use git reflog |
| Detective | Use git blame |
| Team Player | Complete the team workflow |
| Clean Coder | Squash merge messy commits |
| Bug Hunter | Find a bug with git bisect |
| Firefighter | Complete a hotfix workflow |
| Release Manager | Tag a release and complete sprint |

## 📂 Project Structure

```
git-quest/
├── git-quest.py          # The game (single file, zero dependencies)
├── README.md             # You're reading this
├── LICENSE               # MIT License
└── git_quest_save.json   # Auto-generated save file (after playing)
```

## 🤝 Contributing

Contributions welcome! Ideas for new levels, labs, or improvements:

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/new-level`
3. Commit with conventional messages: `git commit -m "feat: add new level"`
4. Push and open a Pull Request

## 📜 License

MIT License — use it, share it, teach with it.

---

**Learn Git the fun way. Stop reading, start playing.** ⚔️
