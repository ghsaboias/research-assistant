import logging
import os
from config import CONFIG
from src.scraper import Scraper
from src.report_generator import ReportGenerator, AIModelInterface

logger = logging.getLogger(__name__)

class Researcher:
    def __init__(self, num_results=3):
        self.scraper = Scraper(num_results)
        self.ai_model = AIModelInterface()
        self.report_generator = ReportGenerator(self.ai_model)

    def research_followup_questions(self, questions):
        """Perform additional research based on follow-up questions."""
        logger.info("Researching follow-up questions")
        additional_data = []
        for question in questions.split('\n'):
            if question.strip():  # Ensure the question is not empty
                logger.info(f"Researching question: {question}")
                question_data = self.scraper.search_and_scrape(question)
                additional_data.append({"question": question, "data": question_data})
        return additional_data

    def general_purpose_research(self, topic):
        logger.info(f"Starting research on topic: {topic}")
        
        with open('debug/results.txt', "w") as f:
            f.write("")
        
        initial_research_data = self.scraper.search_and_scrape(topic)
        
        initial_report = self.report_generator.generate_initial_report(topic, initial_research_data)
        
        followup_questions = self.report_generator.generate_followup_questions(initial_report)
        
        additional_research_data = self.research_followup_questions(followup_questions)
        
        enhanced_report = self.report_generator.enhance_report(initial_report, followup_questions, additional_research_data)
        
        html_report = self.report_generator.generate_html_report(enhanced_report, f"{topic} Research Report")
        
        # Save to report dir, create dir if not exists
        os.makedirs(CONFIG["REPORTS_DIR"], exist_ok=True)
        report_filename = os.path.join(CONFIG["REPORTS_DIR"], f"{topic.replace(' ', '_')}_report.html")
        with open(report_filename, 'w') as f:
            f.write(html_report)
        logger.info(f"HTML report saved as {report_filename}")
        
        logger.info(f"Research on '{topic}' completed. HTML report and conversation saved.")
        return report_filename

if __name__ == "__main__":
    logging.basicConfig(level=CONFIG["LOG_LEVEL"], format=CONFIG["LOG_FORMAT"])
    researcher = Researcher()
    test_topic = "Recent advancements in quantum computing"
    report_file, conversation_file = researcher.general_purpose_research(test_topic)
    print(f"Research completed. Report saved to {report_file}")
    print(f"Conversation saved to {conversation_file}")