import logging
from scraper import search_and_scrape
from report_generator import generate_initial_report, generate_followup_questions, enhance_report, generate_html_report
from conversation_saver import save_conversation
import os

logger = logging.getLogger(__name__)

def general_purpose_researcher(topic):
    logger.info(f"Starting research on topic: {topic}")
    
    research_data = search_and_scrape(topic)
    
    initial_report = generate_initial_report(topic, research_data)
    
    followup_questions = generate_followup_questions(initial_report)
    
    enhanced_report = enhance_report(initial_report, followup_questions)
    
    html_report = generate_html_report(enhanced_report, f"{topic} Research Report")
    
    # save to report dir, create dir if not exists
    os.makedirs("reports", exist_ok=True)
    report_filename = f"reports/{topic.replace(' ', '_')}_report.html"
    with open(report_filename, 'w') as f:
        f.write(html_report)
    logger.info(f"HTML report saved as {report_filename}")

    # Save the conversation
    conversation = [
        {"role": "user", "content": f"Research topic: {topic}"},
        {"role": "assistant", "content": initial_report},
        {"role": "user", "content": "Generate follow-up questions"},
        {"role": "assistant", "content": followup_questions},
        {"role": "user", "content": "Enhance the report"},
        {"role": "assistant", "content": enhanced_report}
    ]
    conversation_filename = save_conversation(topic, conversation)
    
    logger.info(f"Research on '{topic}' completed. HTML report and conversation saved.")
    return report_filename, conversation_filename