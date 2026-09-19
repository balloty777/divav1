from langgraph.graph import StateGraph,START,END
from graph.nodes.chat import ChatNode
from graph.nodes.loader import load_context
from graph.nodes.save_messages import save_messages
from graph.nodes.update_ltm import update_long_term_memory
from graph.nodes.update_stm import update_short_term_memory
from graph.state import State

app= StateGraph(State)

app.add_node("loader",load_context)
app.add_node("chat",ChatNode)
app.add_node("save_messages",save_messages)
app.add_node("update_stm", update_short_term_memory)
app.add_node("update_ltm", update_long_term_memory)

app.add_edge(START,"loader")
app.add_edge("loader","chat")
app.add_edge("chat","save_messages")
app.add_edge("save_messages", "update_stm")
app.add_edge("update_stm", "update_ltm")
app.add_edge("update_ltm", END)

chatbot=app.compile()
