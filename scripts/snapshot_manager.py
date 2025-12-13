#!/usr/bin/env python3
"""
Snapshot Manager - Create, list, and compare historical snapshots of the model database
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path

# Get the absolute path to the data directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
SNAPSHOTS_DIR = os.path.join(DATA_DIR, "snapshots")
MODELS_FILE = os.path.join(DATA_DIR, "models.json")
CHANGELOG_FILE = os.path.join(DATA_DIR, "changelog.json")


def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filepath, data):
    """Save JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def create_snapshot(note=""):
    """
    Create a snapshot of the current models database

    Args:
        note: Optional note about why this snapshot was created
    """
    print("\n" + "="*80)
    print("                    CREATE SNAPSHOT")
    print("="*80 + "\n")

    # Get current date
    now = datetime.now()
    year_month = now.strftime("%Y-%m")
    snapshot_date = now.strftime("%Y-%m-%d")

    # Create year-month directory if it doesn't exist
    month_dir = os.path.join(SNAPSHOTS_DIR, year_month)
    os.makedirs(month_dir, exist_ok=True)

    # Snapshot filename
    snapshot_file = os.path.join(month_dir, f"models_{snapshot_date}.json")

    # Check if snapshot already exists for today
    if os.path.exists(snapshot_file):
        print(f"[WARNING] Snapshot already exists for {snapshot_date}")
        overwrite = input("Overwrite existing snapshot? (yes/no): ").strip().lower()
        if overwrite not in ['yes', 'y']:
            print("Snapshot creation cancelled.")
            return None

    # Copy current models.json to snapshot
    shutil.copy2(MODELS_FILE, snapshot_file)

    # Load current models to get count
    models_data = load_json(MODELS_FILE)
    model_count = len(models_data.get("models", []))

    # Create/update metadata
    metadata_file = os.path.join(month_dir, "snapshot_metadata.json")

    if os.path.exists(metadata_file):
        metadata = load_json(metadata_file)
    else:
        metadata = {"snapshots": []}

    # Add snapshot entry
    snapshot_entry = {
        "date": snapshot_date,
        "timestamp": now.isoformat(),
        "model_count": model_count,
        "note": note if note else "Regular snapshot"
    }

    # Update or append
    existing = [s for s in metadata["snapshots"] if s["date"] == snapshot_date]
    if existing:
        # Update existing entry
        for i, s in enumerate(metadata["snapshots"]):
            if s["date"] == snapshot_date:
                metadata["snapshots"][i] = snapshot_entry
    else:
        # Append new entry
        metadata["snapshots"].append(snapshot_entry)

    # Sort by date (newest first)
    metadata["snapshots"].sort(key=lambda x: x["date"], reverse=True)

    save_json(metadata_file, metadata)

    # Update changelog
    changelog = load_json(CHANGELOG_FILE)
    changelog_entry = {
        "date": snapshot_date,
        "type": "snapshot",
        "description": f"Created snapshot with {model_count} models",
        "models_affected": []
    }
    if note:
        changelog_entry["description"] += f" - {note}"

    changelog["changelog"].insert(0, changelog_entry)
    save_json(CHANGELOG_FILE, changelog)

    print(f"[OK] Snapshot created successfully!")
    print(f"     Location: {snapshot_file}")
    print(f"     Models captured: {model_count}")
    print(f"     Date: {snapshot_date}")
    if note:
        print(f"     Note: {note}")
    print("\n" + "="*80 + "\n")

    return snapshot_file


def list_snapshots():
    """
    List all available snapshots with metadata
    """
    print("\n" + "="*80)
    print("                    AVAILABLE SNAPSHOTS")
    print("="*80 + "\n")

    if not os.path.exists(SNAPSHOTS_DIR):
        print("[INFO] No snapshots directory found. No snapshots exist yet.")
        return []

    # Get all month directories
    month_dirs = sorted([d for d in os.listdir(SNAPSHOTS_DIR)
                        if os.path.isdir(os.path.join(SNAPSHOTS_DIR, d))], reverse=True)

    if not month_dirs:
        print("[INFO] No snapshots found.")
        return []

    all_snapshots = []

    for month_dir in month_dirs:
        month_path = os.path.join(SNAPSHOTS_DIR, month_dir)
        metadata_file = os.path.join(month_path, "snapshot_metadata.json")

        if os.path.exists(metadata_file):
            metadata = load_json(metadata_file)
            snapshots = metadata.get("snapshots", [])

            if snapshots:
                print(f"\n--- {month_dir} ---")
                for snap in snapshots:
                    print(f"  Date: {snap['date']}")
                    print(f"  Models: {snap['model_count']}")
                    print(f"  Note: {snap['note']}")
                    print()
                    all_snapshots.append({
                        "month": month_dir,
                        "path": os.path.join(month_path, f"models_{snap['date']}.json"),
                        **snap
                    })

    print("="*80 + "\n")
    return all_snapshots


