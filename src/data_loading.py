"""Carregamento de eventos do StatsBomb Open Data.

Usa statsbombpy, que baixa os JSONs direto do repositório open-data.
Nao precisa clonar nada; a lib faz o download e cacheia em memoria.
"""

import warnings

import pandas as pd
from statsbombpy import sb

# statsbombpy avisa a cada chamada que esta usando dados abertos; silenciamos.
warnings.filterwarnings("ignore", category=UserWarning)


def list_competitions() -> pd.DataFrame:
    """Retorna todas as competicoes/temporadas disponiveis."""
    return sb.competitions()


def list_matches(competition_id: int, season_id: int) -> pd.DataFrame:
    """Lista as partidas de uma temporada.

    Exemplos de ids uteis:
      - Copa 2018:        competition_id=43, season_id=3
      - Champions final:  competition_id=16, season_id=... (ver list_competitions)
    """
    return sb.matches(competition_id=competition_id, season_id=season_id)


def load_events(match_id: int) -> pd.DataFrame:
    """Carrega todos os eventos de uma partida (passes, chutes, etc.)."""
    return sb.events(match_id=match_id)


def get_passes(events: pd.DataFrame, team: str | None = None) -> pd.DataFrame:
    """Filtra apenas os passes completados de uma partida.

    Um passe e "completado" quando NAO tem 'pass_outcome' (no StatsBomb,
    outcome preenchido = incompleto/interceptado/fora).

    Parametros
    ----------
    team : nome exato do time (ex.: 'Brazil'). Se None, retorna os dois times.
    """
    is_pass = events["type"] == "Pass"
    completed = events["pass_outcome"].isna()  # sem outcome = passe certo
    has_recipient = events["pass_recipient"].notna()

    passes = events[is_pass & completed & has_recipient].copy()

    if team is not None:
        passes = passes[passes["team"] == team]

    return passes


if __name__ == "__main__":
    # Sanity check: roda `python src/data_loading.py` pra ver se puxa dados.
    matches = list_matches(competition_id=43, season_id=3)
    mid = int(matches.iloc[0]["match_id"])
    ev = load_events(mid)
    passes = get_passes(ev)
    print(f"Partida {mid}: {len(ev)} eventos, {len(passes)} passes completados")
    print(passes[["team", "player", "pass_recipient"]].head())
