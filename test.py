import numpy as np
from llm_sdk import Small_LLM_Model

def main():
    print("Loading custom SDK and model... (This takes a moment)")
    # We use the Instruct version so it answers questions properly
    model = Small_LLM_Model(model_name="Qwen/Qwen2.5-0.5B-Instruct") 
    
    # We need the End-Of-Sequence (EOS) token ID so we know when to stop the loop
    eos_token_id = model._tokenizer.eos_token_id

    print("\nModel ready! Type 'exit' to quit.")
    print("-" * 50)
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        # 1. Format the Prompt
        # Qwen-Instruct expects this specific wrapper around user inputs
        formatted_prompt = f"<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n"
        
        # 2. ENCODE: Convert string to list of IDs
        # Your encode() returns a 2D tensor, so we convert it to a flat Python list
        input_ids = model.encode(formatted_prompt).tolist()[0]
        
        generated_ids = []
        print("AI: ", end="", flush=True)
        
        # 3. The Generation Loop (Predicting token by token)
        for _ in range(250):  # Maximum tokens to generate
            
            # Feed the model the prompt PLUS everything it has generated so far
            current_context = input_ids + generated_ids
            
            # 4. LOGITS: Get the raw scores for the next token
            logits = model.get_logits_from_input_ids(current_context)
            
            # 5. GREEDY SEARCH: Pick the token ID with the absolute highest score
            next_token_id = int(np.argmax(logits))
            
            # If the model decides the sentence is over, break the loop early
            if next_token_id == eos_token_id:
                break
                
            # Add the new token to our tracking list
            generated_ids.append(next_token_id)
            
            # 6. DECODE: Convert the single new token ID back to a string and print it
            # This creates a "typewriter" streaming effect in your console
            token_str = model.decode([next_token_id])
            print(token_str, end="", flush=True)
            
        print() # Add a newline when the AI finishes speaking

if __name__ == "__main__":
    main()