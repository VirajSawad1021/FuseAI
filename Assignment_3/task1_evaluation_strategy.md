# Task 1, Part 2: Evaluation Strategy for Text-to-SQL Agents

## Objective
To rigorously evaluate the performance of an autonomous Text-to-SQL agent, we must go beyond just measuring "does the query run?" We need a framework that measures accuracy, robustness, error-handling capabilities, and human readability.

## Evaluation Dimensions

### 1. SQL Correctness and Precision (Exact Match & Execution Match)
- **Execution Match:** Does the generated SQL return the exact same data payload as the Ground Truth SQL? (This is the most critical metric).
- **Correct Table & Column Selection:** Ensure the LLM didn't hallucinate column names or use SELECT * when specific columns were requested.
- **Join Accuracy:** Check if the correct Primary Key / Foreign Key pathways were used to connect multiple tables.

### 2. Execution Success Rate & Error Handling
- **First-Pass Success Rate:** What percentage of queries execute successfully on the very first LLM attempt without raising database errors?
- **Self-Correction Success Rate:** If a query fails (e.g., column not found), does the agent successfully catch the DB exception, rewrite the query, and get a successful result within the allocated retry limit?
- **Resilience to Ambiguity:** How does the agent perform when user phrasing is poor (e.g., "Give me money stuff" instead of "Total revenue from payments")?

### 3. Agentic Behavior and Formatting
- **Natural Language Quality:** Is the final returned summary human-readable, grammatically correct, and accurately reflecting the data? 
- **Latency (Execution Time):** How long does the entire loop (Plan -> Code -> Execute -> Format) take in seconds? High latency might mean the agent is looping out of control.
- **Safe Execution Validations:** Are destructive queries (DROP, DELETE, UPDATE) successfully detected and blocked by the validator?

## Proposed Evaluation Benchmark Pipeline
1. Loop over the 50 Benchmark Questions.
2. Feed each question to the POST /agent/sql endpoint.
3. Compare the generated esult payload against the Ground Truth result.
4. Calculate final score out of 50.
