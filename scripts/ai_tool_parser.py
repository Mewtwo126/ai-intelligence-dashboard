#!/usr/bin/env python3
"""
AI Tool Parser - Extract and analyze AI tool information using local LLM (Ollama)
"""

import os
import sys
import requests
import json


def get_multiline_input():
    """
    Prompts user for multi-line input until 'DONE' is entered.
    Returns the collected text as a single string.
    """
    print("\n" + "="*60)
    print("Paste your AI tool content below.")
    print("When finished, type 'DONE' on a new line and press Enter.")
    print("="*60 + "\n")

    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "DONE":
                break
            lines.append(line)
        except EOFError:
            break

    return "\n".join(lines)


def analyze_with_ollama(text, model="llama3.2", ollama_url="http://localhost:11434"):
    """
    Sends text to local Ollama LLM for analysis.
    Returns the LLM's response.
    """
    prompt = """You are an AI Tech Scout Agent. Analyze the following text about an AI tool and generate a standardized Spec Sheet with these sections:
- Name & Developer
- Core Function (1 sentence)
- Cost Model
- Key Differentiator
- Limitations

Use the Translation Guidelines to explain technical jargon at a high school level. Be educational and warm in tone.

Here is the text to analyze:

""" + text

    print(f"\n🔄 Analyzing with Ollama ({model})...\n")

    try:
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()

        result = response.json()
        return result.get("response", "No response generated")

    except requests.exceptions.ConnectionError:
        raise Exception(
            "Could not connect to Ollama. Make sure Ollama is running.\n"
            "Install: https://ollama.com/download\n"
            f"Start Ollama and run: ollama pull {model}"
        )
    except requests.exceptions.Timeout:
        raise Exception("Request timed out. The model might be too slow or not responding.")
    except Exception as e:
        raise Exception(f"Error communicating with Ollama: {str(e)}")


def save_analysis(analysis, tool_name="analysis"):
    """
    Saves the analysis to a file in the current directory.
    """
    # Sanitize filename
    safe_name = "".join(c for c in tool_name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_')

    if not safe_name:
        safe_name = "ai_tool_analysis"

    filename = f"{safe_name}.txt"

    # Check if file exists and create unique name if needed
    counter = 1
    original_filename = filename
    while os.path.exists(filename):
        filename = f"{safe_name}_{counter}.txt"
        counter += 1

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(analysis)

    return filename


def main():
    """
    Main function to run the AI Tool Parser.
    """
    print("\n" + "="*60)
    print("           AI TOOL PARSER - Local LLM Tech Scout")
    print("="*60)

    # Get input from user
    input_text = get_multiline_input()

    if not input_text.strip():
        print("\n❌ No content provided. Exiting.")
        sys.exit(0)

    # Save to temporary file
    temp_file = "temp_input.txt"
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(input_text)
    print(f"\n✓ Content saved to temporary file: {temp_file}")

    # Analyze with Ollama
    # You can change the model here: llama3.2, mistral, phi3, etc.
    model = os.environ.get("OLLAMA_MODEL", "llama3.2")

    try:
        analysis = analyze_with_ollama(input_text, model=model)

        # Display analysis
        print("\n" + "="*60)
        print("                    ANALYSIS RESULT")
        print("="*60 + "\n")
        print(analysis)
        print("\n" + "="*60 + "\n")

        # Ask to save
        save_choice = input("Would you like to save this analysis? (yes/no): ").strip().lower()

        if save_choice in ['yes', 'y']:
            # Try to extract tool name from analysis for better filename
            tool_name = "ai_tool_analysis"
            if "Name & Developer" in analysis:
                # Try to extract first line after "Name & Developer"
                lines = analysis.split('\n')
                for i, line in enumerate(lines):
                    if "Name & Developer" in line and i + 1 < len(lines):
                        tool_name = lines[i + 1].strip().split(':')[-1].strip()
                        break

            saved_file = save_analysis(analysis, tool_name)
            print(f"\n✓ Analysis saved to: {saved_file}")
        else:
            print("\n✓ Analysis not saved.")

        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"✓ Temporary file removed: {temp_file}")

    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        sys.exit(1)

    print("\n" + "="*60)
    print("                    COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
