import streamlit as st
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

def main():
    st.title("Negotiation Arena")

    # ========== USER INPUT FORM ==========
    with st.form(key="user_input"):
        decision = st.radio("Do you want to accept the proposal?", ["yes", "no"])
        price = st.text_input("Counter offer price (only if proposing):")
        message = st.text_area("Message to other player (only if proposing):")

        submitted = st.form_submit_button("Submit Response")
        if submitted:
            st.session_state.human_decision = decision
            st.session_state.counter_offer_price = price
            st.session_state.counter_offer_message = message
            st.session_state.submitted = True

    # ========== INITIALIZE SESSION STATE ==========
    if "started" not in st.session_state:
        st.session_state.started = False
    if "game" not in st.session_state:
        st.session_state.game = None
    if "game_over" not in st.session_state:
        st.session_state.game_over = False

    # ========== START GAME ONLY ONCE ==========
    if not st.session_state.started:
        try:
            a1 = ChatGPTAgent(agent_name=AGENT_ONE, model="gpt-4o-mini")
            a2 = HumanAgent(agent_name=AGENT_TWO)

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
                    "You are a stubborn, unyielding seller that has been successful by playing this part. You should always be careful about rejecting, however, as you will end the game and walk away with nothing.",
                    ""
                ],
                player_trade_environment=[
                    "You have ten customers lining up to buy your product.",
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

    # ========== RUN ONE TURN ON BUTTON PRESS ==========
    if st.session_state.started and st.button("Run Next Turn"):
        try:
            if not st.session_state.game_over:
                st.session_state.game.run_one_turn()
            if not st.session_state.game_over:
                st.session_state.game.run_one_turn()
        except Exception as e:
            st.error(f"Turn failed: {e}")
            st.text(traceback.format_exc())

    # ========== DISPLAY LAST GAME STATE ==========
    if st.session_state.game:
        st.markdown("## Last Turn Summary")
        if st.session_state.game.game_state:
            last_state = st.session_state.game.game_state[-1]
            for k, v in last_state.items():
                st.markdown(f"**{k}**: `{v}`" if not isinstance(v, dict) else f"**{k}**:")
                if isinstance(v, dict):
                    for sub_k, sub_v in v.items():
                        st.markdown(f"- `{sub_k}`: `{sub_v}`")

if __name__ == "__main__":
    main()
