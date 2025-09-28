import requests
import json

HOST_URL = "http://localhost:5000/api/execute"

def send_command(command):
    """
    사용자 명령어를 호스트 API로 전송합니다.
    """
    headers = {'Content-Type': 'application/json'}
    payload = {'command': command}

    try:
        response = requests.post(HOST_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # 200 OK가 아니면 예외 발생
        
        response_data = response.json()
        print("--- Host Response ---")
        print(f"Status: {response_data.get('status')}")
        print(f"Message: {response_data.get('message')}")
        if 'output' in response_data:
            print(f"Output:\n{response_data['output']}")
        print("---------------------")

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to host: {e}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON response from host: {response.text}")

if __name__ == "__main__":
    print("Welcome to the Client CLI. Enter 'exit' to quit.")
    
    while True:
        user_input = input("> ")
        if user_input.lower() == "exit":
            break
        
        send_command(user_input)
