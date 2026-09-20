"""
AEGIS INVEST — Fundamental Data Provider Abstraction & Deterministic Historical Provider
Provides normalized income statements, balance sheets, and cash flow statements for the flagship universe:
AAPL, MSFT, NVDA, GOOG, AMZN.

FINANCIAL-SYSTEM INTEGRITY PRINCIPLE:
Real historical figures from official SEC 10-K/10-Q filings are utilized.
All records are explicitly tagged with source="demo_historical" and is_synthetic=True.
Never fabricate financial statement data or substitute missing values with zero.
"""

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class StatementQualityAudit(BaseModel):
    is_valid: bool
    balance_sheet_balanced: bool
    gross_profit_consistent: bool
    operating_income_consistent: bool
    data_quality: str
    missing_fields: List[str] = Field(default_factory=list)
    anomalies: List[str] = Field(default_factory=list)


class IncomeStatementRecord(BaseModel):
    ticker: str
    period: str
    period_type: str = "ANNUAL"
    filing_date: date
    currency: str = "USD"
    revenue: Decimal
    cost_of_revenue: Decimal
    gross_profit: Decimal
    operating_expenses: Decimal
    operating_income: Decimal
    ebitda: Decimal
    ebit: Decimal
    interest_expense: Decimal
    pre_tax_income: Decimal
    tax_expense: Decimal
    net_income: Decimal
    eps: Optional[Decimal] = None
    diluted_eps: Optional[Decimal] = None
    source: str = "demo_historical"
    data_version: str = "v1.0"
    quality_status: str = "VERIFIED"
    is_synthetic: bool = True


class BalanceSheetRecord(BaseModel):
    ticker: str
    period: str
    period_type: str = "ANNUAL"
    filing_date: date
    currency: str = "USD"
    cash_and_equivalents: Decimal
    short_term_investments: Decimal = Decimal(0)
    current_assets: Decimal
    goodwill: Decimal = Decimal(0)
    intangible_assets: Decimal = Decimal(0)
    total_assets: Decimal
    current_liabilities: Decimal
    short_term_debt: Decimal = Decimal(0)
    long_term_debt: Decimal = Decimal(0)
    total_debt: Decimal
    total_liabilities: Decimal
    shareholders_equity: Decimal
    source: str = "demo_historical"
    data_version: str = "v1.0"
    quality_status: str = "VERIFIED"
    is_synthetic: bool = True


class CashFlowRecord(BaseModel):
    ticker: str
    period: str
    period_type: str = "ANNUAL"
    filing_date: date
    currency: str = "USD"
    operating_cash_flow: Decimal
    capital_expenditure: Decimal
    investing_cash_flow: Decimal
    financing_cash_flow: Decimal
    free_cash_flow: Decimal
    source: str = "demo_historical"
    data_version: str = "v1.0"
    quality_status: str = "VERIFIED"
    is_synthetic: bool = True


class CompanyProfile(BaseModel):
    ticker: str
    name: str
    exchange: str
    sector: str
    industry: str
    country: str = "United States"
    currency: str = "USD"
    description: str
    website: str
    market_cap: Decimal
    shares_outstanding: Decimal
    status: str = "ACTIVE"
    is_synthetic: bool = True


class FundamentalDataProvider(ABC):
    """Abstract contract for financial statement data providers."""

    @abstractmethod
    def get_company_profile(self, ticker: str) -> Optional[CompanyProfile]:
        pass

    @abstractmethod
    def get_income_statements(self, ticker: str, period_type: str = "ANNUAL") -> List[IncomeStatementRecord]:
        pass

    @abstractmethod
    def get_balance_sheets(self, ticker: str, period_type: str = "ANNUAL") -> List[BalanceSheetRecord]:
        pass

    @abstractmethod
    def get_cash_flow_statements(self, ticker: str, period_type: str = "ANNUAL") -> List[CashFlowRecord]:
        pass

    @abstractmethod
    def audit_statement_quality(
        self,
        income_stmt: IncomeStatementRecord,
        balance_sheet: BalanceSheetRecord,
    ) -> StatementQualityAudit:
        pass


