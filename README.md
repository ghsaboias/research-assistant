# Research Assistant Application

The Research Assistant Application is a comprehensive tool that helps users conduct thorough research on various topics. It integrates web scraping, report generation, and conversation history management to provide a seamless research experience.

## Key Features

1. **Web Scraping**: The `scraper.py` module is responsible for fetching relevant information from the web based on user queries.

   - It performs Google searches, scrapes the top search results, and extracts key data such as headlines and content snippets.

2. **Report Generation**:

   - The `report_generator.py` module takes the scraped data and generates structured research reports.
   - It converts the raw data into a more readable format, adds follow-up questions, and enhances the reports to provide a comprehensive overview of the topic.

3. **Conversation History**: The `conversation_saver.py` module manages the conversation history between the user and the research assistant.

   - It saves the conversation data (user queries and assistant responses) to JSON files, allowing for context and analysis of the research process.

4. **Integrated Workflow**: The `researcher.py` module ties everything together, orchestrating the web scraping, report generation, and conversation saving into a cohesive research workflow.
   - It provides a `general_purpose_researcher` function that can be called with a topic to initiate the full research process.

## Usage

To use the Research Assistant Application, follow these steps:

1. Ensure you have Python 3.x installed on your system.
2. Clone the repository or download the source files.
3. Install the required dependencies by running:
   ```
   pip install -r requirements.txt
   ```
4. Run the `main.py` script with your research topic as an argument:
   ```
   python main.py "Your research topic here"
   ```

## Project Structure

- `scraper.py`: Handles web scraping and data extraction.
- `report_generator.py`: Generates and enhances research reports.
- `conversation_saver.py`: Manages conversation history.
- `researcher.py`: Orchestrates the overall research process.
- `main.py`: Entry point for the application.

## Output

The application generates two main outputs:

1. An HTML report file in the `reports/` directory, containing the comprehensive research findings.
2. A JSON file in the `debug/` directory, storing the conversation history for the research session.

## Customization

You can customize various aspects of the research process by modifying the respective modules:

- Adjust scraping parameters in `scraper.py`
- Modify report generation prompts in `report_generator.py`
- Change conversation saving format in `conversation_saver.py`

## Contributing

Contributions to improve the Research Assistant Application are welcome. Please feel free to submit pull requests or open issues to suggest enhancements or report bugs.

## License

This project is open-source and available under the MIT License.
