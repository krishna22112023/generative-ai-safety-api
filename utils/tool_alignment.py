from typing import List, Union, Dict, Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage, BaseMessage
from llamafirewall import AssistantMessage, UserMessage, Trace


def _convert_message(msg: Any) -> Union[AssistantMessage, UserMessage, None]:
    """Internal helper to convert a LangChain message into a LlamaFirewall message.

    Args:
        msg: A message instance from ``run_agent_workflow``'s state.

    Returns:
        A corresponding ``AssistantMessage`` or ``UserMessage``. ``None`` is
        returned for message types that do not directly map (e.g. system
        messages) so that they can be filtered out.
    """
    # Support native LangChain message instances
    if isinstance(msg, HumanMessage):
        return UserMessage(content=msg.content)
    if isinstance(msg, AIMessage):
        return AssistantMessage(content=msg.content)
    if isinstance(msg, ToolMessage):
        # Treat a tool response as an assistant message to maintain turn order.
        return AssistantMessage(content=msg.content)

    # Support pre-serialised dict format (e.g. sent over the wire)
    if isinstance(msg, dict):
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "user":
            return UserMessage(content=content)
        if role in ("assistant", "tool"):
            return AssistantMessage(content=content)
        return None

    # System messages or unknown types are omitted from the trace.
    return None


def workflow_result_to_trace(result_state: dict) -> Trace:
    """Convert the ``run_agent_workflow`` result into a LlamaFirewall ``Trace``.

    Example:
        >>> trace = workflow_result_to_trace(run_agent_workflow("Hello"))
        >>> scan_result = run_alignment_check(trace)

    Args:
        result_state: The dictionary returned by ``run_agent_workflow``. It
            must contain the key ``"messages"`` with a list of LangChain
            ``BaseMessage`` instances.

    Returns:
        A ``Trace`` (list of ``AssistantMessage``/``UserMessage``) suitable for
        LlamaFirewall scanners.
    """
    messages: List[BaseMessage] = result_state.get("messages", [])
    lf_messages: List[Union[AssistantMessage, UserMessage]] = []

    for msg in messages:
        converted = _convert_message(msg)
        if converted is not None:
            lf_messages.append(converted)

    # LlamaFirewall defines Trace as a plain list (typing alias), so casting is
    # fine. Returning an empty list would violate the expected format, so we
    # raise for that case to surface misuse early.
    if not lf_messages:
        raise ValueError(
            "No convertible messages found in workflow result. Ensure the state "
            "contains human or AI messages."
        )

    return lf_messages  # type: ignore[return-value] 