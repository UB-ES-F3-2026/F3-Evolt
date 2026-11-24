# Pages — page separation map

Pages are grouped by **domain inside each layer**: `views/<domain>/`,
`viewmodels/<domain>/` and `services/<domain>/` hold the files of each page
domain (this domain-subfolder layout is the team-agreed convention, recorded
via the frontend page-separation refactor). The router mirrors the same
domains: `frontend/src/router/routes/<domain>.ts`, one file per domain, with
each view lazy-loaded at the route level.

Full page map (all 26 routes):

## Home

| Route path | Route name | View file | ViewModel file |
|------------|-----------|-----------|----------------|
| `/` | `home` | `views/home/HomeView.vue` | `viewmodels/home/useHomeViewModel.ts` |

## Movements

| Route path | Route name | View file | ViewModel file |
|------------|-----------|-----------|----------------|
| `/movements` | `movements` | `views/movements/MovementsView.vue` | `viewmodels/movements/useMovementsViewModel.ts` |
| `/movements/:movementId` | `movement` | `views/movements/MovementDetailView.vue` | `viewmodels/movements/useMovementDetailViewModel.ts` |
| `/movements/:movementId/report` | `report-movement` | `views/movements/ReportProblemView.vue` | `viewmodels/movements/useReportProblemViewModel.ts` |

## Top-up

| Route path | Route name | View file | ViewModel file |
|------------|-----------|-----------|----------------|
| `/topup` | `topup` | `views/topup/TopUpView.vue` | `viewmodels/topup/useTopUpViewModel.ts` |

## Exchange

| Route path | Route name | View file | ViewModel file |
|------------|-----------|-----------|----------------|
| `/canviar` | `exchange` | `views/exchange/ExchangeView.vue` | `viewmodels/exchange/useExchangeViewModel.ts` |
| `/canviar/resum` | `exchange-summary` | `views/exchange/ExchangeSummaryView.vue` | `viewmodels/exchange/useExchangeSummaryViewModel.ts` |

## Pots

| Route path | Route name | View file | ViewModel file |
|------------|-----------|-----------|----------------|
| `/pots` | `pots` | `views/pots/PotsView.vue` | `viewmodels/pots/usePotsViewModel.ts` |
| `/pots/new` | `create-pot` | `views/pots/CreatePotView.vue` | `viewmodels/pots/useCreatePotViewModel.ts` |
| `/pots/:potId` | `pot` | `views/pots/PotView.vue` | `viewmodels/pots/usePotViewModel.ts` |
| `/pots/:potId/contribute` | `contribute` | `views/pots/ContributeView.vue` | `viewmodels/pots/useContributeViewModel.ts` |
| `/pots/:potId/withdraw` | `withdraw` | `views/pots/WithdrawView.vue` | `viewmodels/pots/useWithdrawViewModel.ts` |
| `/pots/:potId/withdraw/cancelled` | `withdraw-cancelled` | `views/pots/WithdrawCancelledView.vue` | `viewmodels/pots/useWithdrawCancelledViewModel.ts` |

## Payments

| Route path | Route name | View file | ViewModel file |
|------------|-----------|-----------|----------------|
| `/pagaments` | `payments` | `views/payments/PaymentsView.vue` | `viewmodels/payments/usePaymentsViewModel.ts` |
| `/pagaments/enviar` | `send-payment` | `views/payments/SendPaymentView.vue` | `viewmodels/payments/useSendPaymentViewModel.ts` |
| `/pagaments/confirmar` | `confirm-payment` | `views/payments/ConfirmPaymentView.vue` | `viewmodels/payments/useConfirmPaymentViewModel.ts` |

## Requests

| Route path | Route name | View file | ViewModel file |
|------------|-----------|-----------|----------------|
| `/requests` | `money-requests` | `views/requests/MoneyRequestsView.vue` | `viewmodels/requests/useMoneyRequestsViewModel.ts` |
| `/requests/new` | `new-money-request` | `views/requests/NewMoneyRequestView.vue` | `viewmodels/requests/useNewMoneyRequestViewModel.ts` |

## Currencies

| Route path | Route name | View file | ViewModel file |
|------------|-----------|-----------|----------------|
| `/divises` | `currencies` | `views/currencies/CurrenciesView.vue` | `viewmodels/currencies/useCurrenciesViewModel.ts` |
| `/divises/afegir` | `add-currency` | `views/currencies/AddCurrencyView.vue` | `viewmodels/currencies/useAddCurrencyViewModel.ts` |
| `/divises/:subaccountId` | `subaccount` | `views/currencies/SubaccountView.vue` | `viewmodels/currencies/useSubaccountViewModel.ts` |

## Auth

| Route path | Route name | View file | ViewModel file |
|------------|-----------|-----------|----------------|
| `/login` | `login` | `views/auth/LoginView.vue` | `viewmodels/auth/useLoginViewModel.ts` |
| `/register` | `register` | `views/auth/RegisterView.vue` | `viewmodels/auth/useRegisterViewModel.ts` |
| `/verify` | `verify` | `views/auth/VerifyView.vue` | `viewmodels/auth/useVerifyViewModel.ts` |
| `/forgot-password` | `forgot-password` | `views/auth/ForgotPasswordView.vue` | `viewmodels/auth/useForgotPasswordViewModel.ts` |
| `/nova-contrasenya` | `new-password` | `views/auth/NewPasswordView.vue` | `viewmodels/auth/useNewPasswordViewModel.ts` |

