import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python my_script.py <command>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "hello":
        print("Hello from the host!")
    elif command == "status":
        print("Host system status: OK")
    elif command == "clone_repo":
        # 이 부분에 실제 git clone 로직을 추가
        print("Simulating a git clone operation...")
        print("Repository cloned successfully.")
    else:
        print(f"Unknown command received: {command}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
