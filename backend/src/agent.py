import logging
import time

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    room_io,
    tts as tts_module,
)
from livekit.agents.tokenize import basic
from livekit.plugins import elevenlabs, noise_cancellation, openai, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env")

# Knowledge Base - Lithuanian Information
KNOWLEDGE_BASE = """
TESTINIS KNOWLEDGE BASE (LT) — „Lietuva: trumpas gidas"

KB_1. Pagrindiniai faktai
Lietuva yra valstybė Baltijos regione, Šiaurės Europoje.
Sostinė: Vilnius.
Valstybinė kalba: lietuvių.
Valiuta: euras (EUR).
Valstybės šventė: Vasario 16-oji – Lietuvos valstybės atkūrimo diena.
Oficialus interneto domenas: .lt.

KB_2. Geografija ir kaimynai
Lietuva ribojasi su Latvija (šiaurėje), Baltarusija (rytuose ir pietryčiuose), Lenkija (pietuose) ir Rusijos Kaliningrado sritimi (vakaruose).
Vakaruose Lietuvą skalauja Baltijos jūra.
Didžiausia Lietuvos upė yra Nemunas.

KB_3. 3 didžiausi miestai (pagal gyventojų skaičių)
Vilnius – sostinė.
Kaunas – antras pagal dydį miestas, laikinasis sostinės statusas tarpukariu.
Klaipėda – pagrindinis jūrų uostas.

KB_4. Lankytinos vietos
Trakų pilis – salos pilis Galvės ežere netoli Vilniaus.
Kryžių kalnas (netoli Šiaulių) – piligriminė vieta su tūkstančiais kryžių.
Kuršių nerija – UNESCO saugomas pusiasalis su kopomis ir pušynais.
Vilniaus senamiestis – vienas didžiausių Rytų Europoje, UNESCO paveldas.

KB_5. Kultūra ir virtuvė
Tradiciniai lietuviški patiekalai:
Cepelinai – bulviniai kukuliai su mėsos ar varškės įdaru.
Šaltibarščiai – šaltas burokėlių ir kefyro sriubos patiekalas, dažnai su bulvėmis.
Kugelis – keptas bulvių plokštainis.
Populiari vasaros šventė: Joninės (birželio 24 d.) – Rasos šventė.
"""


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=f"""Tu esi draugiškas lietuviškai kalbantis AI asistentas apie Lietuvą.

SVARBU: Atsakinėk TIK remdamasis šia informacija:
{KNOWLEDGE_BASE}

Jei klausimas nėra apie šią informaciją, atsakyk: "Atsiprašau, šioje knowledge base neturiu informacijos apie tai."

Tavo atsakymai yra glaūsti, aiškūs ir be sudėtingo formatavimo ar skyrybos ženklų, įskaitant emocijų ženklelius, žvaigždutes ar kitus simbolius.
Esi draugiškas, mandagus ir profesionalus.""",
        )

    # To add tools, use the @function_tool decorator.
    # Here's an example that adds a simple weather tool.
    # You also have to add `from livekit.agents import function_tool, RunContext` to the top of this file
    # @function_tool
    # async def lookup_weather(self, context: RunContext, location: str):
    #     """Use this tool to look up current weather information in the given location.
    #
    #     If the location is not supported by the weather service, the tool will indicate this. You must tell the user the location's weather is unavailable.
    #
    #     Args:
    #         location: The location to look up weather information for (e.g. city name)
    #     """
    #
    #     logger.info(f"Looking up weather for {location}")
    #
    #     return "sunny with a temperature of 70 degrees."


# TODO: Add RAG integration with Supabase for knowledge base
# TODO: Add function tools for business-specific actions
# TODO: Enable allow_interruptions=True after testing v3 TTS latency
# TODO: Add SIP trunk configuration for telephony support

server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session()
async def my_agent(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a Lithuanian voice AI pipeline with ElevenLabs STT/TTS and OpenAI LLM
    session = AgentSession(
        # Speech-to-text: ElevenLabs Scribe with Lithuanian language support
        stt=elevenlabs.STT(language_code="lt"),
        # Large Language Model: OpenAI GPT-5 Nano with streaming (fastest & cheapest GPT-5)
        llm=openai.LLM(model="gpt-5-nano"),
        # Text-to-speech: ElevenLabs v3 with Arabella voice (Lithuanian)
        # Using StreamAdapter to force non-streaming mode (v3 doesn't support WebSocket streaming)
        tts=tts_module.StreamAdapter(
            tts=elevenlabs.TTS(
                model="eleven_v3",  # v3 model - highest quality
                voice_id="Z3R5wn05IrDiVCyEkUrK",  # Arabella voice
                language="lt",  # Lithuanian language
            ),
            sentence_tokenizer=basic.SentenceTokenizer(),
        ),
        # Turn detection and VAD for Lithuanian
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # Disable interruptions for MVP (v3 TTS is non-streaming)
        allow_interruptions=False,
        # Disable preemptive generation since we can't interrupt
        preemptive_generation=False,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony()
                if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                else noise_cancellation.BVC(),
            ),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()

    # Timing tracking variables
    stt_start_time = None
    llm_start_time = None
    tts_start_time = None

    # Add event listeners for logging STT/TTS activity with timing
    @session.on("user_started_speaking")
    def on_user_started():
        nonlocal stt_start_time
        stt_start_time = time.time()
        logger.info("STT: User started speaking...")

    @session.on("user_speech_committed")
    def on_user_speech(msg):
        nonlocal llm_start_time
        stt_duration = (time.time() - stt_start_time) * 1000 if stt_start_time else 0
        logger.info(f"STT (User said): {msg.text} | Duration: {stt_duration:.0f}ms")
        llm_start_time = time.time()
    
    @session.on("agent_speech_committed")
    def on_agent_speech(msg):
        nonlocal tts_start_time
        llm_duration = (time.time() - llm_start_time) * 1000 if llm_start_time else 0
        logger.info(f"LLM Response: {msg.text} | Duration: {llm_duration:.0f}ms")
        tts_start_time = time.time()
    
    @session.on("agent_started_speaking")
    def on_agent_started():
        logger.info("TTS: Started synthesizing speech...")

    @session.on("agent_stopped_speaking")
    async def on_agent_stopped():
        tts_duration = (time.time() - tts_start_time) * 1000 if tts_start_time else 0
        total_duration = (time.time() - stt_start_time) * 1000 if stt_start_time else 0
        stt_dur = (stt_start_time and llm_start_time) and (llm_start_time - stt_start_time) * 1000 or 0
        llm_dur = (llm_start_time and tts_start_time) and (tts_start_time - llm_start_time) * 1000 or 0
        
        logger.info(f"TTS Duration: {tts_duration:.0f}ms | TOTAL: {total_duration:.0f}ms")
        
        # Send stats via data channel
        stats_msg = f"[STATS] STT:{stt_dur:.0f}ms LLM:{llm_dur:.0f}ms TTS:{tts_duration:.0f}ms TOTAL:{total_duration:.0f}ms"
        await ctx.room.local_participant.publish_data(
            stats_msg.encode('utf-8'),
            topic="lk-chat-topic"
        )

    # Send Lithuanian greeting
    logger.info("Sending greeting to user...")
    await session.say("Sveiki! Aš esu jūsų AI asistentas. Kaip galiu jums padėti?", allow_interruptions=False)


if __name__ == "__main__":
    cli.run_app(server)
