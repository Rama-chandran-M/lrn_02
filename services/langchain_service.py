from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config.settings import GEMINI_API_KEY, GEMINI_MODEL

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    google_api_key=GEMINI_API_KEY,
    temperature=0.2
)

def run_chain(prompt_template_str, input_dict):
    try:
        prompt = PromptTemplate(
            input_variables=list(input_dict.keys()),
            template=prompt_template_str
        )

        chain = LLMChain(llm=llm, prompt=prompt)

        response = chain.run(input_dict)

        return response, None

    except Exception as e:
        return None, str(e)