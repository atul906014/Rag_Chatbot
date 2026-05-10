from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder


prompt_template = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a helpful assistant answering questions about Atul Kumar's resume. "
        "Use ONLY the context provided below to answer. "
        "Do NOT use any knowledge outside the provided context.\n\n"
        "Context:\n{context}\n\n"
        "If the answer is not found, say: "
        "'This information is not mentioned in the resume.'"
    )),
    MessagesPlaceholder(variable_name="chat_history"),  # ✅ correct
    ("human", "{question}"),
])