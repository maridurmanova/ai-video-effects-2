"""Effect registry: /effects2 <name> → module. ORDER is the order used by the showcase reel."""
import importlib

ORDER = ["text-behind", "over-the-shoulder", "tier-list", "freeze-frame", "glass-graph", "color-grade"]
FILES = {"over-the-shoulder": "over_shoulder"}


def load(name):
    return importlib.import_module("effects2." + FILES.get(name, name.replace("-", "_")))


def all_effects():
    return [load(n) for n in ORDER]
