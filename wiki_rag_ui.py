import streamlit as st
from wikipedia_rag import build, ask_agent

from streamlit.web import cli as stcli
from streamlit import runtime
import sys

def main():
    # Initialize session state
    if 'agent' not in st.session_state:
        st.session_state.agent = None

    # Title
    st.title("Wikipedia RAG Chat")

    # Input for the topic
    topic = st.text_input("Enter the Wikipedia topic:", "")

    # Button to build the agent
    if st.button("Build Agent") and topic:
        st.session_state.agent = build(topic)
        if st.session_state.agent:
            st.success("Agent built successfully!")
        else:
            st.error("Failed to build the agent.")

    # Input for the question
    question = st.text_input("Ask a question:", "")

    # Button to ask the agent
    if st.button("Ask Agent") and question:
        if st.session_state.agent:
            answer = ask_agent(question)
            st.write("Answer:", answer)
        else:
            st.error("Please build the agent first by entering a topic and clicking 'Build Agent'.")

# Run the Streamlit app
if __name__ == "__main__":
    if runtime.exists():
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())