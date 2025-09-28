import sys

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "hello":
        print("Hello from the backend script! Arguments received:", sys.argv[2:])
    elif len(sys.argv) > 1 and sys.argv[1] == "status":
        print("Server status is operational.")
    else:
        # 0이 아닌 종료 코드를 반환하여 CalledProcessError를 테스트
        sys.stderr.write("Error: Invalid argument for default script.")
        sys.exit(1)
