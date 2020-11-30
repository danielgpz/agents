from sim import KinderGarden, Baby, Kangaroo, Cleaner
import sys

n, m, dr, ob, bs, t = (int(arg) for arg in sys.argv[1:])

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

print(f'Kangaroo\n\tWon: \t{won1}\n\tFired: \t{fired1}\n\tDirt%: \t{round(100 * sum(dirt_p1)/len(dirt_p1), 2)}%')
print(f'Cleaner\n\tWon: \t{won2}\n\tFired: \t{fired2}\n\tDirt%: \t{round(100 * sum(dirt_p2)/len(dirt_p2), 2)}%')    
