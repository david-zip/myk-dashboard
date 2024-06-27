import os
import sqlalchemy
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent

def initialise_llm():
    """
    Initialize the language model (LLM).

    This function sets up and returns an instance of ChatOpenAI with the model 'gpt-3.5-turbo' and a temperature setting of 0.2, which controls the randomness of the model's responses.

    Returns:
        ChatOpenAI: An instance of the ChatOpenAI class configured with the specified model and temperature.
    """
    return ChatOpenAI(model='gpt-3.5-turbo', temperature=0.2)

def initialise_db(db: 'pandas.DataFrame', db_name: str):
    """
    Initialize the SQL database.

    This function creates a SQLite database from a given pandas DataFrame. The database is saved in the current working directory under a specified name. The DataFrame is stored in the database, and an SQLDatabase instance is returned for further operations.

    Args:
        db (pandas.DataFrame): The DataFrame to be stored in the database.
        db_name (str): The name of the database.

    Returns:
        SQLDatabase: An instance of the SQLDatabase class connected to the newly created SQLite database.
    """
    cwd = os.getcwd()
    conn = sqlalchemy.create_engine(f'sqlite:///{cwd}/data/{db_name}.db')
    db.to_sql(db_name, conn, if_exists='replace', index=False)
    sql_db = SQLDatabase.from_uri(f'sqlite:///{cwd}/data/{db_name}.db')
    
    return sql_db

def invoke_llm(query: str, db: 'pandas.DataFrame', db_name: str):
    """
    Invoke the language model to process a query against a SQL database.

    This function initializes the language model and SQL database, sets up an SQL agent, and uses the agent to process a given query. The response from the agent is cleaned and returned.

    Args:
        query (str): The query to be processed by the language model.
        db (pandas.DataFrame): The DataFrame to be stored in the database.
        db_name (str): The name of the database.

    Returns:
        str: The cleaned response from the language model agent after processing the query.
    """
    # Initialise LLM
    llm = initialise_llm()
    
    # Initialise database
    sql_db = initialise_db(db, db_name)
    
    # Initialise SQL agent
    agent = create_sql_agent(llm, db=sql_db, agent_type="tool-calling")
    
    # Query agent and clean response
    response = agent.invoke(query)['output']
    
    return response