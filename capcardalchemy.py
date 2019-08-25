#!/usr/bin/env python
import string
import functools
import operator
from typing import Callable

class CaptchalogueCard(object):
    __slots__ = ('_code', '_raw_code')
    codestring = (
        string.digits
        + string.ascii_uppercase
        + string.ascii_lowercase
        + '?!'
        )
    bittable = {'1': '■', '0': ' '}

    def __init__(self, code: str):
        if not isinstance(code, str):
            raise TypeError('Captchalogue Card Code must be a string')
        if len(code) != 8 or any(c not in self.codestring for c in code):
            raise ValueError('Invalid Captchalogue Card Code format')
        self._code = code
        self._raw_code = self.code_to_raw(code)

    @classmethod
    def from_raw(cls, raw: int):
        if not isinstance(raw, int):
            raise TypeError('Captchalogue Card Code Number must be an integer')
        instance = object.__new__(cls)
        instance._code = cls.raw_to_code(raw)
        instance._raw_code = raw & ((1 << 48) - 1)
        return instance

    @classmethod
    def code_to_raw(cls, code: str):
        raw = 0
        for char in code:
            raw = (raw << 6) + cls.codestring.index(char)
        return raw

    @classmethod
    def raw_to_code(cls, raw: int):
        code = []
        while len(code) < 8:
            code.append(cls.codestring[raw & 0x3F])
            raw >>= 6
        return ''.join(code[::-1])

    def __str__(self) -> str:
        holearray = ''.join(
            f"║ {' '.join(self.bittable[b] for b in row)} ║\n"
            for row in zip(*zip(*[iter(f'{self._raw_code:048b}')] * 12))
            )
        return f'╔═════════╗\n{holearray}╚═════════╝\n'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._code!r})'

    def __getattr__(self, name: str):
        if name == 'code':
            return self._code
        elif name in {'raw', 'raw_code'}:
            return self._raw_code

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self._raw_code == other._raw_code

    def __hash__(self) -> int:
        return object.__hash__((type(self), self._raw_code))

    def _binop(self, other, op: Callable):
        if isinstance(other, str):
            other = self.__class__(other)
        elif isinstance(other, int):
            other = self.from_raw(other)
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.from_raw(op(self._raw_code, other._raw_code))

    __and__ = functools.partialmethod(_binop, op=operator.and_)
    __or__ = functools.partialmethod(_binop, op=operator.or_)
    __xor__ = functools.partialmethod(_binop, op=operator.xor)

    def __invert__(self):
        return self.from_raw(~self._raw_code & ((1 << 48) - 1))

if __name__ == '__main__':
    assert (
        CaptchalogueCard('nZ7Un6BI')
        & CaptchalogueCard('DQMmJLeK')
        == CaptchalogueCard('126GH48G')
        )
    assert CaptchalogueCard('82THE8TH').raw_code == 35353238472529
