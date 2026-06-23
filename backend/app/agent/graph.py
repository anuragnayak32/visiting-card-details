"""Single LangGraph agent orchestrating card and voice workflows."""

from typing import Any, Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.agent import nodes
from app.agent.state import AgentState


def route_entry(state: AgentState) -> Literal["upload_card", "upload_audio"]:
    """Route to card or voice flow based on input type."""
    if state.get("flow_type") == "voice":
        return "upload_audio"
    return "upload_card"


def route_after_duplicate(state: AgentState) -> Literal["human_confirmation", "__end__"]:
    """End early if duplicate, otherwise proceed to human confirmation."""
    if state.get("duplicate"):
        return "__end__"
    return "human_confirmation"


def route_after_confirmation(state: AgentState) -> Literal["save_google_sheet", "__end__"]:
    """Only save if user confirmed; otherwise end at interrupt."""
    if state.get("user_confirmed"):
        return "save_google_sheet"
    return "__end__"


def route_after_find_contact(state: AgentState) -> Literal["transcribe_audio", "__end__"]:
    """Stop voice flow if no contact is linked to session."""
    if state.get("contact_id"):
        return "transcribe_audio"
    return "__end__"


def build_agent_graph():
    """Build and compile the visiting card orchestration graph."""
    graph = StateGraph(AgentState)

    # Register all nodes
    graph.add_node("upload_card", nodes.upload_card_node)
    graph.add_node("extract_card_data", nodes.extract_card_data_node)
    graph.add_node("duplicate_check", nodes.duplicate_check_node)
    graph.add_node("human_confirmation", nodes.human_confirmation_node)
    graph.add_node("save_google_sheet", nodes.save_google_sheet_node)
    graph.add_node("save_mongodb", nodes.save_mongodb_node)
    graph.add_node("whatsapp_notification", nodes.whatsapp_notification_node)
    graph.add_node("upload_audio", nodes.upload_audio_node)
    graph.add_node("find_contact_by_session", nodes.find_contact_by_session_node)
    graph.add_node("transcribe_audio", nodes.transcribe_audio_node)
    graph.add_node("update_google_sheet", nodes.update_google_sheet_node)
    graph.add_node("update_mongodb", nodes.update_mongodb_node)

    # Entry routing: card flow vs voice flow
    graph.add_conditional_edges(START, route_entry, {
        "upload_card": "upload_card",
        "upload_audio": "upload_audio",
    })

    # Card flow
    graph.add_edge("upload_card", "extract_card_data")
    graph.add_edge("extract_card_data", "duplicate_check")
    graph.add_conditional_edges("duplicate_check", route_after_duplicate, {
        "human_confirmation": "human_confirmation",
        "__end__": END,
    })
    graph.add_conditional_edges("human_confirmation", route_after_confirmation, {
        "save_google_sheet": "save_google_sheet",
        "__end__": END,
    })
    graph.add_edge("save_google_sheet", "save_mongodb")
    graph.add_edge("save_mongodb", "whatsapp_notification")
    graph.add_edge("whatsapp_notification", END)

    # Voice flow
    graph.add_edge("upload_audio", "find_contact_by_session")
    graph.add_conditional_edges("find_contact_by_session", route_after_find_contact, {
        "transcribe_audio": "transcribe_audio",
        "__end__": END,
    })
    graph.add_edge("transcribe_audio", "update_google_sheet")
    graph.add_edge("update_google_sheet", "update_mongodb")
    graph.add_edge("update_mongodb", END)

    memory = MemorySaver()
    return graph.compile(
        checkpointer=memory,
        interrupt_after=["human_confirmation"],
    )


_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent_graph()
    return _agent


async def run_card_flow(session_id: str, image_path: str) -> dict[str, Any]:
    """Run card upload flow until human confirmation interrupt or completion."""
    agent = get_agent()
    config = {"configurable": {"thread_id": session_id}}
    initial_state: AgentState = {
        "session_id": session_id,
        "flow_type": "card",
        "card_image_path": image_path,
        "card_data": {},
        "contact_id": "",
        "duplicate": False,
        "awaiting_confirmation": False,
        "user_confirmed": False,
        "message": "",
        "messages": [],
    }
    result = await agent.ainvoke(initial_state, config)
    return dict(result)


async def resume_card_flow(session_id: str, confirmed: bool, card_data: dict | None = None) -> dict[str, Any]:
    """Resume graph after human confirmation."""
    agent = get_agent()
    config = {"configurable": {"thread_id": session_id}}

    update: AgentState = {"user_confirmed": confirmed}
    if card_data:
        update["card_data"] = card_data

    await agent.aupdate_state(config, update)
    result = await agent.ainvoke(None, config)
    return dict(result)


async def run_voice_flow(session_id: str, audio_path: str) -> dict[str, Any]:
    """Run voice note upload and transcription flow."""
    agent = get_agent()
    config = {"configurable": {"thread_id": f"{session_id}-voice"}}
    initial_state: AgentState = {
        "session_id": session_id,
        "flow_type": "voice",
        "audio_path": audio_path,
        "audio_url": "",
        "transcript": "",
        "contact_id": "",
        "message": "",
        "messages": [],
    }
    result = await agent.ainvoke(initial_state, config)
    return dict(result)
