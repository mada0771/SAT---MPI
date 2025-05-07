import time
import psutil
import os
import sys
from timeit import default_timer as timer

def are_opus(litera1, litera2):
    norm1 = litera1.replace('Â¬', '¬')
    norm2 = litera2.replace('Â¬', '¬')
    return norm1 == "¬" + norm2 or norm2 == "¬" + norm1

def afiseaza_clauze(K):
    print("\nCLAUZE DE INTRARE:")
    for i, clauza in enumerate(K, 1):
        clauza_display = {elem.replace('¬', '¬') for elem in clauza}
        print(f"Clauza {i}: {clauza_display}")

def select_variable(K):
    for clauza in sorted(K, key=len):
        if clauza:
            return next(iter(clauza)).replace("¬", "")
    return None

def davis_putnam(K, metrics, depth=0):
    if depth == 0:
        metrics['start_time'] = timer()
        metrics['start_mem'] = psutil.Process(os.getpid()).memory_info().rss

    metrics['iterations'] += 1

    changed = True
    while changed:
        changed = False
        unit_clauses = [clauza for clauza in K if len(clauza) == 1]
        for unit in unit_clauses:
            literal = next(iter(unit))
            negat = "¬" + literal if not literal.startswith("¬") else literal[1:]

            new_K = []
            for clauza in K:
                metrics['comparisons'] += 1
                if literal in clauza:
                    metrics['clauses_removed'] += 1
                    continue

                new_clauza = {elem for elem in clauza if elem != negat}
                metrics['set_operations'] += len(clauza) + 1

                if new_clauza != clauza:
                    metrics['literals_removed'] += 1
                    print(f"Rezolvând: {literal} și {negat} → {new_clauza}")

                new_K.append(new_clauza)

            if new_K != K:
                changed = True
                K = new_K
                metrics['set_operations'] += 1

    all_literals = set()
    literals_poz = set()
    literals_neg = set()

    for clauza in K:
        for literal in clauza:
            all_literals.add(literal)
            if literal.startswith("¬"):
                literals_neg.add(literal[1:])
            else:
                literals_poz.add(literal)

    pure_literals = []
    for lit in all_literals:
        base_lit = lit.replace("¬", "")
        if (base_lit in literals_poz) ^ (base_lit in literals_neg):
            pure_literals.append(lit)
            metrics['pure_literals_removed'] += 1

    for lit in pure_literals:
        K = [clauza for clauza in K if lit not in clauza]
        metrics['set_operations'] += len(K)
        print(f"Eliminare literal pur: {lit}")

    if any(len(clauza) == 0 for clauza in K):
        metrics['comparisons'] += len(K)
        return "Nesatisfiabil", metrics
    if all(len(clauza) == 0 for clauza in K):
        metrics['comparisons'] += len(K)
        return "Satisfiabil", metrics

    var = select_variable(K)
    if not var:
        return "Satisfiabil", metrics

    new_K = [clauza for clauza in K if var not in clauza]
    new_K = [{lit for lit in clauza if lit != f"¬{var}"} for clauza in new_K]
    metrics['set_operations'] += len(K) * 2
    res, _ = davis_putnam(new_K, metrics, depth + 1)
    if res == "Satisfiabil":
        return res, metrics

    new_K = [clauza for clauza in K if f"¬{var}" not in clauza]
    new_K = [{lit for lit in clauza if lit != var} for clauza in new_K]
    metrics['set_operations'] += len(K) * 2
    return davis_putnam(new_K, metrics, depth + 1)

def citeste_fisier_intrare(nume_fisier):
    try:
        with open(nume_fisier, 'r', encoding='utf-8') as f:
            n = int(f.readline().strip())
            K = []
            for _ in range(n):
                x = int(f.readline().strip())
                clauza = set()
                for _ in range(x):
                    elem = f.readline().strip()
                    clauza.add(elem.replace('Â¬', '¬'))
                K.append(clauza)
        return K
    except UnicodeDecodeError:
        with open(nume_fisier, 'r', encoding='latin-1') as f:
            n = int(f.readline().strip())
            K = []
            for _ in range(n):
                x = int(f.readline().strip())
                clauza = set()
                for _ in range(x):
                    elem = f.readline().strip()
                    clauza.add(elem.replace('Â¬', '¬'))
                K.append(clauza)
        return K

def afiseaza_rezultate(rezultat, metrics):
    metrics['execution_time'] = (timer() - metrics['start_time']) * 1000
    metrics['memory_used'] = float(psutil.Process(os.getpid()).memory_info().rss - metrics['start_mem'])

    print("\n" + "="*60)
    print("REZULTAT FINAL:", rezultat)
    print("="*60)
    print("\nMETRICE DE PERFORMANȚĂ:")
    print(f"Timp execuție: {metrics['execution_time']:.6f} milisecunde")
    print(f"Memorie utilizată: {metrics['memory_used']:.6f} bytes")
    print("\nSTATISTICI OPERAȚII:")
    print(f"- Operații pe seturi: {metrics['set_operations']}")
    print(f"- Comparații: {metrics['comparisons']}")
    print(f"- Iterări bucle: {metrics['iterations']}")
    print(f"- Clauze eliminate: {metrics['clauses_removed']}")
    print(f"- Literali eliminați: {metrics['literals_removed']}")
    print(f"- Literali puri eliminați: {metrics['pure_literals_removed']}")
    print("="*60)

def main():
    fisier_intrare = "date_intrare.txt"

    if not os.path.exists(fisier_intrare):
        print("Fișierul de intrare nu există. Exemplu format:")
        print("3\n2\nP\n¬Q\n3\nQ\nR\n¬P\n1\n¬R")
        return

    try:
        K = citeste_fisier_intrare(fisier_intrare)
        afiseaza_clauze(K)

        print("\nPROCESARE REZOLUȚIE...")

        metrics = {
            'set_operations': 0,
            'comparisons': 0,
            'iterations': 0,
            'clauses_removed': 0,
            'literals_removed': 0,
            'pure_literals_removed': 0
        }

        rezultat, metrics = davis_putnam(K, metrics)

        afiseaza_rezultate(rezultat, metrics)

    except Exception as e:
        print(f"Eroare: {str(e)}")

if __name__ == "__main__":
    if 'psutil' not in sys.modules:
        print("Instalare psutil...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    import psutil
    main()
