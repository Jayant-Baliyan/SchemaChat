import re
import sys
from pathlib import Path
from langchain_groq import ChatGroq
from langchain_community.agent_toolkits import create_sql_agent
from config import GROQ_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from database import get_db_connection

BASE_DIR = Path(__file__).parent

SQL_PREFIX = """You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct SQLite query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 10 results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the below tools. Only use the information returned by the below tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
If the question does not seem related to the database, just return "I do not know" as the answer.
"""

def get_llm():
    if not GROQ_API_KEY:
        raise ValueError("GROQ API key not found. Check your .env file.")
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        max_tokens=1024
    )

def create_agent(db_path: str):
    llm = get_llm()
    db = get_db_connection(db_path)

    agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="tool-calling",
        verbose=True,
        handle_parsing_errors=True,
        prefix=SQL_PREFIX,
        agent_executor_kwargs={"return_intermediate_steps": True}
    )
    return agent

def run_query(agent, question: str):
    try:
        response = agent.invoke({"input": question})
        return response
    except Exception as e:
        return {
            "output": f"Sorry, I encountered an error: {str(e)}",
            "intermediate_steps": [],
            "error": True
        }

def extract_sql(response: dict):
    if not isinstance(response, dict):
        return None

    steps = response.get("intermediate_steps", [])
    # Traverse in reverse to get the last executed SQL query
    for step in reversed(steps):
        if isinstance(step, (tuple, list)) and len(step) >= 2:
            action = step[0]
            if hasattr(action, "tool") and action.tool in ("sql_db_query", "sql_db_query_checker"):
                tool_input = getattr(action, "tool_input", None)
                sql = None
                if isinstance(tool_input, dict):
                    sql = tool_input.get("query") or tool_input.get("sql") or tool_input.get("input")
                elif isinstance(tool_input, str):
                    sql = tool_input

                if sql and isinstance(sql, str):
                    # Strip markdown code fence if wrapped
                    cleaned = re.sub(r"^```sql\s*", "", sql.strip(), flags=re.IGNORECASE)
                    cleaned = re.sub(r"^```\s*", "", cleaned)
                    cleaned = re.sub(r"\s*```$", "", cleaned)
                    return cleaned.strip()

    return None

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    DB_PATH = BASE_DIR / "Database" / "Sample" / "Chinook_Sqlite.sqlite"
    agent = create_agent(str(DB_PATH))
    print("Agent Ready")
    test_questions = [
        "How many tracks are there?",
        "What are the top 5 genres by number of tracks?",
        "Which customer spent the most money?",
    ]
    for question in test_questions:
        print(f"\nQuestion: {question}")
        response = run_query(agent, question)
        print(f"Answer: {response['output']}")
        sql = extract_sql(response)
        if sql:
            print(f"SQL: {sql}")
