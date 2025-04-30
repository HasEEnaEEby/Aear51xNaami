import streamlit as st

def render_chat_page(security_advisor=None):
    st.title("💬 Chat with Security Advisor")

    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Context selection (e.g., industry)
    industry_options = ["Finance", "Healthcare", "Technology", "Education"]
    selected_industry = st.selectbox("Select your industry", industry_options, index=0)

    # Input field
    user_input = st.text_input("Ask a question about security or compliance", key="user_question")

    if st.button("Send") and user_input.strip():
        # Generate response from advisor or fallback
        if security_advisor and hasattr(security_advisor, "answer_question"):
            try:
                response = security_advisor.answer_question(user_input, context=selected_industry)
            except Exception as e:
                response = f"[Error] Failed to get advisor response: {str(e)}"
        else:
            response = f"(Simulated advisor response to: {user_input})"

        st.session_state.chat_history.append({"user": user_input, "bot": response})

    # Display conversation history
    st.subheader("Conversation")
    for i, chat in enumerate(reversed(st.session_state.chat_history[-10:])):
        st.markdown(f"**You:** {chat['user']}")
        st.markdown(f"**Advisor:** {chat['bot']}")
