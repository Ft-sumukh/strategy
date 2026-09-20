"""market_strategy_intelligence

Revision ID: 0003_market_strategy_intelligence
Revises: 0002_financial_intelligence_engine
Create Date: 2026-09-19 16:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0003_market_strategy_intelligence'
down_revision: Union[str, None] = '0002_financial_intelligence_engine'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. News Articles Table
    op.create_table(
        'news_articles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('headline', sa.String(length=500), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('publisher', sa.String(length=100), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('url', sa.String(length=1000), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('retrieved_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('company_id', sa.String(length=36), nullable=True),
        sa.Column('ticker', sa.String(length=20), nullable=True),
        sa.Column('sector', sa.String(length=100), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('data_source', sa.String(length=50), nullable=False),
        sa.Column('data_version', sa.String(length=20), nullable=False),
        sa.Column('quality_status', sa.String(length=30), nullable=False),
        sa.Column('is_synthetic', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('content_hash')
    )
    op.create_index('ix_news_articles_id', 'news_articles', ['id'], unique=False)
    op.create_index('ix_news_articles_publisher', 'news_articles', ['publisher'], unique=False)
    op.create_index('ix_news_articles_published_at', 'news_articles', ['published_at'], unique=False)
    op.create_index('ix_news_articles_ticker', 'news_articles', ['ticker'], unique=False)
    op.create_index('ix_news_articles_sector', 'news_articles', ['sector'], unique=False)
    op.create_index('ix_news_articles_category', 'news_articles', ['category'], unique=False)
    op.create_index('ix_news_articles_content_hash', 'news_articles', ['content_hash'], unique=True)
    op.create_index('ix_news_ticker_published', 'news_articles', ['ticker', 'published_at'], unique=False)
    op.create_index('ix_news_category_published', 'news_articles', ['category', 'published_at'], unique=False)

    # 2. News Entities Table
    op.create_table(
        'news_entities',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('article_id', sa.String(length=36), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_name', sa.String(length=200), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['article_id'], ['news_articles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_news_entities_id', 'news_entities', ['id'], unique=False)
    op.create_index('ix_news_entities_article_id', 'news_entities', ['article_id'], unique=False)

    # 3. News Events Table
    op.create_table(
        'news_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('article_id', sa.String(length=36), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('event_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['article_id'], ['news_articles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_news_events_id', 'news_events', ['id'], unique=False)
    op.create_index('ix_news_events_article_id', 'news_events', ['article_id'], unique=False)
    op.create_index('ix_news_events_event_type', 'news_events', ['event_type'], unique=False)

    # 4. Sentiment Records Table
    op.create_table(
        'sentiment_records',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('article_id', sa.String(length=36), nullable=False),
        sa.Column('ticker', sa.String(length=20), nullable=True),
        sa.Column('sentiment', sa.String(length=20), nullable=False),
        sa.Column('sentiment_score', sa.Float(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['article_id'], ['news_articles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('article_id')
    )
    op.create_index('ix_sentiment_records_id', 'sentiment_records', ['id'], unique=False)
    op.create_index('ix_sentiment_records_article_id', 'sentiment_records', ['article_id'], unique=True)
    op.create_index('ix_sentiment_records_ticker', 'sentiment_records', ['ticker'], unique=False)

    # 5. Aggregate Sentiments Table
    op.create_table(
        'aggregate_sentiments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('entity_type', sa.String(length=20), nullable=False),
        sa.Column('entity_id', sa.String(length=50), nullable=False),
        sa.Column('period', sa.String(length=10), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('dispersion', sa.Float(), nullable=False),
        sa.Column('momentum', sa.Float(), nullable=False),
        sa.Column('article_count', sa.Integer(), nullable=False),
        sa.Column('as_of_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_aggregate_sentiments_id', 'aggregate_sentiments', ['id'], unique=False)
    op.create_index('ix_aggregate_sentiments_entity_type', 'aggregate_sentiments', ['entity_type'], unique=False)
    op.create_index('ix_aggregate_sentiments_entity_id', 'aggregate_sentiments', ['entity_id'], unique=False)
    op.create_index('ix_aggregate_sentiments_period', 'aggregate_sentiments', ['period'], unique=False)
    op.create_index('ix_aggregate_sentiments_as_of_date', 'aggregate_sentiments', ['as_of_date'], unique=False)
    op.create_index('ix_agg_sentiment_lookup', 'aggregate_sentiments', ['entity_type', 'entity_id', 'period', 'as_of_date'], unique=False)

    # 6. Macro Series Table
    op.create_table(
        'macro_series',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('series_code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('country', sa.String(length=50), nullable=False),
        sa.Column('frequency', sa.String(length=20), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('series_code')
    )
    op.create_index('ix_macro_series_id', 'macro_series', ['id'], unique=False)
    op.create_index('ix_macro_series_series_code', 'macro_series', ['series_code'], unique=True)

    # 7. Macro Observations Table
    op.create_table(
        'macro_observations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('series_code', sa.String(length=50), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('data_version', sa.String(length=20), nullable=False),
        sa.Column('quality_status', sa.String(length=30), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['series_code'], ['macro_series.series_code'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_macro_observations_id', 'macro_observations', ['id'], unique=False)
    op.create_index('ix_macro_observations_series_code', 'macro_observations', ['series_code'], unique=False)
    op.create_index('ix_macro_observations_timestamp', 'macro_observations', ['timestamp'], unique=False)
    op.create_index('ix_macro_obs_code_timestamp', 'macro_observations', ['series_code', 'timestamp'], unique=True)

    # 8. Market Regimes Table
    op.create_table(
        'market_regimes',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('regime', sa.String(length=50), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('previous_regime', sa.String(length=50), nullable=True),
        sa.Column('duration_days', sa.Integer(), nullable=False),
        sa.Column('supporting_signals', sa.JSON(), nullable=False),
        sa.Column('methodology', sa.Text(), nullable=False),
        sa.Column('data_source', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_market_regimes_id', 'market_regimes', ['id'], unique=False)
    op.create_index('ix_market_regimes_timestamp', 'market_regimes', ['timestamp'], unique=False)
    op.create_index('ix_market_regimes_regime', 'market_regimes', ['regime'], unique=False)

    # 9. Strategy Definitions Table
    op.create_table(
        'strategy_definitions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('strategy_key', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('universe', sa.String(length=100), nullable=False),
        sa.Column('rebalance_frequency', sa.String(length=30), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=False),
        sa.Column('risk_constraints', sa.JSON(), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('strategy_key')
    )
    op.create_index('ix_strategy_definitions_id', 'strategy_definitions', ['id'], unique=False)
    op.create_index('ix_strategy_definitions_strategy_key', 'strategy_definitions', ['strategy_key'], unique=True)

    # 10. Strategy Signals Table
    op.create_table(
        'strategy_signals',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('strategy_key', sa.String(length=50), nullable=False),
        sa.Column('ticker', sa.String(length=20), nullable=False),
        sa.Column('signal_score', sa.Float(), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('target_weight', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('strategy_version', sa.String(length=20), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_strategy_signals_id', 'strategy_signals', ['id'], unique=False)
    op.create_index('ix_strategy_signals_strategy_key', 'strategy_signals', ['strategy_key'], unique=False)
    op.create_index('ix_strategy_signals_ticker', 'strategy_signals', ['ticker'], unique=False)
    op.create_index('ix_strategy_signals_timestamp', 'strategy_signals', ['timestamp'], unique=False)
    op.create_index('ix_strat_signal_lookup', 'strategy_signals', ['strategy_key', 'ticker', 'timestamp'], unique=False)

    # 11. Experiment Records Table
    op.create_table(
        'experiment_records',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('hypothesis', sa.Text(), nullable=False),
        sa.Column('strategy_key', sa.String(length=50), nullable=False),
        sa.Column('universe', sa.String(length=100), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=False),
        sa.Column('date_range', sa.String(length=100), nullable=False),
        sa.Column('rebalance_frequency', sa.String(length=30), nullable=False),
        sa.Column('transaction_cost_bps', sa.Float(), nullable=False),
        sa.Column('slippage_bps', sa.Float(), nullable=False),
        sa.Column('dataset_version', sa.String(length=30), nullable=False),
        sa.Column('strategy_version', sa.String(length=30), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('results', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_experiment_records_id', 'experiment_records', ['id'], unique=False)
    op.create_index('ix_experiment_records_strategy_key', 'experiment_records', ['strategy_key'], unique=False)
    op.create_index('ix_experiment_strategy_created', 'experiment_records', ['strategy_key', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_table('experiment_records')
    op.drop_table('strategy_signals')
    op.drop_table('strategy_definitions')
    op.drop_table('market_regimes')
    op.drop_table('macro_observations')
    op.drop_table('macro_series')
    op.drop_table('aggregate_sentiments')
    op.drop_table('sentiment_records')
    op.drop_table('news_events')
    op.drop_table('news_entities')
    op.drop_table('news_articles')
