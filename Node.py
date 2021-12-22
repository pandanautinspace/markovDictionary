class Node:
    def __init__(self, word):
        self.word = word
        self.edges = {}

    def add_edge(self, noderef, weight):
        if noderef in self.edges:
            weight += self.edges[noderef]
        self.edges[noderef] = weight

    def update_weight(self, noderef, weight):
        self.edges[noderef] = weight

    def get_weight(self, noderef):
        return self.edges[noderef]

    def rebalance_weights(self):
        total_weight = sum(self.edges.values())
        new_edges = self.edges
        for key, value in self.edges.items():
            new_edges[key] = value / total_weight
        self.edges = new_edges

    def max_weight(self):
        try:
            return max(self.edges.values())
        except ValueError:
            return 1.0

    def min_weight(self):
        try:
            return min(self.edges.values())
        except ValueError:
            return 1.0

    def heaviest_edge(self):
        max_value = 0
        max_key = None
        for key, value in self.edges.items():
            if value > max_value:
                max_key = key
                max_value = value
        return max_key

    def __str__(self) -> str:
        return str(self.edges)