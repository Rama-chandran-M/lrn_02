from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import GEMINI_API_KEY, GEMINI_MODEL

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    google_api_key=GEMINI_API_KEY,
    temperature=0.2
)

def run_chain(prompt_template_str, input_dict):
    try:
        # ✅ Manual safe replacement (NO template engine)
        prompt = prompt_template_str

        for key, value in input_dict.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))

        response = llm.invoke(prompt)

        return getattr(response, "content", str(response)), None

    except Exception as e:
        return None, str(e)