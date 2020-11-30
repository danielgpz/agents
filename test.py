from sim import KinderGarden, Baby, Kangaroo, Cleaner

latex_sec = '\\subsection{Tablero de $%d \\times %d$, %d\\%% de basura, %d\\%% de obst\\\'aculos, %d ni\\~nos y t=%d}'
latex_sim = '''
\\textbf{%s}:
\\begin{itemize}
\\item Victorias: %d/30
\\item Despedido: %d/30
\\item Suciedad: %.2f\\%%
\\end{itemize}
'''

tests = [(10, 10, 5, ob, bs, t) for ob in range(0, 75, 25) for bs in range(4, 10, 3) for t in range(5, 15, 5)]

for test in tests:
    n, m, dr, ob, bs, t = test

    won1, fired1, dirt_p1 = 0, 0, []
    won2, fired2, dirt_p2 = 0, 0, []
    for _ in range(30):
        kangaroo, cleaner = Kangaroo(), Cleaner()
        kg1 = KinderGarden(n, m, dr, ob, [Baby() for _ in range(bs)], [kangaroo], t)
        kg2 = KinderGarden(n, m, dr, ob, [Baby() for _ in range(bs)], [cleaner], t)

        w, dirt_p = kg1.simulate(verbose=False)
        won1 += w == 1
        fired1 += w == -1
        dirt_p1.append(dirt_p)
        w, dirt_p = kg2.simulate(verbose=False)
        won2 += w == 1
        fired2 += w == -1
        dirt_p2.append(dirt_p)

    print(latex_sec % (n, m, dr, ob, bs, t))
    print(latex_sim % ('Kangaroo', won1, fired1, 100 * sum(dirt_p1)/len(dirt_p1)) )
    print(latex_sim % ('Cleaner', won2, fired2, 100 * sum(dirt_p2)/len(dirt_p2)) )
