"""Visualizacao da rede de passes sobre o campo (mplsoccer)."""

import matplotlib.pyplot as plt
import networkx as nx
from mplsoccer import Pitch


def plot_pass_network(
    G: nx.DiGraph,
    title: str = "Rede de Passes",
    min_edge_weight: int = 2,
    save_path: str | None = None,
):
    """Desenha a rede sobre um campo StatsBomb.

    - Posicao dos nos vem dos atributos x, y do grafo.
    - Tamanho do no  ~ numero de passes do jogador.
    - Largura da aresta ~ peso (frequencia de passe), filtrando ruido.
    """
    pitch = Pitch(pitch_type="statsbomb", line_color="#444444", pitch_color="#f5f5f5")
    fig, ax = pitch.draw(figsize=(11, 7.5))

    # Arestas primeiro (ficam atras dos nos).
    for u, v, d in G.edges(data=True):
        if d["weight"] < min_edge_weight:
            continue
        x_start, y_start = G.nodes[u]["x"], G.nodes[u]["y"]
        x_end, y_end = G.nodes[v]["x"], G.nodes[v]["y"]
        pitch.lines(
            x_start, y_start, x_end, y_end,
            lw=d["weight"] * 0.6,
            color="royalblue", alpha=0.6, zorder=1, ax=ax,
        )

    # Nos.
    xs = [G.nodes[n]["x"] for n in G.nodes]
    ys = [G.nodes[n]["y"] for n in G.nodes]
    sizes = [G.nodes[n].get("passes", 1) * 18 for n in G.nodes]
    pitch.scatter(xs, ys, s=sizes, color="#e63946", edgecolors="black",
                  linewidth=1, zorder=2, ax=ax)

    # Rotulos (sobrenome so, pra nao poluir).
    for n in G.nodes:
        last = str(n).split()[-1]
        ax.annotate(
            last, (G.nodes[n]["x"], G.nodes[n]["y"]),
            fontsize=8, ha="center", va="center", zorder=3,
            xytext=(0, 10), textcoords="offset points",
        )

    ax.set_title(title, fontsize=15, pad=12)

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Figura salva em {save_path}")
    return fig, ax
