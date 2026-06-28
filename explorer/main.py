import typer
from scanner import run

def main(host: str = "192.168.1.191"):
    run(host)

if __name__ == "__main__":
    typer.run(main)