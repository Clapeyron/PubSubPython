import time
from scrap_api import Scraper
from web_topics import tf


MY_TOKEN = "9xsE-ce8ZzRUIFogsEMZSWuHVoT7C9etEUx7qvyO-dtTUiXMUch_gO6IAYMATLk9UwEzwqaFEc9zvBJ9MfByuQ"


if __name__=="__main__":
    scraper = Scraper(token=MY_TOKEN)
    while True:
        msgs = scraper.scrap()
        print(f"Last scrapped messages {scraper.last_point}:\n{msgs}")
        for msg in msgs:
            if msg["action"] == "pub":
                chnl = msg["channel"]
                parts = chnl.split(".", 1)
                if parts[0] != "pubsub":
                    print(f"Warning: message adressed to non-pubsub channel '{chnl}', that is not supported yet")
                    continue
                try: tf.write(parts[1], msg["body"])
                except Exception as e: print(f"Error while publishing: {e}")
            else:
                pass #TODO: обработать другие actions
        time.sleep(1)