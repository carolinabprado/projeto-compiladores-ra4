# src/main.py

import sys
import os
from lexer import analisar_lexicamente
from parser_rpn import parse
from semantico import analisar_tipo
from codegen_asm import gerar_inicio, gerar_codigo_expr, gerar_fim
from visualizacao import gerar_imagem_arvore

if len(sys.argv) < 2:
    print("Uso: python3 main.py <caminho_para_txt>")
    sys.exit(1)

caminho = sys.argv[1]

with open(caminho, 'r') as f:
    linhas = [linha.strip() for linha in f if linha.strip()]

contexto = {
    "resultados": [],
    "valor": {"tipo": "float", "resultado": 0}
}

codigo_asm = gerar_inicio()

for i, linha in enumerate(linhas):
    print(f"\nExpressão {i+1}: {linha}")
    try:
        tokens = analisar_lexicamente(linha)
        for t in tokens:
            print(t)
        lista_tokens = [t.valor for t in tokens]
        arvore = parse(lista_tokens)
        tipo = analisar_tipo(arvore, contexto)

        print(f"Árvore Sintática: {arvore}")
        print(f"Tipo final: {tipo}")

        gerar_imagem_arvore(arvore, f"arvore_{i+1}.png")

        # Atualiza contexto: salva resultado atual
        contexto["resultados"].append(tipo)
        contexto["valor"]["resultado"] = tipo

        # Gera código ASM da expressão
        codigo_asm += gerar_codigo_expr(arvore, i + 1, contexto)

    except Exception as e:
        print(f"Erro ao processar expressão {i+1}: {e}")
        codigo_asm.append(f"; EXPRESSAO {i+1} ignorada devido a erro: {e}")

# Finaliza programa
codigo_asm += gerar_fim()

# Salva arquivo
os.makedirs("build", exist_ok=True)
saida = "build/saida.asm"
with open(saida, "w") as f:
    f.write("\n".join(codigo_asm))

print(f"\nArquivo ASM gerado em: {saida}")

