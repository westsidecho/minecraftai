"""
Voice Listener for Minecraft AI Friends
Captures microphone input, transcribes with OpenAI Whisper, sends to bots.

Hold V to talk, release to send your message to Max & Luna.
"""

import json
import sys
import os
import tempfile
import wave
import struct
import math
import time

try:
    import pyaudio
except ImportError:
    print("ERROR: pyaudio not installed. Run: pip install pyaudio")
    sys.exit(1)

try:
    import keyboard
except ImportError:
    print("ERROR: keyboard not installed. Run: pip install keyboard")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    sys.exit(1)

try:
    import socketio
except ImportError:
    print("ERROR: python-socketio not installed. Run: pip install python-socketio[client]")
    sys.exit(1)

# Load API key from keys.json
script_dir = os.path.dirname(os.path.abspath(__file__))
keys_path = os.path.join(script_dir, "keys.json")
with open(keys_path, "r") as f:
    keys = json.load(f)

OPENAI_API_KEY = keys.get("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    print("ERROR: OPENAI_API_KEY not set in keys.json")
    sys.exit(1)

# Settings
MINDSERVER_PORT = 8080
PLAYER_NAME = "VoicePlayer"

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
SILENCE_THRESHOLD = 500       # volume level below this = silence
SILENCE_DURATION = 1.0        # seconds of silence before auto-sending
MIN_AUDIO_CHUNKS = 10         # minimum chunks to count as speech (~0.6s)


def get_volume(data):
    """Calculate RMS volume of audio chunk."""
    count = len(data) // 2
    shorts = struct.unpack(f"{count}h", data)
    sum_squares = sum(s * s for s in shorts)
    rms = math.sqrt(sum_squares / count) if count > 0 else 0
    return rms


def transcribe_audio(audio_file_path):
    """Send audio to OpenAI Whisper API for transcription."""
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}

    with open(audio_file_path, "rb") as f:
        files = {"file": ("audio.wav", f, "audio/wav")}
        data = {"model": "whisper-1", "language": "en"}
        response = requests.post(url, headers=headers, files=files, data=data)

    if response.status_code == 200:
        return response.json().get("text", "").strip()
    else:
        print(f"  Whisper API error: {response.status_code}")
        return None


def send_to_bots(sio, message, bot_names):
    """Send transcribed message to all bots via MindServer."""
    for bot_name in bot_names:
        try:
            sio.emit("send-message", (bot_name, {
                "from": PLAYER_NAME,
                "message": message
            }))
        except Exception as e:
            print(f"  Error sending to {bot_name}: {e}")


def save_audio(frames, sample_width):
    """Save recorded audio frames to a temporary WAV file."""
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    wf = wave.open(tmp.name, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()
    return tmp.name


def main():
    print("==========================================")
    print("  Minecraft Voice Chat")
    print("==========================================")
    print()
    print("  [V] = Hold to talk, release to send")
    print("  [Q] = Quit")
    print()
    print("  Connecting to MindServer...")

    # Connect to MindServer
    sio = socketio.Client()
    bot_names = ["Max", "Luna"]

    try:
        sio.connect(f"http://localhost:{MINDSERVER_PORT}")
        print("  Connected!")
    except Exception as e:
        print(f"  Could not connect to MindServer: {e}")
        print("  Make sure START.bat bots are running first!")
        input("  Press Enter to exit...")
        sys.exit(1)

    # Setup audio
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
    )
    sample_width = pa.get_sample_size(FORMAT)

    audio_frames = []
    v_was_pressed = False
    recording = False

    print()
    print("  Ready! Hold [V] to talk, release to send.")
    print()

    try:
        while True:
            # Check quit
            if keyboard.is_pressed("q"):
                print("\n  Quitting...")
                break

            v_pressed = keyboard.is_pressed("v")

            # V key just pressed - start recording
            if v_pressed and not v_was_pressed:
                recording = True
                audio_frames = []
                print("  ** RECORDING ** - Release [V] to send.")

            # V key just released - stop recording and send
            if not v_pressed and v_was_pressed and recording:
                recording = False
                if len(audio_frames) > MIN_AUDIO_CHUNKS:
                    print("  [Processing...]")
                    wav_path = save_audio(audio_frames, sample_width)
                    text = transcribe_audio(wav_path)
                    os.unlink(wav_path)
                    if text:
                        print(f'  You: "{text}"')
                        send_to_bots(sio, text, bot_names)
                    else:
                        print("  (Could not understand)")
                else:
                    print("  (Too short, ignored)")
                audio_frames = []
                print("  Ready! Hold [V] to talk.")

            v_was_pressed = v_pressed

            if recording:
                # Record audio while V is held
                data = stream.read(CHUNK, exception_on_overflow=False)
                audio_frames.append(data)
            else:
                # Drain mic buffer to avoid buildup
                try:
                    stream.read(CHUNK, exception_on_overflow=False)
                except:
                    pass
                time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n  Quitting...")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        sio.disconnect()


if __name__ == "__main__":
    main()
