from transformers import AutoTokenizer, pipeline
import torch
import argparse

# Command line arguments parsing
parser = argparse.ArgumentParser(description="Generate C language programs")
parser.add_argument("--saveto", type=str, default="output.txt", help="File to save the output")
parser.add_argument("--iteration", type=int, default=100, help="Number of iterations to run")
args = parser.parse_args()

model = "../pretrained_model"

tokenizer = AutoTokenizer.from_pretrained(model)
pipe = pipeline(
    "text-generation",
    model=model,
    torch_dtype=torch.float16,
    device_map="auto",
)

for i in range(args.iteration):
    print(" =======================================================")
    print("")
    sequences = pipe(
        'Write a complex C language program:',
        do_sample=True,
        top_k=10,
        temperature=0.1,
        top_p=0.95,
        num_return_sequences=1,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id,
        max_length=500,
    )

    with open(args.saveto, 'w') as file:
        for seq in sequences:
            generated_text = seq['generated_text']
            file.write(f"Result: {generated_text}\n")

    with open(args.saveto, 'r') as file:
        in_code_block = False  # Track whether inside a code block
        for line in file:
            if line.strip() == r"\begin{code}":
                in_code_block = True
            elif "\end{code}" in line:
                in_code_block = False
                break
            elif in_code_block:
                print(line.strip())
    print("")
