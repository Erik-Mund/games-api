import time
from GameBaseAPI.utilities.cleanup import cleanup

INTERVAL = 60 * 60  # 1 hour

def run_worker():
    while True:
        try:
            cleanup()
        except Exception as e:
            print(f"Worker error: {e}")

        time.sleep(INTERVAL)

if __name__ == "__main__":
    run_worker()