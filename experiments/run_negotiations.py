import os
import sys
import json
import random
import argparse

from dotenv import load_dotenv

sys.path.append('../')
from negotiationarena.agents.chatgpt import ChatGPTAgent
from negotiationarena.game_objects.resource import Resources
from negotiationarena.game_objects.goal import BuyerGoal, SellerGoal
from negotiationarena.game_objects.valuation import Valuation
from negotiationarena.constants import AGENT_ONE, AGENT_TWO, MONEY_TOKEN
import traceback
from games.buy_sell_game.game import BuySellGame


def main(args):

    player1_personas = json.load(open(args.player1_persona_file, "r")) if len(args.player1_persona_file) > 0 else None
    player2_personas = json.load(open(args.player2_persona_file, "r")) if len(args.player2_persona_file) > 0 else None

    for i in range(args.total_negotiations):
        player1_persona, player2_persona = "", ""
        if player1_personas is not None: 
            player1_persona_key = random.choice(list(player1_personas.keys()))
            player1_persona = player1_personas[player1_persona_key]
        if player2_personas is not None:
            player2_persona_key = random.choice(list(player2_personas.keys()))
            player2_persona = player2_personas[player2_persona_key]

        print("====================================================", flush = True)
        print(f"negotiation round {i}", flush = True)
        print(f"player1 persona: {player1_persona} | player2 persona: {player2_persona}", flush = True)
        print("====================================================", flush = True)
        
        try:
            a1 = ChatGPTAgent(agent_name=AGENT_ONE, model=args.agent1_model)
            a2 = ChatGPTAgent(agent_name=AGENT_TWO, model=args.agent2_model)

            if args.player1_is_seller:
                c = BuySellGame(
                    players=[a1, a2],
                    iterations=args.iterations,
                    player_goals=[
                        SellerGoal(cost_of_production=Valuation({"X": args.cost_of_production})),
                        BuyerGoal(willingness_to_pay=Valuation({"X": args.willingness_to_pay})),
                    ],
                    player_starting_resources=[
                        Resources({"X": 1}),
                        Resources({MONEY_TOKEN: args.resources}),
                    ],
                    player_conversation_roles=[
                        f"You are {AGENT_ONE}.",
                        f"You are {AGENT_TWO}.",
                    ],

                    # new social behaviors
                    player_social_behaviour=[
                        player1_persona,
                        player2_persona        
                    ],
                    log_dir= args.log_dir,
                )
            elif args.player2_is_seller:
                c = BuySellGame(
                    players=[a1, a2],
                    iterations=args.iterations,
                    player_goals=[
                        BuyerGoal(willingness_to_pay=Valuation({"X": args.willingness_to_pay})),
                        SellerGoal(cost_of_production=Valuation({"X": args.cost_of_production})),
                    ],
                    player_starting_resources=[
                        Resources({MONEY_TOKEN: args.resources}),
                        Resources({"X": 1}),
                    ],
                    player_conversation_roles=[
                        f"You are {AGENT_ONE}.",
                        f"You are {AGENT_TWO}.",
                    ],

                    # new social behaviors
                    player_social_behaviour=[
                        player1_persona,
                        player2_persona        
                    ],
                    log_dir= args.log_dir,
                )
                
            c.run()
        except Exception as e:
            pass

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Negotiation Arena')
    parser.add_argument('--agent1_model', type=str, default ='gpt-4-1106-preview')
    parser.add_argument('--agent2_model', type=str, default='gpt-4-1106-preview')
    parser.add_argument('--total_negotiations', type=int, default=10)
    parser.add_argument('--iterations', type=int, default=10)
    parser.add_argument('--cost_of_production', type=int, default = 40)
    parser.add_argument('--willingness_to_pay', type=int, default = 60)
    parser.add_argument('--resources', type=int, default = 100)
    parser.add_argument('--player1_persona_file', type=str, default = "")
    parser.add_argument('--player2_persona_file', type=str, default = "")
    parser.add_argument('--player1_is_seller', action = "store_true", default = False)
    parser.add_argument('--player2_is_seller', action = "store_true", default = False)
    parser.add_argument('--log_dir', type=str, default = "../example_logs/buysell")
    parser.add_argument('--api_key_file', type=str, default = "../../tmp/.env")
    args = parser.parse_args()
    
    assert(args.player1_is_seller != args.player2_is_seller)

    # load the api key
    load_dotenv(dotenv_path=args.api_key_file)  
    
    ret = main(args)
    exit(ret)