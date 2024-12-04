import requests
import pyttsx3
import speech_recognition as sr
BASE_URL = "http://127.0.0.1:5000"
client_session = requests.Session()


def initialize_voice_engine():
    """
    Initialize the text-to-speech engine.
    """
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  
    engine.setProperty('volume', 0.9) 
    return engine


def text_to_speak(engine, text):
    """
    Convert text to speech and play it.
    """
    engine.say(text)
    engine.runAndWait()
    

def get_voice_input():
    """
    Record audio from the user and convert it to text using speech recognition.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... (speak now)")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            # text_to_speak(engine, f"You said: {text}")
            # text_to_speak(engine, f"Is this correct?")
            # confirmation = input("Is this correct? (yes/no): ").strip().lower()
            # if confirmation in ["yes", "y"]:
            #     return text
            # else:
            #     print("Let's try again.")
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
            return None
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return None
        except sr.WaitTimeoutError:
            print("No input detected.")
            return None
        
def start_chat(mode, engine):
    """
    Starts the chat by sending the job description to the server.
    Returns the first category and question if successful, or None otherwise.
    """
    if mode == 'voice':
        text_to_speak(engine, f"Please enter the job description")
    job_post = input("Enter the job description: ")
    response = client_session.post(f"{BASE_URL}/start_chat", json={"job_post": job_post})
    if response.status_code == 200:
        data = response.json()
        print("\nChat started! Let's begin.")
        return data.get('next_category'), data.get('next_question')
    else:
        print("Error:", response.json().get('error', 'Unknown error'))
        return None, None

def ask_question(mode, engine=None):
    current_category, current_question = start_chat(mode, engine)
    if not current_category or not current_question:
        print("No questions available. Ending the session.")
        return
    while True:
        print(f"\nCategory: {current_category}")
        if current_question.startswith("Follow-up"):
            print(current_question)
        else:
            print(f"Question: {current_question}")
        if mode == 'voice':
            text_to_speak(engine, f"The current Category is {current_category}, and the question is {current_question}")

      
        if mode == 'voice':
            text_to_speak(engine, f"Please tell me your answer")
            answer = get_voice_input()
        else:
            answer = input("Your Answer (or type 'skip' to move on): ").strip()
        # # Get user answer
        # answer = input(f"Your Answer (or type 'skip' to move on): ").strip()
        # if answer.lower() == 'skip':
        #     answer = "Not applicable"
        if not answer:
            print("No response detected. Skipping...")
            answer = "Not applicable"
        elif answer.lower() == 'skip':
            print("Skipped this question.")
            answer = "Not applicable"


        # Send the answer to the server
        payload = {
            'current_category': current_category,
            'answer': answer
        }
        response = client_session.post(f"{BASE_URL}/ask_question", json=payload)

        if response.status_code == 200:
            data = response.json()
            
            # Check if all questions are answered
            if "message" in data and data["message"] == "All questions answered":
                print("\nAll questions have been answered. Thank you!\n")
                if mode == 'voice':
                    text_to_speak(engine, "All questions have been answered. Thank you!")         
                break

            # Get the next category and question
            current_category = data.get('next_category')
            current_question = data.get('next_question')

            if not current_category or not current_question:
                print("No more questions available. Ending the session.")
                if mode == 'voice':
                    text_to_speak(engine, "No more questions available. Ending the session.")
                break
            # if not current_category or not current_question:
            #     print("No more questions available. Ending the session.")
            #     break
        else:
            error_message = response.json().get('error', 'Unknown error')
            print("Error:", error_message)
            if mode == 'voice':
                text_to_speak(engine, f"Error: {error_message}")
            break

def end_chat():
    """
    Retrieves the summary of all questions and answers from the server.
    """
    print("Please wait while the AI Agent is ganerating the summary\n")
    response = client_session.get(f"{BASE_URL}/end_chat")
    if response.status_code == 200:
        summary = response.json().get('summary', [])
        print(f"Here is the summary that AI Agent summarized based on your answers:\n\n{summary}\n")
        recommendations = response.json().get('recommendations', [])
        print("Recommendations for Job Post Improvement:\n")
        for recommendation in recommendations:
            print(f"- {recommendation}")
    else:
        print("Error:", response.json().get('error', 'Unknown error'))

def main():
    """
    Main function to handle the entire workflow.
    """
    print("Select Interaction Mode: 1. Text  2. Voice")
    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == '2':
        mode = 'voice'
        engine = initialize_voice_engine()
    else:
        mode = 'text'
        engine = None

    ask_question(mode, engine)
    end_chat()

if __name__ == "__main__":
    main()