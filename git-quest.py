"""
THE GIT QUEST - An Interactive Terminal Game to Learn Git
Run this and follow along. It teaches you Git by making you DO things.
"""

import os
import sys
import subprocess
import time
import shutil
import json

# ─── COLORS ─────────────────────────────────────────────
class C:
    GOLD = "\033[93m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    DIM = "\033[90m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

# ─── GAME STATE ─────────────────────────────────────────
xp = 0
achievements = []
current_level = 1
quest_dir = None
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "git_quest_save.json")

# ─── HELPERS ────────────────────────────────────────────
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def pause(msg="Press ENTER to continue..."):
    input(f"\n{C.DIM}{msg}{C.RESET}")

def slow_print(text, delay=0.02):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def banner(text):
    width = 50
    print(f"\n{C.GOLD}{'═' * width}")
    print(f"  {text}")
    print(f"{'═' * width}{C.RESET}\n")

def show_xp():
    print(f"\n{C.GOLD}⭐ Total XP: {xp}{C.RESET}")

def award_xp(amount, reason):
    global xp
    xp += amount
    print(f"\n{C.GREEN}  +{amount} XP! {reason}{C.RESET}")

def achievement(name):
    achievements.append(name)
    print(f"\n{C.MAGENTA}  🏅 ACHIEVEMENT UNLOCKED: {name}!{C.RESET}")

def mission(text):
    print(f"\n{C.CYAN}  🎯 MISSION: {text}{C.RESET}\n")

def story(text):
    print(f"\n{C.DIM}  {text}{C.RESET}")

def instruction(text):
    print(f"\n{C.BOLD}  👉 {text}{C.RESET}")

def success(text):
    print(f"\n{C.GREEN}  ✅ {text}{C.RESET}")

def fail(text):
    print(f"\n{C.RED}  ❌ {text}{C.RESET}")

def hint(text):
    print(f"\n{C.DIM}  💡 Hint: {text}{C.RESET}")

def show_command(cmd):
    print(f"\n  {C.GOLD}$  {cmd}{C.RESET}")

def wait_for_command(prompt_text="Type the command and press ENTER: "):
    return input(f"\n  {C.CYAN}⌨  {prompt_text}{C.RESET}").strip()

