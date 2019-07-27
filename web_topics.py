import ctypes as C
from threading import Thread, Event

from topic import PubSubFactory, TopicSpawnMode


web2topic = PubSubFactory(prefix="clapeyron-v1.")


class WheelSpeed(C.Structure):
    _pack_ = 1
    _fields_=(('left', C.c_float), ('right', C.c_float))


class SomeTextStructure(C.Structure):
    _pack_ = 1
    _fields_ = (("text", C.c_char * 1024), )


class AlgoOn(C.Structure):
    _pack_ = 1
    _fields_ = (("on", C.c_bool), )


web2topic.register_topic("wheels", WheelSpeed, 10, TopicSpawnMode.CREATE)
web2topic.register_topic("chat", SomeTextStructure, 10, TopicSpawnMode.CREATE)
web2topic.register_var("algo_on", AlgoOn, True)


topic2web = PubSubFactory(prefix="clapeyron-v1.")


class FloatStruct(C.Structure):
    _pack_ = 1
    _fields_ = (("val", C.c_float), )


topic2web.register_topic("mass", FloatStruct, 10, TopicSpawnMode.CREATE)


class TopicThread(Thread):
    def __init__(self, topname, rec_id, scraper, *args, **kwargs):
        super(TopicThread, self).__init__(*args, **kwargs)
        self._stop = Event()
        self.topname = topname
        self.scraper = scraper
        self.receivers = {rec_id}

    def add_receiver(self, rec_id):
        self.receivers.add(rec_id)

    def rm_receiver(self, rec_id):
        self.receivers.remove(rec_id)
        return len(self.receivers)

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        while True:
            if self.stopped(): return None
            try:
                dct = topic2web.read(self.topname)
                print(f"Read from topic: {dct}")
                channel = f"pubsub.{self.topname}"
                for i in self.receivers:
                    try:
                        self.scraper.send_msg(action="pub", channel=channel, msg=dct, receiver=i)
                    except Exception as e: print(f"Cannot send to {i}: {e}")
            except Exception as e: print(f"Reading topic {self.topname} in thread error: {e}")


class TopicThreadFactory:
    def __init__(self, scraper):
        self.topics = {}
        self.scraper = scraper

    def start_stream(self, name, rec_id):
        if not name in self.topics:
            t = TopicThread(topname=name, scraper=self.scraper, rec_id=rec_id)
            self.topics[name] = t
            t.start()
        else:
            t: TopicThread = self.topics[name]
            t.add_receiver(name)

    def stop_stream(self, name, rec_id):
        t = self.topics.get(name, None)
        if t is not None:
            l = t.rm_receiver(rec_id)
            if l==0: t.stop()
            del self.topics[name]