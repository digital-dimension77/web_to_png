import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image

LOG_FILE = r"The_log_file"
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG,
                    format="%(asctime)s - %(message)s")

WATCH_FOLDER = r"The folder to be watched"

logging.getLogger("PIL").setLevel(logging.ERROR)
logging.getLogger("watchdog").setLevel(logging.WARNING)


class WebpToPngConverter(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        filepath = event.src_path
        logging.info(f"File detected: {filepath}")

        if filepath.lower().endswith(".webp"):
            self.retry_convert(filepath)

    def retry_convert(self, webp_path, retries=5, delay=2):
        for attempt in range(retries):
            try:
                png_path = os.path.splitext(webp_path)[0] + ".png"
                with Image.open(webp_path) as img:
                    img.save(png_path, "PNG")

                os.remove(webp_path)
                logging.info(
                    f"Converted and deleted: {webp_path} -> {png_path}")
                return
            except PermissionError:
                logging.warning(
                    f"File locked. Retrying {attempt + 1}/{retries}...")
                time.sleep(delay)
        logging.error(
            f"Failed to process {webp_path} after {retries} attempts.")


def start_watching(folder):
    observer = Observer()
    event_handler = WebpToPngConverter()
    observer.schedule(event_handler, folder, recursive=True)
    observer.start()
    logging.info(f"Monitoring '{folder}' for .webp files...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    start_watching(WATCH_FOLDER)
