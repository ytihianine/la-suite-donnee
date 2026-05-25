from infra.http.ping import ping
from utils.settings import load_settings


def main() -> None:
    print("Hello world")
    ping_result = ping("https://example.com")
    print(f"Ping result: {ping_result}")
    print(load_settings().model_dump())


if __name__ == "__main__":
    main()
