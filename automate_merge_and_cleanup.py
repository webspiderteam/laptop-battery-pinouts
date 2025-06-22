import os
import json
import glob
import subprocess
from github import Github

# --- CONFIGURATION ---
REPO_PATH = os.path.dirname(os.path.abspath(__file__))
SUBMISSIONS_DIR = os.path.join(REPO_PATH, "submissions")
PINOUTS_FILE = os.path.join(REPO_PATH, "pinouts.json")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")  # Set in your environment
REPO_NAME = "webspiderteam/laptop-battery-pinouts"  # Change if needed

# --- STEP 1: Pull latest repo ---
subprocess.run(["git", "pull"], cwd=REPO_PATH, check=True)

# --- STEP 2: Load existing pinouts ---
if os.path.exists(PINOUTS_FILE):
    with open(PINOUTS_FILE, "r", encoding="utf-8") as f:
        pinouts = json.load(f)
else:
    pinouts = []

existing = set(json.dumps(p, sort_keys=True) for p in pinouts)
new_count = 0
merged_files = []

# --- STEP 3: Merge new submissions ---
files = sorted(glob.glob(os.path.join(SUBMISSIONS_DIR, "pinout_*.json")))
for file in files:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
    key = json.dumps(data, sort_keys=True)
    if key not in existing:
        pinouts.append(data)
        existing.add(key)
        merged_files.append(file)
        print(f"Added: {file}")
        new_count += 1
    else:
        print(f"Duplicate (skipped): {file}")

# --- STEP 4: Save pinouts.json and delete merged files ---
if new_count > 0:
    with open(PINOUTS_FILE, "w", encoding="utf-8") as f:
        json.dump(pinouts, f, ensure_ascii=False, indent=2)
    for file in merged_files:
        os.remove(file)
        print(f"Deleted: {file}")
    subprocess.run(["git", "add", "pinouts.json"], cwd=REPO_PATH, check=True)
    subprocess.run(["git", "add", "submissions"], cwd=REPO_PATH, check=True)
    subprocess.run(["git", "config", "user.email", "pinout-bot@users.noreply.github.com"], cwd=REPO_PATH, check=True)
    subprocess.run(["git", "config", "user.name", "Pinout Bot"], cwd=REPO_PATH, check=True)
    subprocess.run(["git", "commit", "-m", "Automated daily merge of new pinouts"], cwd=REPO_PATH, check=True)
    subprocess.run(["git", "push"], cwd=REPO_PATH, check=True)
    print(f"Total new pinouts merged and cleaned up: {new_count}")
else:
    print("No new pinouts to merge.") 

# --- STEP 5: (Optional) Auto-merge PRs that only add a new submission file ---
if GITHUB_TOKEN:
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    pulls = repo.get_pulls(state='open', sort='created')
    for pr in pulls:
        files = list(pr.get_files())
        # Only auto-merge if PR only adds a single file in submissions/
        if len(files) == 1 and files[0].filename.startswith("submissions/") and files[0].status == "added":
            try:
                pr.merge(commit_message="Auto-merged by daily merge script (single submission file)")
                print(f"Auto-merged PR #{pr.number}: {pr.title}")
            except Exception as e:
                print(f"Failed to auto-merge PR #{pr.number}: {e}")
else:
    print("GITHUB_TOKEN not set, skipping PR auto-merge.")
