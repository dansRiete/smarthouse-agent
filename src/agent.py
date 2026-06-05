import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools.node_red import read_node_red_flows, deploy_node_red_flows
from tools.kubernetes_tool import get_pod_status, restart_deployment
from tools.github_tool import read_github_file, create_pull_request
from tools.mqtt_tool import publish_mqtt_message
from tools.postgres_tool import execute_postgres_query
from tools.bash_tool import run_bash_command

def create_agent():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    # Initialize the LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        max_retries=1,
        temperature=0.1,
        google_api_key=api_key
    )

    # Define tools available to the agent
    tools = [
        read_node_red_flows,
        deploy_node_red_flows,
        get_pod_status,
        restart_deployment,
        read_github_file,
        create_pull_request,
        publish_mqtt_message,
        execute_postgres_query,
        run_bash_command
    ]

    # Initialize memory so it remembers the conversation
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        k=10,
        return_messages=True
    )

    # Read the master agent manual to inject directly into its brain
    manual_path = os.path.join(os.path.dirname(__file__), "AGENT_MANUAL.md")
    with open(manual_path, "r") as f:
        master_manual = f.read()

    system_prompt = f"""You are the autonomous SmartHouse AI agent.
You have access to tools to read/deploy Node-RED flows, publish MQTT messages to control devices, execute PostgreSQL queries to analyze history, check Kubernetes status, and run bash scripts.

{master_manual}"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Initialize the agent using native tool calling
    agent_definition = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent_definition, tools=tools, verbose=True, memory=memory)

    return agent_executor