def compare_snapshots(snapshot1_path, snapshot2_path):
    """
    Compare two snapshots and identify differences

    Args:
        snapshot1_path: Path to older snapshot
        snapshot2_path: Path to newer snapshot
    """
    print("\n" + "="*80)
    print("                    SNAPSHOT COMPARISON")
    print("="*80 + "\n")

    # Load both snapshots
    snap1 = load_json(snapshot1_path)
    snap2 = load_json(snapshot2_path)

    models1 = {m["id"]: m for m in snap1.get("models", [])}
    models2 = {m["id"]: m for m in snap2.get("models", [])}

    # Find differences
    new_models = set(models2.keys()) - set(models1.keys())
    removed_models = set(models1.keys()) - set(models2.keys())
    common_models = set(models1.keys()) & set(models2.keys())

    # Print summary
    print(f"Snapshot 1: {os.path.basename(snapshot1_path)}")
    print(f"Snapshot 2: {os.path.basename(snapshot2_path)}")
    print()

    # New models
    if new_models:
        print(f"[+] NEW MODELS ({len(new_models)}):")
        for model_id in new_models:
            model = models2[model_id]
            print(f"    + {model['name']} ({model_id})")
            print(f"      Provider: {model['provider']}")
            print(f"      Released: {model['release_date']}")
        print()
    else:
        print("[INFO] No new models added.\n")

    # Removed models
    if removed_models:
        print(f"[-] REMOVED MODELS ({len(removed_models)}):")
        for model_id in removed_models:
            model = models1[model_id]
            print(f"    - {model['name']} ({model_id})")
        print()
    else:
        print("[INFO] No models removed.\n")

    # Changed models
    changes = []
    for model_id in common_models:
        m1 = models1[model_id]
        m2 = models2[model_id]

        model_changes = []

        # Check pricing changes
        if m1["pricing"] != m2["pricing"]:
            old_input = m1["pricing"]["input_per_1m_tokens"]
            new_input = m2["pricing"]["input_per_1m_tokens"]
            old_output = m1["pricing"]["output_per_1m_tokens"]
            new_output = m2["pricing"]["output_per_1m_tokens"]

            if old_input != new_input or old_output != new_output:
                model_changes.append({
                    "type": "pricing",
                    "old": f"${old_input:.2f} / ${old_output:.2f}",
                    "new": f"${new_input:.2f} / ${new_output:.2f}"
                })

        # Check context window changes
        if m1["features"]["context_window"] != m2["features"]["context_window"]:
            model_changes.append({
                "type": "context_window",
                "old": f"{m1['features']['context_window']:,}",
                "new": f"{m2['features']['context_window']:,}"
            })

        # Check modalities changes
        if set(m1["modalities"]) != set(m2["modalities"]):
            model_changes.append({
                "type": "modalities",
                "old": ", ".join(m1["modalities"]),
                "new": ", ".join(m2["modalities"])
            })

        if model_changes:
            changes.append({
                "model_id": model_id,
                "model_name": m2["name"],
                "changes": model_changes
            })

    if changes:
        print(f"[~] MODIFIED MODELS ({len(changes)}):")
        for change in changes:
            print(f"    ~ {change['model_name']} ({change['model_id']})")
            for ch in change["changes"]:
                print(f"      {ch['type']}: {ch['old']} -> {ch['new']}")
            print()
    else:
        print("[INFO] No models modified.\n")

    print("="*80 + "\n")

    return {
        "new": list(new_models),
        "removed": list(removed_models),
        "modified": changes
    }


def main():
    """Main function"""
    print("\n" + "="*80)
    print("              SNAPSHOT MANAGER")
    print("="*80)

    while True:
        print("\nOptions:")
        print("  1. Create snapshot")
        print("  2. List all snapshots")
        print("  3. Compare two snapshots")
        print("  4. Exit")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            note = input("Snapshot note (optional): ").strip()
            create_snapshot(note if note else "")

        elif choice == "2":
            list_snapshots()

        elif choice == "3":
            snapshots = list_snapshots()
            if len(snapshots) < 2:
                print("\n[ERROR] Need at least 2 snapshots to compare.\n")
                continue

            print("Select first snapshot (older):")
            for i, snap in enumerate(snapshots, 1):
                print(f"  {i}. {snap['date']} ({snap['model_count']} models)")

            try:
                idx1 = int(input("Enter number: ").strip()) - 1
                snap1 = snapshots[idx1]

                print("\nSelect second snapshot (newer):")
                for i, snap in enumerate(snapshots, 1):
                    print(f"  {i}. {snap['date']} ({snap['model_count']} models)")

                idx2 = int(input("Enter number: ").strip()) - 1
                snap2 = snapshots[idx2]

                compare_snapshots(snap1["path"], snap2["path"])

            except (ValueError, IndexError):
                print("\n[ERROR] Invalid selection.\n")

        elif choice == "4":
            print("\nGoodbye!\n")
            break

        else:
            print("\n[ERROR] Invalid option\n")


if __name__ == "__main__":
    main()
