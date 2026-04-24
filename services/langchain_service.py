from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from config.settings import GEMINI_API_KEY, GEMINI_MODEL

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    google_api_key=GEMINI_API_KEY,
    temperature=0.2
)

def run_chain(prompt_template_str, input_dict):
    try:
        prompt = PromptTemplate.from_template(prompt_template_str)

        # NEW LCEL chain
        chain = prompt | llm

        response = chain.invoke(input_dict)

        # Extract text properly
        return response.content, None

    except Exception as e:
        return None, str(e)