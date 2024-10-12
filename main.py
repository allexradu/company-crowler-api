import uvicorn
import argparse

parser = argparse.ArgumentParser(description="Run the FastAPI application.")
parser.add_argument(
    '--dev', action='store_true', help='Run in development mode with hot reloading.'
)

args = parser.parse_args()

if __name__ == "__main__":
    if args.dev:
        uvicorn.run(
            "app:app", host="0.0.0.0", port=8000, server_header=False, reload=True
        )
    else:
        uvicorn.run("app:app", host="0.0.0.0", port=8000, server_header=False)