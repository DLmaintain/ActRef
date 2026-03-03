import os
import json
import argparse
from pathlib import Path
from openai import OpenAI



MODEL_NAME = "Model Name"  
TEMPERATURE = 0

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_prompt(prompt_path: str) -> str:
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def build_prompt(template: str, diff_text: str) -> str:
    return template.replace("[Change Codes]", diff_text)

def call_model(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def load_commit_json(json_path: str):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_diff(commit_data):
    """
    commit_data is a list of file-level change objects.
    We concatenate all patches into one diff string.
    """
    diffs = []
    for file_change in commit_data:
        patch = file_change.get("patch")
        if patch:
            diffs.append(f"File: {file_change.get('filename')}\n{patch}")
    return "\n\n".join(diffs)


def process_commit(json_path, prompt_template, output_dir):
    commit_data = load_commit_json(json_path)
    diff_text = extract_diff(commit_data)

    if not diff_text.strip():
        print(f"[Warning] No patch found in {json_path}")
        return

    full_prompt = build_prompt(prompt_template, diff_text)

    print(f"[Running] {json_path}")
    output = call_model(full_prompt)

    sha = commit_data[0]["sha"]
    result = {
        "sha": sha,
        "model": MODEL_NAME,
        "temperature": TEMPERATURE,
        "output": output
    }

    output_path = Path(output_dir) / f"{sha}_llm_output.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"[Saved] {output_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit_dir", type=str, required=True,
                        help="Directory containing commit JSON files")
    parser.add_argument("--prompt", type=str, required=True,
                        help="Path to prompt template file")
    parser.add_argument("--output_dir", type=str, required=True,
                        help="Directory to save model outputs")

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    prompt_template = load_prompt(args.prompt)

    commit_files = list(Path(args.commit_dir).glob("*.json"))

    for json_file in commit_files:
        process_commit(str(json_file), prompt_template, args.output_dir)


if __name__ == "__main__":
    main()
