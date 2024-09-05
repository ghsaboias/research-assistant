import json
from datetime import datetime

class ConversationLogger:
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        self.conversation = []

    def log_interaction(self, role, content):
        timestamp = datetime.now().isoformat()
        interaction = {
            "timestamp": timestamp,
            "role": role,
            "content": content
        }
        self.conversation.append(interaction)
        self._save_to_file()

    def _save_to_file(self):
        with open(self.log_file_path, 'w') as f:
            json.dump(self.conversation, f, indent=2)

    def get_full_conversation(self):
        return self.conversation