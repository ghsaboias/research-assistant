import sys
import logging
from src.researcher import Researcher
from config import CONFIG

# Set up logging
logging.basicConfig(level=CONFIG["LOG_LEVEL"], format=CONFIG["LOG_FORMAT"])
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Please provide a research topic as a command-line argument.")
        sys.exit(1)
    
    topic = " ".join(sys.argv[1:])
    
    researcher = Researcher(num_results=CONFIG["NUM_SEARCH_RESULTS"])
    
    report_filename, conversation_filename = researcher.general_purpose_research(topic)
    
    logger.info(f"Research completed. Report saved as {report_filename}")
    logger.info(f"Conversation saved as {conversation_filename}")