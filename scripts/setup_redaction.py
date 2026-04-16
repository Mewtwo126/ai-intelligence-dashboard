"""
setup_redaction.py
------------------
One-time setup script for the Resume PII Redactor.
Run this once before you start using resume_redactor.py.

What it does:
  1. Installs all required Python packages
  2. Downloads the spaCy language model Presidio needs
  3. Creates the four working folders under ~/ResumePII/
  4. Drops a sample fake resume into incoming/ so you can verify everything works
"""

import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run(cmd: list, description: str) -> bool:
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"\n[ERROR] Command failed: {' '.join(cmd)}")
        return False
    return True


# ---------------------------------------------------------------------------
# Step 1 – Install packages
# ---------------------------------------------------------------------------

REQUIREMENTS = Path(__file__).parent.parent / "requirements-redaction.txt"

print("\nResume PII Redactor — Setup")
print("=" * 60)

if not REQUIREMENTS.exists():
    print(f"[ERROR] Cannot find {REQUIREMENTS}")
    print("Make sure you are running this from inside the ai-intelligence-dashboard folder.")
    sys.exit(1)

ok = run(
    [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS), "--quiet"],
    "Installing Python packages from requirements-redaction.txt…",
)
if not ok:
    print("\nTip: if pip fails, try running this script with Administrator / sudo rights.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Step 2 – Download spaCy language model
# ---------------------------------------------------------------------------

ok = run(
    [sys.executable, "-m", "spacy", "download", "en_core_web_lg"],
    "Downloading spaCy English model (en_core_web_lg, ~560 MB — one-time download)…",
)
if not ok:
    print("\nspaCy model download failed. You can retry manually:")
    print("  python -m spacy download en_core_web_lg")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Step 3 – Create folder structure
# ---------------------------------------------------------------------------

BASE = Path.home() / "ResumePII"
FOLDERS = {
    "incoming": "Drop raw resumes here",
    "redacted": "Redacted copies appear here",
    "archive":  "Originals are moved here after processing",
    "error":    "Files that could not be processed land here",
}

print(f"\n{'='*60}")
print("  Creating folder structure under ~/ResumePII/")
print(f"{'='*60}")

for name, purpose in FOLDERS.items():
    folder = BASE / name
    folder.mkdir(parents=True, exist_ok=True)
    print(f"  OK  {folder}  ({purpose})")

# ---------------------------------------------------------------------------
# Step 4 – Write a sample fake resume into incoming/
# ---------------------------------------------------------------------------

SAMPLE = """\
Jane Doe
123 Maple Street, Springfield, IL 62701
jane.doe@email.com | (555) 867-5309
linkedin.com/in/janedoe | github.com/janedoe

SUMMARY
Results-driven marketing professional with 7 years of experience
in digital strategy and brand development.

EXPERIENCE
Senior Marketing Manager — Acme Corp (2020–2024)
  • Led a team of 8 across paid search, SEO, and social media.
  • Grew organic traffic by 140% in 18 months.

Marketing Coordinator — Globex Inc (2017–2020)
  • Managed monthly email campaigns to 50,000 subscribers.

EDUCATION
B.S. Communications — State University, 2017

REFERENCES
Available upon request.
"""

sample_path = BASE / "incoming" / "sample_fake_resume.txt"
sample_path.write_text(SAMPLE, encoding="utf-8")
print(f"\n  Sample fake resume written to:\n  {sample_path}")

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

print(f"""
{'='*60}
  Setup complete!
{'='*60}

Next steps:
  1. Open a terminal and run the watcher:
       python scripts/resume_redactor.py

  2. The script will immediately process the sample fake resume
     that was just placed in incoming/.

  3. Check ~/ResumePII/redacted/ — you should see a file called
     sample_fake_resume_redacted.txt with PII replaced by labels
     like <PERSON>, <EMAIL_ADDRESS>, <PHONE_NUMBER>, etc.

  4. Once you are happy with the results, drop real resumes into
       ~/ResumePII/incoming/
     and the redacted copies will appear in ~/ResumePII/redacted/

  5. Send only the redacted copies to AI tools — never the originals.

Tip: to run the watcher automatically at login, search for
"startup applications" (Mac: Login Items, Windows: Task Scheduler).
""")
