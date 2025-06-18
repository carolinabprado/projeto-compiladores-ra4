contador_global = 0  # usado para gerar labels únicos

# Gera cabeçalho com inicialização da UART

def gerar_inicio():
    return [
        ".INCLUDE \"m328pdef.inc\"",
        ".equ CR = 13",       # retorno de carro
        ".equ LF = 10",       # avanço de linha
        ".cseg",
        ".org 0x0000",
        "rjmp RESET",
        "",
        "RESET:",
        "    ; Inicializa UART a 9600 baud (16MHz clock)",
        "    ldi r16, 103",         # UBRR0L = 103
        "    sts UBRR0L, r16",
        "    ldi r16, 0",           # UBRR0H = 0
        "    sts UBRR0H, r16",
        "    ldi r16, (1 << TXEN0)",# habilita transmissor
        "    sts UCSR0B, r16",
        "    ldi r16, (1 << UCSZ01) | (1 << UCSZ00)", # 8 bits
        "    sts UCSR0C, r16",
        ""
    ]

# Gera rodapé com rotinas auxiliares

def gerar_fim():
    return [
        "",
        "; Sub-rotina: envia caractere de r18 via serial",
        "envia_serial:",
        "WAIT_TX:",
        "    lds r17, UCSR0A",
        "    sbrs r17, UDRE0",
        "    rjmp WAIT_TX",
        "    sts UDR0, r18",
        "    ret",
        "",
        "; Sub-rotina: imprime valor decimal (0–99) sem zero à esquerda",
        "imprime_decimal:",
        "    mov r19, r18        ; copia valor",
        "    ldi r20, 10",
        "    clr r21            ; contador de dezenas",
        "div10:",
        "    cp r19, r20",
        "    brlo fim_div10",
        "    sub r19, r20",
        "    inc r21",
        "    rjmp div10",
        "fim_div10:",
        "    ldi r22, '0'",
        "    add r21, r22       ; r21 = ascii dezenas",
        "    cpi r21, '0'      ; se dezenas == '0', pula",
        "    breq skip_tens",
        "    mov r18, r21      ; envia dígito das dezenas",
        "    rcall envia_serial",
        "skip_tens:",
        "    ldi r22, '0'",
        "    add r19, r22      ; r19 = ascii unidades",
        "    mov r18, r19      ; envia dígito das unidades",
        "    rcall envia_serial",
        "    ret",
        "",
        "FIM:",
        "    rjmp FIM"
    ]

# Gera código ASM de cada expressão RPN

def gerar_codigo_expr(arvore, contador_expr, contexto):
    linhas = []
    registradores = [f"r{i}" for i in range(16, 30)]
    contador_temp = 0

    def novo_reg():
        nonlocal contador_temp
        if contador_temp >= len(registradores):
            raise Exception("Registradores insuficientes")
        reg = registradores[contador_temp]
        contador_temp += 1
        return reg

    def gerar(no):
        nonlocal linhas

        # Memória e resultado
        if no.value == 'MEM':
            valor = contexto.get("valor", {}).get("resultado", 0)
            reg = novo_reg()
            linhas.append(f"    ldi {reg}, {int(valor)}")
            return reg

        if no.value == 'RES':
            index = int(no.children[0].value)
            try:
                valor = contexto["resultados"][-(index + 1)]
                reg = novo_reg()
                linhas.append(f"    ldi {reg}, {int(valor)}")
                return reg
            except IndexError:
                return None

        if no.value == 'V_MEM':
            reg = gerar(no.children[0])
            if reg:
                try:
                    contexto["valor"]["resultado"] = int(float(no.children[0].value))
                except:
                    contexto["valor"]["resultado"] = 0
                return reg
            return None

        # Número literal
        if not no.children:
            try:
                valor = int(round(float(no.value)))
                reg = novo_reg()
                linhas.append(f"    ldi {reg}, {valor}")
                return reg
            except:
                return None

        # Operadores binários
        regs = [gerar(filho) for filho in no.children]
        if None in regs:
            return None
        a, b = regs[0], regs[1]
        res = novo_reg()

        if no.value == '+':
            linhas += [f"    mov {res}, {a}", f"    add {res}, {b}"]
        elif no.value == '-':
            linhas += [f"    mov {res}, {a}", f"    sub {res}, {b}"]
        elif no.value == '*':
            linhas += [
                f"    mov r0, {a}",
                f"    mov r1, {b}",
                f"    mul r0, r1",
                f"    mov {res}, r0",
                f"    clr r1"
            ]
        elif no.value == '/':
            linhas += [
                f"    mov r24, {a}",
                f"    mov r25, {b}",
                f"    clr {res}",
                f"div{contador_expr}_loop:",
                f"    cp r24, r25",
                f"    brlo div{contador_expr}_fim",
                f"    sub r24, r25",
                f"    inc {res}",
                f"    rjmp div{contador_expr}_loop",
                f"div{contador_expr}_fim:"
            ]
        elif no.value == '^':  # exponenciação a^b, expoente >= 1
            tmp = novo_reg()
            linhas += [
                f"    mov {res}, {a}",     # res = a
                f"    mov {tmp}, {b}",     # tmp = b
                f"    dec {tmp}",          # tmp = b-1
                f"exp{contador_expr}_loop:",
                f"    breq exp{contador_expr}_fim",  # se tmp==0, sai
                f"    mov r0, {res}",     # r0 = res
                f"    mov r1, {a}",       # r1 = a
                f"    mul r0, r1",        # r0 = res * a
                f"    mov {res}, r0",     # res = r0
                f"    clr r1",            # limpa r1
                f"    dec {tmp}",         # tmp--
                f"    rjmp exp{contador_expr}_loop",
                f"exp{contador_expr}_fim:"
            ]
        else:
            return None

        return res

    linhas.append(f"; EXPRESSAO {contador_expr}")
    resultado = gerar(arvore)

    if resultado:
        # registra resultado e prepara envio
        contexto["resultados"].append(contexto["valor"]["resultado"])
        if resultado != "r18":
            linhas.append(f"    mov r18, {resultado}")
        linhas += [
            f"    rcall imprime_decimal",  # imprime sem zero à esquerda
            f"    ldi r18, LF",           # avança para nova linha
            f"    rcall envia_serial",
            f"    ldi r18, CR",           # retorna ao início da linha
            f"    rcall envia_serial",
            ""
        ]
    else:
        linhas.append(f"    ; Expressao {contador_expr} ignorada por erro")

    return linhas














