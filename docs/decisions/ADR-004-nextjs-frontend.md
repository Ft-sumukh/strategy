# ADR-004: Next.js Frontend Foundation

## Status
Accepted

## Context
The AEGIS user experience requires:
* Responsive, high-performance UI rendering for financial data visualization and analytics.
* Strict TypeScript type-checking to prevent frontend runtime exceptions.
* Reusable component system with accessible primitives, loading skeletons, error states, and empty states.
* Centralized API communication layer preventing disparate `fetch` calls.

## Decision
Use **Next.js 14** with the **App Router**, **React 18**, and **Tailwind CSS**.
Enforce:
* Strict TypeScript (`strict: true`, `noImplicitAny: true`).
* A centralized `ApiClient` (`lib/api/client.ts`) that manages base URLs, injects `X-Request-ID`, enforces timeouts, and normalizes errors into `ApiError` instances.
* Reusable design tokens themed for professional financial intelligence.
* Complete absence of fake financial metrics or synthetic confidence scores in Group 1.

## Consequences
### Positive
* Modern component architecture with server and client components.
* Consistent error and loading states across all views.
* Predictable API communication with centralized error handling.

### Negative
* Requires learning Next.js App Router conventions and boundary management between Server and Client Components.

## Alternatives Considered
* **Vite + React SPA:** Rejected due to lack of integrated SSR/SSG capabilities and less streamlined production deployment patterns compared to Next.js.
