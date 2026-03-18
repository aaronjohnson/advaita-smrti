# smṛti-bench — Antigravity agent task

You are participating in a memory benchmark for advaita-smrti.

1. Read bench/prompts/battery.txt in this repo
2. Answer each of the 6 prompts using only what is available to you
   right now (memory tools if connected, nothing else)
3. Do not search the web or read other project files to answer
4. Write results to bench/results/antigravity_{arm}_{timestamp}Z.json
   where arm is "baseline" (no smṛti MCP) or "smrti" (smṛti connected)
5. Match schema in bench/results/antigravity_schema.json
6. Populate tool_calls_observed from your own tool call log
7. Run: git add bench/results/ && git commit -m "bench: antigravity {arm} {timestamp}"
   Do NOT push.