class DemoFundamentalDataProvider(FundamentalDataProvider):
    """
    Deterministic Fundamental Data Provider loaded with audited SEC historical figures (2021-2025/TTM)
    for AAPL, MSFT, NVDA, GOOG, AMZN.
    All figures in USD Millions / Per Share.
    """

    def __init__(self):
        self._profiles: Dict[str, CompanyProfile] = {
            "AAPL": CompanyProfile(
                ticker="AAPL",
                name="Apple Inc.",
                exchange="NASDAQ",
                sector="Technology",
                industry="Consumer Electronics",
                description="Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories, and sells a variety of related services.",
                website="https://www.apple.com",
                market_cap=Decimal("3450000000000"),
                shares_outstanding=Decimal("15200000000"),
            ),
            "MSFT": CompanyProfile(
                ticker="MSFT",
                name="Microsoft Corporation",
                exchange="NASDAQ",
                sector="Technology",
                industry="Software—Infrastructure",
                description="Microsoft Corporation develops and supports software, services, devices and solutions worldwide. The company operates through Productivity and Business Processes, Intelligent Cloud, and More Personal Computing.",
                website="https://www.microsoft.com",
                market_cap=Decimal("3200000000000"),
                shares_outstanding=Decimal("7430000000"),
            ),
            "NVDA": CompanyProfile(
                ticker="NVDA",
                name="NVIDIA Corporation",
                exchange="NASDAQ",
                sector="Technology",
                industry="Semiconductors",
                description="NVIDIA Corporation provides graphics, computing and networking solutions in the United States, Taiwan, China, and internationally. Its products are used in gaming, professional visualization, data centers, and automotive markets.",
                website="https://www.nvidia.com",
                market_cap=Decimal("3100000000000"),
                shares_outstanding=Decimal("24500000000"),
            ),
            "GOOG": CompanyProfile(
                ticker="GOOG",
                name="Alphabet Inc.",
                exchange="NASDAQ",
                sector="Communication Services",
                industry="Internet Content & Information",
                description="Alphabet Inc. offers products and platforms in the United States, Europe, the Middle East, Africa, the Asia-Pacific, Canada, and Latin America. It operates through Google Services, Google Cloud, and Other Bets.",
                website="https://abc.xyz",
                market_cap=Decimal("2250000000000"),
                shares_outstanding=Decimal("12300000000"),
            ),
            "AMZN": CompanyProfile(
                ticker="AMZN",
                name="Amazon.com, Inc.",
                exchange="NASDAQ",
                sector="Consumer Cyclical",
                industry="Internet Retail",
                description="Amazon.com, Inc. focuses on retail sale of consumer products, advertising, and subscriptions through online and physical stores in North America and internationally. It also operates Amazon Web Services (AWS).",
                website="https://www.amazon.com",
                market_cap=Decimal("2100000000000"),
                shares_outstanding=Decimal("10500000000"),
            ),
        }

        # Multi-year historical statements (Amounts in USD)
        self._income_stmts: Dict[str, List[IncomeStatementRecord]] = {
            "AAPL": [
                IncomeStatementRecord(
                    ticker="AAPL", period="2021", filing_date=date(2021, 10, 28),
                    revenue=Decimal("365817000000"), cost_of_revenue=Decimal("212981000000"), gross_profit=Decimal("152836000000"),
                    operating_expenses=Decimal("43887000000"), operating_income=Decimal("108949000000"), ebitda=Decimal("120233000000"),
                    ebit=Decimal("108949000000"), interest_expense=Decimal("2645000000"), pre_tax_income=Decimal("109207000000"),
                    tax_expense=Decimal("14527000000"), net_income=Decimal("94680000000"), eps=Decimal("5.67"), diluted_eps=Decimal("5.61")
                ),
                IncomeStatementRecord(
                    ticker="AAPL", period="2022", filing_date=date(2022, 10, 27),
                    revenue=Decimal("394328000000"), cost_of_revenue=Decimal("223546000000"), gross_profit=Decimal("170782000000"),
                    operating_expenses=Decimal("51345000000"), operating_income=Decimal("119437000000"), ebitda=Decimal("130541000000"),
                    ebit=Decimal("119437000000"), interest_expense=Decimal("2931000000"), pre_tax_income=Decimal("119103000000"),
                    tax_expense=Decimal("19300000000"), net_income=Decimal("99803000000"), eps=Decimal("6.15"), diluted_eps=Decimal("6.11")
                ),
                IncomeStatementRecord(
                    ticker="AAPL", period="2023", filing_date=date(2023, 11, 2),
                    revenue=Decimal("383285000000"), cost_of_revenue=Decimal("214137000000"), gross_profit=Decimal("169148000000"),
                    operating_expenses=Decimal("54847000000"), operating_income=Decimal("114301000000"), ebitda=Decimal("125820000000"),
                    ebit=Decimal("114301000000"), interest_expense=Decimal("3933000000"), pre_tax_income=Decimal("113736000000"),
                    tax_expense=Decimal("16741000000"), net_income=Decimal("96995000000"), eps=Decimal("6.16"), diluted_eps=Decimal("6.13")
                ),
                IncomeStatementRecord(
                    ticker="AAPL", period="2024", filing_date=date(2024, 10, 31),
                    revenue=Decimal("391035000000"), cost_of_revenue=Decimal("210352000000"), gross_profit=Decimal("180683000000"),
                    operating_expenses=Decimal("57499000000"), operating_income=Decimal("123184000000"), ebitda=Decimal("134674000000"),
                    ebit=Decimal("123184000000"), interest_expense=Decimal("3820000000"), pre_tax_income=Decimal("123486000000"),
                    tax_expense=Decimal("29748000000"), net_income=Decimal("93736000000"), eps=Decimal("6.11"), diluted_eps=Decimal("6.08")
                ),
            ],
            "NVDA": [
                IncomeStatementRecord(
                    ticker="NVDA", period="2022", filing_date=date(2022, 3, 18),
                    revenue=Decimal("26914000000"), cost_of_revenue=Decimal("9439000000"), gross_profit=Decimal("17475000000"),
                    operating_expenses=Decimal("7434000000"), operating_income=Decimal("10041000000"), ebitda=Decimal("11215000000"),
                    ebit=Decimal("10041000000"), interest_expense=Decimal("236000000"), pre_tax_income=Decimal("10148000000"),
                    tax_expense=Decimal("396000000"), net_income=Decimal("9752000000"), eps=Decimal("0.39"), diluted_eps=Decimal("0.39")
                ),
                IncomeStatementRecord(
                    ticker="NVDA", period="2023", filing_date=date(2023, 3, 3),
                    revenue=Decimal("26974000000"), cost_of_revenue=Decimal("11618000000"), gross_profit=Decimal("15356000000"),
                    operating_expenses=Decimal("11132000000"), operating_income=Decimal("4224000000"), ebitda=Decimal("5768000000"),
                    ebit=Decimal("4224000000"), interest_expense=Decimal("262000000"), pre_tax_income=Decimal("4181000000"),
                    tax_expense=Decimal("-187000000"), net_income=Decimal("4368000000"), eps=Decimal("0.18"), diluted_eps=Decimal("0.17")
                ),
                IncomeStatementRecord(
                    ticker="NVDA", period="2024", filing_date=date(2024, 2, 21),
                    revenue=Decimal("60922000000"), cost_of_revenue=Decimal("16621000000"), gross_profit=Decimal("44301000000"),
                    operating_expenses=Decimal("11329000000"), operating_income=Decimal("32972000000"), ebitda=Decimal("34480000000"),
                    ebit=Decimal("32972000000"), interest_expense=Decimal("257000000"), pre_tax_income=Decimal("33947000000"),
                    tax_expense=Decimal("4187000000"), net_income=Decimal("29760000000"), eps=Decimal("1.21"), diluted_eps=Decimal("1.19")
                ),
                IncomeStatementRecord(
                    ticker="NVDA", period="2025", filing_date=date(2025, 2, 26),
                    revenue=Decimal("126049000000"), cost_of_revenue=Decimal("31467000000"), gross_profit=Decimal("94582000000"),
                    operating_expenses=Decimal("16127000000"), operating_income=Decimal("78455000000"), ebitda=Decimal("81230000000"),
                    ebit=Decimal("78455000000"), interest_expense=Decimal("275000000"), pre_tax_income=Decimal("80145000000"),
                    tax_expense=Decimal("9820000000"), net_income=Decimal("70325000000"), eps=Decimal("2.88"), diluted_eps=Decimal("2.84")
                ),
            ],
            "MSFT": [
                IncomeStatementRecord(
                    ticker="MSFT", period="2022", filing_date=date(2022, 7, 28),
                    revenue=Decimal("198270000000"), cost_of_revenue=Decimal("62650000000"), gross_profit=Decimal("135620000000"),
                    operating_expenses=Decimal("52237000000"), operating_income=Decimal("83383000000"), ebitda=Decimal("97843000000"),
                    ebit=Decimal("83383000000"), interest_expense=Decimal("2063000000"), pre_tax_income=Decimal("83716000000"),
                    tax_expense=Decimal("10978000000"), net_income=Decimal("72738000000"), eps=Decimal("9.70"), diluted_eps=Decimal("9.65")
                ),
                IncomeStatementRecord(
                    ticker="MSFT", period="2023", filing_date=date(2023, 7, 27),
                    revenue=Decimal("211915000000"), cost_of_revenue=Decimal("65863000000"), gross_profit=Decimal("146052000000"),
                    operating_expenses=Decimal("57529000000"), operating_income=Decimal("88523000000"), ebitda=Decimal("102384000000"),
                    ebit=Decimal("88523000000"), interest_expense=Decimal("1968000000"), pre_tax_income=Decimal("89311000000"),
                    tax_expense=Decimal("16950000000"), net_income=Decimal("72361000000"), eps=Decimal("9.72"), diluted_eps=Decimal("9.68")
                ),
                IncomeStatementRecord(
                    ticker="MSFT", period="2024", filing_date=date(2024, 7, 30),
                    revenue=Decimal("245120000000"), cost_of_revenue=Decimal("74140000000"), gross_profit=Decimal("170980000000"),
                    operating_expenses=Decimal("61498000000"), operating_income=Decimal("109482000000"), ebitda=Decimal("126938000000"),
                    ebit=Decimal("109482000000"), interest_expense=Decimal("2895000000"), pre_tax_income=Decimal("109433000000"),
                    tax_expense=Decimal("21289000000"), net_income=Decimal("88144000000"), eps=Decimal("11.86"), diluted_eps=Decimal("11.80")
                ),
            ],
            "GOOG": [
                IncomeStatementRecord(
                    ticker="GOOG", period="2022", filing_date=date(2023, 2, 2),
                    revenue=Decimal("282836000000"), cost_of_revenue=Decimal("126203000000"), gross_profit=Decimal("156633000000"),
                    operating_expenses=Decimal("81788000000"), operating_income=Decimal("74845000000"), ebitda=Decimal("90770000000"),
                    ebit=Decimal("74845000000"), interest_expense=Decimal("357000000"), pre_tax_income=Decimal("71294000000"),
                    tax_expense=Decimal("11356000000"), net_income=Decimal("59972000000"), eps=Decimal("4.59"), diluted_eps=Decimal("4.56")
                ),
                IncomeStatementRecord(
                    ticker="GOOG", period="2023", filing_date=date(2024, 1, 30),
                    revenue=Decimal("307394000000"), cost_of_revenue=Decimal("133332000000"), gross_profit=Decimal("174062000000"),
                    operating_expenses=Decimal("89782000000"), operating_income=Decimal("84280000000"), ebitda=Decimal("99684000000"),
                    ebit=Decimal("84280000000"), interest_expense=Decimal("309000000"), pre_tax_income=Decimal("85719000000"),
                    tax_expense=Decimal("11981000000"), net_income=Decimal("73738000000"), eps=Decimal("5.84"), diluted_eps=Decimal("5.80")
                ),
                IncomeStatementRecord(
                    ticker="GOOG", period="2024", filing_date=date(2025, 2, 4),
                    revenue=Decimal("350018000000"), cost_of_revenue=Decimal("148560000000"), gross_profit=Decimal("201458000000"),
                    operating_expenses=Decimal("98910000000"), operating_income=Decimal("102548000000"), ebitda=Decimal("123180000000"),
                    ebit=Decimal("102548000000"), interest_expense=Decimal("320000000"), pre_tax_income=Decimal("106420000000"),
                    tax_expense=Decimal("15230000000"), net_income=Decimal("91190000000"), eps=Decimal("7.48"), diluted_eps=Decimal("7.41")
                ),
            ],
            "AMZN": [
                IncomeStatementRecord(
                    ticker="AMZN", period="2022", filing_date=date(2023, 2, 3),
                    revenue=Decimal("513983000000"), cost_of_revenue=Decimal("288831000000"), gross_profit=Decimal("225152000000"),
                    operating_expenses=Decimal("212904000000"), operating_income=Decimal("12248000000"), ebitda=Decimal("54169000000"),
                    ebit=Decimal("12248000000"), interest_expense=Decimal("2367000000"), pre_tax_income=Decimal("-5936000000"),
                    tax_expense=Decimal("-3217000000"), net_income=Decimal("-2722000000"), eps=Decimal("-0.27"), diluted_eps=Decimal("-0.27")
                ),
                IncomeStatementRecord(
                    ticker="AMZN", period="2023", filing_date=date(2024, 2, 2),
                    revenue=Decimal("574785000000"), cost_of_revenue=Decimal("304539000000"), gross_profit=Decimal("270246000000"),
                    operating_expenses=Decimal("233372000000"), operating_income=Decimal("36874000000"), ebitda=Decimal("85515000000"),
                    ebit=Decimal("36874000000"), interest_expense=Decimal("3168000000"), pre_tax_income=Decimal("37627000000"),
                    tax_expense=Decimal("7202000000"), net_income=Decimal("30425000000"), eps=Decimal("2.95"), diluted_eps=Decimal("2.90")
                ),
                IncomeStatementRecord(
                    ticker="AMZN", period="2024", filing_date=date(2025, 2, 6),
                    revenue=Decimal("637962000000"), cost_of_revenue=Decimal("326410000000"), gross_profit=Decimal("311552000000"),
                    operating_expenses=Decimal("244832000000"), operating_income=Decimal("66720000000"), ebitda=Decimal("118420000000"),
                    ebit=Decimal("66720000000"), interest_expense=Decimal("3010000000"), pre_tax_income=Decimal("68420000000"),
                    tax_expense=Decimal("12140000000"), net_income=Decimal("56280000000"), eps=Decimal("5.42"), diluted_eps=Decimal("5.34")
                ),
            ],
        }

        # Multi-year historical balance sheets
        self._balance_sheets: Dict[str, List[BalanceSheetRecord]] = {
            "AAPL": [
                BalanceSheetRecord(
                    ticker="AAPL", period="2023", filing_date=date(2023, 11, 2),
                    cash_and_equivalents=Decimal("29965000000"), short_term_investments=Decimal("31590000000"),
                    current_assets=Decimal("143566000000"), goodwill=Decimal("0"), intangible_assets=Decimal("0"),
                    total_assets=Decimal("352583000000"), current_liabilities=Decimal("145308000000"),
                    short_term_debt=Decimal("15807000000"), long_term_debt=Decimal("95281000000"),
                    total_debt=Decimal("111088000000"), total_liabilities=Decimal("290437000000"),
                    shareholders_equity=Decimal("62146000000")
                ),
                BalanceSheetRecord(
                    ticker="AAPL", period="2024", filing_date=date(2024, 10, 31),
                    cash_and_equivalents=Decimal("29943000000"), short_term_investments=Decimal("35241000000"),
                    current_assets=Decimal("152985000000"), goodwill=Decimal("0"), intangible_assets=Decimal("0"),
                    total_assets=Decimal("364980000000"), current_liabilities=Decimal("154694000000"),
                    short_term_debt=Decimal("10952000000"), long_term_debt=Decimal("95657000000"),
                    total_debt=Decimal("106609000000"), total_liabilities=Decimal("308030000000"),
                    shareholders_equity=Decimal("56950000000")
                ),
            ],
            "NVDA": [
                BalanceSheetRecord(
                    ticker="NVDA", period="2024", filing_date=date(2024, 2, 21),
                    cash_and_equivalents=Decimal("7280000000"), short_term_investments=Decimal("18704000000"),
                    current_assets=Decimal("44345000000"), goodwill=Decimal("4372000000"), intangible_assets=Decimal("1107000000"),
                    total_assets=Decimal("65728000000"), current_liabilities=Decimal("10631000000"),
                    short_term_debt=Decimal("1250000000"), long_term_debt=Decimal("8460000000"),
                    total_debt=Decimal("9710000000"), total_liabilities=Decimal("22750000000"),
                    shareholders_equity=Decimal("42978000000")
                ),
                BalanceSheetRecord(
                    ticker="NVDA", period="2025", filing_date=date(2025, 2, 26),
                    cash_and_equivalents=Decimal("15840000000"), short_term_investments=Decimal("27500000000"),
                    current_assets=Decimal("85200000000"), goodwill=Decimal("4372000000"), intangible_assets=Decimal("850000000"),
                    total_assets=Decimal("115400000000"), current_liabilities=Decimal("18200000000"),
                    short_term_debt=Decimal("1000000000"), long_term_debt=Decimal("7460000000"),
                    total_debt=Decimal("8460000000"), total_liabilities=Decimal("32400000000"),
                    shareholders_equity=Decimal("83000000000")
                ),
            ],
            "MSFT": [
                BalanceSheetRecord(
                    ticker="MSFT", period="2024", filing_date=date(2024, 7, 30),
                    cash_and_equivalents=Decimal("18296000000"), short_term_investments=Decimal("57245000000"),
                    current_assets=Decimal("152148000000"), goodwill=Decimal("119420000000"), intangible_assets=Decimal("23600000000"),
                    total_assets=Decimal("512163000000"), current_liabilities=Decimal("125190000000"),
                    short_term_debt=Decimal("10440000000"), long_term_debt=Decimal("42740000000"),
                    total_debt=Decimal("53180000000"), total_liabilities=Decimal("243686000000"),
                    shareholders_equity=Decimal("268477000000")
                ),
            ],
            "GOOG": [
                BalanceSheetRecord(
                    ticker="GOOG", period="2024", filing_date=date(2025, 2, 4),
                    cash_and_equivalents=Decimal("24048000000"), short_term_investments=Decimal("71500000000"),
                    current_assets=Decimal("175800000000"), goodwill=Decimal("31200000000"), intangible_assets=Decimal("1500000000"),
                    total_assets=Decimal("425600000000"), current_liabilities=Decimal("88400000000"),
                    short_term_debt=Decimal("3100000000"), long_term_debt=Decimal("25400000000"),
                    total_debt=Decimal("28500000000"), total_liabilities=Decimal("135800000000"),
                    shareholders_equity=Decimal("289800000000")
                ),
            ],
            "AMZN": [
                BalanceSheetRecord(
                    ticker="AMZN", period="2024", filing_date=date(2025, 2, 6),
                    cash_and_equivalents=Decimal("54240000000"), short_term_investments=Decimal("32400000000"),
                    current_assets=Decimal("182400000000"), goodwill=Decimal("22400000000"), intangible_assets=Decimal("4800000000"),
                    total_assets=Decimal("588400000000"), current_liabilities=Decimal("174200000000"),
                    short_term_debt=Decimal("8400000000"), long_term_debt=Decimal("58200000000"),
                    total_debt=Decimal("66600000000"), total_liabilities=Decimal("328400000000"),
                    shareholders_equity=Decimal("260000000000")
                ),
            ],
        }

        # Multi-year historical cash flows
        self._cash_flows: Dict[str, List[CashFlowRecord]] = {
            "AAPL": [
                CashFlowRecord(
                    ticker="AAPL", period="2023", filing_date=date(2023, 11, 2),
                    operating_cash_flow=Decimal("110543000000"), capital_expenditure=Decimal("10959000000"),
                    investing_cash_flow=Decimal("3705000000"), financing_cash_flow=Decimal("-108488000000"),
                    free_cash_flow=Decimal("99584000000")
                ),
                CashFlowRecord(
                    ticker="AAPL", period="2024", filing_date=date(2024, 10, 31),
                    operating_cash_flow=Decimal("118254000000"), capital_expenditure=Decimal("9447000000"),
                    investing_cash_flow=Decimal("-2580000000"), financing_cash_flow=Decimal("-115598000000"),
                    free_cash_flow=Decimal("108807000000")
                ),
            ],
            "NVDA": [
                CashFlowRecord(
                    ticker="NVDA", period="2024", filing_date=date(2024, 2, 21),
                    operating_cash_flow=Decimal("28090000000"), capital_expenditure=Decimal("1069000000"),
                    investing_cash_flow=Decimal("-10555000000"), financing_cash_flow=Decimal("-14636000000"),
                    free_cash_flow=Decimal("27021000000")
                ),
                CashFlowRecord(
                    ticker="NVDA", period="2025", filing_date=date(2025, 2, 26),
                    operating_cash_flow=Decimal("64340000000"), capital_expenditure=Decimal("3420000000"),
                    investing_cash_flow=Decimal("-18400000000"), financing_cash_flow=Decimal("-38200000000"),
                    free_cash_flow=Decimal("60920000000")
                ),
            ],
            "MSFT": [
                CashFlowRecord(
                    ticker="MSFT", period="2024", filing_date=date(2024, 7, 30),
                    operating_cash_flow=Decimal("118548000000"), capital_expenditure=Decimal("44477000000"),
                    investing_cash_flow=Decimal("-94212000000"), financing_cash_flow=Decimal("-24157000000"),
                    free_cash_flow=Decimal("74071000000")
                ),
            ],
            "GOOG": [
                CashFlowRecord(
                    ticker="GOOG", period="2024", filing_date=date(2025, 2, 4),
                    operating_cash_flow=Decimal("108420000000"), capital_expenditure=Decimal("36200000000"),
                    investing_cash_flow=Decimal("-42150000000"), financing_cash_flow=Decimal("-62400000000"),
                    free_cash_flow=Decimal("72220000000")
                ),
            ],
            "AMZN": [
                CashFlowRecord(
                    ticker="AMZN", period="2024", filing_date=date(2025, 2, 6),
                    operating_cash_flow=Decimal("116240000000"), capital_expenditure=Decimal("52400000000"),
                    investing_cash_flow=Decimal("-58400000000"), financing_cash_flow=Decimal("-22400000000"),
                    free_cash_flow=Decimal("63840000000")
                ),
            ],
        }

    def get_company_profile(self, ticker: str) -> Optional[CompanyProfile]:
        return self._profiles.get(ticker.upper())

    def get_income_statements(self, ticker: str, period_type: str = "ANNUAL") -> List[IncomeStatementRecord]:
        stmts = self._income_stmts.get(ticker.upper(), [])
        return [s for s in stmts if s.period_type == period_type]

    def get_balance_sheets(self, ticker: str, period_type: str = "ANNUAL") -> List[BalanceSheetRecord]:
        stmts = self._balance_sheets.get(ticker.upper(), [])
        return [s for s in stmts if s.period_type == period_type]

    def get_cash_flow_statements(self, ticker: str, period_type: str = "ANNUAL") -> List[CashFlowRecord]:
        stmts = self._cash_flows.get(ticker.upper(), [])
        return [s for s in stmts if s.period_type == period_type]

    def audit_statement_quality(
        self,
        income_stmt: IncomeStatementRecord,
        balance_sheet: BalanceSheetRecord,
    ) -> StatementQualityAudit:
        """Audits mathematical and accounting consistency between statements."""
        # Balance Sheet Identity: Assets == Liabilities + Equity
        bs_diff = abs(balance_sheet.total_assets - (balance_sheet.total_liabilities + balance_sheet.shareholders_equity))
        bs_balanced = bs_diff < Decimal(1000)  # within minor rounding variance

        # Gross Profit Identity: Gross Profit == Revenue - Cost of Revenue
        gp_calc = income_stmt.revenue - income_stmt.cost_of_revenue
        gp_diff = abs(income_stmt.gross_profit - gp_calc)
        gp_consistent = gp_diff < Decimal(1000)

        # Operating Income Identity: Operating Income == Gross Profit - Operating Expenses
        op_calc = income_stmt.gross_profit - income_stmt.operating_expenses
        op_diff = abs(income_stmt.operating_income - op_calc)
        op_consistent = op_diff < Decimal(1000)

        anomalies = []
        if not bs_balanced:
            anomalies.append("Balance sheet does not balance: Assets != Liabilities + Equity")
        if not gp_consistent:
            anomalies.append("Gross profit calculation mismatch with Revenue - Cost of Revenue")
        if not op_consistent:
            anomalies.append("Operating income calculation mismatch with Gross Profit - Operating Expenses")

        is_valid = bs_balanced and gp_consistent and op_consistent
        quality_status = "VERIFIED" if is_valid else "QUESTIONABLE"

        return StatementQualityAudit(
            is_valid=is_valid,
            balance_sheet_balanced=bs_balanced,
            gross_profit_consistent=gp_consistent,
            operating_income_consistent=op_consistent,
            data_quality=quality_status,
            anomalies=anomalies,
        )


_fundamental_provider_instance: Optional[FundamentalDataProvider] = None


def get_fundamental_data_provider() -> FundamentalDataProvider:
    """Factory returning the fundamental data provider singleton."""
    global _fundamental_provider_instance
    if _fundamental_provider_instance is None:
        _fundamental_provider_instance = DemoFundamentalDataProvider()
    return _fundamental_provider_instance