## Service files by domain

A service lives in `services/<domain>/` when it is used by exactly **one**
domain's ViewModels. When a service is used by 2+ domains (or by shared
infrastructure like the router or `apiClient`), it stays at the `services/`
root.

| Service | Location | Reason |
|---------|----------|--------|
| `authService` | `services/auth/` | auth's service; also consumed by the shared root `useSessionMenuViewModel` (logout) |
| `exchangeService` | `services/exchange/` | exchange only |
| `topupService` | `services/topup/` | top-up only |
| `potsService` | `services/pots/` | pots only |
| `transfersService` | `services/payments/` | payments only |
| `moneyRequestsService` | `services/requests/` | requests only |
| `fileDownload`, `receiptPdf` | `services/movements/` | only consumer is the movement-detail ViewModel |
| `apiClient` | `services/` root (shared) | used by every service |
| `session` | `services/` root (shared) | used by the router guard and auth ViewModels |
| `homeService` | `services/` root (shared) | used by home, payments and pots |
| `usersService` | `services/` root (shared) | used by payments and requests |
| `subaccountsService` | `services/` root (shared) | used by currencies and exchange |
| `movementsService` | `services/` root (shared) | used by movements and currencies (SubaccountView) |

## Shared at layer root

Some files stay directly in the layer folder because they serve several
domains:

- **Services at `services/` root:** `apiClient.ts`, `session.ts`,
  `homeService.ts`, `usersService.ts`, `subaccountsService.ts`,
  `movementsService.ts`.
- **Composables at `viewmodels/` root:** `useBalanceVisibility`,
  `useGoBack`, `usePasswordFields`, `useSessionMenuViewModel` (used across
  domains or by shared `components/`).
- **`models/`, `components/` and `mocks/`** are layer-wide shared — not
  grouped by domain.

## Conventions

1. **Page separation = router + domain subfolders inside the layers.** Each
   layer groups its files by domain: `views/<domain>/`,
   `viewmodels/<domain>/` (9 domains: `home`, `movements`, `topup`,
   `exchange`, `pots`, `payments`, `requests`, `currencies`, `auth`) and
   `services/<domain>/` (only the domains that own a single-domain service;
   `home` and `currencies` have none). Co-located tests move with their
   source files.
   This layout is the **team-agreed convention** (recorded via the
   page-separation refactor); `features/<x>/`, new top-level folders and
   `shared/` remain forbidden. A domain folder may gain subfolders when the
   domain grows.
2. **One route module per domain:** `frontend/src/router/routes/<domain>.ts`
   (`home.ts`, `movements.ts`, `topup.ts`, `exchange.ts`, `pots.ts`,
   `payments.ts`, `requests.ts`, `currencies.ts`, `auth.ts`). A route module
   exports an array of `RouteRecordRaw` for its domain.
3. **Service placement rule:** a service used by exactly one domain lives in
   `services/<domain>/`; a service used by 2+ domains or by shared infra
   stays at the `services/` root (see the table above).
4. **Views are lazy-loaded at the route level:**
   `component: () => import('@/views/<domain>/XxxView.vue')`. Never import a
   view eagerly in a route module.
5. **Route paths and names are a contract.** Backend links
   (`/nova-contrasenya` in the recovery email) and frontend navigation
   (`router.push({ name })`) depend on them — never rename. Add or rename a
   route by editing the right `routes/<domain>.ts` file.
6. **`router/index.ts` never re-centers routes.** It only aggregates the
   `routes/*` modules (`...homeRoutes`, `...movementsRoutes`, …) and wires the
   guards and session hooks
   (`accessGuard`, `touchSession`, `onSessionEnded`).
7. **Dependency rules are unchanged:** a View never imports a service
   directly (View → ViewModel → Service → `apiClient`); ViewModels import
   services; `models/` stays pure data + pure functions.

## How to add a new page

1. Create the view: `frontend/src/views/<domain>/XxxView.vue` (create the
   domain folder if it is new; View only — no service calls, it uses its
   ViewModel).
2. Create the ViewModel: `frontend/src/viewmodels/<domain>/useXxxViewModel.ts`
   (state, validations, actions — no HTML).
3. Add its service to `frontend/src/services/<domain>/xxxService.ts` if it is
   single-domain; if 2+ domains will use it, keep it at the `services/` root.
4. Add the route to the right `frontend/src/router/routes/<domain>.ts` file,
   lazy-loaded:
   `component: () => import('@/views/<domain>/XxxView.vue')`. If the page
   needs a public route, add `meta: { public: true }` like the auth routes.
5. **Never touch `router/index.ts`** unless you are adding a new domain file —
   then also import the new module in the aggregator.
6. Run `npm run check` from `frontend/` (lint, type-check, tests, build).

More detail on layers and folders: `AGENTS.md` §2 and skill `arch-structure`.
