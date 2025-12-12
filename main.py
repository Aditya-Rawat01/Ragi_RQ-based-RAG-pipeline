import uvicorn
from server import app

def main():
    uvicorn.run(app, port=8080, host="0.0.0.0")


if __name__ == "__main__":
    main()
