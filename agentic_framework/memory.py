"""Memory management utilities for agents."""
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime

class AgentMemory:
    """Class to handle persistent memory for agents."""
    
    def __init__(self, agent_name: str, memory_dir: str = "./memory"):
        """
        Initialize the agent memory.
        
        Args:
            agent_name: Name of the agent
            memory_dir: Directory to store memory files
        """
        self.agent_name = agent_name
        self.memory_dir = memory_dir
        self.memory_file = os.path.join(memory_dir, f"{agent_name.lower().replace(' ', '_')}_memory.json")
        self.memory = {}
        
        # Create memory directory if it doesn't exist
        os.makedirs(memory_dir, exist_ok=True)
        
        # Load existing memory if available
        self._load_memory()
    
    def _load_memory(self):
        """Load memory from file."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    self.memory = json.load(f)
            except Exception as e:
                print(f"Error loading memory for {self.agent_name}: {e}")
                self.memory = {}
    
    def _save_memory(self):
        """Save memory to file."""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f)
        except Exception as e:
            print(f"Error saving memory for {self.agent_name}: {e}")
    
    def remember(self, key: str, value: Any):
        """
        Store information in memory.
        
        Args:
            key: Memory key
            value: Value to store
        """
        self.memory[key] = value
        self._save_memory()
    
    def recall(self, key: str) -> Optional[Any]:
        """
        Retrieve information from memory.
        
        Args:
            key: Memory key
        
        Returns:
            Stored value or None if not found
        """
        return self.memory.get(key)
    
    def forget(self, key: str):
        """
        Remove information from memory.
        
        Args:
            key: Memory key to remove
        """
        if key in self.memory:
            del self.memory[key]
            self._save_memory()
    
    def clear(self):
        """Clear all memory."""
        self.memory = {}
        self._save_memory()
    
    def list_keys(self) -> List[str]:
        """
        List all memory keys.
        
        Returns:
            List of memory keys
        """
        return list(self.memory.keys())


class ConversationMemory:
    """Class to handle conversation history."""
    
    def __init__(self, conversation_id: str, memory_dir: str = "./conversations"):
        """
        Initialize the conversation memory.
        
        Args:
            conversation_id: Unique ID for the conversation
            memory_dir: Directory to store conversation files
        """
        self.conversation_id = conversation_id
        self.memory_dir = memory_dir
        self.conversation_file = os.path.join(memory_dir, f"{conversation_id}.json")
        self.messages = []
        
        # Create memory directory if it doesn't exist
        os.makedirs(memory_dir, exist_ok=True)
        
        # Load existing conversation if available
        self._load_conversation()
    
    def _load_conversation(self):
        """Load conversation from file."""
        if os.path.exists(self.conversation_file):
            try:
                with open(self.conversation_file, 'r') as f:
                    self.messages = json.load(f)
            except Exception as e:
                print(f"Error loading conversation {self.conversation_id}: {e}")
                self.messages = []
    
    def _save_conversation(self):
        """Save conversation to file."""
        try:
            with open(self.conversation_file, 'w') as f:
                json.dump(self.messages, f)
        except Exception as e:
            print(f"Error saving conversation {self.conversation_id}: {e}")
    
    def add_message(self, role: str, content: str):
        """
        Add a message to the conversation.
        
        Args:
            role: Message role (user, assistant, system)
            content: Message content
        """
        timestamp = datetime.now().isoformat()
        
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": timestamp
        })
        
        self._save_conversation()
    
    def get_messages(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get conversation messages.
        
        Args:
            limit: Maximum number of most recent messages to return
        
        Returns:
            List of messages
        """
        if limit:
            return self.messages[-limit:]
        return self.messages
    
    def clear(self):
        """Clear the conversation history."""
        self.messages = []
        self._save_conversation()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the conversation.
        
        Returns:
            Summary information
        """
        return {
            "conversation_id": self.conversation_id,
            "message_count": len(self.messages),
            "start_time": self.messages[0]["timestamp"] if self.messages else None,
            "latest_time": self.messages[-1]["timestamp"] if self.messages else None,
            "participants": list(set([msg["role"] for msg in self.messages]))
        }