from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Generic, Optional, Sequence, TypeVar, final

_A = TypeVar("_A")
_A1 = TypeVar("_A1")
_B = TypeVar("_B")
_B1 = TypeVar("_B1")
_B2 = TypeVar("_B2")
_B3 = TypeVar("_B3")
_C = TypeVar("_C")


class Either(Generic[_A, _B], ABC):
    """Either"""

    @property
    @abstractmethod
    def _left(self) -> _A:
        pass

    @property
    @abstractmethod
    def _right(self) -> _B:
        pass

    @final
    def fold(self, fa: Callable[[_A], _C], fb: Callable[[_B], _C]) -> _C:
        if self.is_right:
            return fb(self._right)
        else:
            return fa(self._left)

    def swap(self) -> Either[_B, _A]:
        if self.is_right:
            return Left(self._right)
        else:
            return Right(self._left)

    def get_or_else(self, or_: _B) -> _B:
        if self.is_right:
            return self._right
        else:
            return or_

    def or_else(self, or_: Either[_A1, _B]) -> Either[_A1, _B]:
        if self.is_right:
            return self  # type: ignore
        else:
            return or_

    def contains(self, elem: _B) -> bool:
        if self.is_right:
            return self._right == elem
        else:
            return False

    def exists(self, p: Callable[[_B], bool]) -> bool:
        if self.is_right:
            return p(self._right)
        else:
            return False

    def flatmap(self, f: Callable[[_B], Either[_A, _B1]]) -> Either[_A, _B1]:
        if self.is_right:
            return f(self._right)
        else:
            return self  # type: ignore

    def flatmapa(
        self, f: Callable[[_B], Awaitable[Either[_A, _B1]]]
    ) -> AsyncEither[_A, _B, _B1]:
        if self.is_right:
            return _AsyncRightFlatMapA[_A, _B, _B1](AsyncEitherBase[_A, _B](self), f)
        else:
            return AsyncLeft[_A, _B, _B1](AsyncEitherBase[_A, _B](self))

    def map(self, f: Callable[[_B], _B1]) -> Either[_A, _B1]:
        if self.is_right:
            return Right(f(self._right))
        else:
            return self  # type: ignore

    def mapa(self, f: Callable[[_B], Awaitable[_B1]]) -> AsyncEither[_A, _B, _B1]:
        if self.is_right:
            return _AsyncRightMapA[_A, _B, _B1](AsyncEitherBase[_A, _B](self), f)
        else:
            return AsyncLeft[_A, _B, _B1](AsyncEitherBase[_A, _B](self))

    def to_seq(self) -> Sequence[_B]:
        if self.is_right:
            return [self._right]
        else:
            return []

    def to_option(self) -> Optional[_B]:
        if self.is_right:
            return self._right
        else:
            return None

    @property
    @abstractmethod
    def is_left(self) -> bool:
        """Returns True if this is a Left."""

    @property
    @abstractmethod
    def is_right(self) -> bool:
        """Returns True if this is a Right."""


@final
class Left(Either[_A, _B]):
    def __init__(self, v: _A) -> None:
        self._v = v

    @property
    def _left(self) -> _A:
        return self._v

    @property
    def _right(self) -> _B:
        raise ValueError("This is Left.")

    @property
    def is_left(self) -> bool:
        return True

    @property
    def is_right(self) -> bool:
        return False


@final
class Right(Either[_A, _B]):
    def __init__(self, v: _B) -> None:
        self._v = v

    @property
    def _left(self) -> _A:
        raise ValueError("This is Right.")

    @property
    def _right(self) -> _B:
        return self._v

    @property
    def is_left(self) -> bool:
        return False

    @property
    def is_right(self) -> bool:
        return True


