import asyncio

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from agents.agent import root_agent
from agents.utils import call_agent_async

load_dotenv()

# Persistent session storage via SQLite
db_url = "sqlite+aiosqlite:///./research_data.db"
session_service = DatabaseSessionService(db_url=db_url)

# Initial state for new sessions
initial_state = {
    "user_name": "Researcher",
    "research_history": [],
}


async def main_async():
    APP_NAME = "Research Agent"
    USER_ID = "user001"

    # Check for existing sessions
    existing_sessions = await session_service.list_sessions(
        app_name=APP_NAME,
        user_id=USER_ID,
    )

    if existing_sessions and len(existing_sessions.sessions) > 0:
        SESSION_ID = existing_sessions.sessions[0].id
        print(f"Continuing existing session: {SESSION_ID}")
    else:
        new_session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            state=initial_state,
        )
        SESSION_ID = new_session.id
        print(f"Created new session: {SESSION_ID}")

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    print("\nWelcome to Research Agent!")
    print("Your research history will be remembered across conversations.")
    print("Type 'exit' or 'quit' to end.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Ending conversation. Your research has been saved.")
            break
        await call_agent_async(runner, USER_ID, SESSION_ID, user_input)


if __name__ == "__main__":
    asyncio.run(main_async())
