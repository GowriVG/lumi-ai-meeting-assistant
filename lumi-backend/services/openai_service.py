import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv
from exceptions.custom_exceptions import OpenAIServiceError, PromptValidationError

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")


def summarize_meeting(transcript: str):

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
        raise OpenAIServiceError(f"Azure OpenAI Error: {str(e)}")

def ask_question(transcript: str, question: str):

    prompt = f"""
You are an AI meeting assistant.
Return ONLY valid JSON. Do NOT wrap the JSON inside strings or an 'answer' field. Return the JSON object directly.

Return the answer strictly in JSON format like:
{{ "answer": "your answer here" }}

Rules:
- Answer ONLY from the transcript
- If not found, return:
  {{ "answer": "This information was not discussed in the meeting." }}

Transcript:
{transcript}

Question:
{question}

Return ONLY valid JSON.
"""

    try:

        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful meeting assistant. Always respond in JSON format."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
            timeout = 30
        )

        content = response.choices[0].message.content.strip()

        # ✅ SAFE PARSE
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:].strip()

        return json.loads(content)

    except json.JSONDecodeError:
        raise PromptValidationError(
            f"Invalid JSON returned: {content[:100]}"
        )

    except Exception as e:
        raise OpenAIServiceError(f"Q&A Error: {str(e)}")