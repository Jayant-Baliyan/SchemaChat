from langchain_groq import ChatGroq
from config import GROQ_API_KEY,LLM_MODEL,LLM_TEMPERATURE
from langchain_community.agent_toolkits import create_sql_agent
from database import get_db_connection
from pathlib import Path

BASE_DIR=Path(__file__).parent

def get_llm():
    if not GROQ_API_KEY:
        raise ValueError("GROQ API key not found check your .env file.")
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        max_tokens=1024
    )

def create_agent(db_path:str):
    llm=get_llm()
    db=get_db_connection(db_path)

    agent=create_sql_agent(
        llm=llm,
        db=db,
        agent_type="tool-calling",
        verbose=True,
        handle_parsing_errors=True,
        prefix="""You are an expert SQL analyst..."""
    )
    return agent

def run_query(agent,question:str):
    try:
        response=agent.invoke({"input":question})
        return response
    except Exception as e:
        return{
            "output":f"Sorry, I encountered an error: {str(e)}",
            "error":True
        }

def extract_sql(response:dict):
    steps=response.get("intermediate_steps",[])
    for step in steps:
        if isinstance(step,(tuple,list)) and len(step)>=2:
            action=step[0]
            observation=step[1]
            if hasattr(action,"tool") and action.tool=="sql_db_query":
                return action.tool_input
    return None

if __name__=="__main__":
    DB_PATH=BASE_DIR/"Database"/"Sample"/"Chinook_Sqlite.sqlite"
    agent=create_agent(DB_PATH)
    print("Agent Ready")
    test_questions = [
        "How many tracks are there?",
        "What are the top 5 genres by number of tracks?",
        "Which customer spent the most money?",
    ]
    for question in test_questions:
        print(f"Question: {question}")
        response=run_query(agent,question)
        print(f"Answer: {response['output']}")
        sql = extract_sql(response)
        if sql:
            print(f"SQL: {sql}")