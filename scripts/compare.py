#!/usr/bin/env python3
"""
Compare frontier AI models side-by-side
"""

import json
import os
from tabulate import tabulate

# Get the absolute path to the data directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
MODELS_FILE = os.path.join(DATA_DIR, "models.json")


def load_models():
    """Load models from database"""
    with open(MODELS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_modalities(modalities):
    """Format modalities list for display"""
    return ", ".join(modalities)


def format_price(input_price, output_price):
    """Format pricing for display"""
    return f"${input_price:.2f} / ${output_price:.2f}"


def list_all_models(data):
    """Display all models in database"""
    print("\n" + "="*80)
    print("                    AVAILABLE FRONTIER MODELS")
    print("="*80 + "\n")

    rows = []
    for model in data["models"]:
        rows.append([
            model["id"],
            model["provider"],
            model["name"],
            model["release_date"]
        ])

    print(tabulate(rows, headers=["ID", "Provider", "Name", "Release Date"], tablefmt="grid"))
    print()


def compare_models(models_to_compare):
    """Compare selected models"""
    print("\n" + "="*100)
    print("                         MODEL COMPARISON")
    print("="*100 + "\n")

    # Priority order: Modalities > Context Window > Pricing > Speed
    print("--- MODALITIES ---")
    mod_rows = []
    for model in models_to_compare:
        mod_rows.append([
            model["name"],
            format_modalities(model["modalities"])
        ])
    print(tabulate(mod_rows, headers=["Model", "Supported Modalities"], tablefmt="grid"))

    print("\n--- CONTEXT WINDOW ---")
    context_rows = []
    for model in models_to_compare:
        context_rows.append([
            model["name"],
            f"{model['features']['context_window']:,}",
            f"{model['features']['output_tokens']:,}"
        ])
    print(tabulate(context_rows, headers=["Model", "Input Tokens", "Output Tokens"], tablefmt="grid"))

    print("\n--- PRICING (per 1M tokens) ---")
    price_rows = []
    for model in models_to_compare:
        input_cost = model["pricing"]["input_per_1m_tokens"]
        output_cost = model["pricing"]["output_per_1m_tokens"]
        price_rows.append([
            model["name"],
            f"${input_cost:.2f}",
            f"${output_cost:.2f}",
            model["pricing"].get("notes", "")
        ])
    print(tabulate(price_rows, headers=["Model", "Input Cost", "Output Cost", "Notes"], tablefmt="grid"))

    print("\n--- PERFORMANCE ---")
    perf_rows = []
    for model in models_to_compare:
        perf_rows.append([
            model["name"],
            model["performance"]["speed_tier"],
            model["performance"]["notes"]
        ])
    print(tabulate(perf_rows, headers=["Model", "Speed Tier", "Notes"], tablefmt="grid"))

    print("\n--- USE CASES ---")
    for model in models_to_compare:
        print(f"\n{model['name']}:")
        print(f"  • {', '.join(model['use_cases'])}")

    print("\n" + "="*100 + "\n")


def compare_by_provider(data):
    """Compare all models from the same provider"""
    print("\nAvailable providers:")
    providers = sorted(set(m["provider"] for m in data["models"]))
    for i, provider in enumerate(providers, 1):
        print(f"  {i}. {provider}")

    choice = input("\nSelect provider number: ").strip()
    try:
        provider_name = providers[int(choice) - 1]
        models = [m for m in data["models"] if m["provider"] == provider_name]
        if models:
            compare_models(models)
        else:
            print(f"No models found for {provider_name}")
    except (ValueError, IndexError):
        print("Invalid selection")


def compare_custom(data):
    """Compare custom selection of models"""
    list_all_models(data)

    print("Enter model IDs to compare (comma-separated):")
    ids = input("Model IDs: ").strip().split(",")
    ids = [id.strip() for id in ids]

    models = [m for m in data["models"] if m["id"] in ids]

    if len(models) < 2:
        print("\n❌ Please select at least 2 models to compare")
        return

    compare_models(models)


def compare_all(data):
    """Compare all models in database"""
    compare_models(data["models"])


def cost_analysis(data):
    """Analyze and rank models by cost efficiency"""
    print("\n" + "="*80)
    print("                      COST EFFICIENCY ANALYSIS")
    print("="*80 + "\n")

    # Calculate cost per token and rank
    cost_data = []
    for model in data["models"]:
        input_cost = model["pricing"]["input_per_1m_tokens"]
        output_cost = model["pricing"]["output_per_1m_tokens"]
        avg_cost = (input_cost + output_cost) / 2

        cost_data.append({
            "name": model["name"],
            "input": input_cost,
            "output": output_cost,
            "average": avg_cost,
            "context": model["features"]["context_window"]
        })

    # Sort by average cost
    cost_data.sort(key=lambda x: x["average"])

    rows = []
    for i, model in enumerate(cost_data, 1):
        rows.append([
            i,
            model["name"],
            f"${model['input']:.2f}",
            f"${model['output']:.2f}",
            f"${model['average']:.2f}",
            f"{model['context']:,}"
        ])

    print(tabulate(rows, headers=["Rank", "Model", "Input", "Output", "Avg", "Context"], tablefmt="grid"))
    print("\n[INFO] Ranked by average cost per 1M tokens (lower is cheaper)\n")


def main():
    """Main function"""
    data = load_models()

    print("\n" + "="*80)
    print("              AI MODEL COMPARISON TOOL")
    print("="*80)

    while True:
        print("\nOptions:")
        print("  1. Compare all models")
        print("  2. Compare by provider")
        print("  3. Compare custom selection")
        print("  4. Cost efficiency analysis")
        print("  5. List all models")
        print("  6. Exit")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            compare_all(data)
        elif choice == "2":
            compare_by_provider(data)
        elif choice == "3":
            compare_custom(data)
        elif choice == "4":
            cost_analysis(data)
        elif choice == "5":
            list_all_models(data)
        elif choice == "6":
            print("\nGoodbye!\n")
            break
        else:
            print("\n[ERROR] Invalid option")


if __name__ == "__main__":
    main()
