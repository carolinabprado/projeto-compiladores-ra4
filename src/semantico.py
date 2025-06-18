# src/semantico.py

class SemanticError(Exception):
    pass

def is_float(value):
    try:
        float(value)
        return '.' in value
    except:
        return False

def is_int(value):
    try:
        int(value)
        return '.' not in value
    except:
        return False

def analisar_tipo(node, contexto):
    # === MEM ===
    if node.value == 'MEM' and not node.children:
        node.type = contexto.get("memoria", {}).get("tipo", 'float')
        return node.type

    # === V MEM === (armazenar valor na memoria)
    if node.value == 'V' and len(node.children) == 1 and node.children[0].value == 'MEM':
        filho = node.children[0]
        tipo_valor = analisar_tipo(filho, contexto)
        contexto["memoria"] = {"tipo": tipo_valor}
        node.type = tipo_valor
        return node.type

    # === N RES === (resgatar resultado anterior)
    if node.value == 'RES' and len(node.children) == 1:
        filho = node.children[0]
        if not filho.value.isdigit():
            raise SemanticError("RES requer valor inteiro como indice")
        index = int(filho.value)
        if index < 0:
            raise SemanticError("Indice do RES deve ser nao negativo")
        try:
            tipo_resgatado = contexto["resultados"][-(index + 1)]
            node.type = tipo_resgatado
            return node.type
        except IndexError:
            raise SemanticError(f"Linha RES {index} invalida (nao existe)")

    # === FOR ===
    if node.value == 'FOR':
        if len(node.children) != 3:
            raise SemanticError("FOR deve ter 3 filhos: inicio, fim e corpo")
        tipo_inicio = analisar_tipo(node.children[0], contexto)
        tipo_fim = analisar_tipo(node.children[1], contexto)
        tipo_corpo = analisar_tipo(node.children[2], contexto)

        if tipo_inicio not in ['int', 'float'] or tipo_fim not in ['int', 'float']:
            raise SemanticError("FOR requer inicio e fim numericos")
        if tipo_corpo not in ['int', 'float']:
            raise SemanticError("Corpo do FOR deve ser numerico")
        node.type = tipo_corpo
        return node.type

    # === IF ===
    if node.value == 'IF':
        if len(node.children) != 3:
            raise SemanticError("IF deve ter 3 filhos: condicao, then e else")
        tipo_cond = analisar_tipo(node.children[0], contexto)
        tipo_then = analisar_tipo(node.children[1], contexto)
        tipo_else = analisar_tipo(node.children[2], contexto)

        if tipo_cond != 'int':
            raise SemanticError("A condicao do IF deve ser do tipo int")
        if tipo_then != tipo_else:
            raise SemanticError("Branches THEN e ELSE devem ter o mesmo tipo")
        node.type = tipo_then
        return node.type

    # === Caso base: numero ===
    if not node.children:
        if is_int(node.value):
            node.type = 'int'
        elif is_float(node.value):
            node.type = 'float'
        else:
            raise SemanticError(f"Valor invalido: {node.value}")
        return node.type

    # === Expressoes aritmeticas ===
    tipos_filhos = [analisar_tipo(filho, contexto) for filho in node.children]
    op = node.value

    if op in ['+', '-', '*', '/', '%']:
        node.type = 'float' if 'float' in tipos_filhos else 'int'
    elif op == '|':  # divisao real
        node.type = 'float'
    elif op == '^':
        if tipos_filhos[1] != 'int':
            raise SemanticError("Expoente deve ser inteiro em '^'")
        node.type = 'float' if tipos_filhos[0] == 'float' else 'int'
    elif op == '=':
        if tipos_filhos[0] != tipos_filhos[1]:
            raise SemanticError("Comparacao entre tipos diferentes")
        node.type = 'int'
    else:
        raise SemanticError(f"Operador nao suportado: {op}")

    return node.type


