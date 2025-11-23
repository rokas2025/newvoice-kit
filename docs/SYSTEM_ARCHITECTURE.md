# Lithuanian Voice Agent - System Architecture

## Overview
Real-time Lithuanian voice AI assistant using LiveKit Agents framework with Knowledge Base about Lithuania.

## Tech Stack

### Backend (Python Agent)
- **Framework:** LiveKit Agents v1.3.3
- **Python:** 3.13
- **Deployment:** LiveKit Cloud
- **Package Manager:** pip

### STT (Speech-to-Text)
- **Provider:** ElevenLabs Scribe v2 Realtime
- **Language:** Lithuanian (lt)
- **Mode:** Streaming WebSocket
- **Latency:** ~500-1000ms

### LLM (Language Model)
- **Provider:** OpenAI
- **Model:** gpt-5-nano
- **Context:** 400K tokens
- **Cost:** $0.05/1M input tokens, $0.40/1M output tokens
- **Features:** Streaming responses, hardcoded Knowledge Base
- **Latency:** ~1000-2000ms

### TTS (Text-to-Speech)
- **Provider:** ElevenLabs
- **Model:** eleven_v3 (highest quality)
- **Voice:** Arabella (ID: Z3R5wn05IrDiVCyEkUrK)
- **Language:** Lithuanian (lt)
- **Mode:** Non-streaming (wrapped with StreamAdapter)
- **Latency:** ~500-1000ms

### Frontend
- **Framework:** Next.js 15.5.2 (React 19)
- **LiveKit SDK:** @livekit/components-react v2.x
- **Deployment:** Vercel
- **Features:** 
  - Real-time chat transcript (always visible)
  - Performance stats overlay (STT/LLM/TTS timing)
  - Voice activity detection
  - Audio controls

## Knowledge Base

**Location:** `backend/src/agent.py` (KNOWLEDGE_BASE constant)

**Type:** Hardcoded Lithuanian information

**Content:** Information about Lithuania:
- Basic facts (capital, language, currency, national holiday)
- Geography and neighbors
- 3 largest cities (Vilnius, Kaunas, Klaipeda)
- Tourist attractions (Trakai Castle, Hill of Crosses, Curonian Spit, Vilnius Old Town)
- Culture and cuisine (Cepelinai, Saltibarsciai, Kugelis, Jonines)

**Behavior:** Agent responds ONLY based on Knowledge Base. If information is not in KB, responds: "Atsiprašau, šioje knowledge base neturiu informacijos apie tai."

## Environment Variables

### Backend (backend/.env)
```bash
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxx
LIVEKIT_API_SECRET=secretxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxx
ELEVEN_API_KEY=sk_xxxxxxxxxx
```

### Frontend (frontend/.env.local)
```bash
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxx
LIVEKIT_API_SECRET=secretxxxxxxxxxx
```

**Note:** Same LiveKit credentials for both backend and frontend.

## Project Structure

```
lithuanian-voice-agent/
├── backend/                    # Python agent
│   ├── src/
│   │   ├── __init__.py
│   │   └── agent.py           # Main agent logic with KB
│   ├── tests/
│   │   └── test_agent.py      # Behavioral tests
│   ├── pyproject.toml         # Python dependencies
│   ├── Dockerfile             # For LiveKit Cloud deployment
│   ├── .env                   # Backend environment variables
│   └── README.md
│
├── frontend/                   # React UI
│   ├── app/
│   │   ├── (app)/
│   │   │   └── page.tsx       # Main app page
│   │   └── api/
│   │       └── connection-details/
│   │           └── route.ts   # LiveKit token generation
│   ├── components/
│   │   ├── app/
│   │   │   ├── session-view.tsx  # Main session view (with stats)
│   │   │   └── chat-transcript.tsx
│   │   └── livekit/           # LiveKit components
│   ├── app-config.ts          # App configuration (agentName: '')
│   ├── package.json           # JS dependencies
│   ├── .env.local             # Frontend environment variables
│   └── README.md
│
├── docs/
│   └── SYSTEM_ARCHITECTURE.md # This file
│
├── .gitignore
├── README.md                   # Main project README
└── vercel.json                # Vercel deployment config
```

