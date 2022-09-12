import sys


def fprint(*objs, sep=" ", end="\n", file=sys.stdout):
    print(*objs, sep=sep, end=end, file=file, flush=True)


def up(n):
    fprint(f'\033[{n}A', end="")


def down(n):
    fprint(f'\033[{n}B', end="")


def erase():
    fprint("\033[2K\033[G", end="")


def beginning():
    fprint("\033[G", end="")
