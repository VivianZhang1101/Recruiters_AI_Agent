from flask import Flask, request, session, jsonify
from flask_session import Session
from openai import OpenAI
import json

app = Flask(__name__)
app.secret_key = "resume"
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
# Load your API key from an environment variable or secure source
api_key = 'api_key'
client = OpenAI(api_key=api_key)

@app.route('/start_chat', methods=['POST'])
def start_chat():
    job_post = request.json.get('job_post', '')
    if not job_post:
        return jsonify({'error': 'Job post content is required'}), 400
    
    # Generate survey questions
    prompt = f"""
    You are AI Agent that takes a job post as input and generates personalized survey questions for Recruiter to answer. 
    Given the following job description, generate clarifying questions to ask a recruiter. Focus on:
    1. Responsibilities
    2. Ideal candidate's experience and soft skills
    3. Company culture or team structure
    Example question: Can you elaborate on the specific types of AI features the candidate would be expected to implement?
    Limit the number of questions to 1 per section.
    Return the questions in JSON format:
    {{
        "Responsibilities": [],
        "Ideal Experience": [],
        "Team Structure": []
    }}
    Job Description:
    {job_post}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        max_tokens=500
    )
    
    questions = response.choices[0].message.content
    start_index = questions.find('{')
    if start_index != -1:
        questions = questions[start_index:-3]
    else:
        raise ValueError("No JSON object found in the string!")
    try:
        questions = json.loads(questions)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
    print(questions)
    session['questions'] = questions
    session['answers'] = []
    first_category = list(questions.keys())[0]
    # return jsonify({'message': 'Chat started', 'questions': questions})
    # return jsonify({'message': 'Chat started'})
    return jsonify({
        'message': 'Chat started',
        'next_category': first_category,
        'next_question': questions[first_category][0] if questions[first_category] else None
    })

@app.route('/ask_question', methods=['POST'])
def ask_question():
    questions = session.get('questions', {})
    answers = session.get('answers', [])

    current_category = request.json.get('current_category', '')
    answer = request.json.get('answer', '')

    if not current_category or current_category not in questions:
        return jsonify({'error': 'Invalid category'}), 400

    # Remove answered question and append answer
    current_question = questions[current_category].pop(0)
    answers.append({'category': current_category, 'question': current_question, 'answer': answer})

    # Generate follow-up questions dynamically based on the answer
    if answer and answer != 'Not applicable':
        follow_up_prompt = f"""
        Here is the question: {current_question}. Given the recruiter's answer: "{answer}", determine if a follow-up question is appropriate.

        Consider the following guidelines:
        1. If the answer suggests the recruiter has no more interest in elaborating (e.g., "just normal communication" or "it's standard"), return "None".
        2. If the answer is vague or incomplete and clarification would add value, generate a follow-up question.
        3. If the answer explicitly indicates they don’t know or don’t want to answer, return "None".
        4. If the original question is already a follow-up, avoid trying too hard to generate another follow-up.
        5. Ensure the follow-up question is specific and meaningful, rather than generic or repetitive.

        If a follow-up is needed, return the question as a string. If no follow-up is appropriate, return "None".
        """
        follow_up_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user",  "content": [{"type": "text", "text": follow_up_prompt}]}],
            max_tokens=100
        )
        follow_up_question = follow_up_response.choices[0].message.content.strip()
        if follow_up_question and follow_up_question.lower() != "none":
            questions[current_category].insert(0, "Follow-up questions: " + follow_up_question)  # Add follow-up to the front of the queue

    # Save updated session data
    session['questions'] = questions
    session['answers'] = answers
    session.modified = True

    # Check for next question or category
    if questions[current_category]:
        return jsonify({'next_category': current_category, 'next_question': questions[current_category][0]})
    else:
        next_category = get_next_category(questions, current_category)
        if next_category:
            return jsonify({
                'next_category': next_category,
                'next_question': questions[next_category][0] if questions[next_category] else None
            })
        else:
            return jsonify({'message': 'All questions answered'})
def get_next_category(questions, current_category):
    categories = list(questions.keys())
    current_index = categories.index(current_category) if current_category in categories else -1
    for i in range(current_index + 1, len(categories)):
        if questions[categories[i]]:  # Return the next non-empty category
            return categories[i]
    return None  # No more categories with questions

@app.route('/end_chat', methods=['GET'])
def end_chat():
    """
    Generates a summary of answers and provides recommendations based on recruiter responses.
    """
    answers = session.get('answers', [])
    print(f"Summary answer: {answers}")
    job_post = session.get('job_post', '')

    if not answers:
        return jsonify({'error': 'No answers available to summarize'}), 400

    # Generate a summary and recommendations
    summary_prompt = f"""
    Based on the following recruiter responses and job description, generate:
    1. A concise summary of the recruiter-provided details.
    2. Recommendations to improve the job description, including any missing or unclear details.

    Job Description:
    {job_post}

    Recruiter Responses:
    {json.dumps(answers, indent=2)}

    Return the response in JSON format:
    {{
        "summary": "Concise summary of responses",
        "recommendations": "Recommendations to improve the job description"
    }}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": [{"type": "text", "text": summary_prompt}]}],
        max_tokens=700
    )
    result = response.choices[0].message.content
    start_index = result.find('{')
    if start_index != -1:
        result = result[start_index:-3]
    else:
        raise ValueError("No JSON object found in the string!")
    try:
        result = json.loads(result)
    except json.JSONDecodeError as e:
        return jsonify({'error': f"Failed to parse recommendations: {e}"}), 500

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=False)
