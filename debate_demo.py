# 1. 安裝套件
#pip install "pyautogen[openai]" python-dotenv
#pip install ag2[openai]
# 2. 載入套件
import os
from autogen import ConversableAgent, GroupChat, GroupChatManager
from dotenv import load_dotenv

# 3. 設定 OpenAI API 金鑰
load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

# 4. 設定 LLM 模型參數
config_list_gpt = [
    {
        "model": "gpt-4o-mini",
        "api_key": os.getenv("OPENAI_API_KEY")
    }
]
config_list_claude = [
    {
        "model": "gpt-3.5-turbo",
        "api_key": os.getenv("OPENAI_API_KEY")
    }
]

# 5. 建立三個代理人（兩方＋評審）
elon_musk_agent = ConversableAgent(
    name="elon_musk_fan",
    system_message=(
        "You are a person who admires Elon Musk and believes he is the best leader in the world. "
        "You should speak passionately about why Elon Musk is an exemplary leader and highlight his accomplishments."
    ),
    llm_config={"config_list": config_list_claude},
    human_input_mode="NEVER",
)
sam_altman_agent = ConversableAgent(
    name="sam_altman_fan",
    system_message=(
        "You are a person who admires Sam Altman and believes he is the best leader in the world. "
        "You should speak passionately about why Sam Altman is an exemplary leader and highlight his accomplishments."
    ),
    llm_config={"config_list": config_list_gpt},
    human_input_mode="NEVER",
)
judge_agent = ConversableAgent(
    name="judge_Agent",
    system_message=(
        "You are acting as the ultimate facilitator. Your job is to guide the debate between the two "
        "and declare a winner based on who makes the most convincing argument. "
        "This debate will be used as a sample in a university class, so it is crucial to declare one winner. "
        "Once a clear conclusion is reached, you must declare 'That's enough!' and announce the winner. "
        "The debate cannot end without this phrase, so make sure to include it."
    ),
    llm_config={"config_list": config_list_gpt},
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "That's enough!" in msg["content"],
)
elon_musk_agent.description = "The ultimate Elon Musk fan"
sam_altman_agent.description = "The ultimate Sam Altman fan"
judge_agent.description = "The facilitator who decides the debate winner"

# 6. 組成群組對話（GroupChat）
group_chat = GroupChat(
    agents=[elon_musk_agent, sam_altman_agent, judge_agent],
    messages=[],
    send_introductions=True,
    speaker_selection_method="auto",
    max_round=5
)

# 7. 設定群組對話管理者
group_chat_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config={"config_list": [
        {"model": "gpt-4o-mini", "api_key": os.environ["OPENAI_API_KEY"]}
    ]},
)

# 8. 啟動辯論
debate_topic = input("請輸入辯論問題：")
chat_result = judge_agent.initiate_chat(
    group_chat_manager,
    message=debate_topic,
    summary_method="reflection_with_llm",
)

# 9. 印出辯論結果（可選）
print(chat_result)
