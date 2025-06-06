# Multi-Agent Debate Demo

This repository provides a small demo showing how to build a debate between two LLM agents using the [autogen-agentchat](https://github.com/microsoft/autogen) library.

## Installation

Install the required packages:

```bash
pip install -r requirements.txt
```

## API Key

Create a `.env` file in the project root with your OpenAI API key. The
script reads this value at runtime, so the file must be present:

```bash
echo "OPENAI_API_KEY=sk-your-key" > .env
```

Make sure the key is valid before running the demo. If needed you can
install the dependencies manually with `pip install "pyautogen[openai]" python-dotenv -q`.
The provided `requirements.txt` uses the renamed `autogen-agentchat` package.

## Usage

Run the demo script and follow the prompt to enter a debate topic:

```bash
python multi_agent_debate.py
```

Example interaction:

```text
$ python multi_agent_debate.py
請輸入辯論題目：人工智慧應該開源嗎？
```

The program will print the conversation between Agents A and B, managed by the judge agent, followed by a summary declaring the winner.
By default the script runs a total of 17 rounds (including the judge's final statement),
but you can change this by passing the `rounds` argument to `run_debate()`.

## Web Search Preview

Agent B now attempts to use the `web_search_preview` tool to gather up-to-date information while debating. If the search API is unavailable, the script falls back to a normal debate without web results.

Example:

```text
$ python multi_agent_debate.py
請輸入辯論題目：人工智慧應該開源嗎？
(Agent B may show results from a web search.)
```

The script defaults to the `gpt-4o` and `gpt-4.1` model names. If these models
are unavailable to your account, edit `multi_agent_debate.py` and adjust the
`config_list1`–`config_list3` settings accordingly.

