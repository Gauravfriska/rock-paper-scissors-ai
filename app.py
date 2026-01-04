import streamlit as st
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
import random
import uuid
import warnings

# --- HARDCODED API KEY ---
API_KEY = "AIzaSyDkA58wFwMO1TK4HmrjlAluZB7zSGFzk6s"

# --- CONFIGURATION & SETUP ---
st.set_page_config(page_title="AI Referee: RPS+", layout="wide")

# Suppress Deprecation Warnings for cleaner logs
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# --- CSS STYLING ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        height: 60px;
        font-size: 20px;
        border-radius: 10px;
    }
    .score-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #d1d5db;
        color: #333;
    }
    .game-log {
        background-color: #1e1e1e;
        color: #00ff00;
        padding: 15px;
        border-radius: 5px;
        font-family: monospace;
        height: 300px;
        overflow-y: auto;
    }
    .chat-box {
        border: 1px solid #ddd;
        padding: 10px;
        border-radius: 10px;
        background-color: #ffffff;
        max-height: 300px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# --- CLASS 1: AI REFEREE AGENT ---
class RefereeAgent:
    def __init__(self):
        pass

    def _get_model(self, api_key: str):
        genai.configure(api_key=api_key)
        
        # Define the tool structure
        resolve_tool = {
            "function_declarations": [
                {
                    "name": "resolve_round",
                    "description": "Calculates the winner of a Rock-Paper-Scissors-Plus round based on moves and rules.",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "round_winner": {
                                "type": "STRING",
                                "description": "The winner of the round: 'user', 'bot', or 'draw'."
                            },
                            "is_invalid": {
                                "type": "BOOLEAN",
                                "description": "True if the user's move was invalid (e.g. nonsense or 2nd bomb usage)."
                            },
                            "reasoning": {
                                "type": "STRING",
                                "description": "Short explanation of why this result occurred."
                            }
                        },
                        "required": ["round_winner", "is_invalid", "reasoning"]
                    }
                }
            ]
        }

        # System Prompt
        system_instruction = """
        You are the AI Referee for a game of Rock-Paper-Scissors-Plus.
        
        GAME RULES:
        1. Standard: Rock > Scissors, Scissors > Paper, Paper > Rock.
        2. Bomb: Bomb beats Rock, Paper, and Scissors.
        3. Bomb vs Bomb is a Draw.
        4. Bomb limit: A player can only use Bomb ONCE per game.
        5. Invalid input (nonsense or using Bomb a second time) wastes the round.
        
        YOUR JOB:
        1. Receive User move, Bot move, and State (bomb usage).
        2. Validate the move. If user tries to use Bomb but `user_bomb_used` is True, it is INVALID.
        3. CALL THE TOOL `resolve_round` with the outcome.
        4. Generate short, witty commentary in the `reasoning` field.
        """

        # Using specific version 002 to avoid 404 errors with alias
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-002", 
            tools=[resolve_tool],
            system_instruction=system_instruction
        )
        return model

    def get_intro(self) -> str:
        # Improved conversational intro with bold rules
        return """
        **Hi! Welcome to the Arena!** 🏟️
        
        I'm your AI Referee (v2). Here are the rules for our match:
        
        1. **Rock beats Scissors** 🪨✂️
        2. **Scissors beats Paper** ✂️📄
        3. **Paper beats Rock** 📄🪨
        4. **BOMB beats everything** (but you only have **ONE** per game!) 💣
        
        Let's start! **Choose Your First Move.**
        """

    def answer_question(self, api_key: str, question: str):
        """Simple chat function for the user to ask questions about the game."""
        try:
            genai.configure(api_key=api_key)
            # Using specific version 002
            model = genai.GenerativeModel("gemini-1.5-flash-002")
            prompt = f"""
            You are a helpful and witty AI Referee for a Rock-Paper-Scissors-Plus game.
            The user is asking: "{question}"
            Provide a short, friendly answer explaining the rules or strategy. 
            Keep it under 3 sentences.
            """
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Referee distracted (Chat Error): {str(e)}"

    def resolve_turn(self, api_key: str, current_state: dict, user_move: str, bot_move: str):
        try:
            model = self._get_model(api_key)
            
            prompt = f"""
            Current Game State:
            - User Bomb Used: {current_state['user_bomb_used']}
            - User Score: {current_state['user_score']}
            - Bot Score: {current_state['bot_score']}
            
            Current Turn:
            - User Move: {user_move}
            - Bot Move: {bot_move}
            
            Analyze this turn. Check if User Move is valid (specifically bomb usage). 
            Call the resolve_round tool.
            """

            response = model.generate_content(prompt)
            
            # Extract tool call
            fc = response.candidates[0].content.parts[0].function_call
            if fc and fc.name == "resolve_round":
                args = fc.args
                return {
                    "round_winner": args["round_winner"],
                    "is_invalid": args["is_invalid"],
                    "commentary": args["reasoning"]
                }
            
            # Fallback
            return {
                "round_winner": "draw", "is_invalid": True, 
                "commentary": "Referee error: I couldn't decide the outcome. Round voided."
            }

        except Exception as e:
            return {
                "round_winner": "draw", "is_invalid": True,
                "commentary": f"Referee distracted (Model Error): {str(e)}"
            }

