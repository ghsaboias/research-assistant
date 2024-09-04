# Research Assistant Application Guide

## 1. Setup and Configuration

### Key Configuration Settings

- `CONFIG["NUM_SEARCH_RESULTS"]`: Number of search results to scrape
- `CONFIG["AI_MODEL"]`: AI model for natural language processing
- `CONFIG["REPORTS_DIR"]`: Directory for storing generated reports
- `CONFIG["DEBUG_DIR"]`: Directory for debug files and conversation history

## 2. Core Modules and Workflow

### 2.1 Researcher (`researcher.py`)

- Main function: `general_purpose_researcher(topic)`
  - Orchestrates entire research process
  - Calls functions from other modules in sequence

### 2.2 Scraper (`scraper.py`)

- Key function: `search_and_scrape(topic, delete_results=True)`
  - Performs Google search for the topic
  - Scrapes top results (number defined by `CONFIG["NUM_SEARCH_RESULTS"]`)
  - Uses Selenium for dynamic content
  - Extracts paragraphs, headlines, and lists
- Notable feature: Implements concurrent scraping for efficiency

### 2.3 Report Generator (`report_generator.py`)

- Key functions:
  1. `generate_initial_report(topic, research_data)`
  2. `generate_followup_questions(initial_report)`
  3. `enhance_report(initial_report, followup_questions, additional_research_data)`
  4. `generate_html_report(markdown_content, title)`
- Uses AI model (specified in `CONFIG["AI_MODEL"]`) for natural language processing
- Converts markdown to HTML for final report

### 2.4 Conversation Saver (`conversation_saver.py`)

- Key functions:
  - `save_conversation(topic, conversation)`: Saves to JSON in `CONFIG["DEBUG_DIR"]`
  - `load_conversation(filename)`: Retrieves saved conversations

## 3. Application Workflow

1. User inputs research topic
2. `general_purpose_researcher` initiates process
3. Web scraping performed via `search_and_scrape`
4. Initial report generated using `generate_initial_report`
5. Follow-up questions created with `generate_followup_questions`
6. Additional research conducted based on follow-up questions
7. Report enhanced using `enhance_report`
8. Final HTML report generated with `generate_html_report`
9. Conversation history saved using `save_conversation`

## 4. Error Handling and Logging

- Each module uses Python's `logging` module
- Errors logged with severity levels (INFO, WARNING, ERROR)
- Debug information saved in `CONFIG["DEBUG_DIR"]`

## 5. Extending the Application

- Add new scraping methods in `scraper.py`
- Enhance report generation in `report_generator.py`
- Modify `general_purpose_researcher` to incorporate new features
- Update `CONFIG` dictionary for new settings
