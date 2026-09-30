from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "raw"

FILES = {
    "tickets": "tickets.csv",
    "agents": "agents.csv",
    "orders": "orders.csv",
    "customers": "customers.csv",
    "products": "products.csv",
}


def _path(kind: str) -> Path:
    # Support both normalized filenames in the repo and the original UUID exports.
    p = DATA / FILES[kind]
    if p.exists():
        return p
    matches = list(DATA.glob(f"*{FILES[kind]}"))
    if matches:
        return matches[0]
    raise FileNotFoundError(f"Could not find {FILES[kind]} under {DATA}")


def load_data():
    tickets = pd.read_csv(_path("tickets"))
    agents = pd.read_csv(_path("agents"))
    orders = pd.read_csv(_path("orders"))
    customers = pd.read_csv(_path("customers"))
    products = pd.read_csv(_path("products"))
    return tickets, agents, orders, customers, products
