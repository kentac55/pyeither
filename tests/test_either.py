from unittest import TestCase, main

from pyeither import *


class TestEither(TestCase):

    l = Left[str, int]("a")
    r = Right[str, int](1)

    def test_constructor(self) -> None:
        self.assertTrue(self.l)
        self.assertTrue(self.r)

    def test_is_left(self) -> None:
        self.assertTrue(self.l.is_left)
        self.assertFalse(self.r.is_left)

    def test_is_right(self) -> None:
        self.assertFalse(self.l.is_right)
        self.assertTrue(self.r.is_right)

    def test_fold(self) -> None:
        def fa(x: str) -> int:
            return len(x)

        def fb(x: int) -> int:
            return x * 2

        self.assertTrue(self.l.fold(fa, fb) == 1)
        self.assertTrue(self.r.fold(fa, fb) == 2)

    def test_swap(self) -> None:
        self.assertTrue(self.l.swap().is_right)
        self.assertTrue(self.r.swap().is_left)

    def test_get_or_else(self) -> None:
        self.assertTrue(self.l.get_or_else(2) == 2)
        self.assertTrue(self.r.get_or_else(2) == 1)

    def test_or_else(self) -> None:
        self.assertTrue(self.l.or_else(Left[str, int]("b")).swap().contains("b"))
        self.assertTrue(self.r.or_else(Left[str, int]("b")).contains(1))

    def test_contains(self) -> None:
        self.assertFalse(self.l.contains(1))
        self.assertTrue(self.r.contains(1))

    def test_exists(self) -> None:
        def p(x: int) -> bool:
            return x % 2 == 0

        self.assertFalse(self.l.exists(p))
        self.assertFalse(self.r.exists(p))
        self.assertTrue(Right[str, int](2).exists(p))

    def test_flatmap(self) -> None:
        def f(x: int) -> Either[str, int]:
            if x % 2 == 0:
                return Left[str, int]("b")
            else:
                return Right[str, int](1)

        self.assertTrue(self.l.flatmap(f).swap().contains("a"))
        self.assertTrue(self.r.flatmap(f).contains(1))
        self.assertTrue(Right[str, int](2).flatmap(f).swap().contains("b"))

    def test_map(self) -> None:
        def f(x: int) -> bytes:
            return bytes(x)

        self.assertTrue(self.l.map(f).swap().contains("a"))
        self.assertTrue(self.r.map(f).contains(bytes(1)))

    def test_seq(self) -> None:
        self.assertTrue(self.l.to_seq() == [])
        self.assertTrue(self.r.to_seq() == [1])

    def test_option(self) -> None:
        self.assertTrue(self.l.to_option() is None)
        self.assertTrue(self.r.to_option() == 1)


if __name__ == "__main__":
    main()
