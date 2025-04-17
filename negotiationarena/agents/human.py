import copy
import os

import os
import streamlit as st
import random
from negotiationarena.agents.agents import Agent
import time
from negotiationarena.constants import *
from negotiationarena.agents.agent_behaviours import SelfCheckingAgent
from copy import deepcopy

class HumanAgent(Agent):
    def __init__(
        self,
        agent_name: str,
        *args,
        **kwargs # added args and kwargs for debugging
    ):
        super().__init__(agent_name)
        self.conversation = []
        self.proposal_count = 0

    def init_agent(self, system_prompt, role):
        if AGENT_ONE in self.agent_name:
            # we use the user role to tell the assistant that it has to start.

            self.update_conversation_tracking(
                self.prompt_entity_initializer, system_prompt
            )
            self.update_conversation_tracking("user", role)
        elif AGENT_TWO in self.agent_name:
            system_prompt = system_prompt + role
            self.update_conversation_tracking(
                self.prompt_entity_initializer, system_prompt
            )
        else:
            raise "No Player 1 or Player 2 in role"

    def __deepcopy__(self, memo):
        """
        Deepcopy is needed because we cannot pickle the llama object.
        :param memo:
        :return:
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == "client" and not isinstance(v, str):
                v = v.__class__.__name__
            setattr(result, k, deepcopy(v, memo))
        return result

    def chat(self):
        self.proposal_count += 1

        # Create persistent keys if not already set
        if "human_decision" not in st.session_state:
            st.session_state.human_decision = None
        if "counter_offer_price" not in st.session_state:
            st.session_state.counter_offer_price = ""
        if "counter_offer_message" not in st.session_state:
            st.session_state.counter_offer_message = ""
        if "submitted" not in st.session_state:
            st.session_state.submitted = False

        # Wait loop until user responds
        while not st.session_state.submitted:
            st.warning("Waiting for user input...")
            st.stop()  # Pauses Streamlit execution — resumes on rerun

        decision = st.session_state.human_decision
        counter_offer_price = st.session_state.counter_offer_price
        counter_offer_message = st.session_state.counter_offer_message

        # Reset submission flag after response is used
        st.session_state.submitted = False
        st.session_state.human_decision = None
        st.session_state.counter_offer_price = ""
        st.session_state.counter_offer_message = ""

        message = ""
        if "PROPOSAL" in self.conversation[-1]["content"]:
            if decision.lower() == "yes":
                message += f"<{PROPOSAL_COUNT_TAG}> {self.proposal_count} </{PROPOSAL_COUNT_TAG}>\n"
                message += f"<{RESOURCES_TAG}> ZUP: 100 </{RESOURCES_TAG}>\n"
                message += f"<{GOALS_TAG}> Buy X for the minimum amount of ZUP. </{GOALS_TAG}>\n"
                message += f"<{REASONING_TAG}> NONE </{REASONING_TAG}>\n"
                message += f"<{PLAYER_ANSWER_TAG}> ACCEPT </{PLAYER_ANSWER_TAG}>\n"
                message += f"<{PROPOSED_TRADE_TAG}> NONE </{PROPOSED_TRADE_TAG}>\n"
                message += f"<{MESSAGE_TAG}> NONE </{MESSAGE_TAG}>"
            else:
                if not counter_offer_price.isdigit():
                    raise ValueError("Counter offer price must be a number")
                message += f"<{PROPOSAL_COUNT_TAG}> {self.proposal_count} </{PROPOSAL_COUNT_TAG}>\n"
                message += f"<{RESOURCES_TAG}> ZUP: 100 </{RESOURCES_TAG}>\n"
                message += f"<{GOALS_TAG}> Buy X for the minimum amount of ZUP. </{GOALS_TAG}>\n"
                message += f"<{REASONING_TAG}> </{REASONING_TAG}>\n"
                message += f"<{PLAYER_ANSWER_TAG}> PROPOSAL </{PLAYER_ANSWER_TAG}>\n"
                message += f"<{PROPOSED_TRADE_TAG}> {AGENT_ONE} Gives X: 1 | {AGENT_TWO} Gives ZUP: {counter_offer_price} </{PROPOSED_TRADE_TAG}>\n"
                message += f"<{MESSAGE_TAG}> {counter_offer_message} </{MESSAGE_TAG}>"

        return message


    def update_conversation_tracking(self, role, message):
        self.conversation.append({"role": role, "content": message})


class SelfCheckingHumanAgent(HumanAgent, SelfCheckingAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
