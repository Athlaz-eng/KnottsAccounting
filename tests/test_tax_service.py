"""
Tests for the TaxService class.

This module tests South African tax calculations including VAT, PAYE, UIF, and SDL.
"""

from decimal import Decimal
import pytest

from src.services.tax_service import TaxService


class TestTaxService:
    """Test cases for TaxService."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.service = TaxService()
    
    def test_calculate_vat_exclusive(self):
        """Test VAT calculation for amount excluding VAT."""
        result = self.service.calculate_vat(
            amount=Decimal("1000.00"),
            vat_inclusive=False,
            rate=Decimal("0.15")
        )
        
        assert result["excl_vat"] == Decimal("1000.00")
        assert result["vat_amount"] == Decimal("150.00")
        assert result["incl_vat"] == Decimal("1150.00")
    
    def test_calculate_vat_inclusive(self):
        """Test VAT calculation for amount including VAT."""
        result = self.service.calculate_vat(
            amount=Decimal("1150.00"),
            vat_inclusive=True,
            rate=Decimal("0.15")
        )
        
        assert result["excl_vat"] == Decimal("1000.00")
        assert result["vat_amount"] == Decimal("150.00")
        assert result["incl_vat"] == Decimal("1150.00")
    
    def test_calculate_paye_low_income(self):
        """Test PAYE calculation for low income (below tax threshold)."""
        result = self.service.calculate_paye(
            annual_income=Decimal("200000.00"),
            age=30
        )
        
        # Income below R237,100 taxed at 18%
        # Tax = 200,000 * 0.18 = 36,000
        # Less rebate of 17,235 = 18,765
        assert result["annual_tax"] == Decimal("18765.00")
        assert result["annual_income"] == Decimal("200000.00")
        assert result["monthly_tax"] == Decimal("1563.75")
    
    def test_calculate_paye_high_income(self):
        """Test PAYE calculation for high income."""
        result = self.service.calculate_paye(
            annual_income=Decimal("600000.00"),
            age=35
        )
        
        # Tax calculation for R600,000 annual income
        # This falls in the 36% bracket (R512,801 - R673,000)
        assert result["annual_income"] == Decimal("600000.00")
        assert result["annual_tax"] > Decimal("0")
        assert result["monthly_tax"] == result["annual_tax"] / Decimal("12")
    
    def test_calculate_paye_with_age_rebate(self):
        """Test PAYE calculation with age rebates."""
        # Test for 65+ (gets secondary rebate)
        result_65 = self.service.calculate_paye(
            annual_income=Decimal("400000.00"),
            age=65
        )
        
        # Test for under 65 (primary rebate only)
        result_30 = self.service.calculate_paye(
            annual_income=Decimal("400000.00"),
            age=30
        )
        
        # 65+ should pay less tax due to additional rebate
        assert result_65["annual_tax"] < result_30["annual_tax"]
    
    def test_calculate_uif_employee(self):
        """Test UIF calculation for employee contribution."""
        result = self.service.calculate_uif(
            monthly_salary=Decimal("20000.00"),
            is_employer=False
        )
        
        # UIF is capped at R17,712 monthly salary
        # 1% of R17,712 = R177.12
        assert result["contributable_salary"] == Decimal("17712.00")
        assert result["uif_amount"] == Decimal("177.12")
    
    def test_calculate_uif_below_ceiling(self):
        """Test UIF calculation for salary below ceiling."""
        result = self.service.calculate_uif(
            monthly_salary=Decimal("10000.00"),
            is_employer=False
        )
        
        # 1% of R10,000 = R100.00
        assert result["contributable_salary"] == Decimal("10000.00")
        assert result["uif_amount"] == Decimal("100.00")
    
    def test_calculate_sdl_below_threshold(self):
        """Test SDL calculation for payroll below threshold."""
        result = self.service.calculate_sdl(
            annual_payroll=Decimal("400000.00")
        )
        
        # SDL not applicable below R500,000
        assert result["sdl_applicable"] is False
        assert result["annual_sdl"] == Decimal("0")
        assert result["monthly_sdl"] == Decimal("0")
    
    def test_calculate_sdl_above_threshold(self):
        """Test SDL calculation for payroll above threshold."""
        result = self.service.calculate_sdl(
            annual_payroll=Decimal("1000000.00")
        )
        
        # 1% of R1,000,000 = R10,000
        assert result["sdl_applicable"] is True
        assert result["annual_sdl"] == Decimal("10000.00")
        assert result["monthly_sdl"] == Decimal("833.33")
    
    def test_calculate_provisional_tax_period1(self):
        """Test provisional tax calculation for first period."""
        result = self.service.calculate_provisional_tax(
            estimated_taxable_income=Decimal("500000.00"),
            period=1
        )
        
        # First period is 50% of estimated annual tax
        assert result["period"] == 1
        assert result["provisional_payment"] == result["estimated_annual_tax"] * Decimal("0.5")
    
    def test_calculate_provisional_tax_period2(self):
        """Test provisional tax calculation for second period."""
        result = self.service.calculate_provisional_tax(
            estimated_taxable_income=Decimal("500000.00"),
            period=2
        )
        
        # Second period is remaining 50%
        assert result["period"] == 2
        first_payment = result["estimated_annual_tax"] * Decimal("0.5")
        assert result["provisional_payment"] == result["estimated_annual_tax"] - first_payment
    
    def test_calculate_employee_cost(self):
        """Test total employee cost to company calculation."""
        result = self.service.calculate_employee_cost(
            basic_salary=Decimal("25000.00"),
            include_uif=True,
            include_sdl=True,
            annual_payroll=Decimal("600000.00")
        )
        
        assert result["basic_salary"] == Decimal("25000.00")
        assert result["uif_employee"] == Decimal("177.12")  # Capped at ceiling
        assert result["uif_employer"] == Decimal("177.12")
        assert result["sdl"] == Decimal("500.00")  # 1% of monthly portion
        assert result["net_salary"] < result["basic_salary"]
        assert result["total_cost_to_company"] > result["basic_salary"]
    
    @pytest.mark.parametrize("amount,expected_vat", [
        (Decimal("100.00"), Decimal("15.00")),
        (Decimal("1000.00"), Decimal("150.00")),
        (Decimal("5555.55"), Decimal("833.33")),
    ])
    def test_vat_calculations_parametrized(self, amount, expected_vat):
        """Parametrized test for various VAT calculations."""
        result = self.service.calculate_vat(amount, vat_inclusive=False)
        assert result["vat_amount"] == expected_vat