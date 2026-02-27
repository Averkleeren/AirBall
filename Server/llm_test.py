import ollama
import json
from typing import Any, Dict


def generate_feedback(shot_data: Any) -> str:
    """Send the shot analysis to the Claude‑style model and return the
    textual feedback.  The imported ollama library is used in the
    existing script; we provide the same prompt as before but expose an
    easy API for the rest of the service.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful sports performance coach assistant. Your task is "
                "to provide clear, actionable, and concise feedback on athletic "
                "movement data."
            ),
        },
        {
            "role": "user",
            "content": (
                "I have collected shooting/movement data for a player. Provide "
                "feedback that is: 1. Clear and easy to understand for a coach or "
                "athlete. 2. Divided into sections: overall assessment, strengths, "
                "areas for improvement, and prioritized recommendations. 3. Free of "
                "raw timestamps or exact floating-point numbers; translate these "
                "into plain language. 4. Actionable: each weakness should include "
                "a practical way to improve it. 5. Concise: avoid redundant points "
                "and repetitive phrasing. 6. Professional and encouraging in tone. "
                f"Here is the data: {json.dumps(shot_data, indent=2)}"
            ),
        },
    ]
    response = ollama.chat(model="gemma3:1b", messages=messages)
    # the ollama library returns a dict with a message key
    return response.get("message", {}).get("content", "")


if __name__ == "__main__":
    # keep the old behavior when run as a script
    shot_file_path = "./Shots/shot_9c595354-04cf-48bf-a023-acb61176a20f.json"
    with open(shot_file_path, "r") as f:
        shot_data = json.load(f)
    fb = generate_feedback(shot_data)
    with open("shot_feedback.txt", "w") as f:
        f.write(fb)
    print("Feedback written to shot_feedback.txt")
