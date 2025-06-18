.INCLUDE "m328pdef.inc"
.equ CR = 13
.equ LF = 10
.cseg
.org 0x0000
rjmp RESET

RESET:
    ; Inicializa UART a 9600 baud (16MHz clock)
    ldi r16, 103
    sts UBRR0L, r16
    ldi r16, 0
    sts UBRR0H, r16
    ldi r16, (1 << TXEN0)
    sts UCSR0B, r16
    ldi r16, (1 << UCSZ01) | (1 << UCSZ00)
    sts UCSR0C, r16

; EXPRESSAO 1
    ldi r16, 3
    ldi r17, 4
    mov r18, r16
    add r18, r17
    rcall imprime_decimal
    ldi r18, LF
    rcall envia_serial
    ldi r18, CR
    rcall envia_serial

; EXPRESSAO 2
    ldi r16, 5
    ldi r17, 2
    mov r18, r16
    mov r19, r17
    dec r19
exp2_loop:
    breq exp2_fim
    mov r0, r18
    mov r1, r16
    mul r0, r1
    mov r18, r0
    clr r1
    dec r19
    rjmp exp2_loop
exp2_fim:
    rcall imprime_decimal
    ldi r18, LF
    rcall envia_serial
    ldi r18, CR
    rcall envia_serial

; EXPRESSAO 3
    ldi r16, 6
    ldi r17, 2
    mov r24, r16
    mov r25, r17
    clr r18
div3_loop:
    cp r24, r25
    brlo div3_fim
    sub r24, r25
    inc r18
    rjmp div3_loop
div3_fim:
    ldi r19, 3
    ldi r20, 1
    mov r21, r19
    add r21, r20
    mov r0, r18
    mov r1, r21
    mul r0, r1
    mov r22, r0
    clr r1
    mov r18, r22
    rcall imprime_decimal
    ldi r18, LF
    rcall envia_serial
    ldi r18, CR
    rcall envia_serial


; Sub-rotina: envia caractere de r18 via serial
envia_serial:
WAIT_TX:
    lds r17, UCSR0A
    sbrs r17, UDRE0
    rjmp WAIT_TX
    sts UDR0, r18
    ret

; Sub-rotina: imprime valor decimal (0–99) sem zero à esquerda
imprime_decimal:
    mov r19, r18        ; copia valor
    ldi r20, 10
    clr r21            ; contador de dezenas
div10:
    cp r19, r20
    brlo fim_div10
    sub r19, r20
    inc r21
    rjmp div10
fim_div10:
    ldi r22, '0'
    add r21, r22       ; r21 = ascii dezenas
    cpi r21, '0'      ; se dezenas == '0', pula
    breq skip_tens
    mov r18, r21      ; envia dígito das dezenas
    rcall envia_serial
skip_tens:
    ldi r22, '0'
    add r19, r22      ; r19 = ascii unidades
    mov r18, r19      ; envia dígito das unidades
    rcall envia_serial
    ret

FIM:
    rjmp FIM