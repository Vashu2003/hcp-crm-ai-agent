"""LangGraph agent: a StateGraph that routes natural-language chat to the 5 tools.

Flow:  START -> llm -> (tools? -> back to llm : END)
The LLM node is ChatGroq bound to the 5 tools; a ToolNode executes any tool
calls, then control loops back to the LLM until it produces a final answer.
"""

from datetime import date
from functools import lru_cache

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.errors import GraphRecursionError

from app.agent.llm import get_llm
from app.agent.tools import ALL_TOOLS
from app.agent.prompts import SYSTEM_PROMPT


@lru_cache(maxsize=1)
def get_graph():
    """Build and compile the agent graph once."""
    llm_with_tools = get_llm().bind_tools(ALL_TOOLS)

    def llm_node(state: MessagesState):
        system = SystemMessage(
            content=SYSTEM_PROMPT + f"\n\nToday's date is {date.today().isoformat()}."
        )
        response = llm_with_tools.invoke([system] + state["messages"])
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("llm", llm_node)
    graph.add_node("tools", ToolNode(ALL_TOOLS))
    graph.add_edge(START, "llm")
    graph.add_conditional_edges("llm", tools_condition)  # -> "tools" or END
    graph.add_edge("tools", "llm")
    return graph.compile()


def run_agent(message: str, history: list[dict] | None = None) -> dict:
    """Run one chat turn through the agent. Returns {reply, tool_calls}."""
    messages = []
    for turn in history or []:
        role = turn.get("role")
        content = turn.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    messages.append(HumanMessage(content=message))

    # Stream so that, if the model loops on a tool (hitting the recursion limit) or the
    # Groq API errors mid-run, we still keep the last state and fall back gracefully.
    out_messages: list = []
    error: Exception | None = None
    try:
        for state in get_graph().stream(
            {"messages": messages}, {"recursion_limit": 8}, stream_mode="values"
        ):
            out_messages = state["messages"]
    except GraphRecursionError:
        pass  # model looped; fall back to the last tool result below
    except Exception as exc:  # e.g. Groq rate limit / malformed tool call
        error = exc

    # Collect the names of tools that were invoked this turn (for UI transparency).
    tool_calls = []
    for m in out_messages:
        for tc in getattr(m, "tool_calls", None) or []:
            name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
            if name and name not in tool_calls:
                tool_calls.append(name)

    # Prefer the model's final natural-language answer; if it never produced one
    # (e.g. it looped on a tool), fall back to the most recent tool result.
    reply = ""
    for m in reversed(out_messages):
        if isinstance(m, AIMessage) and isinstance(m.content, str) and m.content.strip():
            reply = m.content
            break
    if not reply:
        for m in reversed(out_messages):
            if isinstance(m, ToolMessage) and isinstance(m.content, str) and m.content.strip():
                reply = m.content
                break
    if not reply:
        reply = (
            "Sorry — I hit a problem handling that request. Please rephrase, or try the "
            "structured Form for logging."
            if error
            else "I'm not sure how to help with that. Try asking me to log, search, "
            "schedule a follow-up, or summarize interactions."
        )
    return {"reply": reply, "tool_calls": tool_calls}
