## 🚀 Getting Started & Local Setup

To run this Multi-Agent Pipeline locally, follow these steps to configure your environment variables and dependencies securely.

### 1. Clone the Repository
```bash
git clone [https://github.com/tvietnhan/auto_apply_agent.git](https://github.com/tvietnhan/auto_apply_agent.git)

cd auto_apply_agent
```
### 2. Install Dependencies
Ensure you have Python installed, then install the official Google GenAI SDK:.
```bash
pip install google-genai
```
### 3. Environment Configuration (API Keys & Credentials)
This project utilizes environment variables to safeguard sensitive credentials. Do not hardcode your keys.

In the project root directory, look for the .env.example file.

Duplicate or rename it to .env:
```bash
cp .env.example .env
```
Open the newly created .env file and replace the placeholders with your own actual credentials:

* SENDER_API_KEY: Your personal Gemini API key generated via Google AI Studio.

* SENDER_EMAIL: The Google account email address you wish to use as the dispatcher.

* SENDER_PASSWORD: Your designated 16-character Google App Password (not your regular login password).

### 4. Execute the Pipeline
Once your .env file is successfully populated, run the master orchestration script:
```bash
python run_pipeline.py
```