def run_git(*args, cwd=None):
    """Run a git command and return (success, output)."""
    try:
        result = subprocess.run(
            ["git"] + list(args),
            cwd=cwd or quest_dir,
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0, result.stdout.strip() + result.stderr.strip()
    except Exception as e:
        return False, str(e)

def check_file_exists(filename):
    if quest_dir:
        return os.path.exists(os.path.join(quest_dir, filename))
    return False

def read_file(filename):
    path = os.path.join(quest_dir, filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read().strip()
    return ""

def write_file(filename, content):
    path = os.path.join(quest_dir, filename)
    with open(path, "w") as f:
        f.write(content)

def append_file(filename, content):
    path = os.path.join(quest_dir, filename)
    with open(path, "a") as f:
        f.write(content)

def get_current_branch():
    ok, out = run_git("branch", "--show-current")
    return out.strip() if ok else ""

def get_commit_count():
    ok, out = run_git("rev-list", "--count", "HEAD")
    try:
        return int(out.strip()) if ok else 0
    except:
        return 0

def is_git_repo():
    return quest_dir and os.path.isdir(os.path.join(quest_dir, ".git"))

def get_branches():
    ok, out = run_git("branch")
    if ok:
        return [b.strip().lstrip("* ") for b in out.strip().split("\n") if b.strip()]
    return []

def has_conflict():
    ok, out = run_git("status")
    return "both modified" in out or "Unmerged" in out

# ─── SAVE / LOAD SYSTEM ────────────────────────────────
def save_progress():
    data = {
        "xp": xp,
        "achievements": achievements,
        "current_level": current_level,
    }
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except:
        pass

def load_progress():
    global xp, achievements, current_level
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
            xp = data.get("xp", 0)
            achievements = data.get("achievements", [])
            current_level = data.get("current_level", 1)
            return True
        except:
            return False
    return False

def reset_progress():
    global xp, achievements, current_level
    xp = 0
    achievements = []
    current_level = 1
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)

# ─── MENU SYSTEM ───────────────────────────────────────
def show_progress_screen():
    clear()
    banner("YOUR PROGRESS")
    total_xp = 3800
    pct = int((xp / total_xp) * 100) if total_xp > 0 else 0
    bar_len = 30
    filled = int(bar_len * pct / 100)
    bar = f"{C.GREEN}{'█' * filled}{C.DIM}{'░' * (bar_len - filled)}{C.RESET}"

    print(f"\n  {C.BOLD}XP: {C.GOLD}{xp} / {total_xp}{C.RESET}  [{bar}] {pct}%")
    print(f"  {C.BOLD}Level: {C.CYAN}{current_level} / 8{C.RESET}")
    print(f"  {C.BOLD}Achievements: {C.MAGENTA}{len(achievements)} / 12{C.RESET}\n")

    if achievements:
        for a in achievements:
            print(f"    {C.MAGENTA}🏅 {a}{C.RESET}")
    else:
        print(f"    {C.DIM}No achievements yet. Start playing!{C.RESET}")
    pause("\n  Press ENTER to go back...")

def level_select_menu():
    levels = [
        ("The Awakening", "Git basics — init, add, commit"),
        ("First Blood", "Undo spells — restore, reset, amend"),
        ("The Multiverse", "Branches, merging, conflict boss"),
        ("The Cloud Kingdom", "GitHub, push, pull, clone"),
        ("The Final Boss", "Stash, recovery, reflog, aliases"),
        ("The Guild", "Team workflow, blame, cherry-pick"),
        ("The War Room", "Code review, squash, bisect"),
        ("The Throne Room", "Tags, hotfix, release management"),
    ]

    while True:
        clear()
        banner("LEVEL SELECT")
        for i, (name, desc) in enumerate(levels, 1):
            if i < current_level:
                status = f"{C.GREEN}✅"
            elif i == current_level:
                status = f"{C.CYAN}▶️ "
            else:
                status = f"{C.DIM}🔒"
            lock = "" if i <= current_level else f" {C.DIM}(locked){C.RESET}"
            print(f"  {status}  {i}. Level {i}: {name}{C.RESET}{lock}")
            print(f"       {C.DIM}{desc}{C.RESET}")

        print(f"\n  {C.DIM}You can play any unlocked level (1-{current_level}).{C.RESET}")
        choice = input(f"\n  {C.CYAN}Choose level (1-8) or 'back': {C.RESET}").strip().lower()

        if choice == "back" or choice == "b":
            return None

        try:
            level = int(choice)
            if 1 <= level <= current_level:
                return level
            elif 1 <= level <= 8:
                print(f"\n  {C.RED}Level {level} is locked! Complete Level {current_level} first.{C.RESET}")
                pause()
            else:
                print(f"\n  {C.RED}Invalid choice.{C.RESET}")
                pause()
        except ValueError:
            pass

def main_menu():
    load_progress()

    while True:
        clear()
        lvl_text = f"Level {current_level}" if current_level <= 8 else "All Complete!"
        print(f"""
{C.GOLD}
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║       ⚔️   T H E   G I T   Q U E S T   ⚔️        ║
    ║                                                  ║
    ╠══════════════════════════════════════════════════╣
    ║                                                  ║
    ║    1.  🆕  New Game                               ║
    ║    2.  ▶️   Continue ({lvl_text:15s})         ║
    ║    3.  🗺️   Level Select                          ║
    ║    4.  📊  Progress                               ║
    ║    5.  ❌  Quit                                   ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
{C.RESET}""")
        choice = input(f"  {C.CYAN}Choose (1-5): {C.RESET}").strip()

        if choice == "1":
            reset_progress()
            return ("new", 1)
        elif choice == "2":
            if current_level > 8:
                print(f"\n  {C.GREEN}You've completed all levels! Start a new game or select a level.{C.RESET}")
                pause()
            else:
                return ("continue", current_level)
        elif choice == "3":
            level = level_select_menu()
            if level is not None:
                return ("select", level)
        elif choice == "4":
            show_progress_screen()
        elif choice == "5":
            print(f"\n  {C.GOLD}Until next time, adventurer! ⚔️{C.RESET}\n")
            sys.exit(0)

# ─── TITLE SCREEN ───────────────────────────────────────
def title_screen():
    clear()
    print(f"""
{C.GOLD}
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║     ⚔️   T H E   G I T   Q U E S T   ⚔️          ║
    ║                                                  ║
    ║     An Interactive Game to Learn Git              ║
    ║                                                  ║
    ║     • 8 Levels  (3 NEW team workflow labs!)       ║
    ║     • Hands-on Labs                              ║
    ║     • 3800 XP to earn                            ║
    ║     • 12 Achievements to unlock                  ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
{C.RESET}
{C.DIM}    You will learn Git by DOING, not reading.
    The game will guide you through every step.
    Type commands when asked. The game checks your work.{C.RESET}
""")
    pause("Press ENTER to begin your quest...")

# ═══════════════════════════════════════════════════════
# LEVEL 1: THE AWAKENING
# ═══════════════════════════════════════════════════════
def level_1():
    global quest_dir
    clear()
    banner("LEVEL 1: THE AWAKENING  ⭐ 100 XP")

    story("You wake up in a world where code disappears,")
    story("files get lost, and nobody knows who changed what.")
    story("You discover an ancient tool called 'Git'...")
    pause()

    # ─── LAB 1: Identity ───
    clear()
    banner("LEVEL 1 — LAB 1: YOUR IDENTITY")
    mission("Tell Git who you are.")
    story("Before wielding Git, you must register your identity.")

    print(f"\n{C.BOLD}  Git needs two things: your name and your email.{C.RESET}")
    print(f"  These appear on every commit you make.\n")

    instruction("Type this command (use YOUR real name):")
    show_command('git config --global user.name "Your Name"')

    while True:
        cmd = wait_for_command()
        if cmd.startswith("git config") and "user.name" in cmd:
            os.system(cmd)
            success("Identity name set!")
            award_xp(10, "Name configured")
            break
        else:
            hint('Type: git config --global user.name "Your Name"')

    instruction("Now set your email:")
    show_command('git config --global user.email "you@example.com"')

    while True:
        cmd = wait_for_command()
        if cmd.startswith("git config") and "user.email" in cmd:
            os.system(cmd)
            success("Identity email set!")
            award_xp(10, "Email configured")
            break
        else:
            hint('Type: git config --global user.email "you@example.com"')

    # Verify
    print(f"\n{C.BOLD}  Let's verify it worked.{C.RESET}")
    instruction("Type:")
    show_command("git config user.name")

    while True:
        cmd = wait_for_command()
        if "config" in cmd and "user.name" in cmd:
            os.system(cmd)
            success("Your name appeared above! Identity confirmed.")
            break
        else:
            hint("Type: git config user.name")

    pause()

    # ─── LAB 2: First Repo ───
    clear()
    banner("LEVEL 1 — LAB 2: CREATE YOUR FIRST REPO")
    mission("Create a Git repository from scratch.")

    story("A 'repo' is just a folder that Git watches over.")
    story("Let's create one called 'git-quest'.\n")

    # Determine quest directory location
    base_dir = os.getcwd()
    quest_dir = os.path.join(base_dir, "git-quest")

    if os.path.exists(quest_dir):
        print(f"{C.DIM}  (Found existing git-quest folder, cleaning up...){C.RESET}")
        shutil.rmtree(quest_dir)

    instruction("Type this to create a new folder:")
    show_command("mkdir git-quest")

    while True:
        cmd = wait_for_command()
        if "mkdir" in cmd and "git-quest" in cmd:
            os.makedirs(quest_dir, exist_ok=True)
            success("Folder created!")
            break
        else:
            hint("Type: mkdir git-quest")

    instruction("Now enter the folder:")
    show_command("cd git-quest")

    while True:
        cmd = wait_for_command()
        if "cd" in cmd and "git-quest" in cmd:
            if os.path.isdir(quest_dir):
                success("You're inside git-quest!")
            break
        else:
            hint("Type: cd git-quest")

    instruction("Now cast the init spell:")
    show_command("git init")

    while True:
        cmd = wait_for_command()
        if cmd.strip() == "git init":
            ok, out = run_git("init")
            if ok:
                print(f"\n  {C.DIM}{out}{C.RESET}")
                success("Repository created! Git is now watching this folder.")
                award_xp(20, "First repository!")
            else:
                fail(f"Something went wrong: {out}")
            break
        else:
            hint("Type exactly: git init")

    pause()

    # ─── LAB 3: The Three Zones ───
    clear()
    banner("LEVEL 1 — LAB 3: THE THREE ZONES")
    mission("Understand how Git saves your work.")

    print(f"""
{C.BOLD}  Git has 3 zones. This is THE key concept:{C.RESET}

  {C.CYAN}📂 WORKING DIR{C.RESET}    →    {C.GOLD}📋 STAGING{C.RESET}    →    {C.GREEN}📦 SAVED{C.RESET}
     (your files)        (ready to save)      (committed!)
                    {C.CYAN}git add{C.RESET}          {C.GOLD}git commit{C.RESET}

  Think of mailing a package:
  1. 📂 Pick items from your room      (edit files)
  2. 📋 Put them in the box             (git add)
  3. 📦 Seal and label the box          (git commit)
""")
    pause("Got it? Press ENTER to try it...")

    instruction("Create your first file — type:")
    show_command('echo "Hello, I am learning Git!" > hero.txt')

    while True:
        cmd = wait_for_command()
        if "hero.txt" in cmd:
            write_file("hero.txt", "Hello, I am learning Git!\n")
            success("File created!")
            break
        else:
            hint('Type: echo "Hello, I am learning Git!" > hero.txt')

    instruction("Now check what Git sees:")
    show_command("git status")

    while True:
        cmd = wait_for_command()
        if cmd.strip() == "git status":
            ok, out = run_git("status")
            print(f"\n{C.RED}  {out.replace(chr(10), chr(10) + '  ')}{C.RESET}")
            print(f"\n  {C.BOLD}See hero.txt in RED? That means it's in your")
            print(f"  working directory but NOT staged yet.{C.RESET}")
            break
        else:
            hint("Type: git status")

    instruction("Stage it (put it in the box):")
    show_command("git add hero.txt")

    while True:
        cmd = wait_for_command()
        if "git add" in cmd:
            run_git("add", "hero.txt")
            success("File staged!")
            break
        else:
            hint("Type: git add hero.txt")

    instruction("Check status again — notice the color change:")
    show_command("git status")

    while True:
        cmd = wait_for_command()
        if "status" in cmd:
            ok, out = run_git("status")
            print(f"\n{C.GREEN}  {out.replace(chr(10), chr(10) + '  ')}{C.RESET}")
            print(f"\n  {C.BOLD}Now it's GREEN! That means it's staged and")
            print(f"  ready to be committed (sealed in the box).{C.RESET}")
            break
        else:
            hint("Type: git status")

    instruction("Commit it (seal the box with a label):")
    show_command('git commit -m "Begin my quest: create hero file"')

    while True:
        cmd = wait_for_command()
        if "git commit" in cmd and "-m" in cmd:
            msg = cmd.split("-m")[-1].strip().strip('"').strip("'")
            if not msg:
                msg = "Begin my quest: create hero file"
            run_git("commit", "-m", msg)
            success("COMMITTED! Your first save point!")
            award_xp(30, "First commit!")
            achievement("First Commit")
            break
        else:
            hint('Type: git commit -m "Begin my quest: create hero file"')

    pause()

    # ─── LAB 4: More History ───
    clear()
    banner("LEVEL 1 — LAB 4: BUILD YOUR HISTORY")
    mission("Make another commit and explore your timeline.")

    instruction("Add a second line to hero.txt:")
    show_command('echo "I completed Level 1!" >> hero.txt')

    while True:
        cmd = wait_for_command()
        if "hero.txt" in cmd:
            append_file("hero.txt", "I completed Level 1!\n")
            success("File updated!")
            break
        else:
            hint('Type: echo "I completed Level 1!" >> hero.txt')

    instruction("See what changed:")
    show_command("git diff")

    while True:
        cmd = wait_for_command()
        if "diff" in cmd:
            ok, out = run_git("diff")
            if out:
                for line in out.split("\n"):
                    if line.startswith("+") and not line.startswith("+++"):
                        print(f"  {C.GREEN}{line}{C.RESET}")
                    elif line.startswith("-") and not line.startswith("---"):
                        print(f"  {C.RED}{line}{C.RESET}")
                    else:
                        print(f"  {C.DIM}{line}{C.RESET}")
                print(f"\n  {C.BOLD}The + line is what you ADDED. Git tracks every change!{C.RESET}")
            break
        else:
            hint("Type: git diff")

    instruction("Stage and commit:")
    show_command("git add hero.txt")

    while True:
        cmd = wait_for_command()
        if "git add" in cmd:
            run_git("add", "hero.txt")
            success("Staged!")
            break
        else:
            hint("Type: git add hero.txt")

    show_command('git commit -m "Update hero: completed Level 1"')

    while True:
        cmd = wait_for_command()
        if "git commit" in cmd:
            msg = "Update hero: completed Level 1"
            try:
                msg = cmd.split("-m")[-1].strip().strip('"').strip("'") or msg
            except:
                pass
            run_git("commit", "-m", msg)
            success("Second commit saved!")
            award_xp(20, "Building history")
            break
        else:
            hint('Type: git commit -m "Update hero: completed Level 1"')

    instruction("View your timeline:")
    show_command("git log --oneline")

    while True:
        cmd = wait_for_command()
        if "log" in cmd:
            ok, out = run_git("log", "--oneline")
            print(f"\n  {C.GREEN}{out.replace(chr(10), chr(10) + '  ')}{C.RESET}")
            print(f"\n  {C.BOLD}Two commits! You can see your entire journey!{C.RESET}")
            achievement("Time Traveler")
            award_xp(10, "Explored history")
            break
        else:
            hint("Type: git log --oneline")

    # ─── Level Complete ───
    clear()
    banner("LEVEL 1 COMPLETE!")
    print(f"""
{C.GREEN}
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║  You learned:                                    ║
    ║                                                  ║
    ║  • git init         → Create a repo              ║
    ║  • git add          → Stage files                ║
    ║  • git commit -m    → Save a snapshot            ║
    ║  • git status       → See what's going on        ║
    ║  • git diff         → See what changed           ║
    ║  • git log          → View your history          ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
{C.RESET}""")
    show_xp()
    pause("Press ENTER to continue to Level 2...")

# ═══════════════════════════════════════════════════════
# LEVEL 2: FIRST BLOOD
# ═══════════════════════════════════════════════════════
def level_2():
    clear()
    banner("LEVEL 2: FIRST BLOOD  ⭐ 200 XP")

    story("You can save your progress. But what happens when")
    story("you make a mistake? Time to learn the UNDO spells.")
    pause()

    # ─── LAB 1: Multiple Files ───
    clear()
    banner("LEVEL 2 — LAB 1: BUILD YOUR PARTY")
    mission("Create multiple files and stage them all at once.")

    instruction("Create three party members:")
    show_command('echo "Warrior - High strength" > warrior.txt')

    while True:
        cmd = wait_for_command()
        if "warrior" in cmd.lower():
            write_file("warrior.txt", "Warrior - High strength\n")
            success("Warrior created!")
            break
        else:
            hint('Type: echo "Warrior - High strength" > warrior.txt')

    show_command('echo "Mage - High intelligence" > mage.txt')
    while True:
        cmd = wait_for_command()
        if "mage" in cmd.lower():
            write_file("mage.txt", "Mage - High intelligence\n")
            success("Mage created!")
            break
        else:
            hint('Type: echo "Mage - High intelligence" > mage.txt')

    show_command('echo "Healer - High wisdom" > healer.txt')
    while True:
        cmd = wait_for_command()
        if "healer" in cmd.lower():
            write_file("healer.txt", "Healer - High wisdom\n")
            success("Healer created!")
            break
        else:
            hint('Type: echo "Healer - High wisdom" > healer.txt')

    instruction("Now stage ALL files at once with the dot shortcut:")
    show_command("git add .")

    while True:
        cmd = wait_for_command()
        if "git add" in cmd:
            run_git("add", ".")
            success("All three files staged at once!")
            print(f"  {C.DIM}The '.' means 'everything that changed'{C.RESET}")
            break
        else:
            hint("Type: git add .")

    instruction("Commit your party:")
    show_command('git commit -m "Recruit party: warrior, mage, healer"')

    while True:
        cmd = wait_for_command()
        if "git commit" in cmd:
            msg = "Recruit party: warrior, mage, healer"
            try:
                msg = cmd.split("-m")[-1].strip().strip('"').strip("'") or msg
            except:
                pass
            run_git("commit", "-m", msg)
            success("Party recruited!")
            award_xp(30, "Multi-file commit")
            break
        else:
            hint('Type: git commit -m "Recruit party: warrior, mage, healer"')

    pause()

    # ─── LAB 2: Undo — Restore ───
    clear()
    banner("LEVEL 2 — LAB 2: UNDO SPELL — RESTORE")
    mission("Undo changes you haven't staged yet.")

    story("Oh no! Someone corrupted your warrior's file!")

    instruction("Break the warrior file on purpose:")
    show_command('echo "CORRUPTED DATA" > warrior.txt')

    while True:
        cmd = wait_for_command()
        if "warrior" in cmd.lower():
            write_file("warrior.txt", "CORRUPTED DATA\n")
            success("File corrupted! 😈")
            break
        else:
            hint('Type: echo "CORRUPTED DATA" > warrior.txt')

    instruction("Check the damage:")
    show_command("git diff warrior.txt")

    while True:
        cmd = wait_for_command()
        if "diff" in cmd:
            ok, out = run_git("diff", "warrior.txt")
            for line in out.split("\n"):
                if line.startswith("+") and not line.startswith("+++"):
                    print(f"  {C.RED}{line}{C.RESET}")
                elif line.startswith("-") and not line.startswith("---"):
                    print(f"  {C.GREEN}{line}{C.RESET}")
            print(f"\n  {C.BOLD}See? Git shows the corruption!{C.RESET}")
            break
        else:
            hint("Type: git diff warrior.txt")

    instruction("Cast the RESTORE spell to undo:")
    show_command("git restore warrior.txt")

    while True:
        cmd = wait_for_command()
        if "restore" in cmd and "warrior" in cmd:
            run_git("restore", "warrior.txt")
            content = read_file("warrior.txt")
            success(f"RESTORED! File says: '{content}'")
            print(f"  {C.BOLD}The corruption is gone! Git had a backup.{C.RESET}")
            award_xp(30, "Restore spell mastered")
            break
        else:
            hint("Type: git restore warrior.txt")

    pause()

    # ─── LAB 3: Unstage ───
    clear()
    banner("LEVEL 2 — LAB 3: UNDO SPELL — UNSTAGE")
    mission("Remove a file from staging without losing changes.")

    instruction("Create and stage a thief:")
    show_command('echo "Thief - High agility" > thief.txt')

    while True:
        cmd = wait_for_command()
        if "thief" in cmd.lower():
            write_file("thief.txt", "Thief - High agility\n")
            success("Thief created!")
            break
        else:
            hint('Type: echo "Thief - High agility" > thief.txt')

    show_command("git add thief.txt")
    while True:
        cmd = wait_for_command()
        if "git add" in cmd:
            run_git("add", "thief.txt")
            success("Thief staged!")
            break
        else:
            hint("Type: git add thief.txt")

    print(f"\n  {C.BOLD}Wait... we don't want the thief yet. UNSTAGE it:{C.RESET}")
    show_command("git restore --staged thief.txt")

    while True:
        cmd = wait_for_command()
        if "restore" in cmd and "staged" in cmd:
            run_git("restore", "--staged", "thief.txt")
            success("Unstaged! The file still exists but won't be committed.")
            award_xp(20, "Unstage spell mastered")
            break
        else:
            hint("Type: git restore --staged thief.txt")

    # Clean up thief
    if os.path.exists(os.path.join(quest_dir, "thief.txt")):
        os.remove(os.path.join(quest_dir, "thief.txt"))

    pause()

    # ─── LAB 4: Amend ───
    clear()
    banner("LEVEL 2 — LAB 4: UNDO SPELL — AMEND")
    mission("Fix a bad commit message.")

    instruction("Make a commit with a typo:")
    write_file("potion.txt", "Health Potion - Restore 50 HP\n")
    run_git("add", "potion.txt")
    show_command('git commit -m "Add heath poton"')

    while True:
        cmd = wait_for_command()
        if "git commit" in cmd:
            run_git("commit", "-m", "Add heath poton")
            success("Committed... but 'heath poton'? That's a typo! 😅")
            break
        else:
            hint('Type: git commit -m "Add heath poton"')

    instruction("Fix it with amend:")
    show_command('git commit --amend -m "Add health potion"')

    while True:
        cmd = wait_for_command()
        if "amend" in cmd:
            msg = "Add health potion"
            try:
                msg = cmd.split("-m")[-1].strip().strip('"').strip("'") or msg
            except:
                pass
            run_git("commit", "--amend", "-m", msg)
            success("Fixed! Check your log — the typo is gone:")
            ok, out = run_git("log", "--oneline", "-1")
            print(f"  {C.GREEN}  {out}{C.RESET}")
            award_xp(20, "Amend spell mastered")
            break
        else:
            hint('Type: git commit --amend -m "Add health potion"')

    pause()

    # ─── LAB 5: Soft Reset ───
    clear()
    banner("LEVEL 2 — LAB 5: UNDO SPELL — RESET")
    mission("Undo your last commit entirely (but keep the files).")

    print(f"""
  {C.BOLD}git reset --soft HEAD~1{C.RESET}

  This means:
  • {C.CYAN}reset{C.RESET}     = go back
  • {C.CYAN}--soft{C.RESET}    = keep the files (just undo the commit)
  • {C.CYAN}HEAD~1{C.RESET}    = go back 1 commit
""")

    instruction("Undo the health potion commit:")
    show_command("git reset --soft HEAD~1")

    while True:
        cmd = wait_for_command()
        if "reset" in cmd and "soft" in cmd:
            run_git("reset", "--soft", "HEAD~1")
            success("Last commit UNDONE! But potion.txt is still here, just staged.")
            ok, out = run_git("status")
            for line in out.split("\n"):
                if "potion" in line:
                    print(f"  {C.GREEN}  {line.strip()}{C.RESET}")
            award_xp(30, "Reset spell mastered")
            break
        else:
            hint("Type: git reset --soft HEAD~1")

    # Re-commit so state is clean
    run_git("commit", "-m", "Add health potion")

    pause()

    # ─── LAB 6: .gitignore ───
    clear()
    banner("LEVEL 2 — LAB 6: THE IGNORE SHIELD")
    mission("Tell Git to ignore files you don't want tracked.")

    story("Some files should NEVER be tracked — passwords, logs, temp files.")

    instruction("Create a secret file:")
    show_command('echo "SECRET_KEY=abc123" > secrets.txt')

    while True:
        cmd = wait_for_command()
        if "secret" in cmd.lower():
            write_file("secrets.txt", "SECRET_KEY=abc123\n")
            success("Secret file created!")
            break
        else:
            hint('Type: echo "SECRET_KEY=abc123" > secrets.txt')

    instruction("Create the ignore shield:")
    show_command('echo "secrets.txt" > .gitignore')

    while True:
        cmd = wait_for_command()
        if "gitignore" in cmd.lower() or "ignore" in cmd.lower():
            write_file(".gitignore", "secrets.txt\n*.log\n")
            success("Ignore shield created!")
            break
        else:
            hint('Type: echo "secrets.txt" > .gitignore')

    instruction("Check status — secrets.txt should be GONE:")
    show_command("git status")

    while True:
        cmd = wait_for_command()
        if "status" in cmd:
            ok, out = run_git("status")
            if "secrets.txt" not in out:
                success("secrets.txt is INVISIBLE to Git! Shield working! 🛡️")
            print(f"  {C.DIM}Only .gitignore shows up — commit it:{C.RESET}")
            break
        else:
            hint("Type: git status")

    run_git("add", ".gitignore")
    run_git("commit", "-m", "Add ignore shield")
    award_xp(20, "Ignore shield activated")

    # ─── Level Complete ───
    clear()
    banner("LEVEL 2 COMPLETE!")
    print(f"""
{C.GREEN}
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║  UNDO SPELLS MASTERED:                           ║
    ║                                                  ║
    ║  • git restore <file>          Undo changes      ║
    ║  • git restore --staged <file> Unstage            ║
    ║  • git commit --amend          Fix last commit   ║
    ║  • git reset --soft HEAD~1     Undo commit        ║
    ║  • .gitignore                  Hide files        ║
    ║  • git add .                   Stage everything  ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
{C.RESET}""")
    show_xp()
    pause("Press ENTER to continue to Level 3: THE MULTIVERSE (Branches!)...")

# ═══════════════════════════════════════════════════════
# LEVEL 3: THE MULTIVERSE (Branching & Merging)
# ═══════════════════════════════════════════════════════
def level_3():
    clear()
    banner("LEVEL 3: THE MULTIVERSE  ⭐ 400 XP")

    print(f"""
  {C.BOLD}This is the level that confuses most people.{C.RESET}
  {C.BOLD}But NOT you — because you're going to DO it.{C.RESET}

  {C.CYAN}A BRANCH is a parallel universe for your code.{C.RESET}

  Imagine you're building a game. It works fine.
  You want to add a new feature — but what if it
  breaks everything?

  {C.GREEN}WITH branches:{C.RESET}

    main (working game) ──────────── still works! ✅
         \\
          feature (experiment) ──── try stuff here 🧪

  If the experiment works → merge it back.
  If it fails → delete it. Main is NEVER broken.
""")
    pause("Ready to create parallel universes? Press ENTER...")

    # ─── LAB 1: Create a Branch ───
    clear()
    banner("LEVEL 3 — LAB 1: YOUR FIRST BRANCH")
    mission("Create a new branch and switch to it.")

    instruction("First, see what branch you're on:")
    show_command("git branch")

    while True:
        cmd = wait_for_command()
        if "branch" in cmd and "checkout" not in cmd and "-b" not in cmd:
            ok, out = run_git("branch")
            print(f"\n  {C.GREEN}{out}{C.RESET}")
            print(f"\n  {C.BOLD}The * means 'you are here'. You're on main.{C.RESET}")
            break
        else:
            hint("Type: git branch")

    instruction("Create AND switch to a new branch:")
    show_command("git checkout -b add-weapons")

    while True:
        cmd = wait_for_command()
        if "checkout" in cmd and "-b" in cmd:
            branch_name = cmd.split()[-1] if len(cmd.split()) > 3 else "add-weapons"
            run_git("checkout", "-b", branch_name)
            cur = get_current_branch()
            success(f"You're now on branch '{cur}'!")
            print(f"\n  {C.BOLD}You just entered a parallel universe! 🌌{C.RESET}")
            award_xp(20, "First branch created")
            break
        else:
            hint("Type: git checkout -b add-weapons")

    pause()

    # ─── LAB 2: Work in a Branch ───
    clear()
    banner("LEVEL 3 — LAB 2: PROOF THAT BRANCHES ARE SEPARATE")
    mission("Add a file on this branch, then watch it DISAPPEAR on main.")

    cur = get_current_branch()
    print(f"\n  {C.BOLD}You're on: {C.CYAN}{cur}{C.RESET}")

    instruction("Create a weapons file:")
    show_command('echo "Sword of Truth - 50 damage" > weapons.txt')

    while True:
        cmd = wait_for_command()
        if "weapon" in cmd.lower():
            write_file("weapons.txt", "Sword of Truth - 50 damage\n")
            success("weapons.txt created!")
            break
        else:
            hint('Type: echo "Sword of Truth - 50 damage" > weapons.txt')

    instruction("Stage and commit:")
    show_command("git add weapons.txt")
    while True:
        cmd = wait_for_command()
        if "git add" in cmd:
            run_git("add", "weapons.txt")
            break
        else:
            hint("Type: git add weapons.txt")

    show_command('git commit -m "Add Sword of Truth"')
    while True:
        cmd = wait_for_command()
        if "git commit" in cmd:
            run_git("commit", "-m", "Add Sword of Truth")
            success("Committed on add-weapons branch!")
            break
        else:
            hint('Type: git commit -m "Add Sword of Truth"')

    print(f"\n  {C.BOLD}Now watch this magic...{C.RESET}")
    pause()

    instruction("Switch back to main:")
    show_command("git checkout main")

    while True:
        cmd = wait_for_command()
        if "checkout" in cmd and "main" in cmd:
            run_git("checkout", "main")
            success("Switched to main!")
            break
        else:
            hint("Type: git checkout main")

    print(f"\n  {C.BOLD}Now check if weapons.txt exists:{C.RESET}")

    if check_file_exists("weapons.txt"):
        print(f"  {C.DIM}weapons.txt is here (fast-forward){C.RESET}")
    else:
        print(f"\n  {C.RED}  ⚡ weapons.txt is GONE!{C.RESET}")
        print(f"  {C.BOLD}  It only exists on add-weapons branch!{C.RESET}")

    instruction("Switch back to confirm it's there:")
    show_command("git checkout add-weapons")

    while True:
        cmd = wait_for_command()
        if "checkout" in cmd and "add-weapons" in cmd:
            run_git("checkout", "add-weapons")
            if check_file_exists("weapons.txt"):
                print(f"\n  {C.GREEN}  ⚡ weapons.txt is BACK!{C.RESET}")
            success("Each branch is its own world! Files appear/disappear!")
            award_xp(40, "Branch isolation proven")
            break
        else:
            hint("Type: git checkout add-weapons")

    pause()

    # ─── LAB 3: First Merge ───
    clear()
    banner("LEVEL 3 — LAB 3: YOUR FIRST MERGE")
    mission("Bring weapons into main.")

    print(f"""
{C.GOLD}  ┌──────────────────────────────────────────┐
  │  THE GOLDEN RULE OF MERGING:             │
  │                                          │
  │  1. Go to the DESTINATION branch first   │
  │  2. Then merge the SOURCE into it        │
  │                                          │
  │  Want weapons in main?                   │
  │  → Go to main  →  merge add-weapons     │
  └──────────────────────────────────────────┘{C.RESET}
""")

    instruction("Step 1 — Go to the destination (main):")
    show_command("git checkout main")

    while True:
        cmd = wait_for_command()
        if "checkout" in cmd and "main" in cmd:
            run_git("checkout", "main")
            success("On main — ready to receive!")
            break
        else:
            hint("Type: git checkout main")

    instruction("Step 2 — Merge weapons into main:")
    show_command("git merge add-weapons")

    while True:
        cmd = wait_for_command()
        if "merge" in cmd:
            ok, out = run_git("merge", "add-weapons")
            print(f"\n  {C.DIM}{out}{C.RESET}")
            if ok:
                success("MERGED! weapons.txt is now on main! 🎉")
            award_xp(40, "First merge!")
            break
        else:
            hint("Type: git merge add-weapons")

    instruction("Clean up — delete the branch:")
    show_command("git branch -d add-weapons")

    while True:
        cmd = wait_for_command()
        if "branch" in cmd and "-d" in cmd:
            run_git("branch", "-d", "add-weapons")
            success("Branch deleted! Clean and tidy.")
            break
        else:
            hint("Type: git branch -d add-weapons")

    instruction("See your history with branches:")
    show_command("git log --oneline --graph --all")

    while True:
        cmd = wait_for_command()
        if "log" in cmd:
            ok, out = run_git("log", "--oneline", "--graph", "--all")
            print(f"\n  {C.GREEN}{out.replace(chr(10), chr(10) + '  ')}{C.RESET}")
            break
        else:
            hint("Type: git log --oneline --graph --all")

    pause()

    # ─── LAB 4: MERGE CONFLICT BOSS FIGHT ───
    clear()
    banner("☠️  BOSS FIGHT: THE MERGE CONFLICT")

    print(f"""
{C.RED}
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║  A MERGE CONFLICT happens when two branches      ║
    ║  change THE SAME LINE in the same file.          ║
    ║                                                  ║
    ║  Git doesn't know which to keep.                 ║
    ║  So it asks YOU to decide.                       ║
    ║                                                  ║
    ║  We're going to CREATE one on purpose            ║
    ║  so you'll never be scared of them again.        ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
{C.RESET}""")
    pause("Ready for the boss fight? Press ENTER...")

    clear()
    banner("BOSS FIGHT — STEP 1: SET THE TRAP")
    mission("Create conflicting changes on two branches.")

    instruction("Create a branch and change hero.txt:")
    show_command("git checkout -b fire-upgrade")

    while True:
        cmd = wait_for_command()
        if "checkout" in cmd and "-b" in cmd:
            run_git("checkout", "-b", "fire-upgrade")
            success("On fire-upgrade branch!")
            break
        else:
            hint("Type: git checkout -b fire-upgrade")

    show_command('echo "Hero Class: Fire Knight" > hero.txt')
    while True:
        cmd = wait_for_command()
        if "hero" in cmd.lower():
            write_file("hero.txt", "Hero Class: Fire Knight\n")
            break
        else:
            hint('Type: echo "Hero Class: Fire Knight" > hero.txt')

    instruction("Stage and commit:")
    show_command("git add hero.txt")
    while True:
        cmd = wait_for_command()
        if "git add" in cmd:
            run_git("add", "hero.txt")
            break
        else:
            hint("Type: git add hero.txt")

    show_command('git commit -m "Upgrade hero to Fire Knight"')
    while True:
        cmd = wait_for_command()
        if "commit" in cmd:
            run_git("commit", "-m", "Upgrade hero to Fire Knight")
            success("Fire Knight committed!")
            break
        else:
            hint('Type: git commit -m "Upgrade hero to Fire Knight"')

    pause()

    instruction("Now go to main and make a DIFFERENT change:")
    show_command("git checkout main")

    while True:
        cmd = wait_for_command()
        if "checkout" in cmd and "main" in cmd:
            run_git("checkout", "main")
            success("Back on main!")
            break
        else:
            hint("Type: git checkout main")

    show_command('echo "Hero Class: Ice Wizard" > hero.txt')
    while True:
        cmd = wait_for_command()
        if "hero" in cmd.lower():
            write_file("hero.txt", "Hero Class: Ice Wizard\n")
            break
        else:
            hint('Type: echo "Hero Class: Ice Wizard" > hero.txt')

    show_command("git add hero.txt")
    while True:
        cmd = wait_for_command()
        if "git add" in cmd:
            run_git("add", "hero.txt")
            break
        else:
            hint("Type: git add hero.txt")

    show_command('git commit -m "Upgrade hero to Ice Wizard"')
    while True:
        cmd = wait_for_command()
        if "commit" in cmd:
            run_git("commit", "-m", "Upgrade hero to Ice Wizard")
            success("Ice Wizard committed on main!")
            break
        else:
            hint('Type: git commit -m "Upgrade hero to Ice Wizard"')

    print(f"""
  {C.RED}
  NOW WE HAVE A CONFLICT:

    main:          hero.txt = "Hero Class: Ice Wizard"
    fire-upgrade:  hero.txt = "Hero Class: Fire Knight"

  Git can't pick for you!{C.RESET}
""")
    pause()

    # ─── Trigger the conflict ───
    clear()
    banner("BOSS FIGHT — STEP 2: TRIGGER THE CONFLICT")

    instruction("Try to merge:")
    show_command("git merge fire-upgrade")

    while True:
        cmd = wait_for_command()
        if "merge" in cmd:
            ok, out = run_git("merge", "fire-upgrade")
            print(f"\n  {C.RED}{out.replace(chr(10), chr(10) + '  ')}{C.RESET}")
            if not ok or "CONFLICT" in out:
                print(f"\n  {C.RED}  ⚡ CONFLICT DETECTED! Don't panic!{C.RESET}")
            break
        else:
            hint("Type: git merge fire-upgrade")

    pause()

    # ─── Resolve the conflict ───
    clear()
    banner("BOSS FIGHT — STEP 3: RESOLVE IT")

    instruction("Look at what's inside hero.txt:")
    show_command("cat hero.txt")

    content = read_file("hero.txt")
    print(f"\n  {C.DIM}File contents:{C.RESET}")
    for line in content.split("\n"):
        if "<<<<<<<" in line:
            print(f"  {C.RED}{line}  ← YOUR branch (main) starts here{C.RESET}")
        elif "=======" in line:
            print(f"  {C.GOLD}{line}  ← Divider between versions{C.RESET}")
        elif ">>>>>>>" in line:
            print(f"  {C.BLUE}{line}  ← Other branch ends here{C.RESET}")
        else:
            print(f"  {C.BOLD}{line}{C.RESET}")

    while True:
        cmd = wait_for_command("Press ENTER when you've seen the markers: ")
        break

    print(f"""
  {C.BOLD}
  YOUR JOB: Delete the markers and keep what you want.
  Let's combine both — make a Fire-Ice Battle Mage!{C.RESET}
""")

    instruction("Replace the file with your resolved version:")
    show_command('echo "Hero Class: Fire-Ice Battle Mage" > hero.txt')

    while True:
        cmd = wait_for_command()
        if "hero" in cmd.lower():
            write_file("hero.txt", "Hero Class: Fire-Ice Battle Mage\n")
            success("Conflict resolved! You chose your own path!")
            break
        else:
            hint('Type: echo "Hero Class: Fire-Ice Battle Mage" > hero.txt')

    instruction("Tell Git you fixed it:")
    show_command("git add hero.txt")

    while True:
        cmd = wait_for_command()
        if "git add" in cmd:
            run_git("add", "hero.txt")
            success("Marked as resolved!")
            break
        else:
            hint("Type: git add hero.txt")

    instruction("Complete the merge:")
    show_command('git commit -m "Merge: combine fire and ice into Battle Mage"')

    while True:
        cmd = wait_for_command()
        if "commit" in cmd:
            run_git("commit", "-m", "Merge: combine fire and ice into Battle Mage")
            break
        else:
            hint('Type: git commit -m "Merge: combine fire and ice into Battle Mage"')

    run_git("branch", "-d", "fire-upgrade")

    clear()
    print(f"""
{C.GREEN}
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║           ☠️  BOSS DEFEATED!  ☠️                   ║
    ║                                                  ║
    ║   You resolved a merge conflict!                 ║
    ║   It's just:                                     ║
    ║                                                  ║
    ║   1. Edit the file (remove markers)              ║
    ║   2. git add <file>                              ║
    ║   3. git commit                                  ║
    ║                                                  ║
    ║   That's it. Never be scared again.              ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
{C.RESET}""")
    award_xp(100, "MERGE CONFLICT BOSS DEFEATED!")
    achievement("Conflict Resolver")
    achievement("Branch Master")

    show_xp()
    pause("Press ENTER to continue to Level 4...")

# ═══════════════════════════════════════════════════════
# LEVEL 4: THE CLOUD KINGDOM
# ═══════════════════════════════════════════════════════
def level_4():
    clear()
    banner("LEVEL 4: THE CLOUD KINGDOM  ⭐ 300 XP")

    print(f"""
  {C.BOLD}Everything so far has been LOCAL (on your computer).{C.RESET}

  Now we connect to GitHub — the cloud.

  {C.CYAN}git push{C.RESET}  = Upload your commits to GitHub
  {C.CYAN}git pull{C.RESET}  = Download commits from GitHub
  {C.CYAN}git clone{C.RESET} = Copy entire repo from GitHub

  {C.DIM}You need a GitHub account for this level.
  If you don't have one, go to github.com and create one (free).{C.RESET}
""")

    print(f"\n  {C.BOLD}Do you have a GitHub account?{C.RESET}")
    print(f"  {C.DIM}(If not, the game will teach the concepts and you can")
    print(f"   try the commands later when you have an account){C.RESET}")

    answer = input(f"\n  {C.CYAN}Type 'yes' or 'no': {C.RESET}").strip().lower()

    if answer in ["yes", "y"]:
        clear()
        banner("LEVEL 4 — LAB 1: CONNECT TO GITHUB")
        mission("Push your git-quest to GitHub.")

        print(f"""
  {C.BOLD}Step 1:{C.RESET} Go to github.com
  {C.BOLD}Step 2:{C.RESET} Click "+" → "New repository"
  {C.BOLD}Step 3:{C.RESET} Name it: git-quest
  {C.BOLD}Step 4:{C.RESET} Do NOT check "Add README"
  {C.BOLD}Step 5:{C.RESET} Click "Create repository"
  {C.BOLD}Step 6:{C.RESET} Copy the URL (https://github.com/YOU/git-quest.git)
""")
        url = input(f"\n  {C.CYAN}Paste your GitHub URL here: {C.RESET}").strip()

        if url:
            instruction("Add the remote:")
            show_command(f"git remote add origin {url}")

            while True:
                cmd = wait_for_command()
                if "remote" in cmd and "add" in cmd:
                    run_git("remote", "add", "origin", url)
                    success("Remote added!")
                    break
                else:
                    hint(f"Type: git remote add origin {url}")

            instruction("Push to GitHub:")
            show_command("git push -u origin main")

            while True:
                cmd = wait_for_command()
                if "push" in cmd:
                    print(f"\n  {C.DIM}Pushing... (this may ask for credentials){C.RESET}")
                    ok, out = run_git("push", "-u", "origin", "main")
                    if ok:
                        success("YOUR CODE IS ON GITHUB! 🎉 Go check it in your browser!")
                        achievement("Cloud Warrior")
                        award_xp(100, "Pushed to GitHub!")
                    else:
                        print(f"\n  {C.DIM}{out}{C.RESET}")
                        print(f"\n  {C.GOLD}If this failed, you may need to:")
                        print(f"  - Create a Personal Access Token on GitHub")
                        print(f"  - Settings → Developer Settings → Tokens{C.RESET}")
                        award_xp(50, "Attempted push (setup needed)")
                    break
                else:
                    hint("Type: git push -u origin main")
        else:
            print(f"\n  {C.DIM}No URL provided. That's fine — we'll cover the concepts.{C.RESET}")
            award_xp(50, "Remote concepts learned")

    else:
        award_xp(50, "Remote concepts learned")

    pause()

    clear()
    banner("LEVEL 4 — THE DAILY WORKFLOW")

    print(f"""
{C.GREEN}
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║  YOUR DAILY ROUTINE WITH GITHUB:                 ║
    ║                                                  ║
    ║  Morning:                                        ║
    ║    git pull              ← Get latest changes    ║
    ║                                                  ║
    ║  During work:                                    ║
    ║    git add .             ← Stage                 ║
    ║    git commit -m "msg"   ← Commit                ║
    ║                                                  ║
    ║  End of day:                                     ║
    ║    git push              ← Upload to GitHub      ║
    ║                                                  ║
    ║  That's the whole routine!                       ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
{C.RESET}""")

    print(f"""
  {C.BOLD}Key commands:{C.RESET}

  {C.CYAN}git clone <url>{C.RESET}        Download a repo for the first time
  {C.CYAN}git push{C.RESET}               Upload your commits
  {C.CYAN}git pull{C.RESET}               Download + merge latest changes
  {C.CYAN}git remote -v{C.RESET}          See your remote connections
  {C.CYAN}git push -u origin main{C.RESET} First push (sets up tracking)
""")

    award_xp(100, "Cloud Kingdom concepts mastered")
    show_xp()
    pause("Press ENTER to continue to the FINAL LEVEL...")

# ═══════════════════════════════════════════════════════
# LEVEL 5: THE FINAL BOSS
# ═══════════════════════════════════════════════════════
def level_5():
    clear()
    banner("LEVEL 5: THE FINAL BOSS  ⭐ 500 XP")

    story("You've come far. Now learn emergency recovery")
    story("and the advanced spells that make you a Git ninja.")
    pause()

    # ─── LAB 1: Stash ───
    clear()
    banner("LEVEL 5 — LAB 1: THE STASH SPELL")
    mission("Save work temporarily without committing.")

    print(f"""
  {C.BOLD}Scenario:{C.RESET} You're working on something, but suddenly
  need to switch branches. Your work isn't ready to commit.

  {C.CYAN}git stash{C.RESET}     = Hide your changes temporarily
  {C.CYAN}git stash pop{C.RESET} = Bring them back
""")

    instruction("Start some work:")
    show_command('echo "World Map - Forest Region" > map.txt')

    while True:
        cmd = wait_for_command()
        if "map" in cmd.lower():
            write_file("map.txt", "World Map - Forest Region\n")
            success("Map started!")
            break
        else:
            hint('Type: echo "World Map - Forest Region" > map.txt')

    instruction("Stash it (hide temporarily):")
    show_command("git stash")

    while True:
        cmd = wait_for_command()
        if cmd.strip() == "git stash" or "stash" in cmd:
            run_git("add", "map.txt")
            ok, out = run_git("stash")
            print(f"  {C.DIM}{out}{C.RESET}")
            success("Changes stashed! Your working directory is clean.")
            break
        else:
            hint("Type: git stash")

    print(f"\n  {C.BOLD}map.txt is hidden. Check:{C.RESET}")
    exists = check_file_exists("map.txt")
    if not exists:
        print(f"  {C.RED}map.txt = GONE (stashed safely){C.RESET}")

    instruction("Bring it back:")
    show_command("git stash pop")

    while True:
        cmd = wait_for_command()
        if "stash" in cmd and "pop" in cmd:
            run_git("stash", "pop")
            if check_file_exists("map.txt"):
                success("map.txt is BACK! Stash is powerful! 💪")
            award_xp(50, "Stash spell mastered")
            break
        else:
            hint("Type: git stash pop")

    # Commit map
    run_git("add", "map.txt")
    run_git("commit", "-m", "Add world map")

    pause()

    # ─── LAB 2: Emergency Recovery ───
    clear()
    banner("LEVEL 5 — LAB 2: EMERGENCY RECOVERY")
    mission("Recover from disasters.")

    print(f"\n  {C.BOLD}Emergency 1: Accidentally deleted a file{C.RESET}")

    instruction("Delete warrior.txt 'by accident':")
    show_command("rm warrior.txt")

    while True:
        cmd = wait_for_command()
        if "rm" in cmd or "del" in cmd or "remove" in cmd:
            path = os.path.join(quest_dir, "warrior.txt")
            if os.path.exists(path):
                os.remove(path)
            success("warrior.txt DELETED! 😱")
            break
        else:
            hint("Type: rm warrior.txt (or del warrior.txt on Windows)")

    instruction("RESTORE it from Git:")
    show_command("git restore warrior.txt")

    while True:
        cmd = wait_for_command()
        if "restore" in cmd and "warrior" in cmd:
            run_git("restore", "warrior.txt")
            if check_file_exists("warrior.txt"):
                success("warrior.txt is BACK! Git never forgets! 🎉")
                award_xp(40, "File recovery mastered")
            break
        else:
            hint("Type: git restore warrior.txt")

    pause()

    # ─── Emergency 2: Bad commit ───
    clear()
    banner("LEVEL 5 — LAB 3: UNDO A BAD COMMIT")
    mission("Remove a commit you didn't want.")

    instruction("Make a bad commit:")
    show_command('echo "GARBAGE DATA" > oops.txt')

    while True:
        cmd = wait_for_command()
        if "oops" in cmd.lower() or "garbage" in cmd.lower():
            write_file("oops.txt", "GARBAGE DATA\n")
            success("Bad file created!")
            break
        else:
            hint('Type: echo "GARBAGE DATA" > oops.txt')

    show_command("git add oops.txt")
    while True:
        cmd = wait_for_command()
        if "add" in cmd:
            run_git("add", "oops.txt")
            break
        else:
            hint("Type: git add oops.txt")

    show_command('git commit -m "Oops bad commit"')
    while True:
        cmd = wait_for_command()
        if "commit" in cmd:
            run_git("commit", "-m", "Oops bad commit")
            success("Bad commit made. Now UNDO it!")
            break
        else:
            hint('Type: git commit -m "Oops bad commit"')

    instruction("Undo the commit (keep files):")
    show_command("git reset --soft HEAD~1")

    while True:
        cmd = wait_for_command()
        if "reset" in cmd:
            run_git("reset", "--soft", "HEAD~1")
            success("Commit UNDONE! The file is still here but uncommitted.")
            award_xp(40, "Commit recovery mastered")
            break
        else:
            hint("Type: git reset --soft HEAD~1")

    # Clean up
    run_git("restore", "--staged", "oops.txt")
    oops_path = os.path.join(quest_dir, "oops.txt")
    if os.path.exists(oops_path):
        os.remove(oops_path)

    pause()

    # ─── LAB 4: Reflog ───
    clear()
    banner("LEVEL 5 — LAB 4: THE REFLOG — YOUR SAFETY NET")
    mission("See EVERYTHING that ever happened.")

    instruction("Type the ultimate safety net command:")
    show_command("git reflog")

    while True:
        cmd = wait_for_command()
        if "reflog" in cmd:
            ok, out = run_git("reflog")
            lines = out.split("\n")[:10]
            for line in lines:
                print(f"  {C.GREEN}{line}{C.RESET}")
            print(f"\n  {C.BOLD}This shows EVERY action — even deleted commits!{C.RESET}")
            print(f"  {C.BOLD}You can recover ANYTHING with: git checkout <hash>{C.RESET}")
            achievement("Rescue Ranger")
            award_xp(40, "Reflog mastered")
            break
        else:
            hint("Type: git reflog")

    pause()

    # ─── LAB 5: Aliases ───
    clear()
    banner("LEVEL 5 — LAB 5: POWER-UP — GIT ALIASES")
    mission("Create shortcuts for commands you use all the time.")

    instruction("Create a shortcut for 'git status':")
    show_command("git config --global alias.st status")

    while True:
        cmd = wait_for_command()
        if "alias" in cmd:
            os.system(cmd)
            success("Alias created!")
            break
        else:
            hint("Type: git config --global alias.st status")

    instruction("Create a shortcut for the visual log:")
    show_command('git config --global alias.lg "log --oneline --graph --all"')

    while True:
        cmd = wait_for_command()
        if "alias" in cmd and "lg" in cmd:
            os.system(cmd)
            success("Alias created!")
            break
        else:
            hint('Type: git config --global alias.lg "log --oneline --graph --all"')

    instruction("Try your new shortcuts:")
    show_command("git st")

    while True:
        cmd = wait_for_command()
        if "git st" in cmd or "git lg" in cmd:
            ok, out = run_git(cmd.replace("git ", ""))
            print(f"  {C.GREEN}{out.replace(chr(10), chr(10) + '  ')}{C.RESET}")
            success("Shortcuts working! So much faster! ⚡")
            award_xp(30, "Aliases configured")
            break
        else:
            hint("Type: git st")

    pause()

    # ─── The Complete Mental Model ───
    clear()
    banner("THE COMPLETE GIT MENTAL MODEL")

    print(f"""
{C.GOLD}
  ┌────────────────────────────────────────────────────────┐
  │                                                        │
  │   YOUR DAILY LIFE WITH GIT:                            │
  │                                                        │
  │   1. git pull              ← Get latest                │
  │   2. git checkout -b feat  ← Branch for your work      │
  │   3. ... edit files ...    ← Do your thing             │
  │   4. git add .             ← Stage changes             │
  │   5. git commit -m "msg"   ← Save snapshot             │
  │   6. ... repeat 3-5 ...    ← Keep working              │
  │   7. git checkout main     ← Switch to main            │
  │   8. git merge feat        ← Merge your work           │
  │   9. git push              ← Upload to GitHub          │
  │   10. git branch -d feat   ← Clean up                  │
  │                                                        │
  │   THAT'S IT. THAT'S 95% OF GIT.                        │
  │                                                        │
  └────────────────────────────────────────────────────────┘
{C.RESET}""")

    award_xp(100, "FINAL BOSS COMPLETE!")
    show_xp()

# ═══════════════════════════════════════════════════════
# LEVEL 6: THE GUILD (Team Workflow)
# ═══════════════════════════════════════════════════════
def level_6():
    global current_level
    clear()
    banner("LEVEL 6: THE GUILD  ⭐ 600 XP")

    print(f"""
  {C.BOLD}Welcome to the real world, developer.{C.RESET}

  In companies, you don't work alone. Teams of 5, 10, 50
  developers all push to the SAME repository.

  {C.CYAN}How do you avoid chaos?{C.RESET}

  With CONVENTIONS — rules everyone agrees on.
  This level teaches you the workflows real teams use.
""")
    pause()

    # ─── LAB 1: Branch Naming Conventions ───
    clear()
    banner("LEVEL 6 — LAB 1: BRANCH NAMING CONVENTIONS")
    mission("Learn how professional teams name branches.")

    print(f"""
  {C.BOLD}In companies, branches follow naming rules:{C.RESET}

  {C.GREEN}feature/{C.RESET}user-login       New features
  {C.GREEN}bugfix/{C.RESET}login-crash       Bug fixes
  {C.GREEN}hotfix/{C.RESET}security-patch    Urgent production fixes
  {C.GREEN}release/{C.RESET}v2.1.0           Release preparation
  {C.GREEN}docs/{C.RESET}update-readme       Documentation changes

  {C.DIM}Many teams also include ticket numbers:{C.RESET}
  {C.GREEN}feature/{C.RESET}JIRA-1234-user-login

  This way, anyone can tell what a branch is for
  just by looking at its name.
""")

    instruction("Create a feature branch the professional way:")
    show_command("git checkout -b feature/add-inventory")

    while True:
        cmd = wait_for_command()
        if "checkout" in cmd and "-b" in cmd and ("feature/" in cmd or "feature\\" in cmd):
            branch = cmd.split()[-1] if len(cmd.split()) > 3 else "feature/add-inventory"
            run_git("checkout", "-b", branch)
            success(f"Professional branch created: {branch}")
            award_xp(30, "Branch naming conventions")
            break
        else:
            hint("Type: git checkout -b feature/add-inventory")

    instruction("Add some work on this feature:")
    show_command('echo "Inventory: Sword, Shield, Potion" > inventory.txt')

    while True:
        cmd = wait_for_command()
        if "inventory" in cmd.lower():
            write_file("inventory.txt", "Inventory: Sword, Shield, Potion\n")
            success("Inventory file created!")
            break
        else:
            hint('Type: echo "Inventory: Sword, Shield, Potion" > inventory.txt')

    show_command("git add inventory.txt")
    while True:
        cmd = wait_for_command()
        if "git add" in cmd:
            run_git("add", "inventory.txt")
            break
        else:
            hint("Type: git add inventory.txt")

    print(f"""
  {C.BOLD}Pro tip — Conventional Commit Messages:{C.RESET}

  Most companies use this format:  {C.CYAN}type: description{C.RESET}

  {C.GREEN}feat:{C.RESET}     New feature          {C.GREEN}fix:{C.RESET}      Bug fix
  {C.GREEN}docs:{C.RESET}     Documentation        {C.GREEN}refactor:{C.RESET} Code restructure
  {C.GREEN}test:{C.RESET}     Adding tests          {C.GREEN}chore:{C.RESET}    Maintenance
""")

    instruction("Commit with a conventional message:")
    show_command('git commit -m "feat: add inventory system"')

    while True:
        cmd = wait_for_command()
        if "commit" in cmd:
            msg = cmd.split("-m")[-1].strip().strip('"').strip("'") if "-m" in cmd else "feat: add inventory system"
            if not msg:
                msg = "feat: add inventory system"
            run_git("commit", "-m", msg)
            success("Committed with professional format!")
            award_xp(20, "Conventional commit")
            break
        else:
            hint('Type: git commit -m "feat: add inventory system"')

    pause()

    # ─── LAB 2: Simulating a Teammate ───
    clear()
    banner("LEVEL 6 — LAB 2: WORKING WITH TEAMMATES")
    mission("See what happens when a coworker pushes to main.")

    print(f"""
  {C.BOLD}Real scenario:{C.RESET}

  You're on your feature branch, working away.
  Meanwhile, your teammate Sarah pushes new code to main.

  {C.RED}Your branch is now BEHIND main.{C.RESET}

  This happens EVERY DAY in real teams.
  Let's simulate it.
""")

    instruction("Switch to main:")
    show_command("git checkout main")

    while True:
        cmd = wait_for_command()
        if "checkout" in cmd and "main" in cmd:
            run_git("checkout", "main")
            success("On main!")
            break
        else:
            hint("Type: git checkout main")

    story("(Simulating Sarah's work on main...)")
    time.sleep(1)

    write_file("api.txt", "API Module - handles HTTP requests\nEndpoint: /users GET\nEndpoint: /login POST\n")
    run_git("add", "api.txt")
    run_git("commit", "-m", "feat: add API module (by Sarah)")

    write_file("database.txt", "Database: PostgreSQL\nTable: users (id, name, email)\nTable: sessions (id, user_id, token)\n")
    run_git("add", "database.txt")
    run_git("commit", "-m", "feat: add database schema (by Sarah)")

    print(f"\n  {C.GREEN}Sarah made 2 commits on main while you were working!{C.RESET}")

    instruction("Check the log to see Sarah's commits:")
    show_command("git log --oneline -5")

    while True:
        cmd = wait_for_command()
        if "log" in cmd:
            ok, out = run_git("log", "--oneline", "-5")
            print(f"\n  {C.GREEN}{out.replace(chr(10), chr(10) + '  ')}{C.RESET}")
            success("See Sarah's commits? Main moved ahead without you!")
            break
        else:
            hint("Type: git log --oneline -5")

    instruction("Switch back to your feature branch:")
    show_command("git checkout feature/add-inventory")

    while True:
        cmd = wait_for_command()
        if "checkout" in cmd and "feature" in cmd:
            run_git("checkout", "feature/add-inventory")
            success("Back on your feature branch!")
            break
        else:
            hint("Type: git checkout feature/add-inventory")

    print(f"\n  {C.RED}Your branch does NOT have Sarah's commits!{C.RESET}")
    print(f"  {C.BOLD}You need to get up to date before your code can be merged.{C.RESET}")
    award_xp(30, "Team simulation")

    pause()

    # ─── LAB 3: Staying Up to Date ───
    clear()
    banner("LEVEL 6 — LAB 3: STAYING UP TO DATE")
    mission("Merge main into your branch to get teammates' changes.")

    print(f"""
  {C.BOLD}Two ways to stay current:{C.RESET}

  {C.CYAN}Option A: git merge main{C.RESET}
    Brings main's changes into your branch
    Creates a merge commit
    {C.GREEN}Safer, easier for beginners{C.RESET}

  {C.CYAN}Option B: git rebase main{C.RESET}
    Replays your commits on top of main
    Cleaner history (no merge commit)
    {C.GOLD}Advanced — we'll use merge for now{C.RESET}

  {C.DIM}Most teams prefer one or the other. Both are valid.{C.RESET}
""")

    instruction("Merge main into your feature branch:")
    show_command("git merge main")

    while True:
        cmd = wait_for_command()
        if "merge" in cmd and "main" in cmd:
            ok, out = run_git("merge", "main")
            print(f"\n  {C.DIM}{out}{C.RESET}")
            success("Your branch now has Sarah's changes PLUS your own work!")
            award_xp(40, "Branch sync mastered")
            break
        else:
            hint("Type: git merge main")

    instruction("Verify — you should have everything:")
    show_command("git log --oneline --graph -6")

    while True:
        cmd = wait_for_command()
        if "log" in cmd:
            ok, out = run_git("log", "--oneline", "--graph", "-6")
            print(f"\n  {C.GREEN}{out.replace(chr(10), chr(10) + '  ')}{C.RESET}")
            print(f"\n  {C.BOLD}You have it all! Sarah's API & DB + your inventory.{C.RESET}")
            break
        else:
            hint("Type: git log --oneline --graph -6")

    pause()

    # ─── LAB 4: Git Blame ───
    clear()
    banner("LEVEL 6 — LAB 4: GIT BLAME — WHO WROTE THIS?")
    mission("Find out who wrote each line in a file.")

    print(f"""
  {C.BOLD}Scenario:{C.RESET} You found a bug in the API module.
  You need to know WHO wrote that line so you can ask them.

  {C.CYAN}git blame <file>{C.RESET} shows who last modified each line.

  {C.DIM}(In a real team this shows different names.
   Here it shows yours since we simulated Sarah.){C.RESET}
""")

    instruction("Blame the API file:")
    show_command("git blame api.txt")

    while True:
        cmd = wait_for_command()
        if "blame" in cmd:
            ok, out = run_git("blame", "api.txt")
            print(f"\n  {C.GREEN}{out.replace(chr(10), chr(10) + '  ')}{C.RESET}")
            print(f"\n  {C.BOLD}Each line shows: commit | author | date | content{C.RESET}")
            print(f"  {C.DIM}Now you know who to ask about the API bug!{C.RESET}")
            award_xp(30, "Git blame mastered")
            achievement("Detective")
            break
        else:
            hint("Type: git blame api.txt")

    pause()

    # ─── LAB 5: Cherry-Pick ───
    clear()
    banner("LEVEL 6 — LAB 5: CHERRY-PICK — STEAL ONE COMMIT")
    mission("Take ONE specific commit from another branch.")

    print(f"""
  {C.BOLD}Scenario:{C.RESET} A coworker made a critical bugfix on THEIR
  feature branch. You need that fix NOW on main, but
  you don't want their whole branch — just that ONE commit.

  {C.CYAN}git cherry-pick <hash>{C.RESET} copies a single commit
  to your current branch.

  {C.DIM}This is used ALL the time for hotfixes in real companies!{C.RESET}
""")

    # Merge current feature to main first, then set up scenario
    run_git("checkout", "main")
    run_git("merge", "feature/add-inventory")
    run_git("branch", "-d", "feature/add-inventory")

    # Create Sarah's branch with a mix of commits
    run_git("checkout", "-b", "feature/sarah-logging")
    write_file("logging.txt", "Logger: console output\nLevel: INFO\n")
    run_git("add", "logging.txt")
    run_git("commit", "-m", "feat: add logging module")

    write_file("security-patch.txt", "CRITICAL FIX: patch XSS vulnerability in login form\n")
    run_git("add", "security-patch.txt")
    run_git("commit", "-m", "fix: patch XSS vulnerability")

    # Get the hash of the security fix commit
    ok, fix_log = run_git("log", "--oneline", "-1")
    fix_hash = fix_log.strip().split()[0] if ok else "abc1234"

    write_file("experimental.txt", "Experimental feature - WIP do not merge\n")
    run_git("add", "experimental.txt")
    run_git("commit", "-m", "wip: experimental feature (not ready)")

    print(f"\n  {C.BOLD}Sarah's branch has 3 commits:{C.RESET}")

    instruction("Look at Sarah's commits:")
    show_command("git log --oneline -3")

    while True:
        cmd = wait_for_command()
        if "log" in cmd:
            ok, out = run_git("log", "--oneline", "-3")
            print(f"\n  {C.GREEN}{out.replace(chr(10), chr(10) + '  ')}{C.RESET}")
            print(f"\n  {C.BOLD}We ONLY want the security fix (commit {C.CYAN}{fix_hash}{C.BOLD}).{C.RESET}")
            break
        else:
            hint("Type: git log --oneline -3")

    instruction("Go back to main:")
    show_command("git checkout main")

    while True:
        cmd = wait_for_command()
        if "checkout" in cmd and "main" in cmd:
            run_git("checkout", "main")
            break
        else:
            hint("Type: git checkout main")

    instruction(f"Cherry-pick JUST the security fix:")
    show_command(f"git cherry-pick {fix_hash}")

    while True:
        cmd = wait_for_command()
        if "cherry-pick" in cmd:
            hash_to_pick = cmd.split()[-1] if len(cmd.split()) > 2 else fix_hash
            ok, out = run_git("cherry-pick", hash_to_pick)
            if ok:
                success("Security fix cherry-picked onto main!")
                print(f"  {C.BOLD}The logging and experimental commits stayed on Sarah's branch.{C.RESET}")
            else:
                print(f"  {C.DIM}{out}{C.RESET}")
                run_git("cherry-pick", fix_hash)
                success("Cherry-picked!")
            award_xp(50, "Cherry-pick mastered")
            break
        else:
            hint(f"Type: git cherry-pick {fix_hash}")

    # Clean up
    run_git("branch", "-D", "feature/sarah-logging")

    # ─── Level Complete ───
    clear()
    banner("LEVEL 6 COMPLETE!")
    print(f"""
{C.GREEN}
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║  TEAM WORKFLOW MASTERED:                         ║
    ║                                                  ║
    ║  • feature/ branch naming    Company convention  ║
    ║  • Conventional commits      Team standard       ║
    ║  • Simulating teammates      Real-world flow     ║
    ║  • git merge main            Stay up to date     ║
    ║  • git blame                 Who wrote this?     ║
    ║  • git cherry-pick           Steal one commit    ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
{C.RESET}""")

    achievement("Team Player")
    current_level = max(current_level, 7)
    save_progress()
    show_xp()
    pause("Press ENTER to continue to Level 7: THE WAR ROOM...")

# ═══════════════════════════════════════════════════════
# LEVEL 7: THE WAR ROOM (Code Review & Clean History)
# ═══════════════════════════════════════════════════════
def level_7():
    global current_level
    clear()
    banner("LEVEL 7: THE WAR ROOM  ⭐ 500 XP")

    print(f"""
  {C.BOLD}In real companies, code doesn't just go to main.{C.RESET}

  It goes through CODE REVIEW first.

  Before your code is merged, teammates:
  • Read your changes (the diff)
  • Leave comments
  • Request changes
  • Approve it

  {C.CYAN}Your job: make your commits CLEAN and REVIEWABLE.{C.RESET}
  {C.DIM}Messy commits = angry reviewers = slow merges!{C.RESET}
""")
    pause()

    # ─── LAB 1: Squashing Commits ───
    clear()
    banner("LEVEL 7 — LAB 1: SQUASH — CLEAN UP YOUR MESS")
    mission("Turn multiple messy commits into one clean commit.")

    print(f"""
  {C.BOLD}Real scenario:{C.RESET}

  You're working on a feature. You make commits like:

  {C.RED}  "wip"
  "fix typo"
  "oops forgot a file"
  "actually fix it this time"
  "final fix for real"{C.RESET}

  Your reviewer does NOT want to see that mess.

  {C.CYAN}git merge --squash{C.RESET} combines all commits from a
  branch into ONE clean commit when merging to main.
""")

    instruction("Create a messy feature branch:")
    show_command("git checkout -b feature/messy-work")

    while True:
        cmd = wait_for_command()
        if "checkout" in cmd and "-b" in cmd:
            run_git("checkout", "-b", "feature/messy-work")
            success("On feature branch!")
            break
        else:
            hint("Type: git checkout -b feature/messy-work")

    story("Let's simulate messy development...")
    time.sleep(0.5)

    write_file("dashboard.txt", "Dashboard v1\n")
    run_git("add", "dashboard.txt")
    run_git("commit", "-m", "wip dashboard")

    write_file("dashboard.txt", "Dashboard v1\nCharts: bar, line\n")
    run_git("add", "dashboard.txt")
    run_git("commit", "-m", "add charts idk")

    write_file("dashboard.txt", "Dashboard v1\nCharts: bar, line, pie\nFilters: date, user\n")
    run_git("add", "dashboard.txt")
    run_git("commit", "-m", "more stuff")

    write_file("dashboard.txt", "Dashboard v2\nCharts: bar, line, pie\nFilters: date, user, status\nExport: CSV, PDF\n")
    run_git("add", "dashboard.txt")
    run_git("commit", "-m", "ok final version hopefully")

    print(f"\n  {C.RED}Look at this messy history:{C.RESET}")
    ok, out = run_git("log", "--oneline", "-4")
    print(f"\n  {C.RED}{out.replace(chr(10), chr(10) + '  ')}{C.RESET}")
    print(f"\n  {C.BOLD}Nobody wants to review 4 messy commits! Let's fix it.{C.RESET}")

    pause()

    instruction("Switch to main:")
    show_command("git checkout main")

    while True:
        cmd = wait_for_command()
        if "checkout" in cmd and "main" in cmd:
            run_git("checkout", "main")
            break
        else:
            hint("Type: git checkout main")

    instruction("Squash merge — combines all 4 commits into ONE:")
    show_command("git merge --squash feature/messy-work")

    while True:
        cmd = wait_for_command()
        if "merge" in cmd and "squash" in cmd:
            ok, out = run_git("merge", "--squash", "feature/messy-work")
            print(f"  {C.DIM}{out}{C.RESET}")
            success("All changes staged but NOT committed yet!")
            print(f"  {C.BOLD}Now write ONE clean message for all that work:{C.RESET}")
            break
        else:
            hint("Type: git merge --squash feature/messy-work")

    instruction("Write the clean commit message:")
    show_command('git commit -m "feat: add dashboard with charts, filters, and export"')

    while True:
        cmd = wait_for_command()
        if "commit" in cmd:
            msg = "feat: add dashboard with charts, filters, and export"
            try:
                msg = cmd.split("-m")[-1].strip().strip('"').strip("'") or msg
            except:
                pass
            run_git("commit", "-m", msg)
            success("ONE clean commit instead of 4 messy ones! ✨")
            award_xp(50, "Squash merge mastered")
            achievement("Clean Coder")
            break
        else:
            hint('Type: git commit -m "feat: add dashboard with charts, filters, and export"')

    run_git("branch", "-D", "feature/messy-work")

    pause()

    # ─── LAB 2: Git Bisect ───
    clear()
    banner("LEVEL 7 — LAB 2: GIT BISECT — HUNT THE BUG")
    mission("Use binary search to find which commit broke things.")

    print(f"""
  {C.BOLD}Scenario:{C.RESET} Something is broken. You have 100 commits.
  Which one introduced the bug?

  Checking each one manually = {C.RED}100 checks{C.RESET}
  Using git bisect            = {C.GREEN}~7 checks!{C.RESET} (binary search)

  {C.CYAN}git bisect{C.RESET} does a binary search through your
  commit history. You tell it "good" or "bad" and
  it narrows down the exact broken commit.
""")

    story("Let's create history with a hidden bug...")
    time.sleep(0.5)

    write_file("app.txt", "App v1.0 - Working\n")
    run_git("add", "app.txt")
    run_git("commit", "-m", "v1.0: initial release")

    write_file("app.txt", "App v1.1 - Added search\n")
    run_git("add", "app.txt")
    run_git("commit", "-m", "v1.1: add search feature")

    write_file("app.txt", "App v1.2 - Added filters\n")
    run_git("add", "app.txt")
    run_git("commit", "-m", "v1.2: add filters")

    # The bad commit
    write_file("app.txt", "App v1.3 - BUG INTRODUCED HERE\n")
    run_git("add", "app.txt")
    run_git("commit", "-m", "v1.3: refactor database layer")

    write_file("app.txt", "App v1.4 - Added export (still has BUG)\n")
    run_git("add", "app.txt")
    run_git("commit", "-m", "v1.4: add export feature")

    write_file("app.txt", "App v1.5 - Added settings (still has BUG)\n")
    run_git("add", "app.txt")
    run_git("commit", "-m", "v1.5: add settings page")

    ok, log_out = run_git("log", "--oneline", "-6")
    commits = log_out.strip().split("\n")

    print(f"\n  {C.BOLD}Commit History:{C.RESET}")
    for c in commits:
        print(f"    {C.DIM}{c}{C.RESET}")

    print(f"""
  {C.RED}The app is broken!{C.RESET} Something went wrong between
  v1.0 (which worked) and v1.5 (which is broken).

  {C.BOLD}Let's use bisect to find the exact bad commit.{C.RESET}
""")

    instruction("Start the bisect hunt:")
    show_command("git bisect start")

    while True:
        cmd = wait_for_command()
        if "bisect" in cmd and "start" in cmd:
            ok, out = run_git("bisect", "start")
            success("Bisect mode activated!")
            break
        else:
            hint("Type: git bisect start")

    instruction("Tell Git the current state is BAD (broken):")
    show_command("git bisect bad")

    while True:
        cmd = wait_for_command()
        if "bisect" in cmd and "bad" in cmd:
            ok, out = run_git("bisect", "bad")
            print(f"  {C.DIM}{out}{C.RESET}")
            success("Current marked as bad!")
            break
        else:
            hint("Type: git bisect bad")

    # Find the oldest commit hash
    ok, oldest = run_git("log", "--oneline", "--reverse")
    first_lines = oldest.strip().split("\n")
    first_hash = first_lines[0].split()[0] if first_lines else "HEAD~20"

    instruction(f"Tell Git a known-good commit (the first one):")
    show_command(f"git bisect good {first_hash}")

    while True:
        cmd = wait_for_command()
        if "bisect" in cmd and "good" in cmd:
            hash_arg = cmd.split()[-1] if len(cmd.split()) > 3 else first_hash
            ok, out = run_git("bisect", "good", hash_arg)
            print(f"  {C.DIM}{out}{C.RESET}")
            success("Git jumped to the middle! Now testing...")
            break
        else:
            hint(f"Type: git bisect good {first_hash}")

    # Auto-bisect loop
    print(f"\n  {C.BOLD}Git will now binary-search for the bad commit.{C.RESET}")
    print(f"  {C.DIM}(Auto-completing the bisect for you...){C.RESET}\n")
    time.sleep(1)

    for _ in range(10):
        content = read_file("app.txt")
        has_bug = "BUG" in content
        label = "BAD" if has_bug else "GOOD"
        color = C.RED if has_bug else C.GREEN
        print(f"    {color}Testing... app says: '{content.strip()}' → {label}{C.RESET}")

        ok, out = run_git("bisect", "bad" if has_bug else "good")

        if "is the first bad commit" in out:
            print(f"\n  {C.GREEN}{'=' * 50}{C.RESET}")
            print(f"  {C.GREEN}{out.strip()}{C.RESET}")
            print(f"  {C.GREEN}{'=' * 50}{C.RESET}")
            success("FOUND IT! Git identified the exact bad commit! 🎯")
            break

        if not ok:
            break

    award_xp(60, "Git bisect mastered")
    achievement("Bug Hunter")

    run_git("bisect", "reset")

    pause()

    # ─── LAB 3: Diff Like a Pro ───
    clear()
    banner("LEVEL 7 — LAB 3: REVIEW DIFFS LIKE A PRO")
    mission("Master the diff commands code reviewers use.")

    print(f"""
  {C.BOLD}When reviewing code (yours or a teammate's), you need:{C.RESET}

  {C.CYAN}git diff --stat{C.RESET}          Quick overview (files + lines changed)
  {C.CYAN}git diff --name-only{C.RESET}     Just the file names
  {C.CYAN}git show <hash>{C.RESET}          See a specific commit's changes
  {C.CYAN}git log --oneline -5{C.RESET}     Recent commits summary
  {C.CYAN}git shortlog -sn{C.RESET}         Who committed how many times
""")

    # Make a change to review
    write_file("app.txt", "App v2.0 - Complete rewrite\nModules: auth, dashboard, api, database\nStatus: production ready\n")
    run_git("add", "app.txt")
    run_git("commit", "-m", "feat: complete app v2.0 rewrite")

    instruction("See a summary of what changed in the last commit:")
    show_command("git diff --stat HEAD~1")

    while True:
        cmd = wait_for_command()
        if "diff" in cmd and "stat" in cmd:
            ok, out = run_git("diff", "--stat", "HEAD~1")
            print(f"\n  {C.GREEN}{out.replace(chr(10), chr(10) + '  ')}{C.RESET}")
            success("Quick overview! Files changed + lines added/removed.")
            award_xp(30, "Diff stats mastered")
            break
        else:
            hint("Type: git diff --stat HEAD~1")

    instruction("See the full details of the last commit:")
    show_command("git show HEAD")

    while True:
        cmd = wait_for_command()
        if "show" in cmd:
            ok, out = run_git("show", "--stat", "HEAD")
            print(f"\n  {C.GREEN}{out.replace(chr(10), chr(10) + '  ')}{C.RESET}")
            success("git show is your go-to for inspecting any commit!")
            award_xp(20, "Git show mastered")
            break
        else:
            hint("Type: git show HEAD")

    instruction("See who contributed the most (great for team leads):")
    show_command("git shortlog -sn")

    while True:
        cmd = wait_for_command()
        if "shortlog" in cmd:
            ok, out = run_git("shortlog", "-sn")
            print(f"\n  {C.GREEN}{out.replace(chr(10), chr(10) + '  ')}{C.RESET}")
            success("Now you can see who's been busy!")
            award_xp(20, "Shortlog mastered")
            break
        else:
            hint("Type: git shortlog -sn")

    pause()

    # ─── LAB 4: Creating a PR-Ready Branch ───
    clear()
    banner("LEVEL 7 — LAB 4: THE PERFECT PULL REQUEST")
    mission("Prepare a branch that's ready for code review.")

    print(f"""
  {C.BOLD}Before opening a Pull Request, pros always:{C.RESET}

  1. {C.CYAN}Update with main{C.RESET}       git merge main
  2. {C.CYAN}Fix any conflicts{C.RESET}      resolve + commit
  3. {C.CYAN}Review own diff{C.RESET}        git diff main..HEAD
  4. {C.CYAN}Squash if messy{C.RESET}        or keep clean commits
  5. {C.CYAN}Write good PR title{C.RESET}    "feat: add user notifications"

  {C.DIM}A good PR makes reviewers HAPPY.
  A messy PR makes them close the tab.{C.RESET}
""")

    instruction("Let's create a clean PR branch:")
    show_command("git checkout -b feature/user-notifications")

    while True:
        cmd = wait_for_command()
        if "checkout" in cmd and "-b" in cmd:
            branch = cmd.split()[-1] if len(cmd.split()) > 3 else "feature/user-notifications"
            run_git("checkout", "-b", branch)
            success("Feature branch created!")
            break
        else:
            hint("Type: git checkout -b feature/user-notifications")

    write_file("notifications.txt", "Notification System\n- Email alerts\n- Push notifications\n- SMS for critical alerts\n- In-app notification center\n")
    run_git("add", "notifications.txt")
    run_git("commit", "-m", "feat: add notification system with email, push, SMS")

    write_file("notification-tests.txt", "Tests for notifications\n- test_email_send: PASS\n- test_push_delivery: PASS\n- test_sms_fallback: PASS\n")
    run_git("add", "notification-tests.txt")
    run_git("commit", "-m", "test: add notification system tests")

    instruction("Review your branch vs main (what the reviewer will see):")
    show_command("git diff main --stat")

    while True:
        cmd = wait_for_command()
        if "diff" in cmd and "main" in cmd:
            ok, out = run_git("diff", "main", "--stat")
            print(f"\n  {C.GREEN}{out.replace(chr(10), chr(10) + '  ')}{C.RESET}")
            print(f"\n  {C.BOLD}This is exactly what appears on a GitHub Pull Request!{C.RESET}")
            award_xp(30, "PR review skills")
            break
        else:
            hint("Type: git diff main --stat")

    instruction("Show your clean commit history for this branch:")
    show_command("git log main..HEAD --oneline")

    while True:
        cmd = wait_for_command()
        if "log" in cmd and "main" in cmd:
            ok, out = run_git("log", "main..HEAD", "--oneline")
            print(f"\n  {C.GREEN}{out.replace(chr(10), chr(10) + '  ')}{C.RESET}")
            print(f"\n  {C.BOLD}Clean, clear commits. Your PR would be approved fast!{C.RESET}")
            award_xp(20, "Clean PR history")
            break
        else:
            hint("Type: git log main..HEAD --oneline")

    # Merge and clean up
    run_git("checkout", "main")
    run_git("merge", "feature/user-notifications")
    run_git("branch", "-d", "feature/user-notifications")

    # ─── Level Complete ───
    clear()
    banner("LEVEL 7 COMPLETE!")
    print(f"""
{C.GREEN}
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║  CODE REVIEW SKILLS MASTERED:                    ║
    ║                                                  ║
    ║  • git merge --squash        Clean up commits    ║
    ║  • git bisect                Find bugs fast      ║
    ║  • git diff --stat           Review like a pro   ║
    ║  • git show                  Inspect commits     ║
    ║  • git shortlog -sn          Team contributions  ║
    ║  • git log main..HEAD        PR-ready review     ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
{C.RESET}""")

    current_level = max(current_level, 8)
    save_progress()
    show_xp()
    pause("Press ENTER to continue to the FINAL Level 8: THE THRONE ROOM...")

# ═══════════════════════════════════════════════════════
# LEVEL 8: THE THRONE ROOM (Release Management)
# ═══════════════════════════════════════════════════════
def level_8():
    global current_level
    clear()
    banner("LEVEL 8: THE THRONE ROOM  ⭐ 700 XP")

    print(f"""
  {C.BOLD}You've reached the top, developer.{C.RESET}

  Companies don't just push code and hope for the best.
  They have RELEASE PROCESSES.

  This level teaches:
  • Git tags for versioned releases
  • Hotfix workflows for production emergencies
  • The complete professional sprint cycle

  {C.CYAN}This is what separates juniors from seniors.{C.RESET}
""")
    pause()

    # ─── LAB 1: Git Tags ───
    clear()
    banner("LEVEL 8 — LAB 1: GIT TAGS — MARKING RELEASES")
    mission("Create version tags for your releases.")

    print(f"""
  {C.BOLD}Semantic Versioning (SemVer):{C.RESET}

  {C.CYAN}v MAJOR . MINOR . PATCH{C.RESET}
  {C.CYAN}v   1   .   0   .   0  {C.RESET}

  {C.GREEN}MAJOR{C.RESET} = Breaking changes       (v1 → v2)
  {C.GREEN}MINOR{C.RESET} = New features            (v1.0 → v1.1)
  {C.GREEN}PATCH{C.RESET} = Bug fixes               (v1.0.0 → v1.0.1)

  {C.DIM}Examples:
  v1.0.0  →  First stable release
  v1.1.0  →  Added notification feature
  v1.1.1  →  Fixed email delivery bug
  v2.0.0  →  Major redesign (might break API){C.RESET}
""")

    instruction("Tag your current code as v1.0.0:")
    show_command('git tag -a v1.0.0 -m "Release v1.0.0: initial stable release"')

    while True:
        cmd = wait_for_command()
        if "tag" in cmd:
            ok, out = run_git("tag", "-a", "v1.0.0", "-m", "Release v1.0.0: initial stable release")
            if not ok and "already exists" in str(out):
                run_git("tag", "-d", "v1.0.0")
                run_git("tag", "-a", "v1.0.0", "-m", "Release v1.0.0: initial stable release")
            success("Tagged v1.0.0! This marks your first official release!")
            award_xp(40, "First release tag")
            break
        else:
            hint('Type: git tag -a v1.0.0 -m "Release v1.0.0: initial stable release"')

    instruction("See all your tags:")
    show_command("git tag")

    while True:
        cmd = wait_for_command()
        if "tag" in cmd:
            ok, out = run_git("tag")
            print(f"\n  {C.GREEN}{out.replace(chr(10), chr(10) + '  ')}{C.RESET}")
            success("Tags are like bookmarks for releases!")
            break
        else:
            hint("Type: git tag")

    # Add a feature and tag a minor release
    write_file("search.txt", "Search Module\n- Full-text search\n- Filters by date, type, author\n- Fuzzy matching\n")
    run_git("add", "search.txt")
    run_git("commit", "-m", "feat: add search module")

    instruction("Tag the new feature release:")
    show_command('git tag -a v1.1.0 -m "Release v1.1.0: add search module"')

    while True:
        cmd = wait_for_command()
        if "tag" in cmd and "1.1" in cmd:
            run_git("tag", "-a", "v1.1.0", "-m", "Release v1.1.0: add search module")
            success("v1.1.0 — new minor release tagged!")
            award_xp(30, "Minor release tagged")
            break
        else:
            hint('Type: git tag -a v1.1.0 -m "Release v1.1.0: add search module"')

    instruction("See your tags with details:")
    show_command("git tag -n")

    while True:
        cmd = wait_for_command()
        if "tag" in cmd:
            ok, out = run_git("tag", "-n")
            print(f"\n  {C.GREEN}{out.replace(chr(10), chr(10) + '  ')}{C.RESET}")
            success("You can see each release with its description!")
            break
        else:
            hint("Type: git tag -n")

    pause()

    # ─── LAB 2: Hotfix Workflow ───
    clear()
    banner("LEVEL 8 — LAB 2: HOTFIX — EMERGENCY IN PRODUCTION!")
    mission("Fix a critical bug using the hotfix workflow.")

    print(f"""
{C.RED}
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║  🚨  ALERT: CRITICAL BUG IN PRODUCTION!  🚨     ║
    ║                                                  ║
    ║  Users can't log in!                             ║
    ║  The CEO is on the phone!                        ║
    ║  Revenue is dropping by the minute!              ║
    ║                                                  ║
    ║  You need to fix it NOW.                         ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
{C.RESET}

  {C.BOLD}The Hotfix Workflow:{C.RESET}

  1. Branch from main (production code)
  2. Fix the bug
  3. Merge back to main
  4. Tag a patch release (v1.1.1)
  5. Deploy immediately
""")

    instruction("Create a hotfix branch:")
    show_command("git checkout -b hotfix/login-crash")

    while True:
        cmd = wait_for_command()
        if "checkout" in cmd and "hotfix" in cmd:
            run_git("checkout", "-b", "hotfix/login-crash")
            success("On hotfix branch! Clock is ticking! ⏰")
            break
        else:
            hint("Type: git checkout -b hotfix/login-crash")

    instruction("Apply the fix:")
    show_command('echo "FIX: handle null session token in auth flow" > hotfix-patch.txt')

    while True:
        cmd = wait_for_command()
        if "fix" in cmd.lower() or "hotfix" in cmd.lower() or "patch" in cmd.lower():
            write_file("hotfix-patch.txt", "FIX: handle null session token in auth flow\nAffected: login, session refresh\nRoot cause: missing null check in token parser\n")
            success("Fix applied!")
            break
        else:
            hint('Type: echo "FIX: handle null session token in auth flow" > hotfix-patch.txt')

    show_command("git add hotfix-patch.txt")
    while True:
        cmd = wait_for_command()
        if "git add" in cmd:
            run_git("add", "hotfix-patch.txt")
            break
        else:
            hint("Type: git add hotfix-patch.txt")

    show_command('git commit -m "fix: handle null session token in login flow"')
    while True:
        cmd = wait_for_command()
        if "commit" in cmd:
            run_git("commit", "-m", "fix: handle null session token in login flow")
            success("Fix committed!")
            break
        else:
            hint('Type: git commit -m "fix: handle null session token in login flow"')

    instruction("Merge hotfix back to main:")
    show_command("git checkout main")

    while True:
        cmd = wait_for_command()
        if "checkout" in cmd and "main" in cmd:
            run_git("checkout", "main")
            break
        else:
            hint("Type: git checkout main")

    show_command("git merge hotfix/login-crash")

    while True:
        cmd = wait_for_command()
        if "merge" in cmd:
            ok, out = run_git("merge", "hotfix/login-crash")
            success("Hotfix merged to production!")
            break
        else:
            hint("Type: git merge hotfix/login-crash")

    instruction("Tag the emergency patch release:")
    show_command('git tag -a v1.1.1 -m "Hotfix: login crash resolved"')

    while True:
        cmd = wait_for_command()
        if "tag" in cmd:
            run_git("tag", "-a", "v1.1.1", "-m", "Hotfix: login crash resolved")
            success("v1.1.1 released! Crisis averted! 🎉")
            award_xp(60, "Hotfix workflow mastered")
            achievement("Firefighter")
            break
        else:
            hint('Type: git tag -a v1.1.1 -m "Hotfix: login crash resolved"')

    run_git("branch", "-d", "hotfix/login-crash")

    print(f"""
  {C.GREEN}
  ┌──────────────────────────────────────────────────┐
  │  HOTFIX COMPLETE!                                │
  │                                                  │
  │  Timeline:                                       │
  │  🚨 Bug reported  → 🔧 hotfix/ branch created   │
  │  → ✅ Fix committed → 🔀 Merged to main         │
  │  → 🏷️  Tagged v1.1.1 → 🚀 Ready to deploy       │
  │                                                  │
  │  Total time: minutes, not hours.                 │
  │  That's the power of a good workflow.            │
  └──────────────────────────────────────────────────┘
  {C.RESET}""")

    pause()

    # ─── LAB 3: Final Boss — Complete Sprint ───
    clear()
    banner("☠️  FINAL BOSS: THE SPRINT SIMULATION")

    print(f"""
{C.GOLD}
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║  FINAL CHALLENGE: Complete Sprint Workflow       ║
    ║                                                  ║
    ║  Do the ENTIRE professional flow:                ║
    ║                                                  ║
    ║  1. Create a feature branch                      ║
    ║  2. Write code with proper commits               ║
    ║  3. Squash merge to main                         ║
    ║  4. Tag a major release (v2.0.0)                 ║
    ║  5. Clean up                                     ║
    ║                                                  ║
    ║  Minimal hand-holding. You know this. GO. 💪     ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
{C.RESET}""")
    pause("Ready for the final challenge? Press ENTER...")

    clear()
    banner("SPRINT TASK: Build Settings Module")

    print(f"""
  {C.BOLD}YOUR MISSION:{C.RESET}

  1. Create branch: {C.CYAN}feature/settings{C.RESET}
  2. Create file:   {C.CYAN}settings.txt{C.RESET}
  3. Commit with conventional format
  4. Squash merge to main
  5. Tag as {C.CYAN}v2.0.0{C.RESET}
  6. Delete the branch

  {C.DIM}Less hand-holding this time — you've earned it.{C.RESET}
""")

    # Step 1
    instruction("Step 1: Create the feature branch")
    show_command("git checkout -b feature/settings")

    while True:
        cmd = wait_for_command()
        if "checkout" in cmd and "-b" in cmd:
            branch = cmd.split()[-1] if len(cmd.split()) > 3 else "feature/settings"
            run_git("checkout", "-b", branch)
            success("Branch created!")
            break
        else:
            hint("Type: git checkout -b feature/settings")

    # Step 2 & 3
    instruction("Step 2 & 3: Create settings and commit")
    show_command('echo "Settings: theme, language, timezone, notifications" > settings.txt')

    while True:
        cmd = wait_for_command()
        if "settings" in cmd.lower():
            write_file("settings.txt", "Settings Module\n- Theme: light/dark\n- Language: en, es, fr, de, ja\n- Timezone: auto-detect\n- Notification preferences\n- Privacy controls\n")
            success("File created!")
            break
        else:
            hint('Type: echo "Settings: theme, language, timezone, notifications" > settings.txt')

    show_command("git add settings.txt")
    while True:
        cmd = wait_for_command()
        if "add" in cmd:
            run_git("add", "settings.txt")
            break
        else:
            hint("Type: git add settings.txt")

    show_command('git commit -m "feat: add settings module with theme, i18n, timezone"')
    while True:
        cmd = wait_for_command()
        if "commit" in cmd:
            msg = "feat: add settings module with theme, i18n, timezone"
            try:
                msg = cmd.split("-m")[-1].strip().strip('"').strip("'") or msg
            except:
                pass
            run_git("commit", "-m", msg)
            success("Committed!")
            break
        else:
            hint('Type: git commit -m "feat: add settings module with theme, i18n, timezone"')

    # Step 4
    instruction("Step 4: Squash merge to main")
    show_command("git checkout main")

    while True:
        cmd = wait_for_command()
        if "checkout" in cmd and "main" in cmd:
            run_git("checkout", "main")
            break
        else:
            hint("Type: git checkout main")

    show_command("git merge --squash feature/settings")

    while True:
        cmd = wait_for_command()
        if "merge" in cmd:
            run_git("merge", "--squash", "feature/settings")
            break
        else:
            hint("Type: git merge --squash feature/settings")

    show_command('git commit -m "feat: add complete settings module"')
    while True:
        cmd = wait_for_command()
        if "commit" in cmd:
            msg = "feat: add complete settings module"
            try:
                msg = cmd.split("-m")[-1].strip().strip('"').strip("'") or msg
            except:
                pass
            run_git("commit", "-m", msg)
            success("Squash merged!")
            break
        else:
            hint('Type: git commit -m "feat: add complete settings module"')

    # Step 5
    instruction("Step 5: Tag the major release:")
    show_command('git tag -a v2.0.0 -m "Release v2.0.0: complete platform with settings"')

    while True:
        cmd = wait_for_command()
        if "tag" in cmd:
            run_git("tag", "-a", "v2.0.0", "-m", "Release v2.0.0: complete platform with settings")
            success("v2.0.0 tagged!")
            break
        else:
            hint('Type: git tag -a v2.0.0 -m "Release v2.0.0: complete platform with settings"')

    # Step 6
    instruction("Step 6: Clean up the feature branch")
    show_command("git branch -D feature/settings")

    while True:
        cmd = wait_for_command()
        if "branch" in cmd and ("-d" in cmd.lower() or "-D" in cmd):
            run_git("branch", "-D", "feature/settings")
            success("Branch cleaned up!")
            break
        else:
            hint("Type: git branch -D feature/settings")

    # VICTORY
    clear()
    print(f"""
{C.GREEN}
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║        ☠️  FINAL BOSS DEFEATED!  ☠️               ║
    ║                                                  ║
    ║   You completed the full professional workflow!  ║
    ║                                                  ║
    ║   feature branch → clean commits →               ║
    ║   squash merge → tag release → clean up          ║
    ║                                                  ║
    ║   This is EXACTLY what companies do every day.   ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
{C.RESET}""")

    award_xp(200, "FINAL BOSS — SPRINT COMPLETE!")
    achievement("Release Manager")

    # Show the complete professional workflow
    clear()
    banner("THE COMPLETE PROFESSIONAL GIT WORKFLOW")

    print(f"""
{C.GOLD}
  ┌────────────────────────────────────────────────────────┐
  │                                                        │
  │   THE PROFESSIONAL DAILY WORKFLOW:                     │
  │                                                        │
  │   1. git pull origin main        ← Start of day       │
  │   2. git checkout -b feature/x   ← New feature        │
  │   3. ... write code ...          ← Do your thing      │
  │   4. git add .                   ← Stage changes      │
  │   5. git commit -m "feat: ..."   ← Conventional msg   │
  │   6. git merge main              ← Stay current       │
  │   7. ... fix conflicts if any    ← Resolve            │
  │   8. git checkout main           ← Switch to main     │
  │   9. git merge --squash feature  ← Clean merge        │
  │  10. git commit -m "feat: ..."   ← One clean commit   │
  │  11. git tag -a v1.x.x           ← If releasing       │
  │  12. git push origin main        ← Upload             │
  │  13. git push --tags             ← Upload tags        │
  │  14. git branch -d feature/x     ← Clean up           │
  │                                                        │
  │   THAT'S THE COMPLETE PROFESSIONAL WORKFLOW.           │
  │                                                        │
  │   Emergency? hotfix/ branch → fix → merge → tag.      │
  │   That's it. You know everything.                      │
  │                                                        │
  └────────────────────────────────────────────────────────┘
{C.RESET}""")

    award_xp(100, "PROFESSIONAL WORKFLOW MASTERED!")
    current_level = max(current_level, 9)
    save_progress()
    show_xp()

# ═══════════════════════════════════════════════════════
# VICTORY SCREEN
# ═══════════════════════════════════════════════════════
def victory():
    clear()
    achievement("Git Master")

    print(f"""
{C.GOLD}
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║         🏆  Q U E S T   C O M P L E T E  🏆      ║
    ║                                                  ║
    ║         ⭐ FINAL SCORE: {xp} XP{' ' * (18 - len(str(xp)))}║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
{C.RESET}

{C.GREEN}  ACHIEVEMENTS UNLOCKED:{C.RESET}
""")
    for a in achievements:
        print(f"  {C.MAGENTA}  🏅 {a}{C.RESET}")

    print(f"""
{C.BOLD}
  WHAT YOU MASTERED:

  ✅ Level 1 — git init, add, commit, status, diff, log
  ✅ Level 2 — restore, amend, reset, .gitignore
  ✅ Level 3 — branches, merge, conflict resolution
  ✅ Level 4 — GitHub push, pull, clone, remotes
  ✅ Level 5 — stash, reflog, recovery, aliases
  ✅ Level 6 — team workflow, blame, cherry-pick
  ✅ Level 7 — squash merge, bisect, diff review, PRs
  ✅ Level 8 — tags, semver, hotfix, release management

  REAL-WORLD SKILLS EARNED:

  🏢 Feature branch workflow      (used at every company)
  🏢 Conventional commits         (team communication)
  🏢 Squash merging               (clean history)
  🏢 Hotfix workflow              (production emergencies)
  🏢 Semantic versioning          (release management)
  🏢 Code review prep             (PR best practices)

  WHAT'S NEXT:

  • Use Git in EVERY project from now on
  • Try github.com — contribute to open source
  • Look for "good first issue" labels on GitHub
  • Practice the professional workflow daily
  • Keep this game — revisit any level anytime!
{C.RESET}

{C.DIM}  Thank you for playing The Git Quest! ⚔️
  You went from zero to professional. Go build things.{C.RESET}
""")
    save_progress()

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════
def main():
    global quest_dir, current_level

    # Enable ANSI colors on Windows
    if os.name == "nt":
        os.system("")

    # Level dispatch table
    level_funcs = {
        1: level_1,
        2: level_2,
        3: level_3,
        4: level_4,
        5: level_5,
        6: level_6,
        7: level_7,
        8: level_8,
    }

    # Show menu
    action, start_level = main_menu()

    if action == "new":
        title_screen()
        start_level = 1

    # Setup quest directory if starting from level > 1
    if start_level > 1:
        base_dir = os.getcwd()
        quest_dir = os.path.join(base_dir, "git-quest")
        if not os.path.exists(quest_dir):
            os.makedirs(quest_dir, exist_ok=True)
        if not is_git_repo():
            run_git("init")
            write_file("hero.txt", "Hero - Git Quest Player\n")
            run_git("add", ".")
            run_git("commit", "-m", "Quest checkpoint")

    # Run levels from start_level onward
    for lvl in range(start_level, 9):
        if lvl in level_funcs:
            level_funcs[lvl]()
            current_level = max(current_level, lvl + 1)
            save_progress()

    victory()

if __name__ == "__main__":
    main()
