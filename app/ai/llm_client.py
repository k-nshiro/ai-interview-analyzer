import json
from openai import AsyncOpenAI
from app.core.config import settings
from app.schemas.evaluation import AnswerEvaluation, NextQuestionGen
from app.ai.prompts.evaluator import EVALUATOR_SYSTEM_PROMPT
from app.ai.prompts.questioner import QUESTIONER_SYSTEM_PROMPT
from app.schemas.report import InterviewReport # New import
from app.ai.prompts.reporter import REPORTER_SYSTEM_PROMPT

# Initialize the async client
# In production, we ensure the API key is loaded from the environment securely
client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
     base_url="https://api.groq.com/openai/v1") # pointing it to Groq's free servers

async def evaluate_candidate_answer(
    role: str, 
    experience_level: str, 
    question: str, 
    candidate_answer: str
) -> AnswerEvaluation:
    """
    Calls the LLM to evaluate an answer and strictly parses the output into our Pydantic schema.
    """
    
    # 1. Format our system prompt with the candidate's context
    system_message = EVALUATOR_SYSTEM_PROMPT.format(
        role=role, 
        experience_level=experience_level
    )
    
    user_message = f"Question: {question}\nCandidate Answer: {candidate_answer}"

    try:
        # 2. Call the LLM using JSON mode
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Or gpt-3.5-turbo-1106 for cost savings
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            response_format={ "type": "json_object" }, # Forces JSON output
            temperature=0.2 # Low temperature so the AI is analytical, not highly creative
        )

        # 3. Extract the raw text
        raw_json = response.choices[0].message.content
        
        # 4. Parse it into a Python dictionary
        parsed_data = json.loads(raw_json)
        
        # 5. Validate and return it via our strict Pydantic contract
        return AnswerEvaluation(**parsed_data)
        
    except Exception as e:
        # In a real system, we would log this error to Sentry or Datadog
        print(f"AI Evaluation Error: {str(e)}")
        raise e
    
async def generate_next_question(
    role: str,
    experience_level: str,
    previous_question: str,
    score: int,
    weaknesses: list[str]
) -> NextQuestionGen:
    """
    Calls the LLM to generate the next adaptive interview question.
    """
    system_message = QUESTIONER_SYSTEM_PROMPT.format(
        role=role,
        experience_level=experience_level,
        previous_question=previous_question,
        score=score,
        weaknesses=", ".join(weaknesses) if weaknesses else "None"
    )
    
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": "Generate the next question."}
            ],
            response_format={ "type": "json_object"},
            temperature=0.6 # Slightly higher temperature for variety in questioning
        )

        raw_json = response.choices[0].message.content
        parsed_data = json.loads(raw_json)

        return NextQuestionGen(**parsed_data)
    
    except Exception as e:
        print(f"AI Question Generation Error: {str(e)}")
        raise e

async def generate_final_report(
    role: str,
    experience_level: str,
    transcript: str
) -> InterviewReport:
    """
    Calls the LLM to analyze the entire interview transcript and generate a final report.
    """
    system_message = REPORTER_SYSTEM_PROMPT.format(
        role=role,
        experience_level=experience_level,
        transcript=transcript
    )
    
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile", # You want a smart model for the final summary
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": "Generate the final interview report."}
            ],
            response_format={ "type": "json_object"},
            temperature=0.3 # Low temperature for an objective, consistent report
        )

        raw_json = response.choices[0].message.content
        parsed_data = json.loads(raw_json)

        return InterviewReport(**parsed_data)
    
    except Exception as e:
        print(f"AI Report Generation Error: {str(e)}")
        raise e