class AsyncEither(Generic[_A, _B1, _B2], ABC):
    @property
    @abstractmethod
    def is_left(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_right(self) -> bool:
        pass

    @abstractmethod
    async def force(self) -> Either[_A, _B2]:
        pass

    async def fold(self, fa: Callable[[_A], _C], fb: Callable[[_B2], _C]) -> _C:
        return (await self.force()).fold(fa, fb)

    def map(self, f: Callable[[_B2], _B3]) -> AsyncEither[_A, _B2, _B3]:
        if self.is_right:
            return _AsyncRightMap[_A, _B2, _B3](self, f)
        else:
            return self  # type: ignore

    def mapa(self, f: Callable[[_B2], Awaitable[_B3]]) -> AsyncEither[_A, _B2, _B3]:
        if self.is_right:
            return _AsyncRightMapA[_A, _B2, _B3](self, f)
        else:
            return self  # type: ignore

    def flatmap(self, f: Callable[[_B2], Either[_A, _B3]]) -> AsyncEither[_A, _B2, _B3]:
        if self.is_right:
            return _AsyncRightFlatMap[_A, _B2, _B3](self, f)
        else:
            return self  # type: ignore

    def flatmapa(
        self, f: Callable[[_B2], Awaitable[Either[_A, _B3]]]
    ) -> AsyncEither[_A, _B2, _B3]:
        if self.is_right:
            return _AsyncRightFlatMapA[_A, _B2, _B3](self, f)
        else:
            return self  # type: ignore


class AsyncRight(AsyncEither[_A, _B1, _B2], ABC):
    @property
    def is_left(self) -> bool:
        return False

    @property
    def is_right(self) -> bool:
        return True


@final
class _AsyncRightMap(AsyncRight[_A, _B1, _B2]):
    def __init__(self, v: AsyncEither[_A, Any, _B1], f: Callable[[_B1], _B2]):
        self._v = v
        self._f = f

    async def force(self) -> Either[_A, _B2]:
        return (await self._v.force()).map(self._f)


@final
class _AsyncRightMapA(AsyncRight[_A, _B1, _B2]):
    def __init__(
        self, v: AsyncEither[_A, Any, _B1], f: Callable[[_B1], Awaitable[_B2]]
    ):
        self._v = v
        self._f = f

    async def force(self) -> Either[_A, _B2]:
        x = (await self._v.force()).map(self._f)
        assert x.is_right, "AsyncRight must be right."
        return Right[_A, _B2](await x._right)  # pylint: disable=protected-access


@final
class _AsyncRightFlatMap(AsyncRight[_A, _B1, _B2]):
    def __init__(
        self, v: AsyncEither[_A, Any, _B1], f: Callable[[_B1], Either[_A, _B2]]
    ) -> None:
        self._v = v
        self._f = f

    async def force(self) -> Either[_A, _B2]:
        return (await self._v.force()).flatmap(self._f)


@final
class _AsyncRightFlatMapA(AsyncRight[_A, _B1, _B2]):
    def __init__(
        self,
        v: AsyncEither[_A, Any, _B1],
        f: Callable[[_B1], Awaitable[Either[_A, _B2]]],
    ) -> None:
        self._v = v
        self._f = f

    async def force(self) -> Either[_A, _B2]:
        x = await self._v.force()
        assert x.is_right, "AsyncRight must be right."
        return await self._f(x._right)  # pylint: disable=protected-access


@final
class AsyncLeft(AsyncEither[_A, _B1, _B2]):
    def __init__(self, v: AsyncEither[_A, Any, _B1]) -> None:
        self._v = v

    @property
    def is_left(self) -> bool:
        return True

    @property
    def is_right(self) -> bool:
        return False

    async def force(self) -> Either[_A, _B2]:
        return await self._v.force()  # type: ignore


@final
class AsyncEitherBase(AsyncEither[_A, _B, _B]):
    def __init__(self, v: Either[_A, _B]) -> None:
        self._v = v

    @property
    def is_left(self) -> bool:
        return self._v.is_left

    @property
    def is_right(self) -> bool:
        return self._v.is_right

    async def force(self) -> Either[_A, _B]:
        return self._v
