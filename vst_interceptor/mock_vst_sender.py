"""Mock VST Sender for testing the PIE Digital Ear IPC.

This simulates a C++ VST plugin that captures audio buffers inside FL Studio
and sends them over UDP to the Python MCP Server.
"""

import socket
import time
import numpy as np

def generate_sine_wave(freq, sample_rate, duration):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio = 0.5 * np.sin(2 * np.pi * freq * t)
    return audio.astype(np.float32)

def main():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 9878
    SAMPLE_RATE = 44100
    BUFFER_SIZE = 512  # Typical audio buffer size

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print(f"Generating 1 second of 440Hz sine wave...")
    audio_data = generate_sine_wave(440.0, SAMPLE_RATE, 1.0)

    print(f"Sending audio buffers to {UDP_IP}:{UDP_PORT}...")

    # Split the audio into buffer chunks and send
    num_buffers = len(audio_data) // BUFFER_SIZE

    for i in range(num_buffers):
        start = i * BUFFER_SIZE
        end = start + BUFFER_SIZE
        chunk = audio_data[start:end]

        # Send raw binary float32 array
        sock.sendto(chunk.tobytes(), (UDP_IP, UDP_PORT))

        # Simulate real-time audio processing (very roughly)
        time.sleep(BUFFER_SIZE / SAMPLE_RATE)

    print("Done sending.")

if __name__ == "__main__":
    main()