# --- CLASS 2: GAME MANAGER ---
class GameManager:
    def __init__(self):
        self.state = {
            "round": 1,
            "user_score": 0,
            "bot_score": 0,
            "user_bomb_used": False,
            "bot_bomb_used": False,
            "history": [],
            "game_over": False,
            "winner": None,
            "message": "",
            "chat_history": [] # Stores Q&A with the Referee
        }
        self.referee = RefereeAgent()

    def generate_bot_move(self) -> str:
        available_moves = ["rock", "paper", "scissors"]
        # 10% chance to bomb if not used yet
        if not self.state["bot_bomb_used"]:
            if random.random() < 0.1: 
                return "bomb"
        return random.choice(available_moves)

    def process_chat(self, question: str, api_key: str):
        if not question: 
            return
        
        # Add user question to history
        self.state["chat_history"].append({"role": "user", "text": question})
        
        # Get answer
        answer = self.referee.answer_question(api_key, question)
        
        # Add bot answer to history
        self.state["chat_history"].append({"role": "assistant", "text": answer})

    def process_move(self, user_move: str, api_key: str):
        if self.state["game_over"]:
            return

        bot_move = self.generate_bot_move()

        # Call AI Referee
        decision = self.referee.resolve_turn(
            api_key, self.state, user_move, bot_move
        )

        # Update State
        self.state["message"] = decision["commentary"]
        
        # Track bomb usage
        if user_move.lower() == "bomb" and not decision["is_invalid"]:
            self.state["user_bomb_used"] = True
        if bot_move.lower() == "bomb":
            self.state["bot_bomb_used"] = True

        # Score update
        winner = decision["round_winner"]
        if winner == "user":
            self.state["user_score"] += 1
        elif winner == "bot":
            self.state["bot_score"] += 1

        # History log
        self.state["history"].append({
            "round": self.state["round"],
            "user": user_move,
            "bot": bot_move,
            "result": winner
        })

        # Check Game Over Conditions
        if self.state["user_score"] >= 2:
            self.state["game_over"] = True
            self.state["winner"] = "User"
            self.state["message"] += " \n\n 🎉 GAME OVER! You Win!"
        elif self.state["bot_score"] >= 2:
            self.state["game_over"] = True
            self.state["winner"] = "Bot"
            self.state["message"] += " \n\n 🤖 GAME OVER! Bot Wins!"
        elif self.state["round"] >= 3:
            self.state["game_over"] = True
            if self.state["user_score"] > self.state["bot_score"]:
                self.state["winner"] = "User"
                self.state["message"] += " \n\n 🎉 GAME OVER! You Win!"
            elif self.state["bot_score"] > self.state["user_score"]:
                self.state["winner"] = "Bot"
                self.state["message"] += " \n\n 🤖 GAME OVER! Bot Wins!"
            else:
                self.state["winner"] = "Draw"
                self.state["message"] += " \n\n 🤝 GAME OVER! It's a Draw!"
        else:
            self.state["round"] += 1

# --- STREAMLIT STATE MANAGEMENT ---
if "game_manager" not in st.session_state:
    st.session_state.game_manager = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🔧 Configuration")
    
    # API KEY is now hardcoded at the top
    if st.button("Start New Game", type="primary"):
        st.session_state.game_manager = GameManager()
        st.session_state.game_manager.state["message"] = st.session_state.game_manager.referee.get_intro()
        st.success("Game Started!")
        st.rerun()
    
    st.divider()
    st.markdown("### 📜 Cheat Sheet")
    st.markdown("- **Bomb** wins against everything.")
    st.markdown("- **Bomb** can be used **ONCE**.")

# --- MAIN UI ---
st.title("🤖 AI Referee: Rock-Paper-Scissors-Plus")

if st.session_state.game_manager is None:
    st.info("👈 Click 'Start New Game' in the sidebar to begin.")
else:
    gm = st.session_state.game_manager
    state = gm.state

    # Top Score Board
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="score-card">
            <h3>👤 User Score</h3>
            <h1>{state['user_score']}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="score-card">
            <h3>🔢 Round</h3>
            <h1>{state['round']}/3</h1>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="score-card">
            <h3>🤖 Bot Score</h3>
            <h1>{state['bot_score']}</h1>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Game Area
    game_col, log_col = st.columns([2, 1])

    with game_col:
        st.subheader("Make your Move")
        
        if not state["game_over"]:
            c1, c2, c3, c4 = st.columns(4)
            
            def handle_click(move):
                with st.spinner("Referee is thinking..."):
                    gm.process_move(move, API_KEY)
            
            if c1.button("🪨 Rock"): handle_click("rock")
            if c2.button("📄 Paper"): handle_click("paper")
            if c3.button("✂️ Scissors"): handle_click("scissors")
            if c4.button("💣 Bomb"): handle_click("bomb")
        else:
            st.warning(f"GAME OVER. Winner: {state['winner']}")
            if st.button("Play Again?"):
                st.session_state.game_manager = None
                st.rerun()

        st.subheader("Referee Commentary")
        st.info(state["message"] if state["message"] else "Waiting for move...")

    with log_col:
        st.subheader("Battle Log")
        log_html = ""
        for h in reversed(state["history"]):
            winner_icon = "👤" if h['result'] == 'user' else "🤖" if h['result'] == 'bot' else "🤝"
            log_html += f"<div>R{h['round']}: You {h['user']} vs {h['bot']} -> {winner_icon}</div><hr>"
        
        st.markdown(f'<div class="game-log">{log_html}</div>', unsafe_allow_html=True)

    # --- CHAT INTERFACE ---
    st.divider()
    with st.expander("💬 Ask the Referee a Question", expanded=True):
        
        # Display chat history
        for chat in state["chat_history"]:
            with st.chat_message(chat["role"]):
                st.write(chat["text"])
        
        # Chat Input
        if question := st.chat_input("Ask about rules, strategy, or just say hi..."):
            gm.process_chat(question, API_KEY)
            st.rerun()