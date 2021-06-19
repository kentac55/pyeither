from asyncio import sleep
from unittest import IsolatedAsyncioTestCase, main

from pyeither import *


class TestEither(IsolatedAsyncioTestCase):

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

    async def test_mapa(self) -> None:
        async def f(x: int) -> bytes:
            await sleep(0.01)
            return bytes(x)

        self.assertTrue((await self.l.mapa(f).force()).swap().contains("a"))
        self.assertTrue((await self.r.mapa(f).force()).contains(bytes(1)))

    async def test_flatmapa(self) -> None:
        async def f(x: int) -> Either[str, int]:
            await sleep(0.01)
            if x % 2 == 0:
                return Left[str, int]("b")
            else:
                return Right[str, int](1)

        self.assertTrue((await self.l.flatmapa(f).force()).swap().contains("a"))
        self.assertTrue((await self.r.flatmapa(f).force()).contains(1))
        self.assertTrue(
            (await Right[str, int](2).flatmapa(f).force()).swap().contains("b")
        )


class TestAsyncEitherChain(IsolatedAsyncioTestCase):
    i = Right[str, int](2)
    o = 8

    @staticmethod
    def mf(x: int) -> int:
        return x * 2

    @staticmethod
    async def mfa(x: int) -> int:
        await sleep(0.01)
        return x * 2

    @staticmethod
    def fmf(x: int) -> Either[str, int]:
        return Right[str, int](x * 2)

    @staticmethod
    async def fmfa(x: int) -> Either[str, int]:
        await sleep(0.01)
        return Right[str, int](x * 2)

    def _assertTrue(self, x: Either[str, int]) -> None:
        self.assertTrue(x.contains(self.o))

    async def _assertTrueA(self, x: AsyncEither[str, int, int]) -> None:
        self.assertTrue((await x.force()).contains(self.o))

    def test_map2map(self) -> None:
        self._assertTrue(self.i.map(self.mf).map(self.mf))

    async def test_map2mapa(self) -> None:
        await self._assertTrueA(self.i.map(self.mf).mapa(self.mfa))

    def test_map2flatmap(self) -> None:
        self._assertTrue(self.i.map(self.mf).flatmap(self.fmf))

    async def test_map2flatmapa(self) -> None:
        await self._assertTrueA(self.i.map(self.mf).flatmapa(self.fmfa))

    async def test_mapa2map(self) -> None:
        await self._assertTrueA(self.i.mapa(self.mfa).map(self.mf))

    async def test_mapa2mapa(self) -> None:
        await self._assertTrueA(self.i.mapa(self.mfa).mapa(self.mfa))

    async def test_mapa2flatmap(self) -> None:
        await self._assertTrueA(self.i.mapa(self.mfa).flatmap(self.fmf))

    async def test_mapa2flatmapa(self) -> None:
        await self._assertTrueA(self.i.mapa(self.mfa).flatmapa(self.fmfa))

    def test_flatmap2map(self) -> None:
        self._assertTrue(self.i.flatmap(self.fmf).map(self.mf))

    async def test_flatmap2mapa(self) -> None:
        await self._assertTrueA(self.i.flatmap(self.fmf).mapa(self.mfa))

    def test_flatmap2flatmap(self) -> None:
        self._assertTrue(self.i.flatmap(self.fmf).flatmap(self.fmf))

    async def test_flatmap2flatmapa(self) -> None:
        await self._assertTrueA(self.i.flatmap(self.fmf).flatmapa(self.fmfa))

    async def test_flatmapa2map(self) -> None:
        await self._assertTrueA(self.i.flatmapa(self.fmfa).map(self.mf))

    async def test_flatmapa2mapa(self) -> None:
        await self._assertTrueA(self.i.flatmapa(self.fmfa).mapa(self.mfa))

    async def test_flatmapa2flatmap(self) -> None:
        await self._assertTrueA(self.i.flatmapa(self.fmfa).flatmap(self.fmf))

    async def test_flatmapa2flatmapa(self) -> None:
        await self._assertTrueA(self.i.flatmapa(self.fmfa).flatmapa(self.fmfa))


