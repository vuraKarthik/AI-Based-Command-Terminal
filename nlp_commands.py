"""
Natural Language Command Processor for Python Terminal
"""
import google.generativeai as genai
import os

class NLCommandProcessor:
    """
    Process natural language commands and convert them to terminal commands using the Gemini API.
    """

    def __init__(self, terminal):
        self.terminal = terminal
        # IMPORTANT: Set your Gemini API key here
        self.api_key = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY")
        if self.api_key == "YOUR_API_KEY":
            print("GEMINI_API_KEY environment variable not set. Please set it to your API key.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def process(self, nl_command):
        """
        Process a natural language command and execute the corresponding terminal command.
        """
        if self.api_key == "YOUR_API_KEY":
            return False, "Gemini API key not configured."

        try:
            # Create a prompt that instructs the model to convert natural language to a shell command
            available_commands = ", ".join(self.terminal.commands.keys())
            prompt = f"""
            You are an expert at converting natural language commands into shell commands.
            Convert the following natural language command into a single, executable shell command.
            The available commands are: {available_commands}.
            Natural language command: "{nl_command}"
            Shell command:
            """

            response = self.model.generate_content(prompt)
            shell_command = response.text.strip()

            # Handle markdown code blocks
            if shell_command.startswith('```') and shell_command.endswith('```'):
                shell_command = shell_command.split('\n')[1:-1][0]

            command_parts = shell_command.split()
            command_name = command_parts[0]

            if command_name in self.terminal.commands:
                method = self.terminal.commands[command_name]
                # The nl command should not be called recursively.
                if command_name == 'nl':
                    return False, "Cannot execute 'nl' command from within 'nl'."
                method(" ".join(command_parts[1:]))
                return True, f"Executed: {shell_command}"
            else:
                return False, f"Command '{command_name}' not found in terminal."

        except Exception as e:
            return False, f"Error processing command with Gemini API: {e}"