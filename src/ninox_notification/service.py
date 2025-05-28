import time
import schedule
from .notify import main as notify_once
from .config import load_config


def run(config_path: str):
    cfg = load_config(config_path)

    def job():
        try:
            notify_once(config_path)
        except Exception as exc:
            print(f"Error running notification job: {exc}")

    schedule.every().day.at(cfg.send_time).do(job)
    print(f"Scheduler started. Sending notifications daily at {cfg.send_time}.")
    while True:
        schedule.run_pending()
        time.sleep(1)


def cli():
    import sys
    if len(sys.argv) < 2:
        print("Usage: notify_service.py <config.yaml>")
        raise SystemExit(1)
    run(sys.argv[1])


if __name__ == "__main__":
    cli()
