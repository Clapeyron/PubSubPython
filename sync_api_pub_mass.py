from web_topics import topic2web


if __name__=="__main__":
    while True:
        ff = float(input("Add float > "))
        print(topic2web.write("mass", {"val": ff}))