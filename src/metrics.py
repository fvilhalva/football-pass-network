"""Metricas de rede sobre o grafo de passes.

- Centralidade: quem sao os jogadores-chave na circulacao de bola.
- Modularidade + comunidades: quais sub-grupos de passe se formam
  (setores/unidades taticas).
"""

import networkx as nx
import pandas as pd
from networkx.algorithms.community import greedy_modularity_communities, modularity


def centrality_table(G: nx.DiGraph) -> pd.DataFrame:
    """Tabela por jogador com as centralidades mais usadas em analise de futebol.

    - betweenness: quanto o jogador e "ponte" na circulacao (armadores/pivos).
    - degree:      densidade de conexoes (quao conectado ele esta).
    - eigenvector: importancia por estar ligado a outros importantes.
    """
    betweenness = nx.betweenness_centrality(G, weight="weight", normalized=True)
    degree = nx.degree_centrality(G)
    try:
        eigen = nx.eigenvector_centrality_numpy(G, weight="weight")
    except Exception:
        eigen = {n: float("nan") for n in G.nodes}

    df = pd.DataFrame(
        {
            "player": list(G.nodes),
            "betweenness": [betweenness[n] for n in G.nodes],
            "degree": [degree[n] for n in G.nodes],
            "eigenvector": [eigen[n] for n in G.nodes],
            "passes": [G.nodes[n].get("passes", 0) for n in G.nodes],
        }
    )
    return df.sort_values("betweenness", ascending=False).reset_index(drop=True)


def detect_communities(G: nx.DiGraph):
    """Detecta comunidades de passe e retorna (comunidades, modularidade Q).

    Modularidade e calculada no grafo NAO-direcionado (convencao para
    greedy_modularity). Q alto (~>0.3) indica estrutura de grupos clara.
    """
    undirected = G.to_undirected()
    communities = list(greedy_modularity_communities(undirected, weight="weight"))
    Q = modularity(undirected, communities, weight="weight")
    return communities, Q


if __name__ == "__main__":
    from data_loading import get_passes, load_events, list_matches
    from pass_network import build_pass_network

    matches = list_matches(43, 3)
    mid = int(matches.iloc[0]["match_id"])
    team = matches.iloc[0]["home_team"]
    ev = load_events(mid)
    G, _ = build_pass_network(ev, get_passes(ev), team)

    print(centrality_table(G).head())
    comms, Q = detect_communities(G)
    print(f"\n{len(comms)} comunidades | modularidade Q = {Q:.3f}")
