import pytest

from home_inventory.database.repositories import InventoryRepository
from home_inventory.database.text import escape_like, fold_text


@pytest.fixture()
def repo(tmp_path) -> InventoryRepository:
    return InventoryRepository(tmp_path / "search.db")


def _names(items) -> list[str]:
    return [item.name for item in items]


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("şem", ["Şemsiye"]),
        ("ŞEM", ["Şemsiye"]),
        ("istanbul", ["İstanbul Haritası"]),
        ("İSTANBUL", ["İstanbul Haritası"]),
        ("ıstanbul", ["İstanbul Haritası"]),
        ("ISPARTA", ["Isparta Gülü"]),
        ("ısparta", ["Isparta Gülü"]),
        ("gül", ["Isparta Gülü"]),
        ("ÇAY", ["Çay Bardağı"]),
    ],
)
def test_search_is_case_insensitive_for_turkish_names(repo, query, expected) -> None:
    for name in ("Şemsiye", "İstanbul Haritası", "Isparta Gülü", "Çay Bardağı", "Laptop"):
        repo.create_item(name=name)

    assert _names(repo.search_items_by_name(query)) == expected


def test_search_keeps_ascii_case_insensitivity(repo) -> None:
    repo.create_item(name="USB-C Cable")
    assert _names(repo.search_items_by_name("usb")) == ["USB-C Cable"]
    assert _names(repo.search_items_by_name("CABLE")) == ["USB-C Cable"]


def test_search_treats_percent_and_underscore_literally(repo) -> None:
    for name in ("100% Cotton Shirt", "a_b", "axb", "Plain"):
        repo.create_item(name=name)

    assert _names(repo.search_items_by_name("%")) == ["100% Cotton Shirt"]
    assert _names(repo.search_items_by_name("_")) == ["a_b"]
    assert _names(repo.search_items_by_name("a_b")) == ["a_b"]


def test_search_treats_backslash_literally(repo) -> None:
    repo.create_item(name="C:\\temp")
    repo.create_item(name="Plain")

    assert _names(repo.search_items_by_name("\\")) == ["C:\\temp"]


def test_fold_text_handles_none_and_decomposed_input() -> None:
    assert fold_text(None) is None
    # "İ" written as "I" + combining dot above must fold like the precomposed form.
    assert fold_text("I\u0307stanbul") == fold_text("İstanbul") == "istanbul"


def test_escape_like_escapes_wildcards_and_escape_char() -> None:
    assert escape_like("50%_off\\") == "50\\%\\_off\\\\"
