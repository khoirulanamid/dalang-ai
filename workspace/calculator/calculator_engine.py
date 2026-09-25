"""
Calculator Engine — Dalang-AI Core Arithmetic Module
Presisi tinggi menggunakan Decimal untuk mengeliminasi floating point artifact (0.1 + 0.2 = 0.3).
"""

from decimal import Decimal, DivisionByZero, InvalidOperation, getcontext
from typing import Union, Tuple

# Tetapkan presisi hingga 28 digit signifikan
getcontext().prec = 28


class CalculatorEngine:
    """Mesin kalkulasi presisi tinggi."""

    @staticmethod
    def _to_decimal(val: Union[int, float, str, Decimal]) -> Decimal:
        try:
            return Decimal(str(val))
        except (InvalidOperation, ValueError, TypeError) as e:
            raise ValueError(f"Nilai tidak valid untuk angka: {val}") from e

    @classmethod
    def add(cls, a: Union[int, float, str], b: Union[int, float, str]) -> Decimal:
        """Operasi Penjumlahan (a + b)."""
        return cls._to_decimal(a) + cls._to_decimal(b)

    @classmethod
    def subtract(cls, a: Union[int, float, str], b: Union[int, float, str]) -> Decimal:
        """Operasi Pengurangan (a - b)."""
        return cls._to_decimal(a) - cls._to_decimal(b)

    @classmethod
    def multiply(cls, a: Union[int, float, str], b: Union[int, float, str]) -> Decimal:
        """Operasi Perkalian (a × b)."""
        return cls._to_decimal(a) * cls._to_decimal(b)

    @classmethod
    def divide(cls, a: Union[int, float, str], b: Union[int, float, str]) -> Decimal:
        """
        Operasi Pembagian (a ÷ b).
        Raises ZeroDivisionError jika pembagi adalah 0.
        """
        dec_b = cls._to_decimal(b)
        if dec_b == Decimal("0"):
            raise ZeroDivisionError("Pembagian dengan nol tidak terdefinisi")
        return cls._to_decimal(a) / dec_b

    @classmethod
    def percentage(cls, a: Union[int, float, str]) -> Decimal:
        """Operasi Persentase (a / 100)."""
        return cls._to_decimal(a) / Decimal("100")

    @classmethod
    def negate(cls, a: Union[int, float, str]) -> Decimal:
        """Membalik tanda angka (+ ke -, atau - ke +)."""
        return -cls._to_decimal(a)

    @classmethod
    def calculate(cls, a: Union[int, float, str], operator: str, b: Union[int, float, str]) -> Decimal:
        """
        Mengevaluasi operasi biner tunggal.
        Operator yang didukung: '+', '-', '*', 'x', '×', '/', '÷'
        """
        op = operator.strip().lower()
        if op == "+":
            return cls.add(a, b)
        elif op in ("-", "−"):
            return cls.subtract(a, b)
        elif op in ("*", "x", "×"):
            return cls.multiply(a, b)
        elif op in ("/", "÷", ":"):
            return cls.divide(a, b)
        else:
            raise ValueError(f"Operator tidak didukung: '{operator}'")

    @classmethod
    def format_result(cls, val: Decimal) -> str:
        """Format hasil ke string rapi: hilangkan trailing zeros jika desimal bulat."""
        if val.is_nan():
            return "NaN"
        # Normalisasi untuk buang trailing zero, misalnya 4.0000 -> 4
        normalized = val.normalize()
        # Jika scientific notation karena terlalu besar/kecil
        str_val = f"{normalized:f}" if -Decimal("1e16") < normalized < Decimal("1e16") else f"{normalized:e}"
        # Jika ada titik desimal dan diakhiri trailing .0, rapikan
        if "." in str_val and not ("e" in str_val or "E" in str_val):
            str_val = str_val.rstrip("0").rstrip(".")
        return str_val
