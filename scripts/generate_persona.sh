#!/bin/bash

MODEL=gpt-4-1106-preview
API_KEY_FILE=../tmp/.env
categories=(
    #"test"
    "syncophant"
    "nonsyncophant"
    "neutral"
)

for category in "${categories[@]}"; do
    echo "Generating personas for $category"

    python -m experiments.generate_persona \
        --category $category \
        --model $MODEL \
        --api_key_file $API_KEY_FILE \
        --output_file "./personas/outputs/${category}_personas.json" \
        --input_file "./personas/inputs/${category}_personas.txt" \

done

echo "Done!"

