import asyncio
import os
from dotenv import load_dotenv
from livekit import api

async def make_outbound_call():
    # Load credentials from .env
    load_dotenv('.env')
    
    lk_api = api.LiveKitAPI(
        url=os.getenv('LIVEKIT_URL'),
        api_key=os.getenv('LIVEKIT_API_KEY'),
        api_secret=os.getenv('LIVEKIT_API_SECRET')
    )
    
    print("Initiating outbound call to +37069309397...")
    
    try:
        # Create SIP participant (outbound call)
        result = await lk_api.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                sip_trunk_id="ST_A8MNPDNxqzty",  # Your outbound trunk
                sip_call_to="+37069309397",      # Target phone number
                room_name="test-outbound-call",   # The room we created
            )
        )
        
        print(f"✅ Call initiated successfully!")
        print(f"   Participant ID: {result.participant_id}")
        print(f"   SIP Call ID: {result.sip_call_id}")
        print(f"\nYou should receive a call shortly...")
        print(f"The voice agent will speak to you in Lithuanian!")
        
    except Exception as e:
        print(f"❌ Error initiating call: {e}")
    
    await lk_api.aclose()

if __name__ == "__main__":
    asyncio.run(make_outbound_call())

