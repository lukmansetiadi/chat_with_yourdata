import json
import re
from sqlalchemy import create_engine, inspect

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from sqlalchemy import text

# from langchain_ollama.llms import OllamaLLM

load_dotenv()

# template version 2 : adding extra information on schema:
template = """
You are a SQL generator.  
When given a schema and a user question, you MUST output only the SQL statement—nothing else.  
Do not wrap the SQL query in any other text, not even backticks.
and get rid of ```sql in start and ``` at end of the query 

extra information on schema: {extrainformation}

For example:
Question: which 3 artists have the most tracks?
SQL Query: SELECT ArtistId, COUNT(*) as track_count FROM Track GROUP BY ArtistId ORDER BY track_count DESC LIMIT 3;
Question: Name 10 artists
SQL Query: SELECT Name FROM Artist LIMIT 10;

Schema: {schema}
User question: {query}
Output (SQL only):
"""

# model = OllamaLLM(model="deepseek-r1")
model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

def extract_schema(db_url):
    engine = create_engine(db_url)
    inspector = inspect(engine)
    schema = {}

    for table in inspector.get_table_names():
        columns = inspector.get_columns(table)
        schema[table] = [col['name'] for col in columns]

    return json.dumps(schema)

def clean_text(text: str):
    # if reasoning llm model
    cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned_text.strip()

def to_sql_query(query, schema, extrainformation):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    return clean_text(chain.invoke({"query": query, "schema": schema, "extrainformation": extrainformation}).content)

    # if using ollama server
    # return clean_text(chain.invoke({"query": query, "schema": schema}))

def execute_sql_query(db_url, sql_query):
    engine = create_engine(db_url)
    with engine.connect() as connection:
        result = connection.execute(text(sql_query))
        rows = result.fetchall()
        # Format the result as a string
        if not rows:
            return "No results found."
        headers = result.keys()
        output = [", ".join(headers)]
        for row in rows:
            output.append(", ".join(str(cell) for cell in row))
        return "\n".join(output)

template_insight = """
You are a Data Analyst.
and you are given a Question :  {question}
and also you already have data related to the question, make this as your context : {data}
this data is coming from a query given : {query}

please also give a chart/visualization that indicate your insight summary
please put a conclusion or summary in the top of your answer, after that detail of your contextual summary

Output (summarize):
"""

def get_insight(question,query, data):
    prompt = ChatPromptTemplate.from_template(template_insight)
    chain = prompt | model

    return clean_text(chain.invoke({"question": question, "data": data,"query": query}).content)

template_matplotlib = """
you are a python developer.
Need you write a matplotlib python code to visualize the data below with a table image:

data: 
{data}

please give me only the python code text 
not the image !

remove text of :
1. ```python
2. ```

and also make the height of image to 3 inches : relate to code fig, ax = plt.subplots(figsize=(10, 3))

output: 
"""

def get_tableimage_code(data):
    prompt = ChatPromptTemplate.from_template(template_matplotlib)
    chain = prompt | model

    return chain.invoke({ "data": data}).content

