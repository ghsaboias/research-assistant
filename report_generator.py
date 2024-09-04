import logging
from interpreter import interpreter
import markdown
from datetime import datetime
import os
import re
from bs4 import BeautifulSoup
from config import CONFIG

logger = logging.getLogger(__name__)

interpreter.llm.model = CONFIG["AI_MODEL"]

def generate_initial_report(topic, research_data):
    logger.info(f"Generating initial report for topic: {topic}")
    
    # Prepare research summary
    research_summary = f"# Research Summary for: {topic}\n\n"
    for result in research_data:
        research_summary += f"## Source: {result['url']}\n\n"
        if result['data']['error']:
            research_summary += f"Error: {result['data']['error']}\n\n"
        else:
            research_summary += "### Headlines:\n"
            for headline in result['data']['headlines']:
                research_summary += f"- {headline}\n"
            research_summary += "\n### Content Excerpts:\n"
            for content in result['data']['content']:
                research_summary += f"{content}\n\n"
        research_summary += "---\n\n"

    # Generate initial report
    initial_report_prompt = f"""
    Using the following research summary, generate a comprehensive report on "{topic}":

    {research_summary}

    The report should include:
    1. An introduction to the topic
    2. Key findings from the research
    3. Analysis of the main points discovered
    4. Comparison of information from different sources (if applicable)
    5. Potential implications or applications of the findings
    6. Conclusion
    7. Areas for further research
    
    Format the report using Markdown syntax. Use appropriate headers, lists, and emphasis.
    Include a table of contents at the beginning.
    Ensure to include specific examples, names, dates, and places where relevant.
    """
    
    try:
        initial_response = interpreter.chat(initial_report_prompt)
        
        # Extract content from the initial response
        if isinstance(initial_response, list):
            initial_content = "\n".join([item.get('content', '') for item in initial_response if isinstance(item, dict)])
        elif isinstance(initial_response, dict):
            initial_content = initial_response.get('content', '')
        else:
            initial_content = str(initial_response)
        
        logger.info("Initial report generation completed successfully")
        return initial_content
    except Exception as e:
        logger.error(f"Error generating initial report: {str(e)}")
        return f"Error generating initial report: {str(e)}"

def generate_followup_questions(initial_report):
    logger.info("Generating follow-up questions")
    
    followup_prompt = f"""
    Based on the following initial report, generate 3 follow-up questions that would elicit more specific information, examples, or details:

    {initial_report}

    Focus on areas where more concrete examples, dates, places, people, information, or explanations would enhance the report's depth and specificity.
    
    Return only the follow-up questions, without any additional comments or meta-information.
    """
    
    try:
        followup_questions = interpreter.chat(followup_prompt)
        
        # Extract follow-up questions
        if isinstance(followup_questions, list):
            questions = "\n".join([item.get('content', '') for item in followup_questions if isinstance(item, dict)])
        elif isinstance(followup_questions, dict):
            questions = followup_questions.get('content', '')
        else:
            questions = str(followup_questions)
        
        os.makedirs("debug", exist_ok=True)
        with open('debug/questions.txt', 'w') as f:
            f.write(questions)
        logger.info("Follow-up questions generated successfully")
        return questions
    except Exception as e:
        logger.error(f"Error generating follow-up questions: {str(e)}")
        return f"Error generating follow-up questions: {str(e)}"

