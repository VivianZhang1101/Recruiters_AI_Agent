# AI-Powered Recruiter Assistant  

This project builds an AI-powered recruiter assistant to generate survey questions, collect responses, and provide actionable insights to improve job postings. It integrates text and voice-based interactions for a dynamic user experience.

---

## **System Overview**  

The solution includes:  
1. A **Python Flask backend** to process job descriptions, generate questions, and manage responses.  
2. A **Python terminal-based frontend** for user interaction.  
3. **OpenAI GPT integration** to generate questions, follow-up queries, summaries, and recommendations.  
4. **Voice support** for input and output, enhancing accessibility and engagement.  

---

## **Features**  

### 1. **Automatic Question Generation**  
  - Generates categorized survey questions based on job descriptions:
    - Responsibilities
    - Ideal Candidate's Experience and Skills
    - Team Structure and Culture
    - Unclear or Missing Details  

### 2. **Question-Answer Recording**  
  - Captures and stores each question-answer pair during the session.  
  - Responses are saved in session variables and summarized at the end of the session.  

### 3. **Follow-Up Questions**  
  - Dynamically generates follow-up questions based on recruiter responses to clarify or explore further.  
  - Analyzes responses for ambiguity or incomplete information.  
  - Avoids redundant follow-ups if the recruiter provides clear or disinterested answers.  

### 4. **Voice Input and Output**  
- Allows users to interact with the system via voice commands and responses.  
- Captures audio via `speech_recognition` and converts it to text.  
-  Uses `pyttsx3` for text-to-speech functionality.  
- Supports retries for unclear or incorrect inputs.  

### 5. **Summary and Recommendations**  
- Summarizes recruiter responses and provides actionable recommendations for improving the job post.  
- Analyzes responses and job descriptions to identify missing or unclear details.  
- Generates personalized recommendations to enhance the job posting.  

---

## **Technologies Used**  

- **Backend**: Python Flask  
- **AI Integration**: OpenAI GPT-4o-mini  
- **Frontend**: Python terminal-based interface  
- **Speech-to-Text**: `speech_recognition`  
- **Text-to-Speech**: `pyttsx3`  

---

## **Installation and Setup**  

1. **Clone the Repository**:  
   ```bash
   git clone git@github.com:VivianZhang1101/Recruiters_AI_Agent.git
   cd Recruiters_AI_Agent
   ```
2. **Install Dependencies**:  
   ```bash
   pip install flask flask-session openai pyttsx3 SpeechRecognition
   ```
3. **Set Your OpenAI API Key**:  
Replace `api_key` in the `server.py` with your OpenAI API key.
4. **Run the Flask Server**:  
   ```bash
   python server.py
   ```
5. **Start the client Interface**:  
   ```bash
   python client.py
   ```

## **Future Development**  
- **Voice Agent**: Using better voice models for improved interaction and natural conversational flow.  
- **Frontend**: Develop a user-friendly frontend using React for enhanced interaction and usability.  
- **Skill Gap Analysis**: Identify potential skill gaps based on recruiter input and suggest additional qualifications or skills.
- **Explainable AI Features**: Provide explanations for why specific questions or insights are generated.
- **Role Matching Suggestions**: Suggest ideal candidate profiles based on job descriptions and recruiter responses.
- **Role-Specific Question Templates**: Adjust questions dynamically based on the role type (e.g., technical, sales, or leadership).



