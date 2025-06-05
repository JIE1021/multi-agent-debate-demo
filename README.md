# Multi-Agent Debate Demo

This repository provides a small demo showing how to build a debate between two LLM agents using the [autogen-agentchat](https://github.com/microsoft/autogen) library.

## Installation

Install the required packages:

```bash
pip install openai autogen-agentchat python-dotenv
```

## API Key

Create a `.env` file in the project root with your OpenAI API key:

```bash
echo "OPENAI_API_KEY=sk-your-key" > .env
```

Make sure the key is valid before running the demo.

## Usage

Run the demo script and follow the prompt to enter a debate topic:

```bash
python debate_demo.py
```

Example interaction:

```text
$ python debate_demo.py
請輸入辯論題目：人工智慧應該開源嗎？
```

The program will print the conversation between Agents A and B, managed by the judge agent, followed by a summary declaring the winner.

