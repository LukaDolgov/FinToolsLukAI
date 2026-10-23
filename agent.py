import json
from dotenv import load_dotenv
from openai import OpenAI

from tools import calculate_return, moving_average

load_dotenv()
client = OpenAI()

#availible tools for model (descriptions)
TOOLS = [
{
    "type": "function",
    "name": "calculate_return",
    "description": "Calculate a stock's price return",
    "parameters": {
        "type": "object",
        "properties": {
            "start_price": {"type": "number"},
            "end_price": {"type": "number"}
        },
        "required": ["start_price", "end_price"],
        "additionalProperties": False
    },
    "strict": True
},
{
    "type": "function",
    "name": "moving_average",
    "description": "Calculate the average of last N prices",
    "parameters": {
        "type": "object",
        "properties": {
            "prices": {
                "type": "array",
                "items": {"type": "number"}
            },
            "window": {"type": "integer"}
        },
        "required": ["prices", "window"],
        "additionalProperties": False
    },
    "strict": True
}
]

#tool dispatcher
def execute_tool(name: str, args: dict):
    if name == "calculate_return":
        return calculate_return(
            args["start_price"],
            args["end_price"]
        )

    elif name == "moving_average":
        return moving_average(
            args["prices"],
            args["window"]
        )

    else:
        raise ValueError(f"Unknown tool: {name}")
    
def ask_agent(question: str):
    conversation = [
        {"role": "user", "content": question}
    ]
    total_cost = 0.0
    for step in range(5):
        response = client.responses.create(
            model="gpt-5-mini",
            instructions=(
                "You are a financial math assistant. "
                "Use tools for all numerical calculations. "
                "The moving_average tool returns only the average "
                "of the final N prices, not a complete time series. "
                "Do not invent additional calculated values. "
                "If a user asks for a complete moving-average series, "
                "explain that the current tool only supports the "
                "most recent window. "
                "Explain stock returns as percentages."
            ),
            input=conversation,
            tools=TOOLS,
            store=False
        )
        usage = response.usage
        cost = (
            usage.input_tokens * 0.25
            + usage.output_tokens * 2.00
        ) / 1_000_000
        total_cost += cost
        print(f"[API COST] ${cost:.6f}")
        for item in response.output:
            conversation.append(item.model_dump(exclude_none=True))
        tool_calls = []
        for item in response.output:
            if item.type == "function_call":
                tool_calls.append(item)
        if not tool_calls:
            print(f"Total API cost: ${total_cost:.6f}")
            return response.output_text
        for call in tool_calls:
            print(f"Requested tool: {call.name}")
            try:
                args = json.loads(call.arguments)
                result = execute_tool(call.name, args)
                tool_output = json.dumps({"result": result})
            except (ValueError, KeyError, TypeError) as error:
                tool_output = json.dumps({"error": str(error)})
            print(f"Tool returned: {tool_output}")
            conversation.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": tool_output
            })     
    return "Agent stopped: maximum iterations reached."
    

if __name__ == "__main__":
    print("Welcome to FinToolsLukAI!")
    print("Type 'quit' to exit.\n")
    while True:
        question = input("You: ").strip()
        if question.lower() == "quit":
            print("Goodbye!")
            break
        if not question:
            continue
        try:
            answer = ask_agent(question)
            print(f"\nAI: {answer}\n")
        except Exception as error:
            print(f"Error: {error}")
