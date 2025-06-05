# Multi-Agent Debate Demo

This repository contains a simple demonstration script for running a multi-agent debate using the `autogen-agentchat` library.

## Installation

Install Python dependencies (requires `openai>=1.23.0` and `autogen-agentchat>=0.4.1`):

```bash
pip install -U "openai>=1.23.0" "autogen-agentchat>=0.4.1"
```

Create a `.env` file and set your OpenAI API key:

```
OPENAI_API_KEY=sk-...
```

## Usage

Run the demo script and enter a debate topic when prompted:

```bash
python debate_demo.py
請輸入辯論題目：電動車是否優於燃油車？
```

The agents will then debate until the judge declares a winner.
