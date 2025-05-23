import os
import json
import requests
from azure.identity import DefaultAzureCredential

# Configuration (replace with your values)
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT = "https://azaifoundrydem5997072235.openai.azure.com/"
API_VERSION = "2025-05-15-preview"  # Use the latest preview API version[](https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/tools/fabric)
MODEL_DEPLOYMENT_NAME = "gpt-4o-deployment"  # Your GPT-4o deployment name
FABRIC_CONNECTION_ID = "/subscriptions/5a44f788-3a03-42bf-b05d-25b0049fdb3d/resourceGroups/rg-techexcel12/providers/Microsoft.CognitiveServices/accounts/openai-bibtws7voxfo2/projects/demoproject1/connections/fabricdemoconnection"

# Instructions for the agent
AGENT_INSTRUCTIONS = """
You are a helpful sales data agent. Use the Microsoft Fabric data agent for all queries related to sales data, such as revenue, orders, or customer metrics. For non-sales-related queries, use your base knowledge from the GPT-4o model. Always provide accurate and concise responses.
"""

def get_access_token():
"""Get an access token using Azure Identity."""
credential = DefaultAzureCredential()
scope = "https://cognitiveservices.azure.com/.default"
token = credential.get_token(scope)
return token.token

def create_agent():
"""Create an Azure AI agent with Fabric data agent integration."""
url = f"{AZURE_AI_FOUNDRY_PROJECT_ENDPOINT}/assistants?api-version={API_VERSION}"
headers = {
"Authorization": f"Bearer {get_access_token()}",
"Content-Type": "application/json"
}
payload = {
"instructions": AGENT_INSTRUCTIONS,
"name": "sales-agent",
"model": MODEL_DEPLOYMENT_NAME,
"tools": [
{
"type": "fabric_dataagent",
"fabric_dataagent": {
"connections": [
{
    "connection_id": FABRIC_CONNECTION_ID
}
]
}
}
]
}
response = requests.post(url, headers=headers, json=payload)
response.raise_for_status()
return response.json()

def test_agent(agent_id, user_query):
"""Test the agent with a user query."""
# Create a thread
thread_url = f"{AZURE_AI_FOUNDRY_PROJECT_ENDPOINT}/threads?api-version={API_VERSION}"
headers = {
"Authorization": f"Bearer {get_access_token()}",
"Content-Type": "application/json"
}
thread_response = requests.post(thread_url, headers=headers, json={})
thread_response.raise_for_status()
thread_id = thread_response.json()["id"]

# Send a message
message_url = f"{AZURE_AI_FOUNDRY_PROJECT_ENDPOINT}/threads/{thread_id}/messages?api-version={API_VERSION}"
message_payload = {
"role": "user",
"content": user_query
}
message_response = requests.post(message_url, headers=headers, json=message_payload)
message_response.raise_for_status()

# Run the agent
run_url = f"{AZURE_AI_FOUNDRY_PROJECT_ENDPOINT}/threads/{thread_id}/runs?api-version={API_VERSION}"
run_payload = {
"assistant_id": agent_id
}
run_response = requests.post(run_url, headers=headers, json=run_payload)
run_response.raise_for_status()
run_id = run_response.json()["id"]

# Get the response
messages_url = f"{AZURE_AI_FOUNDRY_PROJECT_ENDPOINT}/threads/{thread_id}/messages?api-version={API_VERSION}"
response = requests.get(messages_url, headers=headers)
response.raise_for_status()
return response.json()

def main():
try:
# Create the agent
agent_response = create_agent()
agent_id = agent_response["id"]
print(f"Agent created successfully with ID: {agent_id}")

# Test the agent with a sales-related query
test_query = "What were the total sales for Q1 2025?"
response = test_agent(agent_id, test_query)
print("Agent response:")
print(json.dumps(response, indent=2))

except Exception as e:
print(f"Error: {str(e)}")

if __name__ == "__main__":
main()
