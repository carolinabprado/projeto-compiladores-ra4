# src/visualizacao.py

from graphviz import Digraph

def gerar_imagem_arvore(node, nome_arquivo='tree'):
    dot = Digraph()
    contador = [0]

    def adicionar_nos(n, parent_id=None):
        node_id = f"n{contador[0]}"
        contador[0] += 1

        label = f"{n.value}"
        if hasattr(n, 'type'):
            label += f"\n[{n.type}]"

        dot.node(node_id, label)

        if parent_id:
            dot.edge(parent_id, node_id)

        for child in n.children:
            adicionar_nos(child, node_id)

    adicionar_nos(node)
    dot.render(f"{nome_arquivo}", format="png", cleanup=True)
