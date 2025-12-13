#!/usr/bin/env python3
"""
Trend Analyzer - Analyze trends across snapshots and current database
"""

import json
import os
from datetime import datetime
from collections import Counter
from pathlib import Path

# Get the absolute path to the data directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
SNAPSHOTS_DIR = os.path.join(DATA_DIR, "snapshots")
MODELS_FILE = os.path.join(DATA_DIR, "models.json")
REPORTS_DIR = os.path.join(PROJECT_DIR, "reports")


def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filepath, data):
    """Save JSON file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_all_snapshots():
    """
    Get list of all available snapshots sorted by date
    Returns list of dicts with path and metadata
    """
    snapshots = []

    if not os.path.exists(SNAPSHOTS_DIR):
        return snapshots

    # Get all month directories
    for month_dir in os.listdir(SNAPSHOTS_DIR):
        month_path = os.path.join(SNAPSHOTS_DIR, month_dir)
        if not os.path.isdir(month_path):
            continue

        # Look for snapshot files
        for file in os.listdir(month_path):
            if file.startswith("models_") and file.endswith(".json"):
                date_str = file.replace("models_", "").replace(".json", "")
                snapshots.append({
                    "date": date_str,
                    "path": os.path.join(month_path, file),
                    "month": month_dir
                })

    # Sort by date
    snapshots.sort(key=lambda x: x["date"])

    return snapshots


def extract_snapshot_data(snapshot_path):
    """
    Extract key metrics from a snapshot
    Returns dict with analyzed data
    """
    data = load_json(snapshot_path)
    models = data.get("models", [])

    # Extract modalities
    all_modalities = []
    modality_counts = Counter()
    for model in models:
        for modality in model.get("modalities", []):
            all_modalities.append(modality)
            modality_counts[modality] += 1

    # Extract context windows
    context_windows = [m["features"]["context_window"] for m in models]
    avg_context = sum(context_windows) / len(context_windows) if context_windows else 0
    max_context = max(context_windows) if context_windows else 0

    # Extract pricing
    input_prices = [m["pricing"]["input_per_1m_tokens"] for m in models]
    output_prices = [m["pricing"]["output_per_1m_tokens"] for m in models]
    avg_input_price = sum(input_prices) / len(input_prices) if input_prices else 0
    avg_output_price = sum(output_prices) / len(output_prices) if output_prices else 0

    # Extract speed tiers
    speed_tiers = Counter([m["performance"]["speed_tier"] for m in models])

    # Extract providers
    providers = Counter([m["provider"] for m in models])

    return {
        "total_models": len(models),
        "modalities": {
            "counts": dict(modality_counts),
            "unique": len(modality_counts),
            "adoption_rate": {mod: count/len(models)*100 for mod, count in modality_counts.items()}
        },
        "context_windows": {
            "average": avg_context,
            "max": max_context,
            "all": context_windows
        },
        "pricing": {
            "avg_input": avg_input_price,
            "avg_output": avg_output_price,
            "min_input": min(input_prices) if input_prices else 0,
            "max_input": max(input_prices) if input_prices else 0,
            "min_output": min(output_prices) if output_prices else 0,
            "max_output": max(output_prices) if output_prices else 0
        },
        "speed_tiers": dict(speed_tiers),
        "providers": dict(providers)
    }


def analyze_modality_trends(snapshot_data_list):
    """
    Analyze how modalities are evolving over time
    """
    print("\n" + "="*80)
    print("                    MODALITY TRENDS")
    print("="*80 + "\n")

    if len(snapshot_data_list) < 2:
        print("[INFO] Need at least 2 snapshots to analyze trends.\n")
        return {}

    oldest = snapshot_data_list[0]
    newest = snapshot_data_list[-1]

    trends = {}

    # New modalities
    old_mods = set(oldest["data"]["modalities"]["counts"].keys())
    new_mods = set(newest["data"]["modalities"]["counts"].keys())
    added_mods = new_mods - old_mods

    if added_mods:
        print(f"[+] NEW MODALITIES EMERGED:")
        for mod in added_mods:
            adoption = newest["data"]["modalities"]["adoption_rate"][mod]
            print(f"    + {mod.capitalize()} (now in {adoption:.1f}% of models)")
        print()
        trends["new_modalities"] = list(added_mods)

    # Adoption rate changes
    print("[~] MODALITY ADOPTION CHANGES:")
    for mod in old_mods & new_mods:
        old_rate = oldest["data"]["modalities"]["adoption_rate"][mod]
        new_rate = newest["data"]["modalities"]["adoption_rate"][mod]
        change = new_rate - old_rate

        if abs(change) > 5:  # Only show significant changes
            direction = "increased" if change > 0 else "decreased"
            print(f"    {mod.capitalize()}: {old_rate:.1f}% -> {new_rate:.1f}% ({direction} by {abs(change):.1f}%)")

    print("\n" + "="*80 + "\n")

    return trends


def analyze_context_window_trends(snapshot_data_list):
    """
    Analyze context window evolution
    """
    print("\n" + "="*80)
    print("                    CONTEXT WINDOW TRENDS")
    print("="*80 + "\n")

    if len(snapshot_data_list) < 2:
        print("[INFO] Need at least 2 snapshots to analyze trends.\n")
        return {}

    oldest = snapshot_data_list[0]
    newest = snapshot_data_list[-1]

    old_avg = oldest["data"]["context_windows"]["average"]
    new_avg = newest["data"]["context_windows"]["average"]
    old_max = oldest["data"]["context_windows"]["max"]
    new_max = newest["data"]["context_windows"]["max"]

    avg_growth = ((new_avg - old_avg) / old_avg * 100) if old_avg > 0 else 0

    print(f"Average Context Window:")
    print(f"  {oldest['date']}: {old_avg:,.0f} tokens")
    print(f"  {newest['date']}: {new_avg:,.0f} tokens")
    print(f"  Growth: {avg_growth:+.1f}%")
    print()

    print(f"Maximum Context Window:")
    print(f"  {oldest['date']}: {old_max:,} tokens")
    print(f"  {newest['date']}: {new_max:,} tokens")
    if new_max > old_max:
        print(f"  [!] New record set: {new_max:,} tokens")
    print()

    # Million-token club
    old_million = sum(1 for cw in oldest["data"]["context_windows"]["all"] if cw >= 1000000)
    new_million = sum(1 for cw in newest["data"]["context_windows"]["all"] if cw >= 1000000)

    if new_million > 0:
        print(f"'Million-Token Context' Models:")
        print(f"  {oldest['date']}: {old_million} models")
        print(f"  {newest['date']}: {new_million} models")
        if new_million > old_million:
            print(f"  [+] {new_million - old_million} new models joined the million-token club")

    print("\n" + "="*80 + "\n")

    return {
        "avg_growth_pct": avg_growth,
        "max_context_old": old_max,
        "max_context_new": new_max
    }


def analyze_pricing_trends(snapshot_data_list):
    """
    Analyze pricing evolution
    """
    print("\n" + "="*80)
    print("                    PRICING TRENDS")
    print("="*80 + "\n")

    if len(snapshot_data_list) < 2:
        print("[INFO] Need at least 2 snapshots to analyze trends.\n")
        return {}

    oldest = snapshot_data_list[0]
    newest = snapshot_data_list[-1]

    old_avg_in = oldest["data"]["pricing"]["avg_input"]
    new_avg_in = newest["data"]["pricing"]["avg_input"]
    old_avg_out = oldest["data"]["pricing"]["avg_output"]
    new_avg_out = newest["data"]["pricing"]["avg_output"]

    input_change = ((new_avg_in - old_avg_in) / old_avg_in * 100) if old_avg_in > 0 else 0
    output_change = ((new_avg_out - old_avg_out) / old_avg_out * 100) if old_avg_out > 0 else 0

    print(f"Average Input Pricing (per 1M tokens):")
    print(f"  {oldest['date']}: ${old_avg_in:.2f}")
    print(f"  {newest['date']}: ${new_avg_in:.2f}")
    print(f"  Change: {input_change:+.1f}%")

    if abs(input_change) > 10:
        direction = "increased" if input_change > 0 else "decreased"
        print(f"  [!] Significant {direction} in input pricing")
    print()

    print(f"Average Output Pricing (per 1M tokens):")
    print(f"  {oldest['date']}: ${old_avg_out:.2f}")
    print(f"  {newest['date']}: ${new_avg_out:.2f}")
    print(f"  Change: {output_change:+.1f}%")

    if abs(output_change) > 10:
        direction = "increased" if output_change > 0 else "decreased"
        print(f"  [!] Significant {direction} in output pricing")
    print()

    print(f"Price Range:")
    print(f"  Input: ${newest['data']['pricing']['min_input']:.2f} - ${newest['data']['pricing']['max_input']:.2f}")
    print(f"  Output: ${newest['data']['pricing']['min_output']:.2f} - ${newest['data']['pricing']['max_output']:.2f}")

    print("\n" + "="*80 + "\n")

    return {
        "input_change_pct": input_change,
        "output_change_pct": output_change
    }


def analyze_market_trends(snapshot_data_list):
    """
    Analyze market composition and provider trends
    """
    print("\n" + "="*80)
    print("                    MARKET TRENDS")
    print("="*80 + "\n")

    if len(snapshot_data_list) < 2:
        print("[INFO] Need at least 2 snapshots to analyze trends.\n")
        return {}

    oldest = snapshot_data_list[0]
    newest = snapshot_data_list[-1]

    old_providers = set(oldest["data"]["providers"].keys())
    new_providers = set(newest["data"]["providers"].keys())

    # New providers
    added_providers = new_providers - old_providers
    if added_providers:
        print(f"[+] NEW PROVIDERS ENTERED MARKET:")
        for provider in added_providers:
            model_count = newest["data"]["providers"][provider]
            print(f"    + {provider} ({model_count} models)")
        print()

    # Market share changes
    print("Provider Model Count:")
    for provider in sorted(new_providers):
        old_count = oldest["data"]["providers"].get(provider, 0)
        new_count = newest["data"]["providers"][provider]

        if new_count != old_count:
            change = new_count - old_count
            print(f"  {provider}: {old_count} -> {new_count} ({change:+d})")
        else:
            print(f"  {provider}: {new_count}")
    print()

    # Total market growth
    total_growth = newest["data"]["total_models"] - oldest["data"]["total_models"]
    print(f"Total Market:")
    print(f"  {oldest['date']}: {oldest['data']['total_models']} models")
    print(f"  {newest['date']}: {newest['data']['total_models']} models")
    print(f"  Growth: {total_growth:+d} models")

    print("\n" + "="*80 + "\n")

    return {
        "new_providers": list(added_providers),
        "total_growth": total_growth
    }


def main():
    """Main function"""
    print("\n" + "="*80)
    print("              TREND ANALYZER")
    print("="*80)

    # Get all snapshots
    snapshots = get_all_snapshots()

    if len(snapshots) == 0:
        print("\n[ERROR] No snapshots found. Create snapshots first using snapshot_manager.py\n")
        return

    if len(snapshots) < 2:
        print(f"\n[INFO] Only 1 snapshot found. Need at least 2 snapshots to analyze trends.")
        print(f"       Current snapshot: {snapshots[0]['date']}")
        print(f"       Create more snapshots over time to track trends.\n")
        return

    print(f"\n[OK] Found {len(snapshots)} snapshots")
    print(f"     Date range: {snapshots[0]['date']} to {snapshots[-1]['date']}\n")

    # Extract data from all snapshots
    snapshot_data = []
    for snap in snapshots:
        data = extract_snapshot_data(snap["path"])
        snapshot_data.append({
            "date": snap["date"],
            "data": data
        })

    # Run trend analyses (in priority order: Modality > Context > Pricing > Market)
    modality_trends = analyze_modality_trends(snapshot_data)
    context_trends = analyze_context_window_trends(snapshot_data)
    pricing_trends = analyze_pricing_trends(snapshot_data)
    market_trends = analyze_market_trends(snapshot_data)

    # Generate summary report
    print("\n" + "="*80)
    print("                    KEY INSIGHTS")
    print("="*80 + "\n")

    insights = []

    # Context window insights
    if context_trends.get("avg_growth_pct", 0) > 20:
        insights.append(f"[!] Context windows growing rapidly ({context_trends['avg_growth_pct']:+.1f}%)")

    # Pricing insights
    if abs(pricing_trends.get("input_change_pct", 0)) > 15:
        direction = "up" if pricing_trends["input_change_pct"] > 0 else "down"
        insights.append(f"[!] Input prices trending {direction} ({pricing_trends['input_change_pct']:+.1f}%)")

    # Market insights
    if market_trends.get("total_growth", 0) > 0:
        insights.append(f"[+] Market expanding: {market_trends['total_growth']} new models added")

    if market_trends.get("new_providers"):
        providers_str = ", ".join(market_trends["new_providers"])
        insights.append(f"[+] New providers: {providers_str}")

    if modality_trends.get("new_modalities"):
        mods_str = ", ".join(modality_trends["new_modalities"])
        insights.append(f"[+] New modalities emerging: {mods_str}")

    if insights:
        for insight in insights:
            print(f"  {insight}")
    else:
        print("  [INFO] No major trends detected in this period.")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
