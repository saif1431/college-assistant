import os
from typing import TypedDict, Annotated
from click import prompt
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph , START,END
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from dotenv import load_dotenv

load_dotenv()


embeddings = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-MiniLM-L6-v2")


# Step 01 Building the retriever from the PDF file

def build_retriever(pypdf_path: str):
      loader  = PyPDFLoader(pypdf_path)
      documents = loader.load()
      
      text_splitter = RecursiveCharacterTextSplitter(chunk_size = 800, chunk_overlap = 100)
      
      chunks = text_splitter.split_documents(documents)
      vectorstore = FAISS.from_documents(chunks, embeddings)
      
      return vectorstore.as_retriever(search_kwargs={"k": 3})


rule_book = build_retriever("Rule-Book-2023.pdf")
academic_rule_book = build_retriever("UET_Taxila_Sample_Department_Descriptions.pdf")
fee_structure = build_retriever("UET_Taxila_Sample_Fee_Structure.pdf")


llm = ChatGroq(model= "openai/gpt-oss-120b", temperature=0.3,)


# step 02 State


class State(TypedDict):
      programme : str
      messages : Annotated[list, add_messages]
      query_type: str
      retrieved_context: str
      
# Step 03 Create Nodes


def classfier_node(state: State) -> dict:
      """Look at the latest user message and decide which path to take"""
      
      last_message = state["messages"][-1].content
      
      prompt = (
        "Classify the following student query into exactly one category: "
        "'academic', 'fee', or 'general'.\n\n"
        "Use 'academic' for questions about attendance, exams, grading, credits, "
        "promotion, course structure, summer training, or degree requirements.\n"
        "Use 'fee' for questions about tuition, payment, refund, late charges, "
        "scholarships, or any money-related topic.\n"
        "Use 'general' for greetings, casual talk, or anything not related to "
        "the college rules or fee.\n\n"
        f"Query: {last_message}\n\n"
        "Return only one word: academic, fee, or general."
    )
    
    
      response = llm.invoke(prompt)
      category = response.content.strip().lower()

      if "academic" in category:
        category = "academic"
      elif "rule_book" in category:
              category = "rule_book"
      elif "fee" in category:
        category = "fee"
      else:
        category = "general"
        
      return {"query_type": category}
      
      
def academic_rag_node(state: State) -> dict:
      """Retrieve relevant information from the academic rule book based on the user's query."""
      
      query = state["messages"][-1].content
      docs = academic_rule_book.invoke(query)
      context= "\n\n".join([doc.page_content for doc in docs])
      return {"retrieved_context": context}


def rule_book_rag_node(state: State) -> dict:
      """Retrieve relevant information from the rule book based on the user's query."""
      
      query = state["messages"][-1].content
      docs = rule_book.invoke(query)
      context= "\n\n".join([doc.page_content for doc in docs])
      return {"retrieved_context": context}


def fee_rag_node(state: State) -> dict:
      """Retrieve relevant information from the fee structure based on the user's query."""
      
      query = state["messages"][-1].content
      docs = fee_structure.invoke(query)
      context= "\n\n".join([doc.page_content for doc in docs])
      return {"retrieved_context": context}
      
def general_node(state: State) -> dict:
      """Handle general queries that do not require retrieval from any document."""
      
      return {"retrieved_context": "This is a general query. No specific information retrieved."}
      
      
      
def response_node(state: State) -> dict:
    """Generates the final answer, personalized using the student's programme."""
    query = state["messages"][-1].content
    programme = state.get("programme", "Unknown")
    context = state["retrieved_context"]

    if context == "NO_RETRIEVAL_NEEDED":
        prompt = (
            f"You are a friendly college assistant talking to a {programme} student. "
            f"Answer this question using your own general knowledge:\n\n{query}"
        )
    else:
        prompt = (
            f"You are a college assistant helping a {programme} student. "
            f"Use the following context from the official college documents to answer "
            f"the question accurately. If the context mentions specific figures for "
            f"different programmes, highlight the one relevant to {programme} if possible.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}\n\n"
            f"Give a clear, friendly, and precise answer."
        )

    response = llm.invoke(prompt)
    return {"messages": [("ai", response.content.strip())]}
    
    
# Step 4 Router Funtion 


def route_query(state: State):
      if state["query_type"] == "academic":
            return "academic_rag_node"
      elif state["query_type"] == "rule_book":
            return "rule_book_rag_node"
      elif state["query_type"] == "fee":
            return "fee_rag_node"
      else:
            return "general_node"
            
# step 05 Create the StateGraph

graph  = StateGraph(State)

graph.add_node("classfier_node", classfier_node)
graph.add_node("academic_rag_node", academic_rag_node)
graph.add_node("rule_book_rag_node", rule_book_rag_node)
graph.add_node("fee_rag_node", fee_rag_node)
graph.add_node("general_node", general_node)
graph.add_node("response_node", response_node)


# edges


graph.add_edge(START, "classfier_node")
graph.add_conditional_edges("classfier_node", route_query)

graph.add_edge("academic_rag_node", "response_node")
graph.add_edge("rule_book_rag_node", "response_node")
graph.add_edge("fee_rag_node", "response_node")
graph.add_edge("general_node", "response_node")

graph.add_edge("response_node", END)

app = graph.compile()

# Step 06 Run the Code


print("welcome to the College assistant \n\n")

print("which programe are you in ")
print("1. Computer Science")
print("2. Electrical Engineering")
print("3. Mechanical Engineering")
print("4. Civil Engineering")
print("5. Chemical Engineering")
print("6. Software Engineering")


choice = input("\nEnter 1, 2, 3, 4, 5, or 6 ")

program_map = {
      "1": "Computer Science",
      "2": "Electrical Engineering",
      "3": "Mechanical Engineering",
      "4": "Civil Engineering",
      "5": "Chemical Engineering",
      "6": "Software Engineering"
}

student_programme = program_map.get(choice, "Unknown")

print(f"\nGreat! You're set as a {student_programme} student.")


while True:
      user_query = input("You: ")
      
      if user_query.lower() in ["exit", "quit"]:
            print("Exiting the College Assistant. Goodbye!")
            break
      
      
      result = app.invoke({
            "programme": student_programme,
            "messages": [("human", user_query)]
      })
      print(f"Assistant : {result['messages'][-1].content}")     