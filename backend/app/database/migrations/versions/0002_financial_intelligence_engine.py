"""financial_intelligence_engine

Revision ID: 0002_financial_intelligence_engine
Revises: 0001_initial_foundation
Create Date: 2026-09-19 15:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0002_financial_intelligence_engine'
down_revision: Union[str, None] = '0001_initial_foundation'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Companies Table
    op.create_table(
        'companies',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('ticker', sa.String(length=16), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('exchange', sa.String(length=32), nullable=False),
        sa.Column('sector', sa.String(length=64), nullable=False),
        sa.Column('industry', sa.String(length=128), nullable=False),
        sa.Column('country', sa.String(length=64), nullable=False),
        sa.Column('currency', sa.String(length=8), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('market_cap', sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column('shares_outstanding', sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column('status', sa.String(length=16), nullable=False),
        sa.Column('is_synthetic', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_companies_id', 'companies', ['id'], unique=False)
    op.create_index('ix_companies_ticker', 'companies', ['ticker'], unique=True)
    op.create_index('ix_companies_name', 'companies', ['name'], unique=False)
    op.create_index('ix_companies_sector', 'companies', ['sector'], unique=False)
    op.create_index('ix_companies_industry', 'companies', ['industry'], unique=False)

    # 2. Market Price Bars Table
    op.create_table(
        'market_price_bars',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('ticker', sa.String(length=16), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('open', sa.Float(), nullable=False),
        sa.Column('high', sa.Float(), nullable=False),
        sa.Column('low', sa.Float(), nullable=False),
        sa.Column('close', sa.Float(), nullable=False),
        sa.Column('adj_close', sa.Float(), nullable=False),
        sa.Column('volume', sa.Float(), nullable=False),
        sa.Column('vwap', sa.Float(), nullable=True),
        sa.Column('interval', sa.String(length=16), nullable=False),
        sa.Column('is_adjusted', sa.Boolean(), nullable=False),
        sa.Column('data_source', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['ticker'], ['companies.ticker'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_market_price_bars_id', 'market_price_bars', ['id'], unique=False)
    op.create_index('ix_market_price_bars_ticker', 'market_price_bars', ['ticker'], unique=False)
    op.create_index('ix_market_price_bars_timestamp', 'market_price_bars', ['timestamp'], unique=False)
    op.create_index('idx_price_bars_ticker_timestamp', 'market_price_bars', ['ticker', 'timestamp', 'interval'], unique=True)

    # 3. Income Statements Table
    op.create_table(
        'income_statements',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('ticker', sa.String(length=16), nullable=False),
        sa.Column('period', sa.String(length=16), nullable=False),
        sa.Column('period_type', sa.String(length=16), nullable=False),
        sa.Column('filing_date', sa.Date(), nullable=False),
        sa.Column('currency', sa.String(length=8), nullable=False),
        sa.Column('revenue', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('cost_of_revenue', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('gross_profit', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('operating_expenses', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('operating_income', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('ebitda', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('ebit', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('interest_expense', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('pre_tax_income', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('tax_expense', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('net_income', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('eps', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('diluted_eps', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('source', sa.String(length=32), nullable=False),
        sa.Column('data_version', sa.String(length=16), nullable=False),
        sa.Column('quality_status', sa.String(length=16), nullable=False),
        sa.Column('is_synthetic', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['ticker'], ['companies.ticker'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_income_statements_id', 'income_statements', ['id'], unique=False)
    op.create_index('ix_income_statements_ticker', 'income_statements', ['ticker'], unique=False)
    op.create_index('idx_income_stmt_ticker_period', 'income_statements', ['ticker', 'period', 'period_type'], unique=True)

    # 4. Balance Sheets Table
    op.create_table(
        'balance_sheets',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('ticker', sa.String(length=16), nullable=False),
        sa.Column('period', sa.String(length=16), nullable=False),
        sa.Column('period_type', sa.String(length=16), nullable=False),
        sa.Column('filing_date', sa.Date(), nullable=False),
        sa.Column('currency', sa.String(length=8), nullable=False),
        sa.Column('cash_and_equivalents', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('short_term_investments', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('current_assets', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('goodwill', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('intangible_assets', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('total_assets', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('current_liabilities', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('short_term_debt', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('long_term_debt', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('total_debt', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('total_liabilities', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('shareholders_equity', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('source', sa.String(length=32), nullable=False),
        sa.Column('data_version', sa.String(length=16), nullable=False),
        sa.Column('quality_status', sa.String(length=16), nullable=False),
        sa.Column('is_synthetic', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['ticker'], ['companies.ticker'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_balance_sheets_id', 'balance_sheets', ['id'], unique=False)
    op.create_index('ix_balance_sheets_ticker', 'balance_sheets', ['ticker'], unique=False)
    op.create_index('idx_balance_sheet_ticker_period', 'balance_sheets', ['ticker', 'period', 'period_type'], unique=True)

    # 5. Cash Flow Statements Table
    op.create_table(
        'cash_flow_statements',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('ticker', sa.String(length=16), nullable=False),
        sa.Column('period', sa.String(length=16), nullable=False),
        sa.Column('period_type', sa.String(length=16), nullable=False),
        sa.Column('filing_date', sa.Date(), nullable=False),
        sa.Column('currency', sa.String(length=8), nullable=False),
        sa.Column('operating_cash_flow', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('capital_expenditure', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('investing_cash_flow', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('financing_cash_flow', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('free_cash_flow', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('source', sa.String(length=32), nullable=False),
        sa.Column('data_version', sa.String(length=16), nullable=False),
        sa.Column('quality_status', sa.String(length=16), nullable=False),
        sa.Column('is_synthetic', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['ticker'], ['companies.ticker'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_cash_flow_statements_id', 'cash_flow_statements', ['id'], unique=False)
    op.create_index('ix_cash_flow_statements_ticker', 'cash_flow_statements', ['ticker'], unique=False)
    op.create_index('idx_cash_flow_ticker_period', 'cash_flow_statements', ['ticker', 'period', 'period_type'], unique=True)


def downgrade() -> None:
    op.drop_index('idx_cash_flow_ticker_period', table_name='cash_flow_statements')
    op.drop_index('ix_cash_flow_statements_ticker', table_name='cash_flow_statements')
    op.drop_index('ix_cash_flow_statements_id', table_name='cash_flow_statements')
    op.drop_table('cash_flow_statements')

    op.drop_index('idx_balance_sheet_ticker_period', table_name='balance_sheets')
    op.drop_index('ix_balance_sheets_ticker', table_name='balance_sheets')
    op.drop_index('ix_balance_sheets_id', table_name='balance_sheets')
    op.drop_table('balance_sheets')

    op.drop_index('idx_income_stmt_ticker_period', table_name='income_statements')
    op.drop_index('ix_income_statements_ticker', table_name='income_statements')
    op.drop_index('ix_income_statements_id', table_name='income_statements')
    op.drop_table('income_statements')

    op.drop_index('idx_price_bars_ticker_timestamp', table_name='market_price_bars')
    op.drop_index('ix_market_price_bars_timestamp', table_name='market_price_bars')
    op.drop_index('ix_market_price_bars_ticker', table_name='market_price_bars')
    op.drop_index('ix_market_price_bars_id', table_name='market_price_bars')
    op.drop_table('market_price_bars')

    op.drop_index('ix_companies_industry', table_name='companies')
    op.drop_index('ix_companies_sector', table_name='companies')
    op.drop_index('ix_companies_name', table_name='companies')
    op.drop_index('ix_companies_ticker', table_name='companies')
    op.drop_index('ix_companies_id', table_name='companies')
    op.drop_table('companies')
