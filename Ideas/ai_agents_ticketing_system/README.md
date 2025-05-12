# AI Agents Ticketing System

This is a Python-based local application that uses AI agents to:
1. Read email content.
2. Extract action items into JSON.
3. Create JIRA tickets from extracted tasks.

## Architecture
- **Agent 1**: Parses raw email body.
- **Agent 2**: Uses LLaMA/Gemma (via GROQ or LM Studio) to generate structured task JSON.
- **Agent 3**: Uses JIRA API to create tickets.
- **Orchestrator**: Coordinates the flow between agents.

## Prerequisites
- Python 3.8+
- An API key for GROQ or local LM Studio server
- JIRA cloud account with project and API token

## Setup
1. Clone the repo and go into the folder.
2. Create `.env` file (see example in `.env` provided).
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the program:

```bash
python main.py
```

## Notes
- The `models.py` file connects to GROQ or LM Studio.
- The `tools.py` file contains reusable tools for each agent.
- You may adjust `main.py` for more complex orchestration.

## Example Email Input
```
From: someone@example.com
Subject: Follow-up

- Finalize Q3 plan
- Submit designs
- Budget proposal
```

## Output
- JSON key points
- JIRA task(s) created automatically

## License
MIT
