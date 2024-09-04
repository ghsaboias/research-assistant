import sys
import logging
from src.researcher import general_purpose_researcher
from config import CONFIG

# Set up logging
logging.basicConfig(level=CONFIG["LOG_LEVEL"], format=CONFIG["LOG_FORMAT"])
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Please provide a research topic as a command-line argument.")
        sys.exit(1)
    
    topic = " ".join(sys.argv[1:])
    report_filename, conversation_filename = general_purpose_researcher(topic)
    
    logger.info(f"Research completed. Report saved as {report_filename}")
    logger.info(f"Conversation saved as {conversation_filename}")