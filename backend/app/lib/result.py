"""Result sum type for fail-loudly use case returns.

Consumers must always annotate with explicit type parameters, e.g.
`Result[UserDto, DomainError]`. Pattern-match with
`match result: case Ok(v): ...; case Err(e): ...`.
"""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class Ok[T]:
    value: T
    is_ok: Literal[True] = True


@dataclass(frozen=True, slots=True)
class Err[E]:
    error: E
    is_ok: Literal[False] = False


type Result[T, E] = Ok[T] | Err[E]
