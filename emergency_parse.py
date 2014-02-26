__author__ = 'keelan'

import re
import sys
from multiprocessing import Process, JoinableQueue
from threading import Thread
from stat_parser import Parser

class SaveResults(Thread):

    def __init__(self, parsed_queue):
        Thread.__init__(self)
        self.parsed_queue = parsed_queue
        self.results = []
        self.daemon = True
        self.start()

    def run(self):
        while True:
            tree_tuple = self.parsed_queue.get()
            self.results.append(tree_tuple)
            self.parsed_queue.task_done()

    def get_ordered_results(self):
        return zip(*sorted(self.results))[1]


def batch_parse(parser, sentences_queue, parsed_queue):
    while True:
        i,sent = sentences_queue.get()
        tree = parser.parse(sent)
        parsed_queue.put((i,tree))
        sentences_queue.task_done()

def batch_parse_multiprocessing(sentences_list, num_processes=1):

    sentences_queue = JoinableQueue()
    parsed_queue = JoinableQueue()
    parser = Parser()

    for _ in range(num_processes):
        proc = Process(target=batch_parse, args=(parser, sentences_queue, parsed_queue))
        proc.daemon = True
        proc.start()

    sr = SaveResults(parsed_queue)

    for sent in sentences_list:
        sentences_queue.put(sent)

    sentences_queue.join()
    parsed_queue.join()

    return sr.get_ordered_results()

def read_in_data(file_path):
    sentences = []
    s_finder = re.compile(r"<s>(.*?)</s>")
    with open(file_path, "r") as f_in:
        for line in f_in:
            line = line.rstrip()
            sentences.append(s_finder.match(line).group(1))

    return list(enumerate(sentences))



if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python emergency_parse.py [sentences] [num_processes]")
    sentences = read_in_data(sys.argv[1])
    batch_parse_multiprocessing(sentences, int(sys.argv[2]))
