from google.genai import types


async def display_state(
    session_service, app_name, user_id, session_id, label="Current State"
):
    """Display the current session state in a formatted way."""
    try:
        session = await session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )

        print(f"\n{'-' * 10} {label} {'-' * 10}")

        user_name = session.state.get("user_name", "Unknown")
        print(f"👤 User: {user_name}")

        research_history = session.state.get("research_history", [])
        if research_history:
            print("🔬 Research History:")
            for idx, entry in enumerate(research_history, 1):
                topic = entry.get("topic", "N/A")
                results = entry.get("results", "")
                preview = results[:100] + "..." if len(results) > 100 else results
                print(f"  {idx}. [{topic}] {preview}")
        else:
            print("🔬 Research History: None")

        print("-" * (22 + len(label)))
    except Exception as e:
        print(f"Error displaying state: {e}")


async def process_agent_response(event):
    """Process and display agent response events."""
    print(f"Event ID: {event.id}, Author: {event.author}")

    if event.content and event.content.parts:
        for part in event.content.parts:
            if hasattr(part, "executable_code") and part.executable_code:
                print(
                    f"  Debug: Agent generated code:\n```python\n{part.executable_code.code}\n```"
                )
            elif hasattr(part, "code_execution_result") and part.code_execution_result:
                print(
                    f"  Debug: Code Execution Result: {part.code_execution_result.outcome} - Output:\n{part.code_execution_result.output}"
                )
            elif hasattr(part, "tool_response") and part.tool_response:
                print(f"  Tool Response: {part.tool_response.output}")
            elif hasattr(part, "text") and part.text and not part.text.isspace():
                print(f"  Text: '{part.text.strip()}'")

    final_response = None
    if event.is_final_response():
        if (
            event.content
            and event.content.parts
            and hasattr(event.content.parts[0], "text")
            and event.content.parts[0].text
        ):
            final_response = event.content.parts[0].text.strip()
            print(
                "═════════════════════════════════════════ AGENT RESPONSE ═════════════════════════════════════════"
            )
            print(
                "╚═════════════════════════════════════════════════════════════\n\n"
            )
        else:
            print(
                "\n═════════════════════════════════════════ ==> Final Agent Response: [No text content in final event]\n\n"
            )

    return final_response


async def call_agent_async(runner, user_id, session_id, query):
    """Call the agent asynchronously with the user's query."""
    content = types.Content(role="user", parts=[types.Part(text=query)])
    print(
        f"\n═════════════════════════════════════════ Running Query: {query} ═════════════════════════════════════════"
    )
    final_response_text = None

    await display_state(
        runner.session_service,
        runner.app_name,
        user_id,
        session_id,
        "State BEFORE processing",
    )

    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            response = await process_agent_response(event)
            if response:
                final_response_text = response
    except Exception as e:
        print(f"Error during agent call: {e}")

    await display_state(
        runner.session_service,
        runner.app_name,
        user_id,
        session_id,
        "State AFTER processing",
    )

    return final_response_text
