import json
import os

in_file = r"C:\Users\karma\.gemini\antigravity\brain\8637524f-bd1d-4107-ba23-275a4013a9f7\.system_generated\logs\transcript_full.jsonl"
out_file = r"C:\Users\karma\Desktop\ATO_Defence_Chat_History.txt"

with open(in_file, 'r', encoding='utf-8') as f_in, open(out_file, 'w', encoding='utf-8') as f_out:
    f_out.write("========================================================\n")
    f_out.write("CHAT HISTORY - ATO DEFENCE PREPARATION & STAT DECS\n")
    f_out.write("========================================================\n\n")
    for line in f_in:
        try:
            d = json.loads(line.strip())
            content = d.get("content", "")
            step_type = d.get("type", "")
            if not content:
                continue
            if step_type == "USER_INPUT":
                timestamp = d.get("created_at", "")
                f_out.write(f"\n{'='*50}\nUSER ({timestamp}):\n{content}\n")
            elif step_type == "PLANNER_RESPONSE":
                f_out.write(f"\n{'-'*50}\nAI ASSISTANT:\n{content}\n")
        except Exception as e:
            pass

print(f"Chat successfully saved to: {out_file}")
