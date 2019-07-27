import time
from scrap_api import Scraper
from web_topics import web2topic, TopicOutThreadFactory


MY_TOKEN = "9xsE-ce8ZzRUIFogsEMZSWuHVoT7C9etEUx7qvyO-dtTUiXMUch_gO6IAYMATLk9UwEzwqaFEc9zvBJ9MfByuQ"

if __name__=="__main__":
    scraper = Scraper(token=MY_TOKEN)
    ttf = TopicOutThreadFactory(scraper)
    while True:
        msgs = scraper.scrap()
        print(f"Last scrapped messages {scraper.last_point}:\n{msgs}")
        for msg in msgs:
            chnl = msg["channel"]
            parts = chnl.split(".", 1)
            if parts[0] == "pubsub":
                if msg["action"] == "pub":
                    try: web2topic.write(parts[1], msg["body"])
                    except Exception as e: print(f"Error while publishing: {e}")
                elif msg["action"] == "on":
                    ttf.start_stream(parts[1], msg["sender"])
                    print(f"Supscripted to {parts[1]} topic")
                elif msg["action"] == "off":
                    ttf.stop_stream(parts[1], msg["sender"])
                    print(f"Stopped supscription to {parts[1]} topic")
            else:
                pass #TODO: обработать другие actions
        time.sleep(1)