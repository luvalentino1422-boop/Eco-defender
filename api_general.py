from openai import OpenAI

# Crear el cliente con tu API key de Poe
client = OpenAI(
    api_key="4-R6SMoRpTNNVqb4uVa0cnkn8b7MCt7C5v6iH93VQ8k",  # o usa os.getenv("POE_API_KEY")
    base_url="https://api.poe.com/v1",
)

# Crear una conversación simple
response = client.chat.completions.create(
    model="General_defenders",  # nombre del bot/modelo en Poe
    messages=[
        {"role": "user", "content": "Hello world"}
    ],
)

print(response.choices[0].message["content"])