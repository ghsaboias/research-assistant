import logging

from src.scraper import search_and_scrape
from src.report_generator import generate_initial_report, generate_followup_questions, enhance_report, generate_html_report
from src.conversation_saver import save_conversation
import os
from config import CONFIG

logger = logging.getLogger(__name__)

def research_followup_questions(questions):
    """Perform additional research based on follow-up questions."""
    logger.info("Researching follow-up questions")
    additional_data = []
    for question in questions.split('\n'):
        if question.strip():  # Ensure the question is not empty
            logger.info(f"Researching question: {question}")
            question_data = search_and_scrape(question, False)
            additional_data.append({"question": question, "data": question_data})
    return additional_data

def general_purpose_researcher(topic):
    logger.info(f"Starting research on topic: {topic}")
    
    initial_research_data = search_and_scrape(topic, CONFIG["NUM_SEARCH_RESULTS"])
    
    initial_report = generate_initial_report(topic, initial_research_data)
    
    followup_questions = generate_followup_questions(initial_report)
    
    additional_research_data = research_followup_questions(followup_questions)
    
    enhanced_report = enhance_report(initial_report, followup_questions, additional_research_data)
    
    html_report = generate_html_report(enhanced_report, f"{topic} Research Report")
    
    # Save to report dir, create dir if not exists
    os.makedirs(CONFIG["REPORTS_DIR"], exist_ok=True)
    report_filename = os.path.join(CONFIG["REPORTS_DIR"], f"{topic.replace(' ', '_')}_report.html")
    with open(report_filename, 'w') as f:
        f.write(html_report)
    logger.info(f"HTML report saved as {report_filename}")

    # Save the conversation
    conversation = [
        {"role": "user", "content": f"Research topic: {topic}"},
        {"role": "assistant", "content": initial_report},
        {"role": "user", "content": "Generate follow-up questions"},
        {"role": "assistant", "content": followup_questions},
        {"role": "user", "content": "Perform additional research on follow-up questions"},
        {"role": "assistant", "content": "Additional research completed. Enhancing the report."},
        {"role": "user", "content": "Enhance the report"},
        {"role": "assistant", "content": enhanced_report}
    ]
    conversation_filename = save_conversation(topic, conversation)
    
    logger.info(f"Research on '{topic}' completed. HTML report and conversation saved.")
    return report_filename, conversation_filename