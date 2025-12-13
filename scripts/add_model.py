#!/usr/bin/env python3
"""
Add or update AI models in the database
"""

import json
import os
from datetime import datetime

# Get the absolute path to the data directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
MODELS_FILE = os.path.join(DATA_DIR, "models.json")
CHANGELOG_FILE = os.path.join(DATA_DIR, "changelog.json")


def load_models():
    """Load existing models from database"""
    with open(MODELS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_models(data):
    """Save models to database"""
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    with open(MODELS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_changelog():
    """Load changelog"""
    with open(CHANGELOG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_changelog(changelog):
    """Save changelog"""
    with open(CHANGELOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(changelog, f, indent=2, ensure_ascii=False)


def add_changelog_entry(change_type, description, model_id):
    """Add entry to changelog"""
    changelog = load_changelog()
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "type": change_type,
        "description": description,
        "models_affected": [model_id]
    }
    changelog["changelog"].insert(0, entry)  # Add to beginning
    save_changelog(changelog)


def get_user_input(prompt, default=None):
    """Get user input with optional default"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()


def get_modalities():
    """Get modalities from user"""
    print("\nSupported modalities (comma-separated):")
    print("Options: text, images, audio, video, documents")
    modalities_str = input("Enter modalities: ").strip()
    return [m.strip() for m in modalities_str.split(",")]


def get_pricing():
    """Get pricing information from user"""
    print("\n--- Pricing Information ---")
    input_price = float(get_user_input("Input cost per 1M tokens (USD)"))
    output_price = float(get_user_input("Output cost per 1M tokens (USD)"))
    notes = get_user_input("Pricing notes (optional)", "")

    pricing = {
        "input_per_1m_tokens": input_price,
        "output_per_1m_tokens": output_price,
        "currency": "USD",
        "last_updated": datetime.now().strftime("%Y-%m-%d")
    }
    if notes:
        pricing["notes"] = notes
    return pricing


def create_new_model():
    """Interactive model creation"""
    print("\n" + "="*60)
    print("           ADD NEW FRONTIER MODEL")
    print("="*60 + "\n")

    model_id = get_user_input("Model ID (e.g., claude-opus-4.5)")
    provider = get_user_input("Provider (e.g., Anthropic)")
    family = get_user_input("Model Family (e.g., Claude)")
    name = get_user_input("Full Name (e.g., Claude Opus 4.5)")
    release_date = get_user_input("Release Date (YYYY-MM-DD)")

    modalities = get_modalities()

    print("\n--- Features ---")
    context_window = int(get_user_input("Context window (tokens)"))
    output_tokens = int(get_user_input("Max output tokens"))
    vision = get_user_input("Vision support? (yes/no)").lower() == "yes"
    streaming = get_user_input("Streaming support? (yes/no)", "yes").lower() == "yes"

    features = {
        "context_window": context_window,
        "output_tokens": output_tokens,
        "vision": vision,
        "streaming": streaming
    }

    # Optional special features
    special_feature = get_user_input("Special feature (e.g., deep_think_mode, dynamic_thinking) [optional]", "")
    if special_feature:
        features[special_feature] = True

    pricing = get_pricing()

    print("\n--- Performance ---")
    speed_options = ["very_fast", "fast", "medium", "slow", "adaptive"]
    print(f"Speed tier options: {', '.join(speed_options)}")
    speed_tier = get_user_input("Speed tier")
    perf_notes = get_user_input("Performance notes")

    print("\n--- Use Cases ---")
    print("Enter use cases (comma-separated):")
    use_cases_str = input("Use cases: ").strip()
    use_cases = [uc.strip() for uc in use_cases_str.split(",")]

    model = {
        "id": model_id,
        "provider": provider,
        "family": family,
        "name": name,
        "release_date": release_date,
        "modalities": modalities,
        "features": features,
        "pricing": pricing,
        "performance": {
            "speed_tier": speed_tier,
            "notes": perf_notes
        },
        "use_cases": use_cases,
        "last_modified": datetime.now().strftime("%Y-%m-%d")
    }

    return model


def update_existing_model(model):
    """Update an existing model"""
    print(f"\n--- Updating {model['name']} ---")
    print("Leave blank to keep current value\n")

    # Update pricing
    update_price = get_user_input("Update pricing? (yes/no)", "no").lower() == "yes"
    if update_price:
        model["pricing"] = get_pricing()

    # Update features
    update_features = get_user_input("Update features? (yes/no)", "no").lower() == "yes"
    if update_features:
        context = get_user_input("Context window", str(model["features"]["context_window"]))
        output = get_user_input("Output tokens", str(model["features"]["output_tokens"]))
        model["features"]["context_window"] = int(context)
        model["features"]["output_tokens"] = int(output)

    # Update modalities
    update_mod = get_user_input("Update modalities? (yes/no)", "no").lower() == "yes"
    if update_mod:
        model["modalities"] = get_modalities()

    model["last_modified"] = datetime.now().strftime("%Y-%m-%d")
    return model


def main():
    """Main function"""
    data = load_models()

    print("\n" + "="*60)
    print("         AI MODEL DATABASE - ADD/UPDATE TOOL")
    print("="*60)

    # Check if updating existing model
    model_id = get_user_input("\nModel ID to add/update")

    # Search for existing model
    existing_model = None
    for i, model in enumerate(data["models"]):
        if model["id"] == model_id:
            existing_model = (i, model)
            break

    if existing_model:
        print(f"\n[OK] Found existing model: {existing_model[1]['name']}")
        choice = get_user_input("Update this model? (yes/no)", "yes").lower()

        if choice == "yes":
            updated_model = update_existing_model(existing_model[1])
            data["models"][existing_model[0]] = updated_model
            save_models(data)
            add_changelog_entry("update", f"Updated {updated_model['name']}", model_id)
            print(f"\n[OK] Model updated successfully!")
        else:
            print("Update cancelled.")
    else:
        print(f"\n[OK] Creating new model: {model_id}")
        new_model = create_new_model()
        data["models"].append(new_model)
        save_models(data)
        add_changelog_entry("addition", f"Added {new_model['name']}", model_id)
        print(f"\n[OK] Model added successfully!")

    print("\n" + "="*60)
    print(f"Database saved to: {MODELS_FILE}")
    print(f"Changelog updated: {CHANGELOG_FILE}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
