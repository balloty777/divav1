from graph.state import State
from graph.nodes.check_character import character_initialization,initialize_session
from langgraph.graph import StateGraph,START,END
from database import create_tables
create_tables()

character=StateGraph(State)
character.add_node('character_initialization',character_initialization)
character.add_node('session_initialization',initialize_session)
character.add_edge(START,'session_initialization')
character.add_edge('session_initialization','character_initialization')
character.add_edge('character_initialization',END)
character_update=character.compile()
