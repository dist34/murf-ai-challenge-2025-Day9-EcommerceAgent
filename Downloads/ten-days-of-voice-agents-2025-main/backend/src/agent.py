# ======================================================
# DAY 4: TEACH-THE-TUTOR (CODING EDITION)
# Features: Variables, Loops, Active Recall
# ======================================================

import logging
import json
import os
from typing import Annotated, Literal, Optional
from dataclasses import dataclass

from dotenv import load_dotenv
from pydantic import Field
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    WorkerOptions,
    cli,
    function_tool,
    RunContext,
)

from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")
load_dotenv(".env.local")

# ======================================================
# CONTENT FILE
# ======================================================

CONTENT_FILE = "coding_content.json"

DEFAULT_CONTENT = [
    {
        "id": "variables",
        "title": "Variables",
        "summary": "Variables store values so you can reuse them later. They have a name (identifier) and a value. You can assign, read, and update them.",
        "sample_question": "What is a variable and why is it useful?"
    },
    {
        "id": "loops",
        "title": "Loops",
        "summary": "Loops let you repeat an action multiple times. A for-loop iterates over a known range or collection; a while-loop repeats until a condition changes.",
        "sample_question": "Explain the difference between a for loop and a while loop."
    }
]


def load_content():
    """Generate JSON file if missing, otherwise load it."""
    try:
        path = os.path.join(os.path.dirname(__file__), CONTENT_FILE)

        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONTENT, f, indent=4)

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        print(f"Error loading content file: {e}")
        return []


COURSE_CONTENT = load_content()

# ======================================================
# STATE MANAGEMENT
# ======================================================

@dataclass
class TutorState:
    current_topic_id: str | None = None
    current_topic_data: dict | None = None
    mode: Literal["learn", "quiz", "teach_back"] = "learn"

    def set_topic(self, topic_id: str):
        topic = next((item for item in COURSE_CONTENT if item["id"] == topic_id), None)
        if topic:
            self.current_topic_id = topic_id
            self.current_topic_data = topic
            return True
        return False


@dataclass
class Userdata:
    tutor_state: TutorState
    agent_session: Optional[AgentSession] = None

# ======================================================
# TOOLS
# ======================================================

@function_tool
async def select_topic(
    ctx: RunContext[Userdata],
    topic_id: Annotated[str, Field(description="Topic ID (variables, loops)")]
) -> str:
    state = ctx.userdata.tutor_state
    success = state.set_topic(topic_id.lower())

    if success:
        return f"Topic set to {state.current_topic_data['title']}. Ask if the user wants to Learn, take a Quiz, or Teach Back."
    else:
        available = ", ".join([t["id"] for t in COURSE_CONTENT])
        return f"Invalid topic. Available topics: {available}"


@function_tool
async def set_learning_mode(
    ctx: RunContext[Userdata],
    mode: Annotated[str, Field(description="learn, quiz, teach_back")]
) -> str:
    state = ctx.userdata.tutor_state
    state.mode = mode.lower()

    agent_session = ctx.userdata.agent_session

    if agent_session:
        if state.mode == "learn":
            agent_session.tts.update_options(voice="en-US-matthew", style="Promo")
            instruction = f"Explain: {state.current_topic_data['summary']}"

        elif state.mode == "quiz":
            agent_session.tts.update_options(voice="en-US-alicia", style="Conversational")
            instruction = f"Ask: {state.current_topic_data['sample_question']}"

        elif state.mode == "teach_back":
            agent_session.tts.update_options(voice="en-US-ken", style="Promo")
            instruction = "Ask the user to explain the concept in their own words."

        else:
            return "Invalid mode."

    else:
        instruction = "Session not found."

    return f"Switched to {state.mode}. {instruction}"


@function_tool
async def evaluate_teaching(
    ctx: RunContext[Userdata],
    user_explanation: Annotated[str, Field(description="User's explanation")]
) -> str:
    return "Evaluate the explanation, score out of 10, and correct misunderstandings."

# ======================================================
# AGENT
# ======================================================

class TutorAgent(Agent):
    def __init__(self):
        topic_list = ", ".join([f"{t['id']} ({t['title']})" for t in COURSE_CONTENT])

        super().__init__(
            instructions=f"""
            You are a programming tutor for Day 4 (Teach-the-Tutor).

            Topics available: {topic_list}

            Modes:
            - LEARN (Voice: Matthew): Explain the topic.
            - QUIZ (Voice: Alicia): Ask the quiz question.
            - TEACH_BACK (Voice: Ken): Ask the user to teach it back.

            Behavior:
            - First, ask which topic the user wants to study.
            - Use tools immediately when the user asks to switch mode.
            - In teach_back mode, call evaluate_teaching after the user explains.
            """,
            tools=[select_topic, set_learning_mode, evaluate_teaching],
        )

# ======================================================
# ENTRYPOINT
# ======================================================

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

    userdata = Userdata(tutor_state=TutorState())

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew",
            style="Promo",
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        userdata=userdata,
    )

    userdata.agent_session = session

    await session.start(
        agent=TutorAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
