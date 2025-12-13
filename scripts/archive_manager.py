#!/usr/bin/env python3
"""
Archive Manager - Archive and manage deprecated or inactive models
"""

import json
import os
from datetime import datetime

# Get the absolute path to the data directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
MODELS_FILE = os.path.join(DATA_DIR, "models.json")
ARCHIVED_FILE = os.path.join(DATA_DIR, "archived_models.json")
CHANGELOG_FILE = os.path.join(DATA_DIR, "changelog.json")


def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filepath, data):
    """Save JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def archive_model(model_id, reason, notes=""):
    """
    Archive a model from active database to archived database

    Args:
        model_id: ID of model to archive
        reason: Reason for archiving (deprecated, market_inactive, superseded, manual)
        notes: Additional notes about the archival
    """
    print("\n" + "="*80)
    print("                    ARCHIVE MODEL")
    print("="*80 + "\n")

    # Load databases
    models_data = load_json(MODELS_FILE)
    archived_data = load_json(ARCHIVED_FILE)

    # Find model in active database
    model_to_archive = None
    remaining_models = []

    for model in models_data["models"]:
        if model["id"] == model_id:
            model_to_archive = model
        else:
            remaining_models.append(model)

    if not model_to_archive:
        print(f"[ERROR] Model '{model_id}' not found in active database.")
        return False

    # Add archive metadata
    model_to_archive["archive_date"] = datetime.now().strftime("%Y-%m-%d")
    model_to_archive["archive_reason"] = reason
    model_to_archive["archive_notes"] = notes

    # Move to archived database
    archived_data["archived_models"].append(model_to_archive)
    archived_data["last_updated"] = datetime.now().strftime("%Y-%m-%d")

    # Update active database
    models_data["models"] = remaining_models
    models_data["last_updated"] = datetime.now().strftime("%Y-%m-%d")

    # Save both databases
    save_json(MODELS_FILE, models_data)
    save_json(ARCHIVED_FILE, archived_data)

    # Update changelog
    changelog = load_json(CHANGELOG_FILE)
    changelog_entry = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "type": "archive",
        "description": f"Archived {model_to_archive['name']} - Reason: {reason}",
        "models_affected": [model_id]
    }
    if notes:
        changelog_entry["notes"] = notes

    changelog["changelog"].insert(0, changelog_entry)
    save_json(CHANGELOG_FILE, changelog)

    print(f"[OK] Model archived successfully!")
    print(f"     Model: {model_to_archive['name']}")
    print(f"     Reason: {reason}")
    if notes:
        print(f"     Notes: {notes}")
    print("\n" + "="*80 + "\n")

    return True


def unarchive_model(model_id):
    """
    Restore a model from archived database back to active database

    Args:
        model_id: ID of model to unarchive
    """
    print("\n" + "="*80)
    print("                    UNARCHIVE MODEL")
    print("="*80 + "\n")

    # Load databases
    models_data = load_json(MODELS_FILE)
    archived_data = load_json(ARCHIVED_FILE)

    # Find model in archived database
    model_to_restore = None
    remaining_archived = []

    for model in archived_data["archived_models"]:
        if model["id"] == model_id:
            model_to_restore = model
        else:
            remaining_archived.append(model)

    if not model_to_restore:
        print(f"[ERROR] Model '{model_id}' not found in archived database.")
        return False

    # Remove archive metadata
    model_to_restore.pop("archive_date", None)
    model_to_restore.pop("archive_reason", None)
    model_to_restore.pop("archive_notes", None)

    # Update last_modified
    model_to_restore["last_modified"] = datetime.now().strftime("%Y-%m-%d")

    # Move to active database
    models_data["models"].append(model_to_restore)
    models_data["last_updated"] = datetime.now().strftime("%Y-%m-%d")

    # Update archived database
    archived_data["archived_models"] = remaining_archived
    archived_data["last_updated"] = datetime.now().strftime("%Y-%m-%d")

    # Save both databases
    save_json(MODELS_FILE, models_data)
    save_json(ARCHIVED_FILE, archived_data)

    # Update changelog
    changelog = load_json(CHANGELOG_FILE)
    changelog_entry = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "type": "unarchive",
        "description": f"Restored {model_to_restore['name']} to active database",
        "models_affected": [model_id]
    }

    changelog["changelog"].insert(0, changelog_entry)
    save_json(CHANGELOG_FILE, changelog)

    print(f"[OK] Model restored successfully!")
    print(f"     Model: {model_to_restore['name']}")
    print("\n" + "="*80 + "\n")

    return True


def list_archived(filter_reason=None):
    """
    List all archived models

    Args:
        filter_reason: Optional filter by archive reason
    """
    print("\n" + "="*80)
    print("                    ARCHIVED MODELS")
    print("="*80 + "\n")

    archived_data = load_json(ARCHIVED_FILE)
    archived_models = archived_data.get("archived_models", [])

    if not archived_models:
        print("[INFO] No archived models found.\n")
        return []

    # Filter if requested
    if filter_reason:
        archived_models = [m for m in archived_models if m.get("archive_reason") == filter_reason]
        if not archived_models:
            print(f"[INFO] No models archived for reason: {filter_reason}\n")
            return []

    # Group by reason
    by_reason = {}
    for model in archived_models:
        reason = model.get("archive_reason", "unknown")
        if reason not in by_reason:
            by_reason[reason] = []
        by_reason[reason].append(model)

    # Display
    for reason, models in by_reason.items():
        print(f"--- {reason.upper()} ({len(models)} models) ---")
        for model in models:
            print(f"  ID: {model['id']}")
            print(f"  Name: {model['name']}")
            print(f"  Provider: {model['provider']}")
            print(f"  Archived: {model.get('archive_date', 'N/A')}")
            if model.get('archive_notes'):
                print(f"  Notes: {model['archive_notes']}")
            print()

    print("="*80 + "\n")

    return archived_models


def list_active_models():
    """List all currently active models"""
    print("\n" + "="*80)
    print("                    ACTIVE MODELS")
    print("="*80 + "\n")

    models_data = load_json(MODELS_FILE)
    models = models_data.get("models", [])

    if not models:
        print("[INFO] No active models found.\n")
        return []

    for i, model in enumerate(models, 1):
        print(f"{i}. {model['name']} ({model['id']})")
        print(f"   Provider: {model['provider']}")
        print(f"   Released: {model['release_date']}")
        print()

    print("="*80 + "\n")

    return models


def main():
    """Main function"""
    print("\n" + "="*80)
    print("              ARCHIVE MANAGER")
    print("="*80)

    archive_reasons = ["deprecated", "market_inactive", "superseded", "manual"]

    while True:
        print("\nOptions:")
        print("  1. Archive a model")
        print("  2. Unarchive a model")
        print("  3. List archived models")
        print("  4. List active models")
        print("  5. Exit")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            models = list_active_models()
            if not models:
                continue

            model_id = input("Enter model ID to archive: ").strip()

            print("\nArchive reasons:")
            for i, reason in enumerate(archive_reasons, 1):
                print(f"  {i}. {reason}")

            try:
                reason_idx = int(input("Select reason: ").strip()) - 1
                reason = archive_reasons[reason_idx]
            except (ValueError, IndexError):
                print("\n[ERROR] Invalid reason selection.\n")
                continue

            notes = input("Additional notes (optional): ").strip()

            confirm = input(f"\nArchive model '{model_id}'? (yes/no): ").strip().lower()
            if confirm in ['yes', 'y']:
                archive_model(model_id, reason, notes)

        elif choice == "2":
            archived = list_archived()
            if not archived:
                continue

            model_id = input("Enter model ID to unarchive: ").strip()

            confirm = input(f"\nRestore model '{model_id}' to active database? (yes/no): ").strip().lower()
            if confirm in ['yes', 'y']:
                unarchive_model(model_id)

        elif choice == "3":
            print("\nFilter by reason?")
            print("  1. Show all")
            for i, reason in enumerate(archive_reasons, 1):
                print(f"  {i+1}. {reason}")

            try:
                filter_choice = int(input("Select option: ").strip())
                if filter_choice == 1:
                    list_archived()
                else:
                    reason = archive_reasons[filter_choice - 2]
                    list_archived(filter_reason=reason)
            except (ValueError, IndexError):
                list_archived()

        elif choice == "4":
            list_active_models()

        elif choice == "5":
            print("\nGoodbye!\n")
            break

        else:
            print("\n[ERROR] Invalid option\n")


if __name__ == "__main__":
    main()
