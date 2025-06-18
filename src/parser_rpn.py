# src/parser_rpn.py

class Node:
    def __init__(self, value, children=None, pos=None):
        self.value = value
        self.children = children or []
        self.type = None  # usado na analise semantica
        self.pos = pos    # posicao opcional para rastrear erros

    def __repr__(self):
        if self.children:
            return f"({self.value} {' '.join(repr(c) for c in self.children)})"
        return f"{self.value}"

def parse(tokens):
    if not tokens:
        raise SyntaxError("Entrada vazia")

    token = tokens.pop(0)

    if token != '(':
        return Node(token)

    if not tokens:
        raise SyntaxError("Esperado conteudo apos '('")

    lookahead = tokens[0]

    # === IF ===
    if lookahead == 'IF':
        tokens.pop(0)
        cond = parse(tokens)
        entao = parse(tokens)
        senao = parse(tokens)
        if not tokens or tokens.pop(0) != 'IF':
            raise SyntaxError("Esperado token de fechamento 'IF' ao final da estrutura condicional")
        return Node('IF', [cond, entao, senao])

    # === FOR ===
    elif lookahead == 'FOR':
        tokens.pop(0)
        inicio = parse(tokens)
        fim = parse(tokens)
        corpo = parse(tokens)
        if not tokens or tokens.pop(0) != 'FOR':
            raise SyntaxError("Esperado token de fechamento 'FOR' ao final do laco")
        return Node('FOR', [inicio, fim, corpo])

    # === V MEM ===
    elif lookahead == 'V':
        tokens.pop(0)
        expr = parse(tokens)
        if not tokens or tokens.pop(0) != 'MEM':
            raise SyntaxError("Esperado 'MEM' apos 'V' para formar comando (V MEM)")
        if not tokens or tokens.pop(0) != ')':
            raise SyntaxError("Esperado ')' ao final do comando (V MEM)")
        return Node('V_MEM', [expr])

    # === N RES ===
    elif lookahead.isdigit() and len(tokens) > 1 and tokens[1] == 'RES':
        n_token = tokens.pop(0)
        if tokens.pop(0) != 'RES':
            raise SyntaxError("Esperado 'RES' apos numero para comando (N RES)")
        if not tokens or tokens.pop(0) != ')':
            raise SyntaxError("Esperado ')' ao final do comando (N RES)")
        return Node('RES', [Node(n_token)])

    # === MEM ===
    elif lookahead == 'MEM' and len(tokens) > 1 and tokens[1] == ')':
        tokens.pop(0)  # MEM
        tokens.pop(0)  # )
        return Node('MEM')

    # === Expressao generica (aritmetica) ===
    else:
        children = []
        while tokens and tokens[0] != ')':
            children.append(parse(tokens))
        if not tokens:
            raise SyntaxError("Esperado ')' ao final da expressao")
        tokens.pop(0)  # consome ')'

        if not children:
            raise SyntaxError("Expressao vazia entre parenteses")
        if len(children) < 2:
            raise SyntaxError(f"Operacao aritmetica invalida: operador '{children[-1].value}' com menos de 2 operandos")

        op = children[-1].value
        return Node(op, children[:-1])

