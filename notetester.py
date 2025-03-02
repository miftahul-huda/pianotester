import numpy as np
import sounddevice as sd
import scipy.signal as signal
from scipy.fft import fft, fftfreq
import argparse


def detect_tone(duration=1, samplerate=44100, threshold=0.01):
    """
    Listens to audio and attempts to detect the dominant frequency (tone) and convert it to a musical note.

    Args:
        duration (float): Recording duration in seconds.
        samplerate (int): Sampling rate in Hz.
        threshold (float): Amplitude threshold for detecting a tone.

    Returns:
        tuple: (frequency, note_name) or (None, None) if no tone detected.
    """
    try:
        print("Listening...")
        audio_data = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, blocking=True)
        audio_data = audio_data.flatten()

        window = signal.windows.hann(len(audio_data))
        windowed_data = audio_data * window

        yf = fft(windowed_data)
        xf = fftfreq(len(windowed_data), 1 / samplerate)

        magnitude_spectrum = np.abs(yf)
        positive_frequencies = xf[:len(xf) // 2]
        positive_magnitude = magnitude_spectrum[:len(magnitude_spectrum) // 2]

        max_magnitude = np.max(positive_magnitude)
        if max_magnitude > threshold:
            dominant_frequency = positive_frequencies[np.argmax(positive_magnitude)]
            note_name, octave = frequency_to_note(dominant_frequency)
            return dominant_frequency, note_name, octave
        else:
            return None, None, None

    except Exception as e:
        print(f"Error: {e}")
        return None, None

def frequency_to_note(frequency):
    """Converts a frequency to its closest musical note."""
    A4 = 440.0
    C0 = A4 * pow(2, -4.75)
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    if frequency <= 0:
        return "Invalid Frequency"

    h = round(12 * np.log2(frequency / C0))
    octave = h // 12
    note = h % 12

    return f"{note_names[note]}", octave

def generate_random_note():
    """Generates a random musical note."""
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    note = np.random.choice(note_names)
    octave = np.random.randint(2, 6)
    return note, octave


if __name__ == "__main__":
    using_octave = False
    parser = argparse.ArgumentParser(description="Process audio with an optional octave argument.")
    parser.add_argument("--octave", help="Specify the octave (optional).")

    args = parser.parse_args()
    if args.octave == None or args.octave == 0 or args.octave.lower() == "no" or args.octave.lower() == "false":
        using_octave = False
    else:
        using_octave = True

    print(f"Running Piano Tester, Using Octave = {using_octave}\n\n")
    score = 0
    counter = 1
    try:

        while True:
            random_note, random_octave = generate_random_note()
            if using_octave:
                print(f"#{counter} - Test Note: {random_note}{random_octave}")
            else:
                print(f"#{counter} - Test Note: {random_note}")

            frequency, note, octave = detect_tone()

            if frequency:
                if (using_octave and random_note == note and random_octave == octave) or (not using_octave and random_note == note):
                    score = score + 1
                    if using_octave:
                        print(f"Correct! Detected Note: {note}{octave}\n")
                    else:
                       print(f"Correct! Detected Note: {note}\n")
                else:
                    if using_octave:
                        print(f"Wrong! Detected Note: {note}{octave}\n")
                    else:
                        print(f"Wrong! Detected Note: {note}\n")
                
                print(f"Score: {score}\n")
                counter = counter + 1

            else:
                print("No dominant tone detected.")
    
    except KeyboardInterrupt:
        print("\nCtrl+C detected. Exiting...")
        print(f"Final Score: {score} from {counter} tests.")


        