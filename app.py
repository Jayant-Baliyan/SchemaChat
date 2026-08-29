import streamlit as st
from pathlib import Path
from agent import create_agent, run_query, extract_sql
from safety import is_safe_query, sanitize_input

st.set_page_config(
    page_title="SchemaChat-SQL Database Chatbot",
    page_icon="💬",
    layout="wide"
)
st.title("SchemaChat-SQL Database Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages=[]
if "agent" not in st.session_state:
    st.session_state.agent=None

if st.session_state.agent is None:
    DB_PATH=Path(__file__).parent/"Database"/"Sample"/"Chinook_Sqlite.sqlite"
    with st.spinner("Initializing SQL Agent"):
        st.session_state.agent=create_agent(str(DB_PATH))
    st.success("Agent Ready!")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt:=st.chat_input("Ask about your database "):
    clean_prompt=sanitize_input(prompt)

    st.session_state.messages.append({"role":"user","content":clean_prompt})
    with st.chat_message("user"):
        st.markdown(clean_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response=run_query(st.session_state.agent,clean_prompt)
            answer=response["output"]
            st.markdown(answer)


            sql=extract_sql(response)
            st.session_state.messages.append({
                "role":"assistant",
                "content":answer,
                "sql":sql
                
            })
            if sql:
                is_safe,reason=is_safe_query(sql)
                if not is_safe:
                    st.error(f"Blocked : {reason}")
                else:
                    with st.expander("View SQL Query"):
                        st.code(sql,language="sql")