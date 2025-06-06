# -*- coding: utf-8 -*-
"""
Multi‑Agent Debate ‑ 中文題目 / 中文辯論 版本
------------------------------------------------
使用說明
========
1. 在專案根目錄建立 `.env` 檔，內容：
   ```
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
   ```
2. 於命令列或 Jupyter Notebook 執行：
   ```bash
   python multi_agent_debate.py
   ```
   依提示輸入「中文」辯論題目，例如：
   > 紅蘋果和青蘋果哪種更營養？

程式流程
========
* 動態建立三個 Agent：
  - **Agent A**：正方（支持命題）
  - **Agent B**：反方（反對命題）
  - **Judge** ：裁判（最後必須說 **「That's enough!」** 並宣佈勝負）
* 預設 X 回合（A→B→A→B→Judge）。可透過 `rounds` 參數調整。
* 支援 `run_debate(topic, rounds=X)` 反覆或批次呼叫。
"""

# ------------------------------------------------------------
# 1. 安裝套件（第一次執行才需要）
# ------------------------------------------------------------
# 在 Jupyter Notebook 可直接執行，也可於終端機手動安裝
#pip install "pyautogen[openai]" python-dotenv -q

# ------------------------------------------------------------
# 2. 載入套件
# ------------------------------------------------------------
import os
from dotenv import load_dotenv
from autogen import ConversableAgent, GroupChat, GroupChatManager

# web_search_preview tool specification required by the OpenAI API
web_search_preview = {
    "name": "web_search_preview",
    "description": "Search the web and return relevant results.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query string",
            },
            "user_location": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["approximate"]},
                    "country": {"type": "string"},
                },
            },
            "search_context_size": {
                "type": "string",
                "enum": ["low", "medium", "high"],
            },
        },
        "required": ["query"],
    },
}

def _web_search_preview(query: str, user_location: dict | None = None, search_context_size: str = "low") -> str:
    """Return a placeholder string for the given search query.

    This demo does not have network access. The function simply echoes the query
    back to the caller so the debate can proceed without errors.
    """
    return f"[網路搜尋結果：{query}]"

# ------------------------------------------------------------
# 3. 讀取 OpenAI API Key
# ------------------------------------------------------------
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
assert API_KEY, "❌ 找不到 OPENAI_API_KEY，請在 .env 設定！"

# ------------------------------------------------------------
# 4. 共用 LLM 設定（可改 gpt‑3.5‑turbo 節省成本）
# ------------------------------------------------------------
config_list1 = [{"model": "gpt-4o", "api_key": API_KEY}]
config_list2 = [{"model": "gpt-4.1", "api_key": API_KEY}]
config_list3 = [{"model": "gpt-4.1", "api_key": API_KEY}]
# ------------------------------------------------------------
# 5. 動態建立並執行辯論
# ------------------------------------------------------------
#回合數要留下1回合提供給裁判解說，這邊X 最末端就要是X-1回合
def run_debate(topic: str, rounds: int = 17, model_cfg=None):
    """根據題目建立三個中文 Agent 並執行辯論，回傳 ChatResult"""
    if not topic.strip():
        raise ValueError("題目不能空白！")

    model_cfg = model_cfg or config_list1

    # 5‑1. 生成中文 system message
    sys_A = (
        "你是 **Agent A（正方）**。你的任務是支持以下命題，提出有力論點並反駁 Agent B：\n\n"
        f"「{topic}」"
    )
    sys_B = (
        "你是 **Agent B（反方）**。你的任務是確定A的觀點是否正確，否則要根據網路的資料，提出有數據的論點並反駁 Agent A：\n\n"
        f"「{topic}」"
    )
    sys_J = (
        "你是裁判。雙方達成共識後，請主持辯論、必要時要求澄清，最後根據論點強度宣佈勝負。"
        "結尾務必輸出 **完全一致** 的句子：『That's enough!』，接著說明誰獲勝。"
    )

    # 5‑2. 建立三個代理人
    agent_A = ConversableAgent("A", sys_A, llm_config={"config_list": config_list1}, human_input_mode="NEVER")
    # Agent B tries to use web_search_preview for up-to-date information.
    # If the tool fails to initialize, fall back to basic configuration.
    try:
        agent_B = ConversableAgent(
            "B",
            sys_B,
            llm_config={
                "config_list": config_list2,
                "tools": [{"type": "function", "function": web_search_preview}],
            },
            function_map={"web_search_preview": _web_search_preview},
            human_input_mode="NEVER",
        )
    except Exception as e:  # pragma: no cover - tool may not be available
        print(f"[警告] 無法啟用網路搜尋工具：{e}")
        agent_B = ConversableAgent(
            "B", sys_B, llm_config={"config_list": config_list2}, human_input_mode="NEVER"
        )
    judge   = ConversableAgent(
        "Judge", sys_J,
        llm_config={"config_list": config_list3}, human_input_mode="NEVER",
        is_termination_msg=lambda m: "That's enough!" in m["content"],
    )

    # 5‑3. 組群聊
    chat = GroupChat(
        agents=[agent_A, agent_B, judge],
        messages=[],
        send_introductions=True,
        speaker_selection_method="auto",
        max_round=rounds,
    )
    manager = GroupChatManager(groupchat=chat, llm_config={"config_list": model_cfg})

    # 5‑4. 中文開場白 (含規則)
    opening = (
        "這場辯論將作為課堂範例，必須產生一位獲勝者。\n"
        "辯論持續進行，直到裁判下結論並說出『That's enough!』。\n\n"
        f"【辯論題目】{topic}"
    )

    # 5‑5. 啟動辯論
    return judge.initiate_chat(
        manager, message=opening, summary_method="reflection_with_llm"
    )

# ------------------------------------------------------------
# 6. CLI / Notebook 入口點
# ------------------------------------------------------------
if __name__ == "__main__":
    user_topic = input("請輸入辯論題目：").strip()
    # ↓ 這行呼叫 run_debate，rounds=X 表示辯論來回 X 回合
    result = run_debate(user_topic, rounds=16)

    # 7. 列印逐字稿
    print("\n================= 辯論逐字稿 =================")
    for i, m in enumerate(result.chat_history, 1):
        print(f"\n=== #{i} {m['name']} ({m['role']}) ===\n{m['content']}\n")

    # 8. 列印裁判總結
    print("\n================= 裁判總結 =================\n")
    print(result.summary)
