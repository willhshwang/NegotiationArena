import os 
import json
import argparse
from openai import OpenAI
from dotenv import load_dotenv


def get_user_prompt(persona):

    article = "an" if persona[0].lower in ['a', 'e', 'i', 'o', 'u'] else "a"
    prompt = f'''Describe the social behavior of {article} {persona} person. 
    Focus on how they interact with others, their personality, and their interests.
    Your response should be less than 3 sentences. 
    Your response should start with "You are {article} {persona} person ... ".
    ''' 

    return prompt


def main(args):

    personas = open(args.input_file, "r").read().splitlines()

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    result_dict = {}
    for persona in personas:
        print(f"generate persona: {persona}", flush = True)
        conversation = [
            {
                "role": "user",
                "content": get_user_prompt(persona)
            },
        ]

        chat = client.chat.completions.create(
            model=args.model,
            messages=conversation,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )
        response = chat.choices[0].message.content
        response = response.replace("\n", " ")
        result_dict[persona] = response
        
    with open(args.output_file, "w") as f:
        json.dump(result_dict, f, indent=2)

    return 0


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser() 
    arg_parser.add_argument("--category", type=str, default = "test") 
    arg_parser.add_argument("--model", type=str, default = "gpt-4-1106-preview")   
    arg_parser.add_argument("--temperature", type=float, default = 0.7)
    arg_parser.add_argument("--max_tokens", type=int, default = 400) 
    arg_parser.add_argument("--api_key_file", type=str, default = "../../tmp/.env")
    arg_parser.add_argument("--output_file", type=str, default = "../personas/outputs/test_personas.json") 
    arg_parser.add_argument("--input_file", type=str, default = "./personas/inputs/test_personas.txt")
    args = arg_parser.parse_args()

    # load the api key
    load_dotenv(dotenv_path=args.api_key_file)  

    ret = main(args) 
    exit(ret)
