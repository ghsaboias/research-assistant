import sys
import logging
from researcher import general_purpose_researcher

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Please provide a research topic as a command-line argument.")
        sys.exit(1)
    
    topic = " ".join(sys.argv[1:])
    report_filename, conversation_filename = general_purpose_researcher(topic)
    
    logger.info(f"Research completed. Report saved as {report_filename}")
    logger.info(f"Conversation saved as {conversation_filename}")