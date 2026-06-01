# football-pass-network

![Language](https://img.shields.io/badge/language-Python-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-Unspecified-lightgrey)

Network-based football analytics project that models passing interactions as weighted graphs to quantify team structure and identify key playmakers.

## Motivation

Traditional match summaries (possession, shots, pass completion) rarely explain *how* a team builds attacks. This project applies graph theory to passing data so tactical style can be measured quantitatively:

- **Players as nodes**
- **Passes as weighted edges** (edge weight = pass frequency)
- **Centrality metrics** to identify influential players
- **Community detection** to reveal passing sub-structures and tactical units

By combining event data with network metrics, we can compare teams, formations, and matches using reproducible analytics.

## Tech Stack

- **Python**
- **NetworkX**
- **pandas**
- **mplsoccer**
- **matplotlib**
- **StatsBomb Open Data** (JSON event data)

## Directory Structure

Suggested layout for this repository:

```text
football-pass-network/
├── data/
│   └── statsbomb/
│       └── open-data/
│           └── data/
│               ├── competitions.json
│               ├── matches/
│               └── events/
├── notebooks/
├── src/
│   ├── data_loading.py
│   ├── pass_network.py
│   ├── metrics.py
│   └── plotting.py
├── outputs/
│   ├── figures/
│   └── tables/
└── README.md
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install --upgrade pip
pip install pandas networkx matplotlib mplsoccer statsbombpy
```

## Download StatsBomb Open Data

### Option A: Clone official open-data repository

```bash
mkdir -p data/statsbomb
git clone https://github.com/statsbomb/open-data.git data/statsbomb/open-data
```

### Option B: Use `statsbombpy` directly

```python
from statsbombpy import sb

competitions = sb.competitions()
print(competitions[['competition_name', 'season_name']].head())

matches = sb.matches(competition_id=43, season_id=3)
match_id = int(matches.iloc[0]['match_id'])

events = sb.events(match_id=match_id)
print(events[['type', 'player', 'pass_recipient']].head())
```

## Usage Examples

### 1) Build a weighted pass network

```python
import pandas as pd
import networkx as nx
from statsbombpy import sb

match_id = 7585  # example match id
events = sb.events(match_id=match_id)

passes = events[(events['type'] == 'Pass') & (events['player'].notna()) & (events['pass_recipient'].notna())]
edge_table = (
    passes.groupby(['player', 'pass_recipient'])
    .size()
    .reset_index(name='weight')
)

G = nx.DiGraph()
for _, row in edge_table.iterrows():
    G.add_edge(row['player'], row['pass_recipient'], weight=int(row['weight']))

print(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
```

### 2) Compute centrality and modularity

```python
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities, modularity

# Betweenness centrality (playmaking through-ball hubs)
betweenness = nx.betweenness_centrality(G, weight='weight', normalized=True)

# Degree centrality (connection density)
degree = nx.degree_centrality(G)

# Community detection + modularity (group-level passing structure)
undirected = G.to_undirected()
communities = list(greedy_modularity_communities(undirected, weight='weight'))
Q = modularity(undirected, communities, weight='weight')

print('Top betweenness:', sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5])
print('Top degree:', sorted(degree.items(), key=lambda x: x[1], reverse=True)[:5])
print('Modularity:', round(Q, 3))
```

### 3) Visualize pass network with `mplsoccer`

```python
import matplotlib.pyplot as plt
from mplsoccer import Pitch

pitch = Pitch(pitch_type='statsbomb', line_color='black')
fig, ax = pitch.draw(figsize=(10, 7))

# Example: replace with real player positions and edge widths from your pipeline
# pitch.scatter(x_coords, y_coords, s=node_sizes, ax=ax)
# pitch.lines(x_start, y_start, x_end, y_end, lw=edge_widths, ax=ax, color='royalblue', alpha=0.7)

ax.set_title('Pass Network (Example)')
plt.show()
```

## Analysis Examples

> Replace placeholders below with generated project figures.

- ![Pass network example](images/pass-network-example.png)
- ![Betweenness centrality ranking](images/betweenness-centrality-example.png)
- ![Passing communities (modularity)](images/modularity-communities-example.png)

## References

1. Barabási, A.-L. (2016). *Network Science*. Cambridge University Press. https://networksciencebook.com/
2. StatsBomb Open Data. https://github.com/statsbomb/open-data
3. StatsBombPy documentation. https://github.com/statsbomb/statsbombpy
