# Algoritm de rezoluție optimizat
import time
import psutil
import os
import sys
from timeit import default_timer as timer

def are_opus(litera1, litera2):
    """Verifică dacă litera2 este opusul lui litera1"""
    norm1 = litera1.replace('Â¬', '¬')
    norm2 = litera2.replace('Â¬', '¬')
    return norm1 == "¬" + norm2 or norm2 == "¬" + norm1

def rezolutie(K):
    """Algoritmul principal de rezoluție cu optimizări"""
    max_iterations = 10000
    metrics = {
        'set_operations': 0,
        'comparisons': 0,
        'iterations': 0,
        'opposite_checks': 0,
        'new_sets_created': 0,
        'start_time': timer(),
        'start_mem': psutil.Process(os.getpid()).memory_info().rss
    }
    
    # Normalizare și convertire la frozenset
    K = [frozenset({elem.replace('Â¬', '¬') for elem in clauza}) for clauza in K]
    noi_seturi = K.copy()
    metrics['set_operations'] += 1
    schimbari = True
    
    while schimbari and metrics['iterations'] < max_iterations:
        metrics['iterations'] += 1
        schimbari = False
        seturi_noi = list(noi_seturi)  # Facem copie a listei
        
        for i in range(len(seturi_noi)):
            for j in range(i + 1, len(seturi_noi)):
                set1 = seturi_noi[i]
                set2 = seturi_noi[j]
                
                # Generăm toate perechile de literali
                for elem1 in set1:
                    for elem2 in set2:
                        metrics['opposite_checks'] += 1
                        if are_opus(elem1, elem2):
                            nou_set = (set1 - {elem1}).union(set2 - {elem2})
                            metrics['set_operations'] += 3
                            
                            # Verificare clauză vidă
                            if not nou_set:
                                metrics['comparisons'] += 1
                                return "Nesatisfiabil", metrics
                            
                            # Verificare duplicat folosind frozenset
                            if nou_set not in noi_seturi:
                                noi_seturi.append(nou_set)
                                metrics['new_sets_created'] += 1
                                schimbari = True
                                print(f"Adăugată clauză nouă: {nou_set}")
        
        # Log de progres
        if metrics['iterations'] % 100 == 0:
            print(f"Iterația {metrics['iterations']}: {len(noi_seturi)} clauze")
    
    if metrics['iterations'] >= max_iterations:
        return "Limită iterații depășită (posibil ciclare)", metrics
    
    return "Satisfiabil", metrics

def citeste_fisier_intrare(nume_fisier):
    """Citește datele de intrare din fișier"""
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

def afiseaza_clauze(K):
    """Afișează clauzele de intrare"""
    print("\nCLAUZE DE INTRARE:")
    for i, clauza in enumerate(K, 1):
        print(f"Clauza {i}: {clauza}")

def afiseaza_rezultate(rezultat, metrics):
    """Afișează rezultatele finale"""
    metrics['execution_time'] = (timer() - metrics['start_time']) * 1000  # ms
    metrics['memory_used'] = psutil.Process(os.getpid()).memory_info().rss / 1024  # KB
    
    print("\n" + "="*60)
    print("REZULTAT FINAL:", rezultat)
    print("="*60)
    print("\nMETRICE DE PERFORMANȚĂ:")
    print(f"Timp execuție: {metrics['execution_time']:.6f} ms")
    print(f"Memorie utilizată: {metrics['memory_used']:.2f} KB")
    print("\nSTATISTICI OPERAȚII:")
    print(f"- Operații pe seturi: {metrics['set_operations']}")
    print(f"- Comparații: {metrics['comparisons']}")
    print(f"- Iterări bucle: {metrics['iterations']}")
    print(f"- Verificări opuse: {metrics['opposite_checks']}")
    print(f"- Seturi noi create: {metrics['new_sets_created']}")
    print("="*60)

def main():
    if not os.path.exists("date_intrare.txt"):
        print("Creați fișierul 'date_intrare.txt' cu structura:")
        print("""3
2
P
¬Q
3
Q
R
¬P
1
¬R""")
        return

    try:
        K = citeste_fisier_intrare("date_intrare.txt")
        afiseaza_clauze(K)
        print("\nPROCESARE REZOLUȚIE...")
        rezultat, metrics = rezolutie(K)
        afiseaza_rezultate(rezultat, metrics)
    except Exception as e:
        print(f"EROARE: {str(e)}")

if __name__ == "__main__":
    try:
        import psutil
    except ImportError:
        print("Instalare psutil...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        import psutil
    
    main()