class TestAsyncEither(IsolatedAsyncioTestCase):
    r = Right[str, int](2)
    l = Left[str, int]("2")

    @staticmethod
    def f1(x: int) -> int:
        return x * 2

    @staticmethod
    async def f2(x: int) -> int:
        await sleep(0.01)
        return x * 2

    @staticmethod
    def f3(x: int) -> Either[str, int]:
        if x == 8:
            return Left[str, int]("2")
        else:
            return Right[str, int](x * 2)

    @staticmethod
    async def f4(x: int) -> Either[str, int]:
        await sleep(0.01)
        if x == 8:
            return Left[str, int]("2")
        else:
            return Right[str, int](x * 2)

    async def test_is_left(self) -> None:
        self.assertFalse(self.r.mapa(self.f2).is_left)
        self.assertTrue(self.l.mapa(self.f2).is_left)

    async def test_is_right(self) -> None:
        self.assertTrue(self.r.mapa(self.f2).is_right)
        self.assertFalse(self.l.mapa(self.f2).is_right)

    async def test_map(self) -> None:
        self.assertTrue((await self.r.mapa(self.f2).map(self.f1).force()).contains(8))
        self.assertTrue(
            (await self.l.mapa(self.f2).map(self.f1).force()).swap().contains("2")
        )

    async def test_mapa(self) -> None:
        self.assertTrue((await self.r.mapa(self.f2).mapa(self.f2).force()).contains(8))
        self.assertTrue(
            (await self.l.mapa(self.f2).mapa(self.f2).force()).swap().contains("2")
        )

    async def test_flatmap(self) -> None:
        self.assertTrue(
            (await self.r.mapa(self.f2).flatmap(self.f3).force()).contains(8)
        )
        self.assertTrue(
            (await self.l.mapa(self.f2).flatmap(self.f3).force()).swap().contains("2")
        )

    async def test_flatmapa(self) -> None:
        self.assertTrue(
            (await self.r.mapa(self.f2).flatmapa(self.f4).force()).contains(8)
        )
        self.assertTrue(
            (await self.l.mapa(self.f2).flatmapa(self.f4).force()).swap().contains("2")
        )

    async def test_fold(self) -> None:
        def fa(x: str) -> bool:
            return False

        def fb(x: int) -> bool:
            return True

        self.assertTrue(
            await self.r.mapa(self.f2)
            .mapa(self.f2)
            .mapa(self.f2)
            .mapa(self.f2)
            .fold(fa, fb)
        )
        self.assertFalse(
            await self.l.mapa(self.f2)
            .mapa(self.f2)
            .mapa(self.f2)
            .mapa(self.f2)
            .fold(fa, fb)
        )
        self.assertFalse(
            await self.r.mapa(self.f2).mapa(self.f2).flatmapa(self.f4).fold(fa, fb)
        )
        self.assertTrue(
            await self.r.mapa(self.f2)
            .mapa(self.f2)
            .mapa(self.f2)
            .flatmapa(self.f4)
            .fold(fa, fb)
        )
        self.assertFalse(
            await self.r.mapa(self.f2).mapa(self.f2).flatmap(self.f3).fold(fa, fb)
        )
        self.assertTrue(
            await self.r.mapa(self.f2)
            .mapa(self.f2)
            .mapa(self.f2)
            .flatmap(self.f3)
            .fold(fa, fb)
        )
        self.assertFalse(await self.l.flatmapa(self.f4).fold(fa, fb))


class TestAsyncLeft(IsolatedAsyncioTestCase):
    v = AsyncLeft[str, int, bool](AsyncEitherBase(Left[str, int]("2")))

    def test_is_left(self) -> None:
        self.assertTrue(self.v.is_left)

    def test_is_right(self) -> None:
        self.assertFalse(self.v.is_right)


class TestAsyncEitherBase(IsolatedAsyncioTestCase):
    l = AsyncEitherBase(Left[str, int]("2"))
    r = AsyncEitherBase(Right[str, int](2))

    def test_is_left(self) -> None:
        self.assertTrue(self.l.is_left)
        self.assertFalse(self.r.is_left)

    def test_is_right(self) -> None:
        self.assertFalse(self.l.is_right)
        self.assertTrue(self.r.is_right)


if __name__ == "__main__":
    main()
