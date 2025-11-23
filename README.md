# Lithuanian Voice Agent

Real-time Lithuanian voice AI assistant built with LiveKit Agents, featuring a Knowledge Base about Lithuania.

## Features

- Real-time voice conversation in Lithuanian
- Speech-to-Text using ElevenLabs Scribe v2
- LLM powered by OpenAI GPT-5 Nano
- Text-to-Speech using ElevenLabs v3 (Arabella voice)
- Hardcoded Knowledge Base about Lithuania (geography, culture, cities, attractions)
- Performance statistics (STT/LLM/TTS timing displayed in UI)
- Always-visible chat transcript

## Quick Start

### Prerequisites

- Python 3.13
- Node.js 18+
- LiveKit Cloud account (free tier available)
- OpenAI API key
- ElevenLabs API key

### 1. Clone Repository

```powershell
git clone https://github.com/YOUR_USERNAME/lithuanian-voice-agent.git
cd lithuanian-voice-agent
```

### 2. Backend Setup

```powershell
cd backend

# Install dependencies
pip install -e .

# Create .env file with your keys
# LIVEKIT_URL=wss://your-project.livekit.cloud
# LIVEKIT_API_KEY=APIxxxxxxxxxx
# LIVEKIT_API_SECRET=secretxxxxxxxxxx
# OPENAI_API_KEY=sk-xxxxxxxxxx
# ELEVEN_API_KEY=sk_xxxxxxxxxx

# Run agent locally
python src/agent.py dev
```

### 3. Frontend Setup

Open a new terminal:

```powershell
cd frontend

# Install dependencies
npm install

# Create .env.local file with LiveKit credentials
# LIVEKIT_URL=wss://your-project.livekit.cloud
# LIVEKIT_API_KEY=APIxxxxxxxxxx
# LIVEKIT_API_SECRET=secretxxxxxxxxxx

# Run development server
npm run dev
```

### 4. Test

Open your browser at **http://localhost:3001**

- Click "Start call"
- Allow microphone access
- Start speaking in Lithuanian!

Try asking about Lithuania:
- "Kokia Lietuvos sostinė?"
- "Kur yra Trakų pilis?"
- "Kas yra cepelinai?"

## Project Structure

```
lithuanian-voice-agent/
├── backend/          # Python agent with LiveKit Agents
├── frontend/         # Next.js React UI
├── docs/            # Documentation
│   └── SYSTEM_ARCHITECTURE.md
├── README.md        # This file
└── vercel.json      # Vercel deployment config
```

## Deployment

### Backend (LiveKit Cloud)

The Python agent runs on LiveKit Cloud automatically when you start it in dev/production mode.

### Frontend (Vercel)

1. Push repository to GitHub
2. Connect to Vercel
3. Set root directory to `frontend`
4. Add environment variables in Vercel dashboard
5. Deploy

See `docs/SYSTEM_ARCHITECTURE.md` for detailed deployment instructions.

## Knowledge Base

The agent has information about:
- Lithuania basics (capital, language, currency)
- Geography and neighboring countries
- 3 largest cities
- Tourist attractions (Trakai Castle, Hill of Crosses, etc.)
- Traditional cuisine (Cepelinai, Saltibarsciai, Kugelis)

If you ask about topics outside the Knowledge Base, the agent will politely decline.

## Performance

Average response times:
- STT: 500-1000ms
- LLM: 1000-2000ms
- TTS: 500-1000ms
- **Total: 2-4 seconds**

Performance statistics are displayed in real-time in the UI overlay.

## Tech Stack

- **Backend:** Python 3.13, LiveKit Agents 1.3.3
- **Frontend:** Next.js 15, React 19, LiveKit Components
- **STT:** ElevenLabs Scribe v2 (Lithuanian)
- **LLM:** OpenAI GPT-5 Nano
- **TTS:** ElevenLabs v3, Arabella voice (Lithuanian)
- **Infrastructure:** LiveKit Cloud + Vercel

## Documentation

See `docs/SYSTEM_ARCHITECTURE.md` for:
- Detailed architecture
- Component specifications
- Deployment guides
- Troubleshooting

## License

MIT

## Contributing

Contributions are welcome! Please open an issue or pull request.

## Support

For issues or questions:
- Check `docs/SYSTEM_ARCHITECTURE.md`
- Open a GitHub issue
- LiveKit Docs: https://docs.livekit.io

