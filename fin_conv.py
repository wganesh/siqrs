import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"

# Device: Apple Silicon (MPS)
device = "mps" if torch.backends.mps.is_available() else "cpu"

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_ID,
    trust_remote_code=True
)

# Load model
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float16,
    device_map=None,
    trust_remote_code=True
).to(device)

model.eval()

def ask(question, max_new_tokens=256):
    prompt = f"<|user|>\n{question}<|end|>\n<|assistant|>"

    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=0.0,
            use_cache=False,   # MPS stability
            pad_token_id=tokenizer.eos_token_id
        )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# -----------------------------
# CLI loop
# -----------------------------
print("\nPhi-3 Mini Q&A (type exit() to quit)\n")

while True:
    try:
        question = input(">> ")

        if question.strip().lower() == "exit()":
            print("Exiting. Goodbye!")
            break

        if not question.strip():
            continue

        answer = ask(question)
        print("\n" + answer + "\n")

    except KeyboardInterrupt:
        print("\nInterrupted. Type exit() to quit.")
