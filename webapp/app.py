import streamlit as st
st.set_page_config(layout="wide")

import sys
from dotenv import load_dotenv

sys.path.append("../")
sys.path.append(".")

load_dotenv("../.env")
from utils import *
from negotiationarena.constants import *

from negotiationarena.agents.chatgpt import ChatGPTAgent
from negotiationarena.agents.human import HumanAgent
from negotiationarena.game_objects.resource import Resources
from negotiationarena.game_objects.goal import BuyerGoal, SellerGoal
from negotiationarena.game_objects.valuation import Valuation
from negotiationarena.constants import AGENT_ONE, AGENT_TWO, MONEY_TOKEN
import traceback
from games.buy_sell_game.game import BuySellGame
import json
import os
import random

def main():
    st.title("Negotiation Arena")

    if "personas" not in st.session_state or "classifications" not in st.session_state:
        # Define paths to the JSON files (adjust paths as needed)
        json_files = ["personas/outputs/neutral_personas.json", 
                    "personas/outputs/sycophant_personas.json", 
                    "personas/outputs/nonsycophant_personas.json"
        ]
        combined_data = {}
        classifications = {}

        current = ["neutral", "sycophant", "nonsycophant"]
        i = 0
        for file_path in json_files:
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                        # Merge data into combined_data dictionary
                        combined_data.update(data)

                        for key, value in data.items():
                            classifications[key] = current[i]
            except Exception as e:
                st.error(f"Error reading {file_path}: {e}")

            i += 1
        
        st.session_state.personas = combined_data
        st.session_state.classifications = classifications

    
    print(f"Loaded personas: {st.session_state.personas}")

    col1, col2 = st.columns(2)

    # ========== USER INPUT FORM ==========
    with col2:
        with st.form(key="user_input"):
            decision = st.radio("Do you want to accept the proposal?", ["yes", "no"])
            price = st.text_input("Counter offer price (only if proposing):")
            message = st.text_area("Message to other player (only if proposing):")

            submitted = st.form_submit_button("Submit Response")
            if submitted:
                st.session_state.human_decision = decision
                st.session_state.counter_offer_price = price
                if decision == "yes":
                    message = "I accept your proposal."
                else:
                    st.session_state.counter_offer_message = message
                if "messages" not in st.session_state:
                    st.session_state.messages = []
                
                if message != "":
                    st.session_state.messages.append({
                        "role": "user",
                        "content": message,
                    })
                st.session_state.submitted = True
                try:
                    if not st.session_state.game_over:
                        st.session_state.game_over = st.session_state.game.run_one_turn()
                    if not st.session_state.game_over:
                        st.session_state.game_over = st.session_state.game.run_one_turn()
                except Exception as e:
                    st.error(f"Turn failed: {e}")
                    st.text(traceback.format_exc())

    # ========== INITIALIZE SESSION STATE ==========
    if "started" not in st.session_state:
        st.session_state.started = False
    if "game" not in st.session_state:
        st.session_state.game = None
    if "game_over" not in st.session_state:
        st.session_state.game_over = False

    if st.session_state.game_over:
        # Button to reset the game
        if st.button("Start New Negotiation"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()  # Restart the app with clean state

    # ========== START GAME ONLY ONCE ==========
    if not st.session_state.started:
        try:
            a1 = ChatGPTAgent(agent_name=AGENT_ONE, model="gpt-4o-mini")
            a2 = HumanAgent(agent_name=AGENT_TWO)

            # Pick a random persona from the available personas
            if st.session_state.personas:
                random_persona_key = random.choice(list(st.session_state.personas.keys()))
                random_persona = st.session_state.personas[random_persona_key]
                # st.sidebar.write(f"Selected Persona: {random_persona_key}")
            else:
                random_persona = ""
                st.sidebar.write("No personas available")
            
            game = BuySellGame(
                players=[a1, a2],
                iterations=10,
                player_goals=[
                    SellerGoal(cost_of_production=Valuation({"X": 40})),
                    BuyerGoal(willingness_to_pay=Valuation({"X": 60})),
                ],
                player_starting_resources=[
                    Resources({"X": 1}),
                    Resources({MONEY_TOKEN: 100}),
                ],
                player_conversation_roles=[
                    f"You are {AGENT_ONE}.",
                    f"You are {AGENT_TWO}.",
                ],
                player_social_behaviour=[
                    random_persona,
                    ""
                ],
                player_trade_environment=[
                    "You have ten customers lining up to buy your product. If you reject you will walk away with a payoff of 0, otherwise you will walk away with a payoff of sell price minus cost of production.",
                    ""
                ],
                log_dir="../example_logs/buysell/test_human",
            )

            st.session_state.game = game
            st.session_state.game.initialize_first_state()
            st.session_state.started = True
            st.success("Game initialized. Ready to play!")
            st.session_state.game.run_one_turn()

        except Exception as e:
            st.error(f"Exception: {e}")
            st.text(traceback.format_exc())

    # ========== DISPLAY LAST GAME STATE ==========
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if st.session_state.game:
        st.markdown("## Last Turn Summary")
        if st.session_state.game.game_state:
            last_state = st.session_state.game.game_state[-1]
            for k, v in last_state.items():
                if k == "player_public_info_dict":
                    st.markdown(f"**The seller responded:**")
                    if isinstance(v, dict):
                        for sub_k, sub_v in v.items():
                            st.markdown(f"- **{sub_k}**: `{sub_v}`")
                            if sub_k == "message" and sub_v not in st.session_state.messages:
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": sub_v,
                                })
        
    with col1:
        # Create a scrollable container for chat messages
        chat_container = st.container(height=400)
        
        with chat_container:
            if st.session_state.messages:
                for message in st.session_state.messages:
                    st.chat_message(message.get("role")).write(message.get("content"))
            else:
                st.markdown("No messages yet.")

if __name__ == "__main__":
    main()
