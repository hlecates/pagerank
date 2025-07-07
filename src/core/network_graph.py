from typing import Dict, Any, List, Optional, Set, Tuple

class NetworkGraph:
    def __init__(self):
        self.nodes: Set[Any] = set()
        self.edges: Dict[Any, Dict[Any, Dict[str, Any]]] = {}
        self.node_attrs: Dict[Any, Dict[str, Any]] = {}

    def add_node(self, node: Any, **attrs):
        self.nodes.add(node)
        if node not in self.node_attrs:
            self.node_attrs[node] = {}
        self.node_attrs[node].update(attrs)
        if node not in self.edges:
            self.edges[node] = {}

    def add_edge(self, src: Any, dst: Any, weight: float = 1.0, time_profile: Optional[Dict[str, float]] = None, **attrs):
        self.add_node(src)
        self.add_node(dst)
        edge_attrs = {'weight': weight, **attrs}
        if time_profile is not None:
            edge_attrs['time_profile'] = time_profile
        self.edges[src][dst] = edge_attrs

    def remove_node(self, node: Any):
        self.nodes.discard(node)
        self.node_attrs.pop(node, None)
        self.edges.pop(node, None)
        for src in self.edges:
            self.edges[src].pop(node, None)

    def remove_edge(self, src: Any, dst: Any):
        if src in self.edges and dst in self.edges[src]:
            self.edges[src].pop(dst)

    def get_neighbors(self, node: Any) -> List[Any]:
        return list(self.edges.get(node, {}).keys())

    def get_edge_weight(self, src: Any, dst: Any) -> Optional[float]:
        return self.edges.get(src, {}).get(dst, {}).get('weight')

    def get_edge_time_profile(self, src: Any, dst: Any) -> Optional[Dict[str, float]]:
        return self.edges.get(src, {}).get(dst, {}).get('time_profile')

    def get_node_attrs(self, node: Any) -> Dict[str, Any]:
        return self.node_attrs.get(node, {})

    def get_edge_attrs(self, src: Any, dst: Any) -> Dict[str, Any]:
        return self.edges.get(src, {}).get(dst, {})

    def nodes_list(self) -> List[Any]:
        return list(self.nodes)

    def edges_list(self) -> List[Tuple[Any, Any, Dict[str, Any]]]:
        edge_list = []
        for src in self.edges:
            for dst, attrs in self.edges[src].items():
                edge_list.append((src, dst, attrs))
        return edge_list

    def to_adjacency_matrix(self, time_context: Optional[str] = None) -> Tuple[List[Any], List[List[float]]]:
        node_list = self.nodes_list()
        idx_map = {node: i for i, node in enumerate(node_list)}
        n = len(node_list)
        matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        for src in self.edges:
            for dst, attrs in self.edges[src].items():
                i, j = idx_map[src], idx_map[dst]
                base_weight = attrs.get('weight', 1.0)
                if time_context and 'time_profile' in attrs and time_context in attrs['time_profile']:
                    matrix[i][j] = base_weight * attrs['time_profile'][time_context]
                else:
                    matrix[i][j] = base_weight
        return node_list, matrix

    def to_adjacency_binary_matrix(self) -> Tuple[List[Any], List[List[int]]]:
        node_list = self.nodes_list()
        idx_map = {node: i for i, node in enumerate(node_list)}
        n = len(node_list)
        matrix = [[0 for _ in range(n)] for _ in range(n)]
        for src in self.edges:
            for dst in self.edges[src]:
                i, j = idx_map[src], idx_map[dst]
                matrix[i][j] = 1
        return node_list, matrix 