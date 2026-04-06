# LUMI AI – Meeting Intelligence Assistant

LUMI AI is an enterprise-grade AI-powered meeting assistant that transforms meeting conversations into structured insights, actionable tasks, and Azure DevOps work items.

---

## Features

* Intelligent Meeting Summarization
* Key Points and Decision Extraction
* Automatic Work Item Generation
* Azure DevOps Integration
* Context-based Q&A from meeting transcript
* Enterprise-ready UI (Microsoft Teams style)

---

## How It Works

1. Upload or load a meeting transcript
2. LUMI analyzes the discussion using Azure OpenAI
3. Extracts:

   * Key Points
   * Decisions
   * Action Items
4. Converts action items into structured work items
5. Pushes items to Azure DevOps

---

## Tech Stack

### Frontend

* Angular (Standalone Components)
* TypeScript
* HTML / CSS (Enterprise UI Design)

### Backend

* FastAPI (Python)
* Azure OpenAI (GPT-based model)
* REST APIs

### Integration

* Azure DevOps (Work Item Sync)

---

## Project Structure

```
frontend/
  ├── chat-view-component
  ├── services
backend/
  ├── openai_service.py
  ├── main.py
  ├── ado_service.py
```

---

## Setup Instructions

### 1. Clone Repository

```
git clone https://github.com/YOUR_USERNAME/lumi-ai-meeting-assistant.git
cd lumi-ai-meeting-assistant
```

### 2. Backend Setup

```
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 3. Frontend Setup

```
cd frontend
npm install
ng serve
```

---

## Environment Variables

Create a `.env` file in backend:

```
AZURE_OPENAI_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT=your_deployment
AZURE_OPENAI_API_VERSION=your_version
```

---

## Example Use Cases

* Sprint planning automation
* Meeting documentation
* Agile workflow generation
* Developer task tracking

---

## Future Enhancements

* Microsoft Teams Live Integration
* Role-based work item assignment
* Voice-based meeting input
* Dashboard analytics

---


