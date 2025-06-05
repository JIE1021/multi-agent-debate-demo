# -*- coding: utf-8 -*-
"""
Multi-Agent Debate - 中文題目 / 中文辯論 版本（官方 SDK，B 強制搜尋）
====================================================================

⚙️ 需求摘要
-----------
* **僅** 用 `web_search_preview` 內建工具；其他工具停用。
* **Agent B** 必須在每輪回答時「一定」呼叫搜尋 → 透過
  `tool_choice` 放進 **config_list**（這是 AutoGen v0.4+ 接收的地方），
  而非 llm_config 頂層，才能通過 Pydantic 驗證。
* 需 `openai>=1.23.0`, `autogen-agentchat>=0.4.1`。
"""

# ------------------------------------------------------------
# 1. 安裝（僅首次）
# ------------------------------------------------------------
#pip install -U "openai>=1.23.0" "autogen-agentchat>=0.4.1"

# ------------------------------------------------------------
# 2. 載入套件
# ------------------------------------------------------------
import os, openai
try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    def load_dotenv(*_args, **_kwargs):
        """Fallback if python-dotenv isn't installed."""
        pass
from autogen import ConversableAgent, GroupChat, GroupChatManager

# ------------------------------------------------------------
# 3. API Key
# ------------------------------------------------------------
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
assert openai.api_key, "❌ 找不到 OPENAI_API_KEY，請在 .env 設定！"

# ------------------------------------------------------------
# 4. LLM 基本設定
# ------------------------------------------------------------
config_list1 = [{"model": "gpt-4o"}]  # A / Judge 使用
# B 使用：同時塞入 tool_choice => required
config_list2 = [{
    "model": "gpt-4o",
    "tool_choice": {"type": "required", "id": "web_search_preview"}
}]
config_list3 = [{"model": "gpt-4o"}]

# ------------------------------------------------------------
# 5. 官方 WebSearch 工具字典
# ------------------------------------------------------------
WEB_SEARCH_DICT = {
    "type": "web_search_preview",
    "user_location": {"type": "approximate", "country": "TW"},
    "search_context_size": "high"
}

# ------------------------------------------------------------
# 6. 辯論主程式
# ------------------------------------------------------------

def run_debate(topic: str, rounds: int = 10):
    if not topic.strip():
        raise ValueError("題目不能空白！")

    sys_A = f"你是 **Agent A（正方）**，支持：「{topic}」。提出論點並反駁 B。"
    sys_B = f"你是 **Agent B（反方）**，反對：「{topic}」。提出論點並反駁 A。"
    sys_J = (
        "你是裁判，主持辯論並依據論點強度決定勝負。最後必須輸出『That's enough!』再宣佈勝負。"
    )

    agent_A = ConversableAgent(
        name="A",
        system_message=sys_A,
        llm_config={"config_list": config_list1},
        human_input_mode="NEVER",
    )

    agent_B = ConversableAgent(
        name="B",
        system_message=sys_B,
        llm_config={
            "config_list": config_list2,
            "tools": [WEB_SEARCH_DICT],
        },
        human_input_mode="NEVER",
    )

    judge = ConversableAgent(
        name="Judge",
        system_message=sys_J,
        llm_config={"config_list": config_list3},
        human_input_mode="NEVER",
        is_termination_msg=lambda m: "That's enough!" in m["content"],
    )

    chat = GroupChat(
        agents=[agent_A, agent_B, judge],
        messages=[],
        send_introductions=True,
        speaker_selection_method="auto",
        max_round=rounds,
    )
    manager = GroupChatManager(groupchat=chat, llm_config={"config_list": config_list1})

    opening = (
        "這場辯論將產生一位獲勝者，直到裁判說出『That's enough!』結束。\n\n"
        f"【題目】{topic}"
    )
    return judge.initiate_chat(amanager, message=opening, summary_method="reflection_with_llm")

# ------------------------------------------------------------
# 7. CLI
# ------------------------------------------------------------
if __name__ == "__main__":
    user_topic = input("請輸入辯論題目：").strip()
    result = run_debate(user_topic, rounds=10)

    print("\n================= 辯論逐字稿 =================")
    for i, m in enumerate(result.chat_history, 1):
        print(f"\n=== #{i} {m['name']} ({m['role']}) ===\n{m['content']}\n")

    print("\n================= 裁判總結 =================\n")
    print(result.summary)
