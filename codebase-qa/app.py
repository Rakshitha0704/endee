import os
import time
import hashlib
import streamlit as st
from dotenv import load_dotenv
from indexer import index_repository
from retriever import get_answer

load_dotenv()

st.set_page_config(
    page_title="Codebase Q&A",
    page_icon="💻",
    layout="wide"
)

st.title("💻 Codebase Q&A")
st.markdown("Ask any question about a codebase and get answers grounded in the actual code.")

if "indexed" not in st.session_state:
    st.session_state.indexed = False
if "collection" not in st.session_state:
    st.session_state.collection = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "repo_path" not in st.session_state:
    st.session_state.repo_path = ""
if "index_name" not in st.session_state:
    st.session_state.index_name = ""

with st.sidebar:
    st.header("Step 1: Index a Repository")
    st.markdown("Paste the path to a local cloned GitHub repo.")

    repo_path = st.text_input(
        "Repository path",
        placeholder="e.g. C:/Users/User/Desktop/RAG-2/click-repo"
    )

    if st.button("Index Repository", type="primary"):
        if not repo_path:
            st.error("Please enter a repository path first.")
        elif not os.path.exists(repo_path):
            st.error("That path doesn't exist. Please check and try again.")
        else:
            with st.spinner("Indexing repository... this may take a minute."):
                try:
                    import endee
                    db = endee.Endee()

                    index_name = "idx_" + hashlib.md5(repo_path.encode()).hexdigest()[:8]

                    try:
                        db.delete_index(index_name)
                        time.sleep(1)
                    except Exception:
                        pass

                    db.create_index(
                        name=index_name,
                        dimension=384,
                        space_type="cosine"
                    )
                    time.sleep(1)
                    collection = db.get_index(index_name)

                    total = index_repository(repo_path, collection)

                    st.session_state.collection = collection
                    st.session_state.indexed = True
                    st.session_state.repo_path = repo_path
                    st.session_state.index_name = index_name

                    st.success(f"Indexed {total} chunks successfully!")
                except Exception as e:
                    st.error(f"Error during indexing: {str(e)}")

    if st.session_state.indexed:
        st.markdown("---")
        st.success("Repository is indexed and ready!")
        st.caption(f"Path: {st.session_state.repo_path}")
        st.markdown("**Try asking:**")
        questions = [
            "Where is authentication handled?",
            "How is the database connected?",
            "What does the main function do?",
            "Where are API routes defined?"
        ]
        for q in questions:
            if st.button(q, key=q):
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": q
                })

if not st.session_state.indexed:
    st.info("Index a repository using the sidebar to get started.")
else:
    st.header("Step 2: Ask Questions")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("View retrieved source chunks"):
                    for i, chunk in enumerate(message["sources"]):
                        st.caption(f"Source {i+1}: {chunk['meta'].get('file', 'unknown')}")
                        st.code(chunk['meta'].get('content', ''), language="python")

    user_question = st.chat_input("Ask a question about the codebase...")

    if user_question:
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_question
        })

        with st.chat_message("user"):
            st.markdown(user_question)

        with st.chat_message("assistant"):
            with st.spinner("Searching codebase..."):
                try:
                    answer, sources = get_answer(
                        user_question,
                        st.session_state.collection
                    )
                    st.markdown(answer)
                    with st.expander("View retrieved source chunks"):
                        for i, chunk in enumerate(sources):
                            st.caption(f"Source {i+1}: {chunk['meta'].get('file', 'unknown')}")
                            st.code(chunk['meta'].get('content', ''), language="python")
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                except Exception as e:
                    st.error(f"Error getting answer: {str(e)}")
