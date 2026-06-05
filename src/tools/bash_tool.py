import subprocess
from langchain.tools import tool

@tool
def run_bash_command(command: str) -> str:
    """Useful to run arbitrary bash commands inside the agent's secure Linux container sandbox. 
    You can use this to clone git repositories (e.g., 'git clone https://github.com/dansRiete/smarthouse-controller.git /tmp/controller'), 
    grep through files, run python scripts, or curl APIs. 
    The command runs as a restricted non-root user. The current directory is /app. 
    Use this when you need to explore the codebase or write/execute custom data analysis scripts."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        if not output.strip():
            return "Command executed successfully with no output."
        # Limit output length to prevent breaking context window
        if len(output) > 4000:
            return output[:4000] + "\n...[OUTPUT TRUNCATED]..."
        return output
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds."
    except Exception as e:
        return f"Error executing bash command: {str(e)}"
