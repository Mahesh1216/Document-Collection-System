# QuickDocs Document Management System

This is technical assessment to build a complete document collection system with an AI query interface for QuickDocs startup.

## Requirements

*   **Part 1:** Database schema with 5 entities
*   **Part 2:** Web interface with 3 pages
*   **Part 3:** AI-powered natural language to SQL query system

## Tech Stack

*   **Backend:** Python Flask
*   **Database:** SQLite
*   **Frontend:** HTML5, CSS3, vanilla JavaScript
*   **AI Query:** LLM (Gemini API)

## Project Structure

```
/quickdocs-assessment/
├── app.py
├── requirements.txt
├── README.md
├── /database/
│   ├── schema.sql
│   └── sample_data.sql
└── /templates/
    ├── base.html
    ├── index.html
    ├── customers.html
    ├── documents.html
    ├── dashboard.html
    └── query.html
```

## Setup
Create an env file with Gemini API key and Flask_Secert_Key
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Initialize the database:
    ```bash
    flask initdb
    ```
3.  Run the application:
    ```bash
    flask run
    ```

## Pages

*   `/`: Home page
*   `/customers`: Customer registration and list
*   `/documents`: Document submission and list
*   `/dashboard`: Status dashboard
*   `/query`: AI query interface
