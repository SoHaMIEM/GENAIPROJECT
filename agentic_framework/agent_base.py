"""Base class for all agents in the system."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from langchain.schema import HumanMessage, SystemMessage
import google.generativeai as genai
import os

class AgentState(BaseModel):
    """State representation for agents."""
    context: Dict[str, Any] = {}
    messages: List[Dict[str, Any]] = []
    memory: Dict[str, Any] = {}

class Agent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, 
                 name: str, 
                 system_prompt: str,
                 model_name: str = "gemini-1.5-flash"):
        """
        Initialize the agent.
        
        Args:
            name: Name of the agent
            system_prompt: System prompt to guide the agent's behavior
            model_name: LLM model to use
        """
        self.name = name
        self.system_prompt = system_prompt
        self.model_name = model_name
        self.state = AgentState()
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the LLM model."""
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(self.model_name)
    
    def add_to_context(self, key: str, value: Any):
        """Add information to the agent's context."""
        self.state.context[key] = value
    
    def add_message(self, role: str, content: str):
        """Add a message to the agent's message history."""
        self.state.messages.append({"role": role, "content": content})
    
    def remember(self, key: str, value: Any):
        """Store information in the agent's memory."""
        self.state.memory[key] = value
    
    def recall(self, key: str) -> Optional[Any]:
        """Retrieve information from the agent's memory."""
        return self.state.memory.get(key)
    
    def generate_response(self, user_input: str) -> str:
        """Generate a response using the LLM."""
        # Construct prompt with system message and conversation history
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]
        
        # Add conversation history
        for msg in self.state.messages:
            messages.append(msg)
            
        # Add the current user input
        messages.append({"role": "user", "content": user_input})
        
        # Generate response
        response = self.model.generate_content(messages)
        response_text = response.text
        
        # Add to conversation history
        self.add_message("user", user_input)
        self.add_message("assistant", response_text)
        
        return response_text
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results. Each agent should implement this."""
        pass