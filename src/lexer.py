# src/lexer.py

import re

class Token:
    def __init__(self, valor, tipo, pos):
        self.valor = valor
        self.tipo = tipo
        self.pos = pos

    def __repr__(self):
        return f"{self.tipo.upper():<10} {self.valor:<10} (posição {self.pos})"

def analisar_lexicamente(linha):
    tokens = []
    padrao = r'\s*(\(|\)|\d+\.\d+|\d+|[+\-*/%^|]|[A-Z]+)\s*'
    pos = 0

    for match in re.finditer(padrao, linha):
        valor = match.group(1)
        inicio = match.start(1)

        if valor in ('(', ')'):
            tipo = 'parêntese'
        elif re.fullmatch(r'\d+', valor):
            tipo = 'int'
        elif re.fullmatch(r'\d+\.\d+', valor):
            tipo = 'float'
        elif valor in ['+', '-', '*', '/', '%', '^', '|']:
            tipo = 'operador'
        elif valor in ['MEM', 'RES', 'IF', 'FOR', 'V']:
            tipo = 'comando'
        elif re.fullmatch(r'[A-Z]+', valor):  # Ex: V de (V 3.0 MEM)
            tipo = 'identificador'
        else:
            tipo = 'desconhecido'

        tokens.append(Token(valor, tipo, inicio))

    return tokens