## Architecture Diagram

```
┌─────────────────────┐
│   User (Browser)    │
│   localhost:3001    │
└──────────┬──────────┘
           │ WebRTC
           ↓
┌─────────────────────┐
│   LiveKit Cloud     │
│   (SFU Server)      │
└──────────┬──────────┘
           │ Agent Protocol
           ↓
┌─────────────────────┐
│  Python Agent       │
│  (Your Backend)     │
└──────────┬──────────┘
           │
    ┌──────┴──────┬──────────┬──────────┐
    ↓             ↓          ↓          ↓
┌────────┐  ┌─────────┐ ┌────────┐ ┌────────┐
│ ElevenLabs │ OpenAI   │ ElevenLabs │ Silero│
│ STT (WS)   │ GPT-5    │ TTS v3     │ VAD   │
│ Scribe v2  │ Nano     │ Arabella   │       │
└────────┘  └─────────┘ └────────┘ └────────┘
```

## Performance Metrics (Average)

- **STT latency:** 500-1000ms
- **LLM latency:** 1000-2000ms (depends on response length)
- **TTS latency:** 500-1000ms
- **Total response time:** 2-4 seconds (from user speech end to agent speech start)

**Logged in terminal with timestamps for each phase.**

## Deployment

### Backend (Python Agent)
**Platform:** LiveKit Cloud

**Steps:**
1. Ensure `backend/.env` has all required keys
2. From `backend/` directory:
   ```powershell
   python src/agent.py dev      # Local testing
   python src/agent.py start    # Production (LiveKit Cloud handles deployment)
   ```

### Frontend (React UI)
**Platform:** Vercel

**Steps:**
1. Push monorepo to GitHub
2. Connect repository to Vercel
3. Set **Root Directory** to `frontend`
4. Add environment variables in Vercel dashboard:
   - `LIVEKIT_URL`
   - `LIVEKIT_API_KEY`
   - `LIVEKIT_API_SECRET`
5. Deploy

**Vercel Config:** See `vercel.json` in root

## Local Development

### Terminal 1 (Backend):
```powershell
cd backend
python src/agent.py dev
```

### Terminal 2 (Frontend):
```powershell
cd frontend
npm run dev
```

**Access:** http://localhost:3001

### Testing Knowledge Base:
Ask questions about Lithuania:
- "Kokia Lietuvos sostinė?"
- "Kur yra Trakų pilis?"
- "Kas yra cepelinai?"
- "Su kuo ribojasi Lietuva?"

Ask questions outside KB (should refuse):
- "Koks oras Paryžiuje?" → "Atsiprašau, šioje knowledge base..."

## Version History

- **v1.0.0** (2025-11-23)
  - Initial implementation
  - GPT-5 Nano LLM
  - ElevenLabs STT (Scribe v2) + TTS (v3, Arabella)
  - Hardcoded Knowledge Base about Lithuania
  - Performance timing stats
  - Chat transcript always visible
  - Monorepo structure

## Future Enhancements (TODOs in code)

- RAG integration with Supabase for dynamic knowledge base
- Function tools for business-specific actions
- Enable `allow_interruptions=True` after testing v3 TTS latency
- SIP trunk configuration for telephony support
- Vector search for larger knowledge bases
- Multi-language support (currently Lithuanian only)

## Troubleshooting

### Agent not joining room
- Check `agentName: ''` in `frontend/app-config.ts`
- Verify backend agent is running (`python src/agent.py dev`)
- Check LiveKit credentials match in both .env files

### Unicode errors in logs
- Ensure no emoji in logger.info() calls
- Windows PowerShell uses cp1257 encoding

### TTS timeout errors
- ElevenLabs v3 is non-streaming, may take 1-2 seconds
- Check `ELEVEN_API_KEY` is set correctly

## Support & Documentation

- LiveKit Docs: https://docs.livekit.io
- LiveKit Agents: https://docs.livekit.io/agents
- ElevenLabs API: https://elevenlabs.io/docs
- OpenAI API: https://platform.openai.com/docs

