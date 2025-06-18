## Estrutura LL(1) e Tabela Preditiva

O parser deste projeto segue o modelo LL(1), com decisões tomadas a partir do lookahead (próximo token de entrada). Cada expressão da linguagem começa obrigatoriamente com `(`, e o segundo token determina a produção aplicada.

### Gramática simplificada da linguagem (notação RPN estendida)

<program> → <stmt>*

<stmt> →
( IF <expr> <stmt> <stmt> IF )
| ( FOR <expr> <expr> <stmt> FOR )
| ( V <expr> MEM )
| ( <int> RES )
| ( MEM )
| ( <expr> )

<expr> →
<literal>
| ( <expr> <expr> <op> )
| MEM
| ( <int> RES )
| ( V <expr> MEM )

<literal> → INT | FLOAT
<op> → + | - | * | / | % | ^ | | | = | < | >


### Conjuntos FIRST

| N-terminal | FIRST                        |
|--------------|------------------------------|
| `<stmt>`     | `IF`, `FOR`, `V`, `MEM`, `INT`, `FLOAT`, `(` |
| `<expr>`     | `INT`, `FLOAT`, `(`, `MEM`    |

### 📘 Tabela preditiva LL(1)

| `<stmt>`     | `IF`            | `FOR`             | `V`             | `MEM`           | `INT`              | `FLOAT`            | `(`                          |
|--------------|------------------|--------------------|------------------|------------------|---------------------|---------------------|------------------------------|
| Produção     | `( IF ... IF )`  | `( FOR ... FOR )`  | `( V ... MEM )`  | `( MEM )`        | `( INT RES )` ou `(<expr>)` | `(<expr>)`         | depende do 2º token          |

> A decisão é feita com base no lookahead (2º token após `'('`). Por isso, o parser é determinístico e compatível com LL(1).
