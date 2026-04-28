import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv
from exceptions.custom_exceptions import OpenAIServiceError, PromptValidationError
from logger import logger
from services.retrieval_service import retrieve_relevant_chunks

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

def normalize_question(q: str):
    return q.lower().strip()

def generate_insights(summary):
    insights = []

    items = summary.get("action_items", [])

    unassigned = [i for i in items if not i.get("owner")]
    if unassigned:
        insights.append(f"{len(unassigned)} tasks have no owner")

    bugs = [i for i in items if i.get("type") == "Bug"]
    if bugs:
        insights.append(f"{len(bugs)} bugs mentioned")

    no_priority = [i for i in items if not i.get("priority")]
    if no_priority:
        insights.append(f"{len(no_priority)} tasks have no priority")

    return insights

def summarize_meeting(transcript: str):
    logger.info("Calling OpenAI for summarization")

    prompt = f"""
You are an AI meeting assistant.

Your job is to analyze a meeting transcript and extract structured work items for Azure DevOps.

Return ONLY valid JSON. Do NOT wrap the JSON inside strings or an 'answer' field. Return the JSON object directly.

From the transcript identify:
1. Key discussion points
2. Important decisions
3. Work items that should be created in Azure DevOps

Work items must be classified into these types:
- Epic → large initiative or business goal
- Feature → product capability
- User Story → user requirement
- Task → engineering implementation work
- Bug → defect or issue

Rules:
- Extract items only if clearly mentioned.
- Maintain hierarchy when possible: Epic → Feature → User Story → Task
- Bugs should be created separately.
- Tasks should usually belong to a User Story.
- If no Epic or Feature is discussed, create only the relevant work items.

Return the response in STRICT JSON format:

{{
  "key_points": [],
  "decisions": [],
  "action_items": [
    {{
      "title": "",
      "description": "",
      "type": "Epic | Feature | User Story | Task | Bug",
      "priority": "optional",
      "story_points": "optional",
      "owner": "optional"
    }}
  ]
}}

Transcript:
{transcript}

Return ONLY valid JSON.
"""

    try:

        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are a structured meeting assistant. Always return strictly valid JSON. Never wrap JSON inside strings or inside an 'answer' field."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content.strip()

        # Remove markdown if model returns ```json
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:].strip()

        parsed = json.loads(content)

        # unwrap if wrongly nested
        if "answer" in parsed and isinstance(parsed["answer"], str):
            parsed = json.loads(parsed["answer"])

        # 🔥 FIX ONLY action_items
        if isinstance(parsed.get("action_items"), str):
            try:
                parsed["action_items"] = json.loads(parsed["action_items"])
            except:
                pass

        return parsed

    except json.JSONDecodeError:
        raise PromptValidationError(
            f"AI returned invalid JSON. Raw content: {content[:100]}..."
        )

    except Exception as e:
        logger.error("OpenAI call failed", exc_info=True)
        raise OpenAIServiceError(f"Azure OpenAI Error: {str(e)}")
    
def ask_question(meeting_id: str, transcript: str, question: str):
    logger.info("Calling OpenAI for question answering")

    question = normalize_question(question)

    chunks = retrieve_relevant_chunks(meeting_id, question)

    context = "\n\n".join(chunks) if chunks else transcript[:1000]

    prompt = f"""
You are LUMI, an intelligent enterprise meeting assistant.

Use the meeting context to answer naturally.

RULES:
1. Understand spelling mistakes, shorthand, broken grammar.
2. Infer intent from vague questions.
3. If user asks about ownership, assignee, responsibility:
   check names, owners, assigned people, tasks.
4. If partial info exists, answer with best possible inference.
5. If no exact answer exists, say:
   "No clear owner was mentioned in the meeting."

Return JSON:
{{ "answer": "your answer here" }}

CONTEXT:
{context}

QUESTION:
{question}
"""

    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are a smart enterprise assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
            timeout=30
        )

        content = response.choices[0].message.content.strip()

        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:].strip()

        return json.loads(content)

    except json.JSONDecodeError:
        raise PromptValidationError(f"Invalid JSON returned: {content[:100]}")

    except Exception as e:
        raise OpenAIServiceError(f"Q&A Error: {str(e)}")
    
def detect_intent(message: str):
    logger.info("Calling OpenAI for intent detection")

    prompt = f"""
Classify the user message into ONLY one of these intents:

summary
work_items
qa
greeting
epic_check

STRICT RULES:

summary:
- Asking for full meeting summary
- Example: "give summary", "summarize meeting"

work_items:
- Asking to create tasks, backlog, devops items

qa:
- ANY specific question about meeting
- Asking about person, owner, task, decision
- Example:
  "who did what"
  "what did shobha commit to"
  "who owns login"
  "what was decided"

greeting:
- hi, hello, hey

epic_check:
- asking if epic exists or should be created

VERY IMPORTANT:
If question mentions a PERSON, TASK, or SPECIFIC DETAIL → ALWAYS classify as qa

Return JSON only:
{{ "intent": "qa" }}

User message:
{message}
"""

    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are an intent classifier. Return JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content.strip()
        return json.loads(content)

    except Exception as e:
        raise OpenAIServiceError(f"Intent Detection Error: {str(e)}")