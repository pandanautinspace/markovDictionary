import json
import operator
from typing import List, Dict
from Node import Node
from timeit import default_timer as timer

MAX_DEPTH = 1


def gen_ngrams(string, n):
    last_start = len(string) - n
    for i in range(0, last_start + 1):
        yield string[i:i + n]


def grams_upto(string, max_n):
    for n in range(1, max_n + 1):
        for gram in gen_ngrams(string, n):
            yield gram


def build_graph(dic):
    gram_nods: Dict[str, Node] = {}
    word_nods: Dict[str, Node] = {}
    for word, defs in dic.items():
        for gram in grams_upto(word, 3):
            base_weight = 1.0
            gram_ref: Node = None
            if gram in gram_nods:
                gram_ref = gram_nods[gram]
            else:
                gram_ref = Node(gram)
            for definition in defs:
                weight = base_weight
                prev_ref: Node = None
                for w in definition.split(" "):
                    # if n % 1000000 == 0:
                    #     print(n, timer() - to)
                    #     to = timer()
                    # n += 1
                    # word_ref = Node(w)
                    word_ref = None
                    if w in word_nods:
                        word_ref = word_nods[w]
                    else:
                        word_ref = Node(w)
                    gram_ref.add_edge(w, weight)
                    if prev_ref is not None and prev_ref.word != w:
                        prev_ref.add_edge(w, 1.0)
                        # prev_ref.rebalance_weights()
                    prev_ref = word_ref
                    word_nods[w] = word_ref
                    weight *= 0.9
            # gram_ref.rebalance_weights()
            gram_nods[gram] = gram_ref
    return gram_nods, word_nods


def rebalance_nodes(node_map):
    for node in node_map.values():
        node.rebalance_weights()


def build_def_graph(gram_nods, word_nods, rebalance_queue):
    def_node = Node(word_to_define)
    def_nodes = {}
    for gram in grams_upto(word_to_define, 3):
        if gram in gram_nods:
            gram_nod = gram_nods[gram]
            for word, weight in gram_nod.edges.items():
                if word in def_nodes:
                    def_node.add_edge(word, weight)
                else:
                    def_nodes[word] = word_nods[word]
                    def_node.add_edge(word, weight)
                rebalance_queue.append((word, weight, 0))
    return def_node, def_nodes


def recursive_ish_balance(def_node, def_nodes, word_queue):
    processed = set()
    processed2 = set()
    total_times = 0
    queue2 = word_queue.copy()
    while len(queue2) > 0:
        total_times += 1
        cur_word, cur_weight, cur_d = queue2.pop()
        if cur_word in processed:
            continue
        depth = cur_d + 1
        if depth < MAX_DEPTH:
            for word, weight in word_nods[cur_word].edges.items():
                queue2.append((word, weight, depth))
        processed2.add(cur_word)

    num_current = 0
    five_percent = int(.05 * total_times)
    while len(word_queue) > 0:
        num_current += 1
        if num_current % five_percent == 0:
            yield (1.0 * num_current) / total_times

        cur_word, cur_weight, cur_d = word_queue.pop()
        if cur_word in processed:
            continue
        depth = cur_d + 1
        if depth < MAX_DEPTH:
            for word, weight in word_nods[cur_word].edges.items():
                word_queue.append((word, weight, depth))
        for w in def_nodes:
            if cur_word in def_nodes[w].edges:
                def_nodes[w].add_edge(cur_word, cur_weight * (0.5 ** cur_d))
        if cur_word in def_node.edges:
            def_node.add_edge(cur_word, cur_weight * 0.5 ** depth)
        processed.add(cur_word)


if __name__ == '__main__':
    dic_file = open("dic.json", "r")
    dic: Dict[str, List[str]] = json.load(dic_file)
    stop_file = open("stopwords.txt", "r")
    stop_words = [line.strip() for line in stop_file.readlines()]

    print("Building graph...")
    gram_nods, word_nods = build_graph(dic)

    print("Rebalancing weights...")
    rebalance_nodes(gram_nods)
    rebalance_nodes(word_nods)

    print("Done!")

    word_to_define = input("Word to define: ")

    print("Building definition graph...")
    # apparently it's actually a stack but oh well
    word_queue = []
    def_node, def_nodes = build_def_graph(gram_nods, word_nods, word_queue)

    print(f'Reweighting recursively... up to a max depth of {MAX_DEPTH}')
    for percent in recursive_ish_balance(def_node, def_nodes, word_queue):
        print(percent*100, "% done")
    def_node.rebalance_weights()
    cur = def_node.heaviest_edge()
    print("\nRelated words:")
    for k, v in sorted(def_node.edges.items(), key=operator.itemgetter(1)):
        print(k, v)

    print("\nDefinition-ish:")
    for k, v in sorted(def_node.edges.items(), key=operator.itemgetter(1), reverse=True):
        if k not in stop_words:
            cur = k
            break
    N = 1
    while cur in word_nods and N < 20:
        print(cur)
        for k, v in sorted(word_nods[cur].edges.items(), key=operator.itemgetter(1), reverse=True):
            if N % 10 == 0 or k not in stop_words:
                cur = k
                break
        # cur = word_nods[cur].heaviest_edge()
        N += 1
