# API Testing Tool

A simple desktop application built with Python and Tkinter to test APIs (GET, POST, PUT, DELETE).

## Features

*   Send GET, POST, PUT, DELETE requests.
*   Add optional headers and JSON/text request body.
*   View response status, headers, and body.
*   Save request/response history locally (using SQLite).
*   Export response or entire history to a file.
*   View request response time.
*   Clear input/output fields.

## Getting Started

1.  Ensure you have Python 3.10+ installed.
2.  Clone or download this project.
3.  Navigate to the project directory (`api_tester`).
4.  Install dependencies: `pip install -r requirements.txt`
5.  Run the application: `python main.py`

## Usage

1.  Enter the API URL in the "URL" field.
2.  Select the HTTP method (GET, POST, PUT, DELETE) from the dropdown.
3.  (Optional) Add headers in JSON format in the "Headers (JSON)" text box.
4.  (Optional) Add request body in JSON or plain text format in the "Body (JSON/Text)" text box.
5.  Click the "Send Request" button.
6.  View the response status code, headers, and body in the designated text areas below.
7.  Use the "Clear" button to reset all input and output fields.
8.  Use the "Save Response" button to save the *current* response body to a file.
9.  Use the "Export History" button to save the *entire* request history to a JSON file.