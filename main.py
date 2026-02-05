import sys
import itertools
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Gamer(Base):
    __tablename__ = 'gamers'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    mmr = Column(Float)
    server = Column(String)
    last_ten = Column(String)

    def __repr__(self):
        return f"{self.name} (MMR: {self.mmr})"


engine = create_engine('sqlite:///titanfall_rank.db', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def load_data_if_empty():
    count = session.query(Gamer).count()
    if count == 0:
        print("Baza pusta. Ładowanie danych z pliku 'gracze.txt'...")
        try:
            with open('gracze.txt', 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) >= 4:
                        new_gamer = Gamer(
                            name=parts[0].strip(),
                            mmr=float(parts[1].strip()),
                            server=parts[2].strip(),
                            last_ten=parts[3].strip()
                        )
                        session.add(new_gamer)
            session.commit()
            print("Dane załadowane pomyślnie.")
        except FileNotFoundError:
            print("Błąd: Nie znaleziono pliku 'gracze.txt'. Utwórz go i spróbuj ponownie.")
            sys.exit(1)
    else:
        print("Dane istnieją w bazie. Pomijanie ładowania z pliku.")


def balance_teams(gamers_pool):
    total_mmr = sum(g.mmr for g in gamers_pool)
    perfect_balance = total_mmr / 2

    best_diff = float('inf')
    team1 = []
    team2 = []

    for combo in itertools.combinations(gamers_pool, 5):
        current_team_mmr = sum(g.mmr for g in combo)
        diff = abs(current_team_mmr - perfect_balance)

        if diff < best_diff:
            best_diff = diff
            team1 = list(combo)
            team1_ids = [g.id for g in team1]
            team2 = [g for g in gamers_pool if g.id not in team1_ids]

    return team1, team2


def calculate_mmr_update(winner, team1, team2, flag_diff):
    t1_flag_adv = flag_diff if winner == 1 else -flag_diff
    t2_flag_adv = -flag_diff if winner == 1 else flag_diff

    for i in range(5):
        update_gamer(team1[i], winner == 1, t1_flag_adv)
        update_gamer(team2[i], winner == 2, t2_flag_adv)

    session.commit()


def update_gamer(gamer, won, flag_advantage):
    last_ten_int = int(gamer.last_ten, 2)

    streak = 0
    temp_last_ten = last_ten_int
    for _ in range(10):
        if (temp_last_ten & 1) == 1:
            streak += 1
        temp_last_ten >>= 1

    points = 0.0

    if (streak == 7 or streak == 8) and won:
        points = 1.2
    elif (streak == 2 or streak == 3) and not won:
        points = -1.2
    elif streak > 1 and not won:
        points = -1.0
    elif streak >= 9 and won:
        points = 1.5
    elif streak <= 1 and not won:
        points = -1.5
    elif streak < 9 and won:
        points = 1.0

    points += (flag_advantage / 5.0)

    if won:
        points -= 0.2
    else:
        points += 0.2

    gamer.mmr = round(gamer.mmr + points, 1)

    if won:
        new_last_ten_int = (last_ten_int >> 1) | 512
    else:
        new_last_ten_int = (last_ten_int >> 1)

    gamer.last_ten = format(new_last_ten_int, '010b')


def main():
    print("--- SYSTEM RANKINGOWY TITANFALL 2 (PYTHON) ---")

    load_data_if_empty()

    gamers_pool = session.query(Gamer).limit(10).all()

    if len(gamers_pool) < 10:
        print("Za mało graczy w bazie (wymagane 10). Dodaj więcej do pliku txt.")
        return

    print("\nZnaleziono 10 graczy. Obliczanie balansu drużyn...")

    team1, team2 = balance_teams(gamers_pool)

    print("\n" + "=" * 40)
    print(f"DRUŻYNA 1 (Suma MMR: {sum(g.mmr for g in team1):.1f})")
    for g in team1: print(f" - {g.name} [{g.mmr}] (Streak: {g.last_ten})")

    print("-" * 40)
    print(f"DRUŻYNA 2 (Suma MMR: {sum(g.mmr for g in team2):.1f})")
    for g in team2: print(f" - {g.name} [{g.mmr}] (Streak: {g.last_ten})")
    print("=" * 40 + "\n")

    try:
        winner = int(input("Kto wygrał mecz? (Wpisz 1 lub 2): "))
        if winner not in [1, 2]:
            print("Nieprawidłowy wybór drużyny.")
            return

        flags = int(input("Jaka była różnica flag/punktów? (np. 3): "))
    except ValueError:
        print("Błąd: Wprowadź liczbę całkowitą.")
        return

    print("\nAktualizowanie MMR...")
    calculate_mmr_update(winner, team1, team2, flags)

    print("\n--- WYNIKI PO MECZU ---")
    session.expire_all()

    print("DRUŻYNA 1:")
    for g in team1: print(f" - {g.name}: {g.mmr} (Nowy LastTen: {g.last_ten})")

    print("\nDRUŻYNA 2:")
    for g in team2: print(f" - {g.name}: {g.mmr} (Nowy LastTen: {g.last_ten})")

    print("\nDane zostały zapisane w bazie SQLite.")


if __name__ == "__main__":
    main()
