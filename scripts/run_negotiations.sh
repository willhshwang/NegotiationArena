#!/bin/bash
#SBATCH --account=visualai    # Specify VisualAI
#SBATCH --nodes=1             # nodes requested
#SBATCH --ntasks=1            # tasks requested
#SBATCH --cpus-per-task=8    # Specify the number of CPUs your task will need.
#SBATCH --mem=50G             # memory
#SBATCH -o slurm/%j_%x_%A.out         # send stdout to outfile
#SBATCH -e slurm/%j_%x_%A.err         # send stderr to errfile
#SBATCH -t 01:00:00           # time requested in hour:minute:second
#SBATCH --array=4-4           # array job

AGENT1_MODEL="gpt-4-1106-preview"
AGENT2_MODEL="gpt-4-1106-preview"
TOTAL_NEGOTIATIONS=10
ITERATIONS=10
COST_OF_PRODUCTION=40
WILLINGNESS_TO_PAY=60
RESOURCES=100
LOG_DIR="./example_logs/buysell"
API_KEY_FILE=../tmp/.env

categories=(
    #"test"
    "syncophant"
    "nonsyncophant"
    #"neutral"
)

players=(
    "player1"
    "player2"
)

# no personas
if [ $SLURM_ARRAY_TASK_ID == 1 ]; then
    for player in "${players[@]}"; do
        echo "no personas"
        python -m experiments.run_negotiations \
            --agent1_model $AGENT1_MODEL \
            --agent2_model $AGENT2_MODEL \
            --total_negotiations $TOTAL_NEGOTIATIONS \
            --iterations $ITERATIONS \
            --cost_of_production $COST_OF_PRODUCTION \
            --willingness_to_pay $WILLINGNESS_TO_PAY \
            --resources $RESOURCES \
            --${player}_is_seller \
            --log_dir "$LOG_DIR/${player}_seller/no_persona/" \
            --api_key_file $API_KEY_FILE
    done

fi

# one player has persona
if [ $SLURM_ARRAY_TASK_ID == 3 ]; then
    for category1 in "${categories[@]}"; do
        for category2 in "${categories[@]}"; do
            echo "seller persona: $category1 | buyer persona: $category2"
            python -m experiments.run_negotiations \
                --agent1_model $AGENT1_MODEL \
                --agent2_model $AGENT2_MODEL \
                --total_negotiations $TOTAL_NEGOTIATIONS \
                --iterations $ITERATIONS \
                --cost_of_production $COST_OF_PRODUCTION \
                --willingness_to_pay $WILLINGNESS_TO_PAY \
                --resources $RESOURCES \
                --player1_persona_file "./personas/outputs/${category1}_personas.json" \
                --player2_persona_file "./personas/outputs/${category2}_personas.json" \
                --player2_is_seller \
                --log_dir $LOG_DIR/player1_${category1}_player2_${category2}/ \
                --api_key_file $API_KEY_FILE
        done
    done
fi


# players have same personas  
if [ $SLURM_ARRAY_TASK_ID == 3 ]; then
    for category1 in "${categories[@]}"; do
        for category2 in "${categories[@]}"; do
            echo "seller persona: $category1 | buyer persona: $category2"
            python -m experiments.run_negotiations \
                --agent1_model $AGENT1_MODEL \
                --agent2_model $AGENT2_MODEL \
                --total_negotiations $TOTAL_NEGOTIATIONS \
                --iterations $ITERATIONS \
                --cost_of_production $COST_OF_PRODUCTION \
                --willingness_to_pay $WILLINGNESS_TO_PAY \
                --resources $RESOURCES \
                --player1_persona_file "./personas/outputs/${category1}_personas.json" \
                --player2_persona_file "./personas/outputs/${category2}_personas.json" \
                --player2_is_seller \
                --log_dir $LOG_DIR/player1_${category1}_player2_${category2}/ \
                --api_key_file $API_KEY_FILE
        done
    done
fi

# players have different personas  
if [ $SLURM_ARRAY_TASK_ID == 3 ]; then
    for category1 in "${categories[@]}"; do
        for category2 in "${categories[@]}"; do
            echo "seller persona: $category1 | buyer persona: $category2"
            python -m experiments.run_negotiations \
                --agent1_model $AGENT1_MODEL \
                --agent2_model $AGENT2_MODEL \
                --total_negotiations $TOTAL_NEGOTIATIONS \
                --iterations $ITERATIONS \
                --cost_of_production $COST_OF_PRODUCTION \
                --willingness_to_pay $WILLINGNESS_TO_PAY \
                --resources $RESOURCES \
                --player1_persona_file "./personas/outputs/${category1}_personas.json" \
                --player2_persona_file "./personas/outputs/${category2}_personas.json" \
                --player2_is_seller \
                --log_dir $LOG_DIR/player1_${category1}_player2_${category2}/ \
                --api_key_file $API_KEY_FILE
        done
    done
fi

echo "Done!"

