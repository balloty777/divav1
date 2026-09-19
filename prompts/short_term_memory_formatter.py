from memory.short_term_memory import ShortTermMemory


def format_stm(stm: ShortTermMemory) -> str:
    lines = []

    if stm.current_situation:
        lines.append(f"Current Situation:\n{stm.current_situation}")

    if stm.current_location:
        lines.append(
            f"Current Location:\n{stm.current_location}"
        )

    if stm.current_goal:
        lines.append(
            f"Current Goal:\n{stm.current_goal}"
        )

    if stm.important_events:
        lines.append(
            "Recent Important Events:\n- "
            + "\n- ".join(stm.important_events)
        )

    if stm.relationship_updates:
        lines.append(
            "Relationship Updates:\n- "
            + "\n- ".join(stm.relationship_updates)
        )

    if stm.emotional_context:
        lines.append(
            "Current Emotional Context:\n- "
            + "\n- ".join(stm.emotional_context)
        )

    if stm.active_topics:
        lines.append(
            "Active Conversation Topics:\n- "
            + "\n- ".join(stm.active_topics)
        )

    if stm.unresolved_threads:
        lines.append(
            "Things Still Unresolved:\n- "
            + "\n- ".join(stm.unresolved_threads)
        )

    return "\n\n".join(lines)