
from chisel import longest
from chisel.cli import main


def test_main():
    main([])


def test_longest():
    assert longest([b'a', b'bc', b'abc']) == b'abc'
