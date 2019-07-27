from topic import TopicSpawnMode, Topic


if __name__ == "__main__":
    t = Topic(b"Mycooltopic", 60, 10, TopicSpawnMode.CREATE)
    try:
        while True: t.write(input("> ").encode("ascii"))
    except: t.free()