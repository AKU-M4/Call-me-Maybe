import json
import numpy as np
from pathlib import Path
from llm_sdk import Small_LLM_Model


DEFAULT_PROMPTS = Path("data/input/function_calling_tests.json")
DEFAULT_FN_CALLS = Path("data/input/functions_definition.json")
DEFAULT_OUTPUT = Path("data/output/function_calls.json")

class AssistanceModel(Small_LLM_Model):
    def __init__(self) -> None:
        super().__init__()
        self.eos_token_id = self._tokenizer.eos_token_id

    def read_fn_calls(self, path: Path) -> list[dict]:
        with open(path, "r") as file:
            loaded_fns = json.load(file)
        return loaded_fns

    def read_prompts(self, path: Path) -> list[str]:
        with open(path, "r") as file:
            loaded_prompts = json.load(file)
        prompts = [item['prompt'] for item in loaded_prompts]
        return prompts
    
    def generated_response(self, formatted_prompt: str) -> str:
            """Helper method that handles the token generation loop."""
            input_ids = self.encode(formatted_prompt).tolist()[0]
            generated_ids = []

            for _ in range(250):
                current_context = input_ids + generated_ids
                logits = self.get_logits_from_input_ids(current_context)
                next_token_id = int(np.argmax(logits))
                
                if next_token_id == self.eos_token_id:
                    break
                    
                generated_ids.append(next_token_id)
                
                # Decode and print just the newest token
                new_token_str = self.decode([next_token_id])
                print(new_token_str, end="", flush=True)
                
            print() # Drop to a new line when the loop finishes
            return self.decode(generated_ids)
    
    def run_option_1(self) -> None:
        """Handles normal chat assistance."""
        print("\n--- Normal Assistance Mode ---")
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit', 'done', 'out']:
                break
            print("Model is Thinking...")
            response = self.generated_response(user_input)
            print(f"Model: {response}\n")
    
    def run_option_2(self) -> None:
        """Handles batch processing of JSON prompts for function calling."""
        print("---\n JSON Function Calling Mode ---")
        fn_descriptions = self.read_fn_calls(DEFAULT_FN_CALLS)
        user_prompts = self.read_prompts(DEFAULT_PROMPTS)

        for prompt in prompts:
            formated_prompt = (
                f"You are a strict JSON function calling AI.\n"
                f"Available functions:\n{json.dumps(fn_descriptions, indent=2)}\n\n"
                f"User request: {prompt}\n\n"
                f"Respond with a complete JSON object matching the exact schema.\n"
            )
            print(f"Processing prompt: {prompt}")
            response_str = self.generated_response(formated_prompt)

            try:
                response_json = json.loads(response_str)
                results.append({"prompt":prompt, "function_call": response_json})
            except json.JSONDecodeError:
                print(f"Warning Model did not output valid JSON for prompt: {prompt}")
                results.append({"prompt": prompt, "raw_ouput": response_str})
        
        with open(DEFAULT_OUTPUT, "w") as file:
            json.dump(results, indent=4)
            print(f"Finished processing. Results saved to {DEFAULT_OUTPUT}")
    
    
    def start(self) -> None:
        """Main rooting loop"""
        print("\n Model Ready!")
        print("*" * 50)
        while True:
            option = input("\nType |1| for normal assistance\nType |2| for JSON function calling assistance\nType |exit| to quit\nChoice: ")
                
            if option == '1':
                self.run_option_1()
            elif option == '2':
                self.run_option_2()
            elif option.lower() in ['exit', 'quit']:
                print("Shutting down...")
                break
            else:
                print("Invalid option. Please enter 1 or 2.")

def main() -> None:
    app = AssistanceModel()
    app.start()
        
if __name__ == "__main__":
    main()