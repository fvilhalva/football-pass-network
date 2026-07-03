"""Construcao do grafo de passes a partir dos eventos filtrados.

Convencao classica de "pass network":
  - No     = jogador
  - Aresta = passe de A -> B (direcionada), peso = frequencia
  - Posicao do no = localizacao media de onde o jogador tocou na bola
  - Tamanho do no = numero de passes dados/recebidos (envolvimento)

Por padrao, restringe-se aos jogadores ATE a primeira substituicao, pra que
a posicao media faca sentido (o time nao mudou de formacao ainda).
"""

import networkx as nx
import pandas as pd


def _first_substitution_minute(events: pd.DataFrame, team: str) -> float:
    """Minuto da primeira substituicao do time (ou infinito se nao houve)."""
    subs = events[(events["type"] == "Substitution") & (events["team"] == team)]
    if subs.empty:
        return float("inf")
    return subs["minute"].min()


def build_pass_network(
    events: pd.DataFrame,
    passes: pd.DataFrame,
    team: str,
    until_first_sub: bool = True,
) -> tuple[nx.DiGraph, pd.DataFrame]:
    """Constroi o grafo direcionado de passes de um time.

    Retorna
    -------
    G : nx.DiGraph com atributo 'weight' nas arestas
    nodes_df : DataFrame com posicao media (x, y) e contagem de passes por jogador
    """
    team_passes = passes[passes["team"] == team].copy()

    if until_first_sub:
        cutoff = _first_substitution_minute(events, team)
        team_passes = team_passes[team_passes["minute"] < cutoff]

    # location e uma lista [x, y]; separamos em colunas.
    locs = team_passes["location"].apply(pd.Series)
    team_passes["x"] = locs[0]
    team_passes["y"] = locs[1]

    # Posicao media do no = onde o jogador ORIGINOU seus passes.
    node_pos = (
        team_passes.groupby("player")
        .agg(x=("x", "mean"), y=("y", "mean"), passes=("player", "size"))
        .reset_index()
    )

    # Arestas: contagem de passes A -> B.
    edge_table = (
        team_passes.groupby(["player", "pass_recipient"])
        .size()
        .reset_index(name="weight")
    )

    G = nx.DiGraph()
    for _, r in node_pos.iterrows():
        G.add_node(r["player"], x=r["x"], y=r["y"], passes=int(r["passes"]))
    for _, r in edge_table.iterrows():
        # so adiciona aresta se o destinatario tambem e um no valido (jogou no periodo)
        if r["pass_recipient"] in G:
            G.add_edge(r["player"], r["pass_recipient"], weight=int(r["weight"]))

    return G, node_pos


if __name__ == "__main__":
    from data_loading import get_passes, load_events, list_matches

    matches = list_matches(43, 3)
    mid = int(matches.iloc[0]["match_id"])
    team = matches.iloc[0]["home_team"]
    ev = load_events(mid)
    passes = get_passes(ev)
    G, nodes = build_pass_network(ev, passes, team)
    print(f"{team}: {G.number_of_nodes()} nos, {G.number_of_edges()} arestas")
