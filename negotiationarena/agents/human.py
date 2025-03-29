import os
from negotiationarena.agents.agents import Agent
from negotiationarena.constants import AGENT_TWO, AGENT_ONE
from negotiationarena.agents.agent_behaviours import SelfCheckingAgent
from copy import deepcopy
from negotiationarena.constants import *


class HumanAgent(Agent):
    def __init__(
        self,
        agent_name: str,
        *args,
        **kwargs # added args and kwargs for debugging
    ):
        super().__init__(agent_name)
        self.conversation = []

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
        print(self.conversation[-1]["content"], flush = True)  # Print the last message from the conversation for reference
        if "PROPOSAL" in self.conversation[-1]["content"]:
            choice = ""
            while choice.lower() not in ['yes', 'no']:
                choice = input("Do you want to accept the proposal? (yes/no): ")
                if choice.lower() == "yes":
                    message = f"<{PROPOSAL_COUNT_TAG}> 1 </{PROPOSAL_COUNT_TAG}>\n"                    # nonessential tag
                    message += f"<{RESOURCES_TAG}> ZUP: 100 </{RESOURCES_TAG}>\n"                      # nonessential tag
                    message += f"<{GOALS_TAG}> Buy X for the minimum amount of ZUP. </{GOALS_TAG}>\n"  # nonessential tag
                    message += f"<{REASONING_TAG}>  </{REASONING_TAG}>\n"                              # nonessential tag         
                    message += f"<{PLAYER_ANSWER_TAG}> ACCEPT </{PLAYER_ANSWER_TAG}>\n"               
                    message += f"<{PROPOSED_TRADE_TAG}> NONE </{PROPOSED_TRADE_TAG}>\n"              
                    message += f"<{MESSAGE_TAG}> NONE </{MESSAGE_TAG}>"                                # nonessential tag
                else:
                    counter_offer_price = ""
                    while not counter_offer_price.isdigit():
                        counter_offer_price = input(f"Propose a counter offer. Respond with an integer.\n")  # make sure the input is an integer
                    counter_offer_message = input(f"Create a message to send to the other player. Remember, you proposed {counter_offer_price} ZUP for 1 X.\n")  # later we need to make sure counter_offer_price is equal to the price stated in the message
                    
                    message = f"<{PROPOSAL_COUNT_TAG}> 1 </{PROPOSAL_COUNT_TAG}>\n"                    # nonessential tag
                    message += f"<{RESOURCES_TAG}> ZUP: 100 </{RESOURCES_TAG}>\n"                      # nonessential tag
                    message += f"<{GOALS_TAG}> Buy X for the minimum amount of ZUP. </{GOALS_TAG}>\n"  # nonessential tag
                    message += f"<{REASONING_TAG}>  </{REASONING_TAG}>\n"                              # nonessential tag         
                    message += f"<{PLAYER_ANSWER_TAG}> PROPOSAL </{PLAYER_ANSWER_TAG}>\n"
                    message += f"<{PROPOSED_TRADE_TAG}> {AGENT_ONE} Gives X: 1 | {AGENT_TWO} Gives ZUP: {counter_offer_price} </{PROPOSED_TRADE_TAG}>\n" # Only in one item trade setting and currency is ZUP
                    message += f"<{MESSAGE_TAG}> {counter_offer_message} </{MESSAGE_TAG}>"
                    
        return message

    def update_conversation_tracking(self, role, message):
        self.conversation.append({"role": role, "content": message})


class SelfCheckingHumanAgent(HumanAgent, SelfCheckingAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
