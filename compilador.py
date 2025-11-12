#!/usr/bin/env python3
"""
Projeto: Compiladores Interativo — Linguagens Formais e Autômatos
Autor: João Armando Ferreira de Faria

Funcionalidades:
1) Tokenizador (análise léxica simples)
2) Simulador AFD (identificadores)
3) Parser recursivo-descendente (expressões aritméticas)
4) Guia rápido Git
5) Sair

Execução:
$ python3 compiladores_compacto.py
"""

import re
import sys

# =========================================
# Cores (opcionais via colorama)
# =========================================
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Dummy:
        RESET = RED = GREEN = YELLOW = CYAN = MAGENTA = BLUE = BRIGHT = ""
    Fore = Style = Dummy()

# =========================================
# TOKENIZADOR — análise léxica
# =========================================
KEYWORDS = {"if", "else", "while", "return", "int", "float", "for", "break", "continue"}

TOKEN_SPEC = [
    ("NUMBER",   r"\d+(\.\d+)?"),
    ("ID",       r"[A-Za-z_][A-Za-z0-9_]*"),
    ("OP",       r"==|!=|<=|>=|\+|\-|\*|/|=|<|>"),
    ("LPAREN",   r"\("),
    ("RPAREN",   r"\)"),
    ("SEMI",     r";"),
    ("COMMA",    r","),
    ("SKIP",     r"[ \t\n]+"),
    ("MISMATCH", r"."),
]

MASTER_RE = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC))

def tokenize(code):
    """Converte o código-fonte em lista de tokens."""
    tokens = []
    for mo in MASTER_RE.finditer(code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == "NUMBER":
            tokens.append(("NUMBER", value))
        elif kind == "ID":
            tokens.append(("KEYWORD", value) if value in KEYWORDS else ("ID", value))
        elif kind == "SKIP":
            continue
        elif kind == "MISMATCH":
            tokens.append(("ERROR", value))
        else:
            tokens.append((kind, value))
    return tokens

def show_tokenizer():
    print(Fore.CYAN + "\n=== TOKENIZADOR ===" + Style.RESET_ALL)
    code = input("Digite um trecho de código: ")
    for t in tokenize(code):
        color = Fore.RED if t[0] == "ERROR" else Fore.GREEN
        print(color + f"  {t}" + Style.RESET_ALL)

# =========================================
# AFD — simulador simples (identificadores)
# =========================================
def simulate_dfa(s):
    """Simula AFD para [A-Za-z_][A-Za-z0-9_]*"""
    state = 0
    for ch in s:
        if state == 0 and re.match(r"[A-Za-z_]", ch):
            state = 1
        elif state == 1 and re.match(r"[A-Za-z0-9_]", ch):
            state = 1
        else:
            state = -1
            break
    return state == 1 and len(s) > 0

def show_dfa():
    print(Fore.CYAN + "\n=== SIMULADOR DE AFD ===" + Style.RESET_ALL)
    s = input("Digite uma string: ")
    print(Fore.GREEN + "ACEITA" if simulate_dfa(s) else Fore.RED + "REJEITADA", Style.RESET_ALL)

# =========================================
# PARSER — recursivo-descendente
# =========================================
TOKEN_RE = re.compile(r"\s*(?:(\d+(?:\.\d+)?)|([A-Za-z_][A-Za-z0-9_]*)|(.))")

class Lexer:
    def __init__(self, text):
        self.tokens = []
        for mo in TOKEN_RE.finditer(text):
            num, ident, other = mo.groups()
            if num: self.tokens.append(("NUMBER", num))
            elif ident: self.tokens.append(("ID", ident))
            elif other in "+-*/()": self.tokens.append((other, other))
        self.pos = 0

    def peek(self): return self.tokens[self.pos] if self.pos < len(self.tokens) else ("EOF", "")
    def next(self): tok = self.peek(); self.pos += 1; return tok

def parse_expression(text):
    """Parser recursivo-descendente para expressões simples."""
    lex = Lexer(text)

    def E():
        node = T()
        while lex.peek()[0] in ("+", "-"):
            op = lex.next()[0]; node = ("BINOP", op, node, T())
        return node

    def T():
        node = F()
        while lex.peek()[0] in ("*", "/"):
            op = lex.next()[0]; node = ("BINOP", op, node, F())
        return node

    def F():
        tok = lex.peek()
        if tok[0] == "(":
            lex.next(); node = E()
            if lex.peek()[0] != ")": raise SyntaxError("Faltando ')'")
            lex.next(); return node
        elif tok[0] == "NUMBER": return ("NUMBER", lex.next()[1])
        elif tok[0] == "ID": return ("ID", lex.next()[1])
        raise SyntaxError(f"Token inesperado: {tok}")

    tree = E()
    if lex.peek()[0] != "EOF": raise SyntaxError("Entrada extra.")
    return tree

def pretty_tree(node, indent=0):
    pad = "  " * indent
    if node[0] == "BINOP":
        _, op, left, right = node
        print(pad + f"BINOP {op}")
        pretty_tree(left, indent + 1)
        pretty_tree(right, indent + 1)
    else:
        print(pad + f"{node[0]}: {node[1]}")

def show_parser():
    print(Fore.CYAN + "\n=== PARSER ===" + Style.RESET_ALL)
    expr = input("Digite uma expressão (ex: a + 3*(b-2)): ")
    try:
        pretty_tree(parse_expression(expr))
    except Exception as e:
        print(Fore.RED + "Erro:", e)

# =========================================
# GIT HELP — guia rápido
# =========================================
def show_git():
    print(Fore.CYAN + "\n=== COMANDOS GIT ===" + Style.RESET_ALL)
    print("""git init
git add .
git commit -m "Trabalho Compiladores"
git branch -M main
git remote add origin https://github.com/usuario/repositorio.git
git push -u origin main""")

# =========================================
# MENU PRINCIPAL
# =========================================
def main():
    while True:
        print(Fore.YELLOW + "\n=== MENU COMPILADORES ===" + Style.RESET_ALL)
        print("1) Tokenizador")
        print("2) Simulador AFD")
        print("3) Parser")
        print("4) Comandos Git")
        print("5) Sair")
        op = input("> ").strip()
        if op == "1": show_tokenizer()
        elif op == "2": show_dfa()
        elif op == "3": show_parser()
        elif op == "4": show_git()
        elif op == "5": break
        else: print("Opção inválida.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nEncerrado pelo usuário.")