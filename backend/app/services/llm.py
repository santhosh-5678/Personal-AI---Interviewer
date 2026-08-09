from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_NAME = "HuggingFaceTB/SmolLM2-135M-Instruct"

print("Loading model...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

print("Model loaded successfully.")


def generate_interview_response(messages):

    prompt = ""

    for message in messages:
        role = message["role"]
        content = message["content"]

        prompt += f"{role}: {content}\n"

    prompt += "assistant:"

    inputs = tokenizer(
        prompt,
        return_tensors="pt"
    )

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )

    generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]

    response = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True
    )

    return response.strip()