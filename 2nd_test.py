import numpy as np
from llm_sdk import Small_LLM_Model

def main():
    print("Loading Custom SDK and model.... (this may take a moment :))")
    model = Small_LLM_Model(model_name="Qwen/Qwen2.5-0.5B-Instruct")

    eos_token_id = model._tokenizer.eos_token_id

    print("\Model ready! Type 'exit' to quit.")
    print("-" * 50)

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit', 'bye bye']:
            break

        formated_prompt = f"<|im_start|>user\n{user_input}<|im_end|>\n<|im_end|>\n<|im_start|>assistant\n"

        input_ids = model.encode(formated_prompt).tolist()[0]

        generated_ids = []
        print("AI:", end="", flush=True)

        for _ in range(250):

            current_context = input_ids + generated_ids

            logits = model.get_logits_from_input_ids(current_context)

            next_token_id = int(np.argmax(logits))

            if next_token_id == eos_token_id:
                break

            generated_ids.append(next_token_id)

            token_str = model.decode([next_token_id])
            print(token_str, end="", flush=True)

        print()

if __name__ == "__main__":
    main()