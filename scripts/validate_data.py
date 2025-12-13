#!/usr/bin/env python3
"""
Data validation script to check for common issues in models.json
"""

import json
from datetime import datetime

def validate_models():
    """Check models.json for common data quality issues"""

    with open('../data/models.json', 'r') as f:
        data = json.load(f)

    issues = []
    warnings = []

    print("Validating models.json...\n")

    for idx, model in enumerate(data['models'], 1):
        model_name = model.get('name', f"Model #{idx}")

        # Check for future release dates
        release_date = model.get('release_date', '')
        if release_date:
            try:
                release_dt = datetime.strptime(release_date, '%Y-%m-%d')
                if release_dt > datetime.now():
                    warnings.append(f"WARNING: {model_name}: Future release date ({release_date})")
            except ValueError:
                issues.append(f"ERROR: {model_name}: Invalid date format ({release_date})")

        # Check for missing required fields
        required_fields = ['id', 'provider', 'name', 'features', 'pricing', 'performance']
        for field in required_fields:
            if field not in model:
                issues.append(f"ERROR: {model_name}: Missing required field '{field}'")

        # Check pricing
        pricing = model.get('pricing', {})
        if pricing:
            input_price = pricing.get('input_per_1m_tokens')
            output_price = pricing.get('output_per_1m_tokens')

            if input_price is None:
                issues.append(f"ERROR: {model_name}: Missing input pricing")
            elif input_price < 0:
                issues.append(f"ERROR: {model_name}: Negative input price")

            if output_price is None:
                issues.append(f"ERROR: {model_name}: Missing output pricing")
            elif output_price < 0:
                issues.append(f"ERROR: {model_name}: Negative output price")

            # Check if output is more expensive than input (usually true)
            if input_price and output_price and output_price < input_price:
                warnings.append(f"WARNING:  {model_name}: Output price < input price (unusual)")

        # Check context window
        features = model.get('features', {})
        context_window = features.get('context_window')
        if context_window:
            if context_window < 1000:
                warnings.append(f"WARNING:  {model_name}: Very small context window ({context_window})")
            if context_window > 10000000:
                warnings.append(f"WARNING:  {model_name}: Extremely large context window ({context_window})")

        # Check for inconsistent feature flags
        vision = features.get('vision', False)
        modalities = model.get('modalities', [])
        if vision and 'images' not in modalities:
            warnings.append(f"WARNING:  {model_name}: Has vision=true but 'images' not in modalities")
        if not vision and 'images' in modalities:
            warnings.append(f"WARNING:  {model_name}: Has 'images' in modalities but vision=false")

    # Print results
    print(f"Total models: {len(data['models'])}\n")

    if issues:
        print("CRITICAL ISSUES (must fix):")
        for issue in issues:
            print(f"  {issue}")
        print()

    if warnings:
        print("WARNINGS (review recommended):")
        for warning in warnings:
            print(f"  {warning}")
        print()

    if not issues and not warnings:
        print("All checks passed! Data looks good.\n")

    return len(issues) == 0

if __name__ == "__main__":
    validate_models()
