class Queue:
    def __init__(self):
        self.queue = []

    def empty(self):
        return len(self.queue) == 0

    def reset(self):
        del self.queue[:]
        self.queue = []

    def enqueue(self, item):
        self.queue.append(item)

    def dequeue(self):
        return self.queue.pop(0)