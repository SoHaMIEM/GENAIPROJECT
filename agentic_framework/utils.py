"""Utility functions for the agentic framework."""
import os
import json
import re
import hashlib
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def generate_uuid() -> str:
    """Generate a unique identifier."""
    return str(uuid.uuid4())

def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
    
    Returns:
        Dictionary containing the data
    """
    try:
        if not os.path.exists(file_path):
            return {}
        
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {e}")
        return {}

def save_json_file(data: Dict[str, Any], file_path: str) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        file_path: Path to the JSON file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {e}")
        return False

def validate_email(email: str) -> bool:
    """
    Validate an email address.
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """
    Validate a phone number.
    
    Args:
        phone: Phone number to validate
    
    Returns:
        True if valid, False otherwise
    """
    # Remove any non-digit characters
    phone = re.sub(r'\D', '', phone)
    # Check if the phone number has a valid length
    return 10 <= len(phone) <= 15

def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256.
    
    Args:
        password: Password to hash
    
    Returns:
        Hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_timestamp() -> str:
    """
    Get the current timestamp in ISO format.
    
    Returns:
        Current timestamp
    """
    return datetime.now().isoformat()

def format_currency(amount: float) -> str:
    """
    Format a number as currency.
    
    Args:
        amount: Amount to format
    
    Returns:
        Formatted currency string
    """
    return f"${amount:,.2f}"

def extract_entities(text: str, entity_types: List[str]) -> Dict[str, List[str]]:
    """
    Extract entities from text using simple pattern matching.
    
    Args:
        text: Text to extract entities from
        entity_types: Types of entities to extract (email, phone, date, etc.)
    
    Returns:
        Dictionary with entity types as keys and lists of extracted entities as values
    """
    entities = {}
    
    if "email" in entity_types:
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if emails:
            entities["email"] = emails
    
    if "phone" in entity_types:
        phones = re.findall(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', text)
        if phones:
            entities["phone"] = phones
    
    if "date" in entity_types:
        dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text)
        if dates:
            entities["date"] = dates
    
    if "url" in entity_types:
        urls = re.findall(r'https?://\S+|www\.\S+', text)
        if urls:
            entities["url"] = urls
    
    return entities

def chunked_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.
    
    Args:
        lst: List to split
        chunk_size: Size of each chunk
    
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def set_env_variable(key: str, value: str):
    """
    Set an environment variable.
    
    Args:
        key: Environment variable key
        value: Environment variable value
    """
    os.environ[key] = value

def get_env_variable(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get an environment variable.
    
    Args:
        key: Environment variable key
        default: Default value if not found
    
    Returns:
        Environment variable value or default
    """
    return os.environ.get(key, default)

def ensure_directory_exists(directory_path: str):
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)