def enhance_report(initial_report, followup_questions, additional_research_data):
    logger.info("Enhancing report with follow-up questions and additional research")
    
    enhancement_prompt = f"""
    Enhance the following initial report by addressing these follow-up questions and incorporating the additional research data:

    Initial Report:
    {initial_report}

    Follow-up Questions:
    {followup_questions}

    Additional Research Data:
    {format_additional_research(additional_research_data)}

    Please incorporate answers to these questions into the relevant sections of the report, adding specific examples, data, and detailed explanations where possible. Use the additional research data to provide more in-depth answers and insights. Maintain the overall structure and formatting of the initial report, but feel free to expand sections or add new subsections as needed to accommodate the additional information. Return just the enhanced report, with no meta-comments.
    """
    
    try:
        enhanced_response = interpreter.chat(enhancement_prompt)
        
        # Extract content from the enhanced response
        if isinstance(enhanced_response, list):
            enhanced_content = "\n".join([item.get('content', '') for item in enhanced_response if isinstance(item, dict)])
        elif isinstance(enhanced_response, dict):
            enhanced_content = enhanced_response.get('content', '')
        else:
            enhanced_content = str(enhanced_response)
        
        logger.info("Report enhancement completed successfully")
        return enhanced_content
    except Exception as e:
        logger.error(f"Error enhancing report: {str(e)}")
        return f"Error enhancing report: {str(e)}"

def format_additional_research(additional_research_data):
    """Format the additional research data for inclusion in the prompt."""
    formatted_data = ""
    for item in additional_research_data:
        formatted_data += f"Question: {item['question']}\n"
        for result in item['data']:
            formatted_data += f"Source: {result['url']}\n"
            formatted_data += "Content Excerpts:\n"
            for content in result['data']['content'][:2]:  # Limit to first 2 content excerpts for brevity
                formatted_data += f"- {content}\n"
        formatted_data += "\n"
    return formatted_data

def generate_html_report(markdown_content, title):
    logger.info(f"Generating HTML report: {title}")
    
    try:
        # Convert markdown to HTML
        html_content = markdown.markdown(markdown_content, extensions=['extra'])
        
        # Improve the HTML structure
        improved_html = improve_html_structure(html_content)
        
        html_template = f"""
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
            <nav>
                <ul>
                    <li><a href="#introduction">Introduction</a></li>
                    <li><a href="#key-findings">Key Findings</a></li>
                    <li><a href="#conclusion">Conclusion</a></li>
                </ul>
            </nav>
            <main>
                {improved_html}
            </main>
            <footer>
                <p>&copy; {datetime.now().year} Research Report</p>
            </footer>
        </body>
        </html>
        """
        
        logger.info("HTML report generated successfully")
        return html_template
    except Exception as e:
        logger.error(f"Error generating HTML report: {str(e)}")
        return f"<html><body><h1>Error</h1><p>Error generating HTML report: {str(e)}</p></body></html>"

def improve_html_structure(html_content):
    """
    Improve the HTML structure by converting certain patterns to more semantic HTML.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Convert dash lists and other potential bullet point formats to proper HTML lists
    convert_to_list(soup)
    
    # Wrap content between headers in sections
    wrap_sections(soup)
    
    return str(soup)

def convert_to_list(soup):
    """
    Convert various bullet point formats to proper HTML lists.
    """
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

def wrap_sections(soup):
    """
    Wrap content between headers in sections.
    """
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

if __name__ == "__main__":
    # For testing purposes
    logging.basicConfig(level=CONFIG["LOG_LEVEL"], format=CONFIG["LOG_FORMAT"])
    test_topic = "Artificial Intelligence in Healthcare"
    test_research_data = [
        {
            "url": "https://example.com/ai-healthcare",
            "data": {
                "headlines": ["AI revolutionizes healthcare", "Machine learning in diagnosis"],
                "content": ["AI is transforming healthcare in numerous ways...", "Machine learning algorithms can analyze medical images..."],
                "error": None
            }
        }
    ]
    
    initial_report = generate_initial_report(test_topic, test_research_data)
    print("Initial Report:")
    print(initial_report)
    print("\n---\n")
    
    followup_questions = generate_followup_questions(initial_report)
    print("Follow-up Questions:")
    print(followup_questions)
    print("\n---\n")
    
    enhanced_report = enhance_report(initial_report, followup_questions)
    print("Enhanced Report:")
    print(enhanced_report)
    print("\n---\n")
    
    html_report = generate_html_report(enhanced_report, f"{test_topic} Research Report")
    print("HTML Report (excerpt):")
    print(html_report[:500] + "...")  # Print first 500 characters of HTML report