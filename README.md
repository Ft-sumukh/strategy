# Aegis Invest

Runnable MVP for the Aegis Invest decision-intelligence platform. This slice is intentionally
safe for demos: all market values are deterministic synthetic data and every response is labelled
as such. It does not provide investment advice, execute trades, or make return guarantees.

## Run locally

### API

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API is available at `http://localhost:8000` and its OpenAPI document at
`http://localhost:8000/docs`.

### Web

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`. Set `NEXT_PUBLIC_API_URL` to point at another API host if needed.

### Docker Compose

```powershell
docker compose up --build
```

## MVP surface

- Market overview with regime, index cards, breadth, and recent intelligence
- Stock screener with valuation, quality, momentum, and risk filters
- Company intelligence view with fundamentals, scenarios, evidence, and uncertainty
- Portfolio risk view with allocation, concentration, volatility, drawdown, and stress scenarios
- Provider-agnostic API contracts under `backend/app/providers` and typed frontend API helpers

Synthetic records use `data_status: "synthetic"` and `as_of` timestamps. They must not be
presented as live market data.
