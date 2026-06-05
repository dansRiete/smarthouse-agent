import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools.node_red import read_node_red_flows, deploy_node_red_flows
from tools.kubernetes_tool import get_pod_status, restart_deployment
from tools.github_tool import read_github_file, create_pull_request

def create_agent():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    # Initialize the LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=0,
        google_api_key=api_key
    )

    # Define tools available to the agent
    tools = [
        read_node_red_flows,
        deploy_node_red_flows,
        get_pod_status,
        restart_deployment,
        read_github_file,
        create_pull_request
    ]

    # Initialize memory so it remembers the conversation
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        k=10,
        return_messages=True
    )

    system_message = """You are the autonomous SRE and Smart Home Agent for Alex's SmartHouse.
Your goal is to help maintain, debug, and monitor the home automation infrastructure.
You have access to tools that allow you to read Node-RED flows, check Kubernetes status, and read/write the codebase.
Always be concise, careful, and think step-by-step before deploying changes."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Initialize the agent using native tool calling
    agent_definition = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent_definition, tools=tools, verbose=True, memory=memory)

    return agent_executor
