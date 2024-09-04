import json
import logging
from datetime import datetime
import os
import re
from config import CONFIG

logger = logging.getLogger(__name__)

def generate_filename(topic):
    """Generate a filename based on timestamp and the first few words of the topic."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Clean and truncate the topic to use in the filename
    clean_topic = re.sub(r'[^\w\s-]', '', topic.lower())
    words = clean_topic.split()[:4]  # Take up to 4 words
    topic_part = '_'.join(words)
    
    return f"{timestamp}_{topic_part}.json"

def save_conversation(topic, conversation):
    """Save the conversation history to a JSON file."""
    logger.info(f"Saving conversation for topic: {topic}")
    
    try:
        filename = generate_filename(topic)
        
        # Ensure the filename is unique
        counter = 1
        while os.path.exists(os.path.join(CONFIG["DEBUG_DIR"], filename)):
            name_parts = filename.rsplit('.', 1)
            filename = f"{name_parts[0]}_{counter}.{name_parts[1]}"
            counter += 1
        
        # Save the conversation
        os.makedirs(CONFIG["DEBUG_DIR"], exist_ok=True)
        full_path = os.path.join(CONFIG["DEBUG_DIR"], filename)
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(conversation, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Conversation saved to {full_path}")
        return full_path
    except Exception as e:
        logger.error(f"Error saving conversation: {str(e)}")
        return None

def load_conversation(filename):
    """Load a conversation history from a JSON file."""
    logger.info(f"Loading conversation from file: {filename}")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            conversation = json.load(f)
        logger.info(f"Conversation loaded successfully from {filename}")
        return conversation
    except Exception as e:
        logger.error(f"Error loading conversation: {str(e)}")
        return None

if __name__ == "__main__":
    # For testing purposes
    logging.basicConfig(level=CONFIG["LOG_LEVEL"], format=CONFIG["LOG_FORMAT"])
    
    test_topic = "Artificial Intelligence in Healthcare"
    test_conversation = [
        {"role": "user", "content": "Research topic: Artificial Intelligence in Healthcare"},
        {"role": "assistant", "content": "Certainly! I'll research the topic of Artificial Intelligence in Healthcare for you."},
        {"role": "user", "content": "What are the main applications of AI in healthcare?"},
        {"role": "assistant", "content": "There are several main applications of AI in healthcare:\n1. Diagnosis and disease detection\n2. Drug discovery and development\n3. Personalized treatment plans\n4. Medical imaging analysis\n5. Predictive analytics for patient outcomes"},
    ]
    
    # Test saving conversation
    saved_filename = save_conversation(test_topic, test_conversation)
    if saved_filename:
        print(f"Conversation saved to: {saved_filename}")
        
        # Test loading conversation
        loaded_conversation = load_conversation(saved_filename)
        if loaded_conversation:
            print("Loaded conversation:")
            for message in loaded_conversation:
                print(f"{message['role']}: {message['content'][:50]}...")  # Print first 50 characters of each message