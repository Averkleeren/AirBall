import ollama
import json

# Load the shot data from the JSON file
shot_file_path = "./Shots/shot_9c595354-04cf-48bf-a023-acb61176a20f.json"
with open(shot_file_path, 'r') as f:
    shot_data = json.load(f)

response = ollama.chat(
    model="gemma3:1b",
    messages=[
        {"role": "system", "content": "You are a helpful sports performance coach assistant. Your task is to provide clear, actionable, and concise feedback on athletic movement data."},
        {"role": "user", "content": f"I have collected shooting/movement data for a player. Provide feedback that is: 1. Clear and easy to understand for a coach or athlete. 2. Divided into sections: overall assessment, strengths, areas for improvement, and prioritized recommendations. 3. Free of raw timestamps or exact floating-point numbers; translate these into plain language. 4. Actionable: each weakness should include a practical way to improve it. 5. Concise: avoid redundant points and repetitive phrasing. 6. Professional and encouraging in tone. Here is the data: {json.dumps(shot_data, indent=2)}"}
    ]
)

# Write the response to a text file
with open("shot_feedback.txt", "w") as f:
    f.write(response["message"]["content"])

print("Feedback written to shot_feedback.txt")
