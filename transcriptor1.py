import speech_recognition as sr
import threading
import queue
import time

class RealTimeTranscriber:
    def __init__(self):
        # Initialize recognizer and microphone
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Queue to store transcription results
        self.transcription_queue = queue.Queue()
        
        # Flag to control transcription loop
        self.is_running = False
        
        # Configure recognizer settings
        self.recognizer.pause_threshold = 0.5  # Pause before phrase is considered complete
        self.recognizer.dynamic_energy_threshold = True
    
    def start_listening(self):
        """Start the transcription process in a separate thread."""
        self.is_running = True
        self.transcription_thread = threading.Thread(target=self._transcribe_audio)
        self.transcription_thread.start()
        print("Transcription started. Speak into the microphone.")
    
    def stop_listening(self):
        """Stop the transcription process."""
        self.is_running = False
        if hasattr(self, 'transcription_thread'):
            self.transcription_thread.join()
        print("Transcription stopped.")
    
    def _transcribe_audio(self):
        """Continuous audio transcription method."""
        with self.microphone as source:
            # Adjust for ambient noise at the start
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while self.is_running:
                try:
                    # Listen for audio input
                    audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=5)
                    
                    # Transcribe in a separate thread to avoid blocking
                    transcribe_thread = threading.Thread(
                        target=self._process_transcription, 
                        args=(audio,)
                    )
                    transcribe_thread.start()
                
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"Error during transcription: {e}")
    
    def _process_transcription(self, audio):
        """Process and queue transcription results."""
        try:
            # Attempt to transcribe using Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            
            if text:
                # Put transcribed text in queue and print
                self.transcription_queue.put(text)
                print(f"Transcribed: {text}")
        
        except sr.UnknownValueError:
            # Speech was unintelligible
            pass
        except sr.RequestError as e:
            # Could not request results from speech recognition service
            print(f"Could not request results; {e}")
    
    def get_transcriptions(self):
        """Retrieve transcriptions from the queue."""
        transcriptions = []
        while not self.transcription_queue.empty():
            transcriptions.append(self.transcription_queue.get())
        return transcriptions

def main():
    # Create transcriber instance
    transcriber = RealTimeTranscriber()
    
    try:
        # Start listening
        transcriber.start_listening()
        
        # Let it run for a while (e.g., 30 seconds)
        while True:
            time.sleep(5)
            
            # Periodically check and print transcriptions
            current_transcriptions = transcriber.get_transcriptions()
            if current_transcriptions:
                print("Recent transcriptions:", current_transcriptions)
    
    except KeyboardInterrupt:
        print("\nStopping transcription...")
    
    finally:
        # Ensure transcription stops
        transcriber.stop_listening()

if __name__ == "__main__":
    main()