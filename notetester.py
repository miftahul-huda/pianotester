import numpy as np
import sounddevice as sd
import scipy.signal as signal
from scipy.fft import fft, fftfreq
import argparse
import time
from colorama import Fore, Back, Style, init

init(autoreset=True) #Automatically resets colors after each print.



def get_loopback_device_index():
    try:
        devices = sd.query_devices()
        loopback_device_index = None

        # Find the index of your loopback device (e.g., BlackHole)
        for i, device in enumerate(devices):
            if "BlackHole" in device["name"]:  # Adjust for Loopback if needed
                loopback_device_index = i
                break

        if loopback_device_index is None:
            print("Loopback device not found.")
            return None
        else:
            return loopback_device_index


    except sd.PortAudioError as e:
        print(f"PortAudio error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def detect_tone(duration=1, samplerate=44100, threshold=0.01, device = None):
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
        #print("Listening...")
        print("Waiting for sound...\n\n")
        timeout = 10  # Adjust timeout as needed
        start_time = time.time()
        audio_data = None

        while True:
            audio_data = sd.rec(int(samplerate * duration), samplerate=samplerate, device=device,  channels=2, blocking=True)
            sd.wait()
            audio_data = audio_data.flatten()


            # Calculate the root mean square (RMS) amplitude
            rms_amplitude = np.sqrt(np.mean(audio_data**2))

            if rms_amplitude > threshold:
                #print("Sound detected!")
                break  # Exit the loop if sound is detected

            """
            if time.time() - start_time > timeout:
                print("Timeout. No sound detected.")
                return None, None, None
            """
            
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
        return None, None, None

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

    print("==========================\n")
    print("Available Devices:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        print(f"Device {i}: {device['name']}")

    print("\n")
    loopback_device_index = get_loopback_device_index()
    print(f"Loopback Device Index: {loopback_device_index}\n")

    print("\n==========================\n")

    score = 0
    counter = 1
    try:

        while True:
            random_note, random_octave = generate_random_note()
            print(f"\n#{counter} ==========================")
            if using_octave:
                print(Fore.BLUE + f"Test Note: {random_note}{random_octave}")
            else:
                print(Fore.BLUE + f"Test Note: {random_note}")

            frequency, note, octave = detect_tone(duration=1, samplerate=44100, threshold=0.01, device=loopback_device_index )

            if frequency:
                if (using_octave and random_note == note and random_octave == octave) or (not using_octave and random_note == note):
                    score = score + 1
                    if using_octave:
                        print( Fore.GREEN + f"Correct! Detected Note: {note}{octave}\n")
                    else:
                       print(Fore.GREEN + f"Correct! Detected Note: {note}\n")
                else:
                    if using_octave:
                        print( Fore.RED + f"Wrong! Detected Note: {note}{octave}\n")
                    else:
                        print( Fore.RED +  f"Wrong! Detected Note: {note}\n")
                
                print(f"Score: {score}\n")
                counter = counter + 1

            else:
                print("No dominant tone detected.")
    
    except KeyboardInterrupt:
        print("\nCtrl+C detected. Exiting...")
        print(f"Final Score: {score} from {counter} tests.")


        