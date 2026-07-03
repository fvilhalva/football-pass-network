"""Pipeline completo: dados -> grafo -> metricas -> figura + tabelas.

Uso:
    python src/main.py

Ajuste COMPETITION_ID / SEASON_ID / o time abaixo pra analisar outra partida.
"""

from pathlib import Path

from data_loading import get_passes, list_matches, load_events
from metrics import centrality_table, detect_communities
from pass_network import build_pass_network
from plotting import plot_pass_network

# --- Configuracao da analise -------------------------------------------------
COMPETITION_ID = 43  # Copa do Mundo 2018
SEASON_ID = 3
OUT = Path(__file__).resolve().parent.parent / "outputs"


def main():
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)

    matches = list_matches(COMPETITION_ID, SEASON_ID)
    match = matches.iloc[0]
    match_id = int(match["match_id"])
    team = match["home_team"]
    print(f"Analisando {match['home_team']} x {match['away_team']} (id {match_id})")

    events = load_events(match_id)
    passes = get_passes(events)
    G, nodes = build_pass_network(events, passes, team)
    print(f"Rede de {team}: {G.number_of_nodes()} nos, {G.number_of_edges()} arestas")

    # Metricas
    cent = centrality_table(G)
    comms, Q = detect_communities(G)
    print(f"\nTop 3 por betweenness:\n{cent[['player', 'betweenness']].head(3)}")
    print(f"\nComunidades: {len(comms)} | modularidade Q = {Q:.3f}")

    # Salvar tabela de metricas
    cent.to_csv(OUT / "tables" / "centrality.csv", index=False)

    # Figura
    plot_pass_network(
        G,
        title=f"Rede de Passes — {team} (ate 1a substituicao)",
        save_path=str(OUT / "figures" / "pass-network.png"),
    )


if __name__ == "__main__":
    main()
