#!/usr/bin/env python3
"""
Interactive script to add or update AI provider ecosystems in providers.json
"""

import json
import os
from datetime import datetime

def load_providers():
    """Load existing providers data"""
    file_path = '../data/providers.json'

    if not os.path.exists(file_path):
        return {"last_updated": datetime.now().strftime("%Y-%m-%d"), "providers": []}

    with open(file_path, 'r') as f:
        return json.load(f)

def save_providers(data):
    """Save providers data"""
    file_path = '../data/providers.json'
    data['last_updated'] = datetime.now().strftime("%Y-%m-%d")

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n✅ Providers data saved successfully to {file_path}")

def add_llm_model():
    """Add an LLM model to a provider"""
    print("\n--- Add LLM Model ---")
    name = input("Model name (e.g., 'Claude Opus 4.5'): ").strip()
    model_type = input("Type (e.g., 'Large Language Model'): ").strip()
    description = input("Description: ").strip()

    return {
        "name": name,
        "type": model_type,
        "description": description
    }

def add_specialized_product():
    """Add a specialized product to a provider"""
    print("\n--- Add Specialized Product ---")
    name = input("Product name (e.g., 'DALL-E 3'): ").strip()
    product_type = input("Type (e.g., 'Image Generation'): ").strip()
    description = input("Description: ").strip()

    return {
        "name": name,
        "type": product_type,
        "description": description
    }

def add_capability():
    """Add or update a capability"""
    print("\n--- Add/Update Capability ---")
    cap_name = input("Capability name (e.g., 'image_generation'): ").strip().lower().replace(' ', '_')
    available = input("Available? (y/n): ").strip().lower() == 'y'

    products = []
    if available:
        print("Enter product names (one per line, empty line to finish):")
        while True:
            product = input("  Product: ").strip()
            if not product:
                break
            products.append(product)

    description = input("Description (optional): ").strip()

    capability = {
        "available": available,
        "products": products
    }

    if description:
        capability["description"] = description

    return cap_name, capability

def add_or_update_provider():
    """Main function to add or update a provider"""
    data = load_providers()

    print("\n=== Add/Update AI Provider ===")
    print("\nExisting providers:")
    for i, p in enumerate(data['providers'], 1):
        print(f"  {i}. {p['name']} ({p['id']})")

    print("\nOptions:")
    print("  1. Add new provider")
    print("  2. Update existing provider")
    choice = input("\nChoice (1 or 2): ").strip()

    if choice == '1':
        # Add new provider
        print("\n--- New Provider Details ---")
        provider_id = input("Provider ID (lowercase, e.g., 'anthropic'): ").strip().lower()
        name = input("Provider name (e.g., 'Anthropic'): ").strip()
        description = input("Description: ").strip()
        founded = input("Founded year: ").strip()
        headquarters = input("Headquarters: ").strip()

        provider = {
            "id": provider_id,
            "name": name,
            "description": description,
            "founded": founded,
            "headquarters": headquarters,
            "product_families": {
                "llm_models": [],
                "specialized_products": []
            },
            "capabilities": {}
        }

        data['providers'].append(provider)
        print(f"\n✅ Added new provider: {name}")

    elif choice == '2':
        # Update existing provider
        provider_num = int(input("Select provider number: ").strip()) - 1
        provider = data['providers'][provider_num]
        print(f"\nUpdating: {provider['name']}")

    else:
        print("Invalid choice")
        return

    # Menu for updates
    while True:
        print(f"\n--- {provider['name']} ---")
        print("1. Add LLM model")
        print("2. Add specialized product")
        print("3. Add/update capability")
        print("4. View current data")
        print("5. Save and exit")

        action = input("\nChoice: ").strip()

        if action == '1':
            model = add_llm_model()
            provider['product_families']['llm_models'].append(model)
            print(f"✅ Added LLM model: {model['name']}")

        elif action == '2':
            product = add_specialized_product()
            provider['product_families']['specialized_products'].append(product)
            print(f"✅ Added product: {product['name']}")

        elif action == '3':
            cap_name, capability = add_capability()
            provider['capabilities'][cap_name] = capability
            print(f"✅ Updated capability: {cap_name}")

        elif action == '4':
            print("\n--- Current Provider Data ---")
            print(json.dumps(provider, indent=2))

        elif action == '5':
            save_providers(data)
            print("\n🎉 Done! The dashboard will auto-refresh on next page load.")
            break

        else:
            print("Invalid choice")

if __name__ == "__main__":
    try:
        add_or_update_provider()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
