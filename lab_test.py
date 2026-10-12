from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6",
    input="Explain what an AI agent is in exactly two sentences."
)

print(response.output_text)