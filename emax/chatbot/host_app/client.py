import requests
import json

def send_command_to_host(command_name):
    """
    Sends a command to the host's Flask API.
    """
    # Assuming the host's IP is 172.17.0.1 (Docker default gateway) and API port is 5000
    host_url = "http://host.docker.internal:5000/api/execute" # For Docker Desktop
    # host_url = "http://172.17.0.1:5000/api/execute" # For Linux Docker
    
    headers = {'Content-Type': 'application/json'}
    payload = {'command': command_name}

    try:
        response = requests.post(host_url, headers=headers, data=json.dumps(payload))
        response_data = response.json()
        print(f"Status: {response_data.get('status')}")
        print(f"Message: {response_data.get('message')}")
        if 'output' in response_data:
            print(f"Output:\n{response_data['output']}")
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

# Example usage in your chatbot's code
send_command_to_host("run_my_script")
