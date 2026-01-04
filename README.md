🤖 AI Referee: Rock-Paper-Scissors-Plus

An intelligent, AI-powered twist on the classic game, featuring a witty referee, a "Bomb" mechanic, and interactive commentary.

1. Project Description

This project is a modern reimagining of Rock-Paper-Scissors, built with a Streamlit frontend and powered by Google's Gemini 1.5 Flash model.

Instead of simple if-else logic, an AI Referee agent analyzes every move. It validates rules, enforces the special "Bomb" mechanic (limited to one use per game), and provides dynamic, funny, and context-aware commentary for every round. The application also features a chat mode where users can ask the referee questions about strategy or rules in real-time.

2. Technical Architecture

2.1 Tech Stack

Language: Python 3.x

Frontend Framework: Streamlit (Interactive Web UI)

API Integration: Google Generative AI SDK (google-generativeai)

State Management: Python Class-based in-memory storage

2.2 ADK Agents & Tools Used

This project utilizes specific Agent Development Kit (ADK) patterns to create a reliable AI Referee:

The Model: We use gemini-1.5-flash-002, optimized for high speed and low latency, which is essential for a real-time game loop.

System Instructions (Persona): The Agent is initialized with a strict system prompt that defines its role: "You are the AI Referee... Bomb beats everything... Invalid input wastes the round." This ensures the AI stays in character.

Tool Use (Function Calling):

Tool Name: resolve_round

Purpose: Instead of letting the LLM generate free text (which might hallucinate the winner), we force it to call this tool.

Structure: The tool accepts specific parameters: round_winner (user/bot/draw), is_invalid (boolean), and reasoning (string). This guarantees that the game logic—such as the complex "Bomb" interaction—is handled structurally and reliably.

Reasoning Loop: The application injects the current Game State (scores, bomb usage history) into the prompt on every turn, allowing the Agent to make state-aware decisions (e.g., rejecting a second Bomb attempt).

3. Screenshots


3.1 Game Landing Page

![Game Landing Page](https://github.com/Gauravfriska/rock-paper-scissors-ai/blob/main/image.png)  

3.2 The Gameplay Arena

![The interactive board showing scorecards, move buttons, and the round counter](https://github.com/Gauravfriska/rock-paper-scissors-ai/blob/main/Battle.png)

3.3 AI Referee Commentary

![The AI analyzing a move and declaring a winner with witty reasoning](https://github.com/Gauravfriska/rock-paper-scissors-ai/blob/main/Ai%20Refree.png)

3.4 Battle Log

![Battle Log](https://github.com/Gauravfriska/rock-paper-scissors-ai/blob/main/Battle%20logs.png)

3.5 Chat with Referee

![The interactive chat feature where users can ask questions about the game](https://github.com/Gauravfriska/rock-paper-scissors-ai/blob/main/Ask%20Questions%20.png)

4. How to Run This Project

Follow these steps to get the game running on your local machine.

4.1 Clone the Repository

Open your terminal and run:

git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
cd YOUR_REPO_NAME


4.2 Install Dependencies

Make sure you have Python installed, then run:

pip install streamlit google-generativeai


4.3 Run the Application

Start the Streamlit server:

streamlit run app.py


4.4 Start Playing

The game will open automatically in your browser (usually at http://localhost:8501).

5. Gameplay Guide

5.1 The Rules

Start the Match: Click the "Start New Game" button in the sidebar.

Basic Moves:

🪨 Rock beats Scissors.

📄 Paper beats Rock.

✂️ Scissors beats Paper.

5.2 The Special "Bomb" Mechanic

💣 BOMB: The ultimate weapon! It beats Rock, Paper, and Scissors.

Constraint: You can only use the Bomb ONCE per game.

Penalty: If you try to use it a second time, the Referee will flag it as an Invalid Move, and you will waste your turn (likely losing the round).

5.3 Winning the Game

Format: Best of 3 Rounds.

Objective: The first player (User or Bot) to reach 2 wins is crowned the Champion.

Feedback: Read the "Referee Commentary" box after every move for a witty explanation of the result.

6. Interactive Features

6.1 Battle Log

Use the "Battle Log" on the right side of the screen to track the history of moves (R1, R2, R3) and verify past results.

6.2 Ask the Referee

Stuck? Confused? Scroll down to the "Ask the Referee a Question" section.
You can ask things like:

"What happens if we both play Bomb?"

"How many rounds are left?"

"Tell me a joke."


The AI will respond instantly without interrupting the flow of your match.



