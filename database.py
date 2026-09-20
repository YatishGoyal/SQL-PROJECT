import streamlit as st
import psycopg2 as psql


def connection():
    conn = psql.connect(
        host=st.secrets["database"]["host"],
        database=st.secrets["database"]["database"],
        user=st.secrets["database"]["user"],
        password=st.secrets["database"]["password"],
        port=st.secrets["database"]["port"]
    )

    return conn
