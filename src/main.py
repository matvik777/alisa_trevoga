from alisa_api import run_scenario, AlisaAPIError


def main() -> None:
    try:
        result = run_scenario()
        print("Scenario started successfully")
        print(result)
    except AlisaAPIError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()