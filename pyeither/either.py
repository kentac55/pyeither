from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Generic, Optional, Sequence, TypeVar, final

_A = TypeVar("_A")
_A1 = TypeVar("_A1")
_B = TypeVar("_B")
_B1 = TypeVar("_B1")
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
        if self.is_left:
            return fa(self._left)
        else:
            return fb(self._right)

    def swap(self) -> Either[_B, _A]:
        if self.is_left:
            return Right(self._left)
        else:
            return Left(self._right)

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

    def map(self, f: Callable[[_B], _B1]) -> Either[_A, _B1]:
        if self.is_right:
            return Right(f(self._right))
        else:
            return self  # type: ignore

    def to_seq(self) -> Sequence[_B]:
        if self.is_right:
            return [self._right]
        else:
            return []

    def to_option(self) -> Optional[_B]:
        return self._right if self.is_right else None

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
