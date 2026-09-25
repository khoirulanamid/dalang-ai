"""
Test Suite: Kalkulator Dingin (Ren — Wayang Jaksa)
Standar Internasional:
- AAA Pattern (Arrange, Act, Assert)
- Boundary Value Analysis (BVA) & Partitioning
- Zero Division Exception Handling
- Floating Point Precision (0.1 + 0.2 = 0.3)
"""

import pytest
from decimal import Decimal
from calculator_engine import CalculatorEngine


class TestPenjumlahan:
    """Uji coba operasi penjumlahan (+)."""

    def test_tambah_bilangan_bulat_positif(self):
        # Arrange
        a, b = 15, 27
        # Act
        hasil = CalculatorEngine.add(a, b)
        # Assert
        assert hasil == Decimal("42")

    def test_tambah_bilangan_negatif(self):
        # Arrange
        a, b = -10, -25
        # Act
        hasil = CalculatorEngine.add(a, b)
        # Assert
        assert hasil == Decimal("-35")

    def test_tambah_desimal_presisi_tinggi(self):
        """Memastikan tidak ada artifact floating-point IEEE 754 (0.1 + 0.2 = 0.30000000000000004)."""
        # Arrange
        a, b = "0.1", "0.2"
        # Act
        hasil = CalculatorEngine.add(a, b)
        # Assert
        assert hasil == Decimal("0.3")

    def test_tambah_dengan_nol(self):
        # Arrange
        a, b = 999.99, 0
        # Act
        hasil = CalculatorEngine.add(a, b)
        # Assert
        assert hasil == Decimal("999.99")


class TestPengurangan:
    """Uji coba operasi pengurangan (−)."""

    def test_kurang_positif(self):
        # Arrange
        a, b = 100, 37
        # Act
        hasil = CalculatorEngine.subtract(a, b)
        # Assert
        assert hasil == Decimal("63")

    def test_kurang_menghasilkan_negatif(self):
        # Arrange
        a, b = 25, 75
        # Act
        hasil = CalculatorEngine.subtract(a, b)
        # Assert
        assert hasil == Decimal("-50")

    def test_kurang_dengan_bilangan_negatif(self):
        # Arrange (minus ketemu minus jadi plus)
        a, b = 50, -30
        # Act
        hasil = CalculatorEngine.subtract(a, b)
        # Assert
        assert hasil == Decimal("80")


class TestPerkalian:
    """Uji coba operasi perkalian (×)."""

    def test_kali_bilangan_bulat(self):
        # Arrange
        a, b = 12, 12
        # Act
        hasil = CalculatorEngine.multiply(a, b)
        # Assert
        assert hasil == Decimal("144")

    def test_kali_dengan_nol(self):
        # Arrange
        a, b = 987654321, 0
        # Act
        hasil = CalculatorEngine.multiply(a, b)
        # Assert
        assert hasil == Decimal("0")

    def test_kali_desimal_presisi(self):
        # Arrange
        a, b = "2.5", "4.2"
        # Act
        hasil = CalculatorEngine.multiply(a, b)
        # Assert
        assert hasil == Decimal("10.50")

    def test_kali_tanda_berlawanan(self):
        # Arrange
        a, b = -8, 9
        # Act
        hasil = CalculatorEngine.multiply(a, b)
        # Assert
        assert hasil == Decimal("-72")


class TestPembagian:
    """Uji coba operasi pembagian (÷)."""

    def test_bagi_habis(self):
        # Arrange
        a, b = 100, 4
        # Act
        hasil = CalculatorEngine.divide(a, b)
        # Assert
        assert hasil == Decimal("25")

    def test_bagi_desimal(self):
        # Arrange
        a, b = 7, 2
        # Act
        hasil = CalculatorEngine.divide(a, b)
        # Assert
        assert hasil == Decimal("3.5")

    def test_pembagian_dengan_nol_harus_raise_error(self):
        # Arrange
        a, b = 42, 0
        # Act & Assert
        with pytest.raises(ZeroDivisionError, match="Pembagian dengan nol tidak terdefinisi"):
            CalculatorEngine.divide(a, b)


class TestFungsiKhusus:
    """Uji coba fungsi persentase (%), negasi (±), dan evaluasi ekspresi."""

    def test_persentase(self):
        # Arrange
        a = 250
        # Act
        hasil = CalculatorEngine.percentage(a)
        # Assert
        assert hasil == Decimal("2.5")

    def test_negasi_positif_ke_negatif(self):
        # Arrange
        a = 45.6
        # Act
        hasil = CalculatorEngine.negate(a)
        # Assert
        assert hasil == Decimal("-45.6")

    def test_negasi_negatif_ke_positif(self):
        # Arrange
        a = -99
        # Act
        hasil = CalculatorEngine.negate(a)
        # Assert
        assert hasil == Decimal("99")

    def test_calculate_router_semua_operator(self):
        assert CalculatorEngine.calculate(10, "+", 5) == Decimal("15")
        assert CalculatorEngine.calculate(10, "-", 5) == Decimal("5")
        assert CalculatorEngine.calculate(10, "×", 5) == Decimal("50")
        assert CalculatorEngine.calculate(10, "÷", 5) == Decimal("2")

    def test_format_result_clean(self):
        """Memastikan format hasil tidak menyisakan trailing zeros yang jelek."""
        assert CalculatorEngine.format_result(Decimal("4.0000")) == "4"
        assert CalculatorEngine.format_result(Decimal("12.500")) == "12.5"
        assert CalculatorEngine.format_result(Decimal("0.300")) == "0.3"
