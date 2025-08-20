"""
Tax calculation service for South African tax compliance.

This module provides comprehensive tax calculation services including
VAT, PAYE, UIF, SDL, and provisional tax calculations.
"""

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class TaxService:
    """Service for handling South African tax calculations."""
    
    # PAYE tax brackets for 2024/2025 tax year
    PAYE_BRACKETS = [
        (237100, Decimal("0.18"), 0),
        (370500, Decimal("0.26"), 42678),
        (512800, Decimal("0.31"), 77362),
        (673000, Decimal("0.36"), 121475),
        (857900, Decimal("0.39"), 179147),
        (1817000, Decimal("0.41"), 251258),
        (float('inf'), Decimal("0.45"), 644489),
    ]
    
    # Tax rebates for 2024/2025
    TAX_REBATES = {
        "primary": Decimal("17235"),  # All taxpayers
        "secondary": Decimal("9444"),  # 65 years and older
        "tertiary": Decimal("3145"),   # 75 years and older
    }
    
    def calculate_vat(
        self,
        amount: Decimal,
        vat_inclusive: bool = False,
        rate: Optional[Decimal] = None
    ) -> Dict[str, Decimal]:
        """
        Calculate VAT for a given amount.
        
        Args:
            amount: The amount to calculate VAT for
            vat_inclusive: Whether the amount includes VAT
            rate: VAT rate (default 15%)
            
        Returns:
            Dictionary with excl_vat, vat_amount, and incl_vat
        """
        if rate is None:
            rate = Decimal(str(settings.vat_rate))
        
        if vat_inclusive:
            # Amount includes VAT, calculate exclusive amount
            vat_divisor = Decimal("1") + rate
            excl_vat = (amount / vat_divisor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            vat_amount = (amount - excl_vat).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            incl_vat = amount
        else:
            # Amount excludes VAT, calculate inclusive amount
            excl_vat = amount
            vat_amount = (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            incl_vat = (excl_vat + vat_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        logger.debug(
            "VAT calculated",
            amount=float(amount),
            vat_inclusive=vat_inclusive,
            rate=float(rate),
            excl_vat=float(excl_vat),
            vat_amount=float(vat_amount),
            incl_vat=float(incl_vat),
        )
        
        return {
            "excl_vat": excl_vat,
            "vat_amount": vat_amount,
            "incl_vat": incl_vat,
        }
    
    def calculate_paye(
        self,
        annual_income: Decimal,
        age: int = 30,
        tax_year: str = "2024/2025"
    ) -> Dict[str, Decimal]:
        """
        Calculate PAYE (Pay As You Earn) tax.
        
        Args:
            annual_income: Annual taxable income
            age: Age of the taxpayer
            tax_year: Tax year for calculation
            
        Returns:
            Dictionary with tax calculations
        """
        # Calculate tax based on brackets
        tax = Decimal("0")
        
        for threshold, rate, base_tax in self.PAYE_BRACKETS:
            if annual_income <= threshold:
                taxable_in_bracket = annual_income - (
                    self.PAYE_BRACKETS[self.PAYE_BRACKETS.index((threshold, rate, base_tax)) - 1][0]
                    if self.PAYE_BRACKETS.index((threshold, rate, base_tax)) > 0
                    else 0
                )
                tax = Decimal(str(base_tax)) + (taxable_in_bracket * rate)
                break
        
        # Apply rebates
        rebate = self.TAX_REBATES["primary"]
        if age >= 65:
            rebate += self.TAX_REBATES["secondary"]
        if age >= 75:
            rebate += self.TAX_REBATES["tertiary"]
        
        # Calculate net tax
        annual_tax = max(Decimal("0"), tax - rebate)
        monthly_tax = (annual_tax / Decimal("12")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        # Calculate net income
        annual_net = annual_income - annual_tax
        monthly_net = (annual_net / Decimal("12")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        logger.info(
            "PAYE calculated",
            annual_income=float(annual_income),
            age=age,
            annual_tax=float(annual_tax),
            monthly_tax=float(monthly_tax),
        )
        
        return {
            "annual_income": annual_income,
            "annual_tax": annual_tax,
            "monthly_tax": monthly_tax,
            "annual_net": annual_net,
            "monthly_net": monthly_net,
            "effective_rate": (annual_tax / annual_income * Decimal("100")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ) if annual_income > 0 else Decimal("0"),
        }
    
    def calculate_uif(
        self,
        monthly_salary: Decimal,
        is_employer: bool = False
    ) -> Dict[str, Decimal]:
        """
        Calculate UIF (Unemployment Insurance Fund) contributions.
        
        Args:
            monthly_salary: Monthly salary
            is_employer: Whether calculating employer contribution
            
        Returns:
            Dictionary with UIF calculations
        """
        # UIF ceiling (as of 2024)
        uif_ceiling = Decimal("17712")
        
        # Use the lower of salary or ceiling
        contributable_salary = min(monthly_salary, uif_ceiling)
        
        # Calculate UIF (1% each for employee and employer)
        uif_rate = Decimal(str(settings.uif_rate_employer if is_employer else settings.uif_rate_employee))
        uif_amount = (contributable_salary * uif_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        
        logger.debug(
            "UIF calculated",
            monthly_salary=float(monthly_salary),
            is_employer=is_employer,
            uif_amount=float(uif_amount),
        )
        
        return {
            "monthly_salary": monthly_salary,
            "contributable_salary": contributable_salary,
            "uif_amount": uif_amount,
            "is_employer": is_employer,
        }
    
    def calculate_sdl(
        self,
        annual_payroll: Decimal
    ) -> Dict[str, Decimal]:
        """
        Calculate SDL (Skills Development Levy).
        
        SDL is payable by employers with annual payroll exceeding R500,000.
        
        Args:
            annual_payroll: Total annual payroll
            
        Returns:
            Dictionary with SDL calculations
        """
        # SDL threshold
        sdl_threshold = Decimal("500000")
        
        if annual_payroll <= sdl_threshold:
            sdl_amount = Decimal("0")
            monthly_sdl = Decimal("0")
        else:
            # SDL rate (1% of payroll)
            sdl_rate = Decimal(str(settings.sdl_rate))
            sdl_amount = (annual_payroll * sdl_rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            monthly_sdl = (sdl_amount / Decimal("12")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        
        logger.debug(
            "SDL calculated",
            annual_payroll=float(annual_payroll),
            sdl_amount=float(sdl_amount),
            monthly_sdl=float(monthly_sdl),
        )
        
        return {
            "annual_payroll": annual_payroll,
            "sdl_applicable": annual_payroll > sdl_threshold,
            "annual_sdl": sdl_amount,
            "monthly_sdl": monthly_sdl,
        }
    
    def calculate_provisional_tax(
        self,
        estimated_taxable_income: Decimal,
        period: int = 1,
        previous_year_tax: Optional[Decimal] = None
    ) -> Dict[str, Decimal]:
        """
        Calculate provisional tax payments.
        
        Args:
            estimated_taxable_income: Estimated taxable income for the year
            period: Period number (1 or 2)
            previous_year_tax: Previous year's assessed tax
            
        Returns:
            Dictionary with provisional tax calculations
        """
        # Calculate estimated tax for the year
        tax_calculation = self.calculate_paye(estimated_taxable_income)
        estimated_tax = tax_calculation["annual_tax"]
        
        if period == 1:
            # First period: 50% of estimated annual tax
            provisional_payment = (estimated_tax * Decimal("0.5")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        elif period == 2:
            # Second period: Remaining balance
            first_payment = (estimated_tax * Decimal("0.5")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            provisional_payment = estimated_tax - first_payment
        else:
            raise ValueError("Period must be 1 or 2")
        
        logger.info(
            "Provisional tax calculated",
            estimated_income=float(estimated_taxable_income),
            period=period,
            provisional_payment=float(provisional_payment),
        )
        
        return {
            "estimated_taxable_income": estimated_taxable_income,
            "estimated_annual_tax": estimated_tax,
            "period": period,
            "provisional_payment": provisional_payment,
        }
    
    def calculate_employee_cost(
        self,
        basic_salary: Decimal,
        include_uif: bool = True,
        include_sdl: bool = True,
        annual_payroll: Optional[Decimal] = None
    ) -> Dict[str, Decimal]:
        """
        Calculate total employee cost to company.
        
        Args:
            basic_salary: Monthly basic salary
            include_uif: Whether to include UIF
            include_sdl: Whether to include SDL
            annual_payroll: Annual payroll for SDL calculation
            
        Returns:
            Dictionary with comprehensive employee cost breakdown
        """
        # Calculate PAYE
        annual_salary = basic_salary * Decimal("12")
        paye = self.calculate_paye(annual_salary)
        
        # Calculate UIF (employee and employer)
        uif_employee = self.calculate_uif(basic_salary, is_employer=False) if include_uif else {"uif_amount": Decimal("0")}
        uif_employer = self.calculate_uif(basic_salary, is_employer=True) if include_uif else {"uif_amount": Decimal("0")}
        
        # Calculate SDL if applicable
        if include_sdl and annual_payroll:
            sdl = self.calculate_sdl(annual_payroll)
            monthly_sdl = sdl["monthly_sdl"]
        else:
            monthly_sdl = Decimal("0")
        
        # Calculate totals
        employee_deductions = paye["monthly_tax"] + uif_employee["uif_amount"]
        employer_contributions = uif_employer["uif_amount"] + monthly_sdl
        
        net_salary = basic_salary - employee_deductions
        total_cost = basic_salary + employer_contributions
        
        return {
            "basic_salary": basic_salary,
            "paye": paye["monthly_tax"],
            "uif_employee": uif_employee["uif_amount"],
            "uif_employer": uif_employer["uif_amount"],
            "sdl": monthly_sdl,
            "employee_deductions": employee_deductions,
            "employer_contributions": employer_contributions,
            "net_salary": net_salary,
            "total_cost_to_company": total_cost,
        }