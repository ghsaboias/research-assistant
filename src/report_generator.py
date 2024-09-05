import logging
import markdown
from datetime import datetime
import os
import re
from bs4 import BeautifulSoup
from config import CONFIG
from anthropic import Anthropic
from src.conversation_logger import ConversationLogger

logger = logging.getLogger(__name__)

class AIModelInterface:
    def __init__(self):
        self.anthropic = Anthropic(api_key=CONFIG["ANTHROPIC_API_KEY"])
        self.model = "claude-3-haiku-20240307"
        self.conversation_logger = ConversationLogger("debug/conversation_log.json")

    def generate_response(self, prompt, max_tokens=2000):
        try:
            self.conversation_logger.log_interaction("user", prompt)
            
            response = self.anthropic.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            ai_response = response.content[0].text
            self.conversation_logger.log_interaction("assistant", ai_response)
            
            return ai_response
        except Exception as e:
            error_message = f"Error generating response: {str(e)}"
            logger.error(error_message)
            self.conversation_logger.log_interaction("system", error_message)
            return error_message

class ReportGenerator:
    def __init__(self, ai_model):
        self.ai_model = ai_model

    def generate_initial_report(self, topic, research_data):
        logger.info(f"Generating initial report for topic: {topic}")
        
        research_summary = self._prepare_research_summary(topic, research_data)
        initial_report_prompt = self._create_initial_report_prompt(topic, research_summary)
        
        initial_content = self.ai_model.generate_response(initial_report_prompt, max_tokens=2000)
        logger.info("Initial report generation completed successfully")
        return initial_content

    def _analyze_information_gaps(self, initial_report):
        logger.info("Analyzing information gaps using LLM")
        
        analysis_prompt = f"""
        Analyze the following report for information gaps, missing details, or areas that need more specific examples or evidence:

        {initial_report}

        Please identify at least 3 and up to 5 specific areas where the report could be improved. For each area, provide:
        1. The section or topic that needs improvement
        2. What kind of information is missing (e.g., specific examples, dates, data, expert opinions, comparisons)
        3. Why this information would be valuable to include

        Format your response as a list, with each item clearly stating the section and the type of information needed.
        """

        analysis_response = self.ai_model.generate_response(analysis_prompt, max_tokens=1000)
        
        # Parse the response into a list of gaps
        gaps = [line.strip() for line in analysis_response.split('\n') if line.strip()]
        
        logger.info(f"Identified {len(gaps)} information gaps")
        return gaps

    def generate_followup_questions(self, initial_report):
        logger.info("Generating follow-up questions")
        
        gaps = self._analyze_information_gaps(initial_report)
        
        questions_prompt = f"""
        Based on the following analysis of information gaps in a report, generate 3 specific follow-up questions:

        Information gaps:
        {gaps}

        Generate questions that will help fill these gaps with more specific information, examples, or details. Each question should be clear, focused, and designed to elicit detailed responses.

        Return only the questions, one per line, numbered 1-3.
        """

        questions = self.ai_model.generate_response(questions_prompt, max_tokens=1000)
        
        os.makedirs("debug", exist_ok=True)
        with open('debug/questions.txt', 'w') as f:
            f.write(questions)
        logger.info("Follow-up questions generated successfully")
        return questions

    def enhance_report(self, initial_report, followup_questions, additional_research_data=None):
        logger.info("Enhancing report with follow-up questions and additional research")
        
        enhancement_prompt = self._create_enhancement_prompt(initial_report, followup_questions, additional_research_data)
        enhanced_content = self.ai_model.generate_response(enhancement_prompt, max_tokens=3000)
        logger.info("Report enhancement completed successfully")
        return enhanced_content

    def generate_html_report(self, markdown_content, title):
        logger.info(f"Generating HTML report: {title}")
        
        try:
            html_content = markdown.markdown(markdown_content, extensions=['extra'])
            improved_html = self._improve_html_structure(html_content)
            html_template = self._create_html_template(title, improved_html)
            
            logger.info("HTML report generated successfully")
            return html_template
        except Exception as e:
            logger.error(f"Error generating HTML report: {str(e)}")
            return f"<html><body><h1>Error</h1><p>Error generating HTML report: {str(e)}</p></body></html>"

    def _prepare_research_summary(self, topic, research_data):
        research_summary = f"# Research Summary for: {topic}\n\n"
        for result in research_data:
            research_summary += f"## Source: {result['url']}\n\n"
            if result['error']:
                research_summary += f"Error: {result['error']}\n\n"
            else:
                research_summary += f"### Title: {result['title']}\n\n"
                research_summary += "### Content Excerpt:\n"
                research_summary += f"{result['content']}...\n\n" 
            research_summary += "---\n\n"
        return research_summary

    def _create_initial_report_prompt(self, topic, research_summary):
        return f"""
        Using the following research summary, generate a comprehensive report on "{topic}":

        {research_summary}

        Please structure the report in a way that best suits the topic and available information. The report should:

        1. Begin with an introduction to the topic.
        2. Include all relevant key findings and main points discovered in the research.
        3. Provide analysis and, where applicable, compare information from different sources.
        4. Discuss potential implications or applications of the findings.
        5. End with a conclusion and suggest areas for further research.

        Determine appropriate section titles and organization based on the content and nature of the topic. 
        You are not limited to a fixed structure - create sections and subsections as needed to best present the information.

        Format the report using Markdown syntax. Use appropriate headers, lists, and emphasis.
        Include a table of contents at the beginning that reflects your chosen structure.
        Ensure to include specific examples, names, dates, and places where relevant.

        Be creative and analytical in your approach, focusing on producing a well-organized, 
        informative, and engaging report that best represents the research findings on {topic}.
        """

    def _create_followup_prompt(self, initial_report):
        return f"""
        Based on the following initial report, generate 3 follow-up questions that would elicit more specific information, examples, or details:

        {initial_report}

        Focus on areas where more concrete examples, dates, places, people, information, or explanations would enhance the report's depth and specificity.
        
        Return only the follow-up questions, without any additional comments or meta-information.
        Return as a list of questions, each on a new line, preceded by a number.
        Don't add any extra information, just the questions.
        """

    def _create_enhancement_prompt(self, initial_report, followup_questions, additional_research_data):
        return f"""
        Enhance the following initial report by addressing these follow-up questions and incorporating the additional research data:

        Initial Report:
        {initial_report}

        Follow-up Questions:
        {followup_questions}

        Additional Research Data:
        {self._format_additional_research(additional_research_data) if additional_research_data else "No additional research data available."}

        Please incorporate answers to these questions into the relevant sections of the report, adding specific examples, data, and detailed explanations where possible. Use the additional research data to provide more in-depth answers and insights. Maintain the overall structure and formatting of the initial report, but feel free to expand sections or add new subsections as needed to accommodate the additional information. Return just the enhanced report, with no meta-comments.
        """

    def _format_additional_research(self, additional_research_data):
        formatted_data = ""
        for item in additional_research_data:
            formatted_data += f"Question: {item['question']}\n"
            for result in item['data']:
                formatted_data += f"Source: {result['url']}\n"
                formatted_data += "Content Excerpts:\n"
                formatted_data += f"- {result['content']}\n"
                formatted_data += f"Error: {result['error']}\n" if result['error'] else ""
            formatted_data += "\n"
        return formatted_data

    def _improve_html_structure(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        self._convert_to_list(soup)
        self._wrap_sections(soup)
        return str(soup)

    def _convert_to_list(self, soup):
        bullet_point_patterns = [
            r'^\s*[-•]\s',  # Matches lines starting with - or •
            r'^\s*\d+\.\s',  # Matches lines starting with numbers followed by a period
        ]
        
        for p in soup.find_all('p'):
            text = p.text.strip()
            lines = text.split('\n')
            
            if any(re.match(pattern, line) for pattern in bullet_point_patterns for line in lines):
                new_list = soup.new_tag('ul' if re.match(bullet_point_patterns[0], lines[0]) else 'ol')
                
                for line in lines:
                    if any(re.match(pattern, line) for pattern in bullet_point_patterns):
                        li = soup.new_tag('li')
                        li.string = re.sub(r'^\s*[-•\d.]\s', '', line).strip()
                        new_list.append(li)
                
                p.replace_with(new_list)

    def _wrap_sections(self, soup):
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        for i in range(len(headers)):
            section = soup.new_tag('section')
            headers[i].wrap(section)
            
            next_sibling = headers[i].next_sibling
            while next_sibling and (next_sibling.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] or 
                                    (next_sibling.name == headers[i].name and i < len(headers) - 1)):
                next_element = next_sibling.next_sibling
                section.append(next_sibling)
                next_sibling = next_element

    def _create_html_template(self, title, content):
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                header {{
                    background-color: #f4f4f4;
                    padding: 20px;
                    margin-bottom: 20px;
                }}
                h1, h2, h3, h4 {{
                    color: #2c3e50;
                }}
                a {{
                    color: #3498db;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                .timestamp {{
                    font-style: italic;
                    color: #7f8c8d;
                }}
                nav {{
                    background-color: #ecf0f1;
                    padding: 10px;
                    margin-bottom: 20px;
                }}
                nav ul {{
                    list-style-type: none;
                    padding: 0;
                }}
                nav ul li {{
                    display: inline;
                    margin-right: 10px;
                }}
                ul {{
                    padding-left: 20px;
                }}
                @media (max-width: 600px) {{
                    body {{
                        padding: 10px;
                    }}
                }}
            </style>
        </head>
        <body>
            <header>
                <h1>{title}</h1>
                <p class="timestamp">Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </header>
            <main>
                {content}
            </main>
            <footer>
                <p>&copy; {datetime.now().year} Research Report</p>
            </footer>
        </body>
        </html>
        """

if __name__ == "__main__":
    # For testing purposes
    logging.basicConfig(level=CONFIG["LOG_LEVEL"], format=CONFIG["LOG_FORMAT"])
    ai_model = AIModelInterface()
    report_generator = ReportGenerator(ai_model)
    
    test_topic = "Artificial Intelligence in Healthcare"
    test_research_data = [
        {
            "url": "https://example.com/ai-healthcare",
            "title": "AI in Healthcare: Revolutionizing Patient Care",
            "content": "AI is transforming healthcare in numerous ways, from improving diagnosis accuracy to personalizing treatment plans...",
            "error": None
        }
    ]
    
    initial_report = report_generator.generate_initial_report(test_topic, test_research_data)
    print("Initial Report:")
    print(initial_report)
    print("\n---\n")
    
    followup_questions = report_generator.generate_followup_questions(initial_report)
    print("Follow-up Questions:")
    print(followup_questions)
    print("\n---\n")
    
    enhanced_report = report_generator.enhance_report(initial_report, followup_questions)
    print("Enhanced Report:")
    print(enhanced_report)
    print("\n---\n")
    
    html_report = report_generator.generate_html_report(enhanced_report, f"{test_topic} Research Report")
    print("HTML Report (excerpt):")
    print(html_report[:500] + "...")  # Print first 500 characters of HTML report