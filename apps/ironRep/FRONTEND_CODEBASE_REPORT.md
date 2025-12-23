# FRONTEND_CODEBASE_REPORT.md

## Scopo
Audit completo **file-by-file** della codebase frontend in `apps/frontend/src` con standard “Ferrari-level” (2025):
- ✅ mappatura struttura + entrypoint
- ✅ runtime tracing (cosa viene davvero caricato/usato)
- ✅ inventory hardcoded/duplicate/dead code
- ✅ backlog miglioramenti prioritizzato
- ✅ checklist coverage 100% per ogni file

## Regole operative (non negoziabili)
- ✅ Solo evidenze verificate (file/path).
- ✅ Analisi progressiva: ogni sezione viene aggiornata iterativamente.
- ❌ No hardcoded (URL, magic numbers, stringhe duplicate) se evitabile: centralizzare.
- ❌ No duplicate code: estrazione in componenti/hooks/shared utils.
- ❌ No dead/old code: rimuovere file non importati (verificato con runtime tracing + route tree).

## Snapshot iniziale (struttura top-level `src`)
(Generato da `list_dir` e aggiornato quando esploro le sottocartelle.)

- `assets/`
- `components/`
- `config/`
- `features/`
- `hooks/`
- `index.css`
- `main.tsx`
- `pages/`
- `routeTree.gen.ts` (autogenerato TanStack Router)
- `router.tsx`
- `routes/`
- `shared/`
- `styles/`
- `types/`

## Entrypoint e routing
### Entrypoint
- `apps/frontend/src/main.tsx`

### Router
- `apps/frontend/src/router.tsx`
- `apps/frontend/src/routeTree.gen.ts` (autogenerato)
- `apps/frontend/src/routes/**` (file-based routing TanStack)

## Runtime tracing (metodologia)
Obiettivo: determinare **moduli realmente caricati** e **routes realmente raggiungibili**.
- Catena di import da `main.tsx` → `router.tsx` → `routeTree.gen.ts` → `routes/*`.
- Verifica component tree root (`routes/__root.tsx`) e layout.
- Identificazione lazy routes (`*.lazy.tsx`) e split points.

---

## Runtime tracing — evidenze iniziali (verificate)

### Catena di bootstrap
- `apps/frontend/src/main.tsx`
  - Render `RouterProvider` e `QueryClientProvider`.
- `apps/frontend/src/router.tsx`
  - Crea `QueryClient` (default `staleTime=5min`, `gcTime=10min`).
  - Crea `router` con `routeTree` da `routeTree.gen.ts`.
- `apps/frontend/src/routeTree.gen.ts` (autogenerato)
  - Root: `routes/__root.tsx`
  - Lazy routes registrate (dalle prime righe lette):
    - `/` → `routes/index.lazy.tsx`
    - `/login` → `routes/login.lazy.tsx`
    - `/register` → `routes/register.lazy.tsx`
    - `/wizard` → `routes/wizard.lazy.tsx`
    - `/workout` → `routes/workout.lazy.tsx`
    - `/medical` → `routes/medical.lazy.tsx`
    - `/coach` → `routes/coach.lazy.tsx`
    - `/nutrition` → `routes/nutrition.lazy.tsx`
    - `/nutrition-coach` → `routes/nutrition-coach.lazy.tsx`
    - `/pain-tracker` → `routes/pain-tracker.lazy.tsx`
    - `/progress` → `routes/progress.lazy.tsx`
    - `/profile` → `routes/profile.lazy.tsx`
    - `/biometrics` → `routes/biometrics.lazy.tsx`
    - `/exercises` → `routes/exercises.lazy.tsx`
    - `/icon-generator` → `routes/icon-generator.lazy.tsx`

### Root component tree / gating
**Evidenza:** `apps/frontend/src/routes/__root.tsx`
- Wrappa l’app in `AuthProvider`.
- Gating basato su:
  - `isAuthenticated`/`isLoading` da `useAuth()`.
  - `pathname` da `useLocation()`.
  - Check onboarding via `usersApi.getMe()`.
- Layout:
  - Pagine auth (`/login`, `/register`) senza `AppLayout`.
  - `wizard` senza `AppLayout`.
  - Tutto il resto dentro `AppLayout`.

---

## Analisi sistematica file-by-file (inizio)

### `apps/frontend/src/routes/__root.tsx`
**Finding critici:**
- ⚠️ **Hardcoded routes**: controllo `pathname === '/login' || '/login/' || ...` e `'/wizard'`.
  - Impatto: duplicazione stringhe, rischio drift se cambia il routing; soluzione: helper `isRoute(location, '/login')` o usare route ids.
- ⚠️ **Fallback onboarding fragile**: `catch { setIsOnboarded(true) }`.
  - Impatto: se `usersApi.getMe()` fallisce per errore di rete/token scaduto, l’utente viene considerato onboarded e può bypassare wizard.
  - Nota: va deciso comportamento target (fail-closed vs fail-open).

### `apps/frontend/src/routes/index.lazy.tsx`
**Finding critici:**
- ⚠️ **Componente molto grande** (Dashboard page ~385 righe) con UI + micro-logic (greeting/time) + animazioni + gesture.
  - Rischio: manutenzione, re-render cost, testing difficile.
- ⚠️ **Hardcoded stringhe/UI** in molte parti (testi, labels, aria-label) → ok per MVP, ma serve i18n strategy o centralizzazione stringhe.
- ⚠️ `DashboardTour autoStart={true}`: comportamento “sempre on” lato UI; serve gating (es. solo nuovi utenti) e persistenza.

### `apps/frontend/src/lib/api.ts`
**Finding BLOCCANTI (qualità/architettura):**
- ❌ File monolitico (~885 righe): contiene **axios instance**, **interceptor**, **tipi**, e **tutte le API clients**.
  - Impatto: alto rischio di regressioni e merge conflicts; impossibile imporre policy coerenti (timeout, retry, error handling) per modulo.
- ❌ Uso estensivo di `any` (es. `onboardingApi.complete(data: any)`, `plansApi` varie) → perdita type-safety.

**Finding critici:**
- ⚠️ Duplicazione/overlap di concern:
  - Config URL in `config/api.config.ts` + `BASE_URL` calcolato in `lib/api.ts`.
  - Token letto da `sessionStorage.getItem('token')` nell’interceptor, mentre `AuthContext` usa `useAuthStorage()` (da verificare se sempre sessionStorage).
- ⚠️ `API_CONFIG.TIMEOUT` esiste ma **non è usato** in `axios.create(...)`.
- ⚠️ Hardcoded endpoints ripetuti come stringhe (es. `'/plans/...`', `'/medical/...`', `'/auth/login'`) → candidato a `paths` centralizzati.

### `apps/frontend/src/config/api.config.ts`
**Finding critici:**
- ✅ Base URL da `import.meta.env.VITE_API_URL` (corretto).
- ⚠️ `BASE_URL` default `''`: se env mancante in produzione, chiamate diventano relative e dipendono dall’origin → va esplicitato comportamento desiderato.

### `apps/frontend/src/features/auth/AuthContext.tsx`
**Finding critici:**
- ⚠️ `login(newToken)` non fa `setUser(...)`: lo user viene ricostruito solo al prossimo `useEffect` (dipende dal comportamento di `useAuthStorage`).
- ⚠️ In `initAuth`, su errore chiama `logout()` (che chiama `removeToken()`) e poi `setIsLoading(false)`.
  - Impatto: ok fail-closed, ma da allineare col fallback onboarding in `__root.tsx`.

### `apps/frontend/src/components/layout/AppLayout.tsx`
**Finding critici:**
- ✅ Layout responsivo con sidebar + bottomnav + drawer.
- ⚠️ `isMobileDrawerOpen` non viene mai impostato a `true` qui: l’apertura dipende da `Sidebar/BottomNav/MobileDrawer` (da verificare).

### `apps/frontend/src/routes/progress.lazy.tsx`
**Finding critici:**
- ⚠️ File molto grande (hub + calendario mensile + week detail) → rischio “spaghetti UI”.
- ⚠️ Fetch dati gestito manualmente con `useEffect` + state locali invece di TanStack Query.

### `apps/frontend/src/routes/medical.lazy.tsx`
**Finding critici:**
- ⚠️ Magic number: `plansApi.generateMedicalProtocol({ current_pain_level: 5 })`.
- ⚠️ Completion esercizi solo client-side (`completedExercises: Set<number>`) senza persistenza.

### `apps/frontend/src/routes/medical.lazy.tsx`
**Finding critici (NO SCROLL):**
- ✅ Fix applicato: rimosso `overflow-y-auto` dal wrapper `PainCheckInTab`.
- ⚠️ Contenuto attuale può eccedere la viewport → va trasformato in layout “fit” (step/accordion/route dedicate).

### `apps/frontend/src/lib/logger.ts`
**Finding critici:**
- ⚠️ Escape ANSI in console (`\x1b[...]`) non garantiti su browser.
- ⚠️ Sentry placeholder (`sentryEnabled=false`, `(window as any).Sentry`).

### `apps/frontend/src/lib/apiErrorHandler.ts`
**Finding critici:**
- ✅ Utility centralizzata `handleApiError`.
- ⚠️ Type-safety bassa (`any`, `(error as any)`), possibile leak di dettagli nei log.

### `apps/frontend/src/hooks/useAuthStorage.ts`
**Finding critici:**
- ✅ Token in `sessionStorage` (coerente con interceptor in `lib/api.ts`).
- ⚠️ Lettura token solo on-mount → timing coupling con `AuthContext`.

### `apps/frontend/src/components/layout/AppLayout.tsx`
**Finding critici:**
- ⚠️ Stato `isMobileDrawerOpen` non viene mai portato a `true` dentro `AppLayout`: non esiste alcun trigger in questo file che apra il drawer.

### `apps/frontend/src/components/layout/BottomNav.tsx`
**Finding critici:**
- ⚠️ Badge polling con `setInterval(..., 5 * 60 * 1000)` hardcoded.
- ⚠️ `useEffect` ha deps `[]` ma usa `bottomNavItems` (calcolato fuori dall’effect) → rischio drift se `navigationItems` cambiano (basso ma reale).

### `apps/frontend/src/features/chat/ChatInterface.tsx`
**Finding critici (NO SCROLL):**
- ✅ Fix applicato: rimosso container scrollabile e auto-scroll; layout ora `h-full overflow-hidden`.
- ⚠️ Con “NO SCROLL assoluto”, una chat lunga richiede redesign (paginazione/step/route dedicate).

### `apps/frontend/src/features/chat/components/MessageList.tsx`
**Finding critici (NO SCROLL):**
- ✅ Fix applicato: rimosso `overflow-y-auto` e `scrollIntoView`.
- ✅ Guardrail temporaneo: mostra solo ultimi N messaggi (per rispettare fit-viewport).

### `apps/frontend/src/features/chat/QuickActions.tsx`
**Finding critici:**
- ✅ Fix applicato: aggiunto `import type React` (uso di `React.ReactNode`).

### `apps/frontend/src/features/wizard/WizardChat.tsx`
**Finding critici (NO SCROLL):**
- ✅ Fix applicato: rimosso `overflow-y-auto` e auto-scroll; guardrail “ultimi N messaggi”.
- ✅ Fix applicato: aggiunto `import type React` (uso di `React.KeyboardEvent`).

### `apps/frontend/src/features/chat/components/ChatMessages.tsx`
**Finding critici:**
- ✅ Fix applicato: non è più dead code. Ora è un wrapper di `MessageList` (single source of truth) ed è usato da `ChatInterface`.

### `apps/frontend/src/features/wizard/steps/BaselineStrengthStep.tsx`
**Finding critici (NO SCROLL):**
- ✅ Fix applicato: rimosso `overflow-y-auto` dal contenuto; layout `h-full overflow-hidden`.

### `apps/frontend/src/features/wizard/steps/BiometricsStep.tsx`
**Finding critici (NO SCROLL):**
- ✅ Fix applicato: rimosso `overflow-y-auto` dal contenuto; layout `h-full overflow-hidden`.

### `apps/frontend/src/features/wizard/steps/InjuryDetailsStep.tsx`
**Finding critici (NO SCROLL):**
- ✅ Fix applicato: rimosso `overflow-y-auto` dal contenuto; layout `h-full overflow-hidden`.

### `apps/frontend/src/features/wizard/steps/FoodPreferencesStep.tsx`
**Finding critici (NO SCROLL):**
- ✅ Fix applicato: rimosso `overflow-y-auto` dai risultati; guardrail “primi N risultati”.
- ✅ Fix applicato: root `h-full overflow-hidden`.

### `apps/frontend/src/features/wizard/steps/LifestyleStep.tsx`
**Finding critici (NO SCROLL):**
- ✅ Fix applicato: `overflow-y-auto` rimosso su mobile/tablet (rimane solo su `lg` per debug).
- ✅ Fix applicato: aggiunto `import type React` (uso `React.Dispatch`).
- ✅ Guardrail temporaneo: opzioni chip limitate a N.

### `apps/frontend/src/features/wizard/steps/NutritionGoalsStep.tsx`
**Finding critici (NO SCROLL):**
- ✅ Fix applicato: `overflow-y-auto` rimosso su mobile/tablet (rimane solo su `lg` per debug).
- ✅ Fix applicato: aggiunto `import type React` (uso `React.Dispatch`).
- ✅ Guardrail temporaneo: opzioni limitate a N.

### `apps/frontend/src/features/wizard/steps/TrainingGoalsStep.tsx`
**Finding critici (NO SCROLL):**
- ✅ Fix applicato: `overflow-y-auto` rimosso su mobile/tablet (rimane solo su `lg` per debug).
- ✅ Guardrail temporaneo: opzioni limitate a N.

### `apps/frontend/src/components/layout/Sidebar.tsx`
**Finding critici:**
- ⚠️ `isSidebarOpen` è stato locale (nessuna persistenza) e logica `isActive` basata su `pathname.startsWith(to)`.

### `apps/frontend/src/components/layout/MobileDrawer.tsx`
**Finding critici:**
- ⚠️ Footer hardcoded: `"ironRep v1.0 • Medical Trainer"`.
- ⚠️ Logica `isActive` basata su `pathname.startsWith(item.to!)` (coerente, ma stessa duplicazione presente in `BottomNav`/`Sidebar`).

### `apps/frontend/src/components/layout/MobileHeader.tsx`
**Finding critici:**
- ⚠️ Notifica “dot” sempre visibile (hardcoded), non derivata da stato/feature.

### `apps/frontend/src/components/layout/Sidebar.tsx`
**Finding critici (NO SCROLL):**
- ⚠️ `nav` usa `overflow-y-auto` → incompatibile con NO SCROLL (desktop-only, ma va comunque uniformato se il mandato è globale).
- ✅ Fix applicato: aggiunto `import type React` (uso di `React.ReactNode` nei types).

### `apps/frontend/src/components/layout/MobileDrawer.tsx`
**Finding critici (NO SCROLL):**
- ⚠️ `nav` usava `overflow-y-auto` → scroll interno nel drawer.
- ✅ Fix applicato: rimosso `overflow-y-auto` e introdotto guardrail temporaneo (mostra solo prime N voci).
- ✅ Fix applicato: aggiunto `import type React` (uso di `React.ReactNode`).

### `apps/frontend/src/features/chat/AgentSwitcher.tsx`
**Finding critici (NO SCROLL):**
- ⚠️ Uso di `scrollIntoView(...)` può indurre scroll verticale/side-effects.
- ✅ Fix applicato: sostituito con `container.scrollTo({ left })` (solo scroll orizzontale nel container).

### `apps/frontend/src/features/tour/components/TourSpotlight.tsx`
**Finding critici (NO SCROLL):**
- ⚠️ `element.scrollIntoView(...)` + listener su `window.scroll` incompatibili con scroll-lock.
- ✅ Fix applicato: rimosso `scrollIntoView` e listener su `scroll`; rettangolo calcolato senza `window.scrollY`.
- ✅ Fix applicato: aggiunto `import type React` (uso `React.ReactNode`).

### `apps/frontend/src/lib/navigation.ts`
**Finding critici:**
- ⚠️ `getBadge` su `medical` fa chiamata API (`checkinApi.getHistory(1)`) e assume che `history` sia un array con `.length` e `[0].date`.
- ⚠️ Confronto date via `toISOString().split('T')[0]` (timezone-sensitive) → rischio off-by-one per utenti non UTC.

### `apps/frontend/src/lib/touch-targets.ts`
**Finding critici:**
- ⚠️ Commento incongruente: `44px = 11rem` (in realtà `min-h-11` in Tailwind è 2.75rem = 44px).
- ✅ Utility utile per audit (`auditTouchTargets`, `highlightUnsafeTouchTargets`).

### `apps/frontend/src/features/auth/LoginForm.tsx`
**Finding critici:**
- ✅ Fix applicato: rimosso import non usato (TS `noUnusedLocals`).
- ⚠️ Error handling non centralizzato (non usa `handleApiError`) e messaggio generico.

### `apps/frontend/src/features/auth/RegisterForm.tsx`
**Finding critici:**
- ⚠️ Error handling via cast manuale `err as { response?: ... }` (type-safety bassa) invece di usare `handleApiError`.
- ⚠️ Dopo registrazione fa redirect a `"/login"` (non effettua login automatico) → da allineare con UX desiderata.

### `apps/frontend/src/routes/login.lazy.tsx`
**Finding critici:**
- ✅ Semplice wrapper route: usa `OptimizedAvatar` con `src="/pwa-192x192.png"`.
- ⚠️ Asset path hardcoded (ok se file esiste in `public/`, ma è coupling a naming).

### `apps/frontend/src/routes/register.lazy.tsx`
**Finding critici:**
- ✅ Speculare a login: stesso avatar `"/pwa-192x192.png"`.

### `apps/frontend/src/features/auth/index.ts`
**Finding critici:**
- ✅ Fix applicato: barrel export ora esporta `AuthProvider` e `useAuth`.

### `apps/frontend/src/components/ui/Toast.tsx`
**Finding critici:**
- ⚠️ Gestione stato globale in modulo (`toasts`, `listeners`, `toastCounter`) → attenzione a HMR e test isolation.
- ⚠️ `setTimeout` per auto-dismiss senza cleanup se componenti/unmount → rischio leak minore.

### `apps/frontend/src/components/ui/Modal.tsx`
**Finding critici:**
- ✅ Fix applicato: z-index ora impostato via `style={{ zIndex }}` (niente classi Tailwind dinamiche).

### `apps/frontend/src/components/ui/Button.tsx`
**Finding critici:**
- ✅ Fix applicato: rimosso import non usato (TS `noUnusedLocals`).

### `apps/frontend/src/components/ui/PWAInstallBanner.tsx`
**Finding critici:**
- ⚠️ Testo/CTA hardcoded (ok UX, ma i18n/centralizzazione mancante).
- ⚠️ `usePWAInstallPrompt(3)` → magic number.

### `apps/frontend/src/components/ui/OfflineIndicator.tsx`
**Finding critici:**
- ⚠️ Usa `queue.length` direttamente: ok, ma se la queue cresce serve rate-limit UI (valutare).

### `apps/frontend/src/components/ui/OptimizedImage.tsx`
**Finding critici:**
- ⚠️ Usa `document.getElementById(\`img-${src}\`)`:
  - `src` può contenere `/`, `?`, `#` → id DOM potenzialmente non valido o collisioni.
  - Coupling a `src` come chiave stabile.
- ⚠️ `IntersectionObserver` creato per immagine: ok, ma la selezione via `getElementById` è fragile rispetto a ref.

### `apps/frontend/src/components/ui/Skeletons.tsx`
**Finding critici:**
- ⚠️ Usa `Math.random()` dentro render (`ProgressChartSkeleton`) → output non deterministico, può creare mismatch visivi e rende i test fragili.

### `apps/frontend/src/components/ui/ExerciseDetailModal.tsx`
**Finding critici:**
- ⚠️ Modal custom “inline” con `z-50` (hardcoded) e gestione focus/ESC assente (rispetto a `components/ui/Modal.tsx`).
- ⚠️ Video URL mostrato come testo (non embedding) → ok, ma UX.

### `apps/frontend/src/components/ui/Input.tsx`
**Finding critici:**
- ✅ Input base con altezza `h-11` coerente con touch target.

### `apps/frontend/src/components/ui/MobileInput.tsx`
**Finding critici:**
- ✅ Pattern mobile-first (16px font, min height 48px) anti iOS zoom.
- ⚠️ Duplica concetto con `TouchInput` e `Input` → rischio duplicazione design-system.

### `apps/frontend/src/components/ui/Card.tsx`
**Finding critici:**
- ✅ Variants via `cva` ben strutturate.

### `apps/frontend/src/components/ui/sonner.tsx`
**Finding critici:**
- ✅ Fix applicato: aggiunto `import type React from "react"` per `React.ComponentProps`.

### `apps/frontend/src/components/ErrorBoundary.tsx`
**Finding critici:**
- ✅ Fix applicato: sostituito `process.env.NODE_ENV` con `import.meta.env.DEV`.

### `apps/frontend/src/components/ui/mobile/GestureWrapper.tsx`
**Finding critici:**
- ✅ Cleanup timer long-press su unmount.
- ⚠️ `dragElastic=0` e reset manuale `x.set(0)`/`y.set(0)` → ok, ma attenzione a gesture in scroll containers.

### `apps/frontend/src/components/ui/mobile/PullToRefresh.tsx`
**Finding critici:**
- ⚠️ `console.error` in catch: usare logger centralizzato.

### `apps/frontend/src/components/ui/mobile/PullToRefresh.tsx`
**Finding critici (NO SCROLL):**
- ✅ Fix applicato: rimosso `overflow-y-auto` dal container interno (componente non deve introdurre scroll).

### `apps/frontend/src/features/nutrition/components/MealPlanner/MealPlannerPage.tsx`
**Finding critici (NO SCROLL):**
- ✅ Fix applicato: rimossi container `overflow-y-auto` nei tab; pagina ora `overflow-hidden`.
- ✅ Fix applicato: rimossi import inutili (noUnusedLocals).
- ⚠️ Richiede redesign UX (planner/search) per contenuti lunghi senza scroll.

### `apps/frontend/src/features/nutrition/components/MealPlanner/WeeklyMealCalendar.tsx`
**Finding critici (NO SCROLL):**
- ✅ Fix applicato: `overflow-y-auto` ora solo su `lg`, mobile/tablet `overflow-hidden`.
- ✅ Guardrail temporaneo: lista alimenti limitata a N per pasto.

### `apps/frontend/src/features/nutrition/components/FoodSearch/FoodSearchPanel.tsx`
**Finding critici (P0 - qualità risultati FatSecret):**
- ❌ La query veniva arricchita con keyword **in inglese** (es. `chicken`, `bread`, `milk`) → bias verso risultati US/EN (“cibi americani”).
- ✅ Fix applicato: keyword di categoria convertite in italiano/neutrali.

**Finding critici (P0 - Preferiti):**
- ✅ Fix applicato: preferiti completati end-to-end (client API + hooks TanStack Query + ⭐ toggle in UI).
- ✅ Hardening: niente chiamate favorites senza token + gestione errore `GET /foods/favorites` con toast una sola volta (no spam).

### `apps/backend/src/infrastructure/external/fatsecret_service.py`
**Finding critici (P0 - localizzazione FatSecret):**
- ⚠️ `foods.search` non forzava `language/region` → risultati dipendenti dai default del provider.
- ✅ Fix applicato: aggiunti parametri `language`/`region` (default `it`/`IT`, configurabili via env `FATSECRET_LANGUAGE`/`FATSECRET_REGION`).

**Finding critici (P0 - NO MOCK):**
- ✅ Fix applicato: rimosso completamente ogni fallback mock. Se FatSecret non è configurato o fallisce, l’API ora ritorna errore (no dati finti).

### `apps/backend/src/interfaces/api/routers/foods.py`
**Finding critici (P0 - Preferiti auth-based):**
- ✅ Fix applicato: favorites basati su `CurrentUser` (token) + `DELETE /favorites/{food_id}` + caching robusto (cache miss → fetch+cache prima di salvare/rimuovere).

### `apps/frontend/src/routes/index.lazy.tsx`
**Finding critici (P0 - NO SCROLL / Dashboard):**
- ❌ Prima: container principale `space-y-4 pb-20` → dipendenza dallo scroll.
- ✅ Fix applicato: layout `flex h-full overflow-hidden` + guardrail (sezioni pesanti solo `md+`, liste orizzontali su mobile).

### `apps/frontend/src/routes/progress.lazy.tsx`
**Finding critici (P0 - NO SCROLL / Progress):**
- ❌ Prima: layout con `pb-24` + `space-y-*` → dipendenza dallo scroll.
- ✅ Fix applicato: layout `flex flex-col h-full overflow-hidden` (fit‑viewport).
- ✅ Guardrail: calendario visibile solo `md+`; su tab `all` le sezioni extra (Medical/Coach/Nutrition) sono solo `md+`.

### `apps/frontend/src/features/wizard/WizardChat.tsx` + `apps/frontend/src/features/chat/*`
**Finding critici (P0 - NO SCROLL / Wizard+Chat):**
- ✅ Fix applicato: pill e quick replies resi orizzontali su mobile (`overflow-x`) per evitare overflow verticale.
- ✅ Fix applicato: clamp messaggi assistente su mobile (no scroll, ultimi N messaggi visibili).
- ✅ Fix applicato: `QuickActions` orizzontali su mobile.
- ✅ Fix applicato: rimosse classi Tailwind dinamiche (`bg-${...}`, `border-${...}`, `text-${...}`) in `ChatEmpty` (build-safe).

### `apps/frontend/src/routes/medical.lazy.tsx`
**Finding critici (P0 - Medico / NO SCROLL):**
- ⚠️ Rischio overflow (check-in + protocollo) su mobile.
- ✅ Fix applicato: `BodyHeatmap` in modalità `compact` e guardrail su liste lunghe (esercizi/restrizioni).
- ✅ Fix applicato: scope guardrail corretto (evita `noUnusedLocals` / undefined).
- ✅ Fix applicato: layout fit‑viewport (no `space-y-*`/scroll-first), restrizioni e stats solo `md+`.
- ✅ Fix applicato: tab Biometrics ridotta a CTA verso `/biometrics` (route dedicata) per NO‑SCROLL.

### `apps/frontend/src/lib/api.ts` + `apps/backend/src/interfaces/api/routers/medical.py`
**Finding critici (P0 - Medico / pipeline FE↔BE):**
- ❌ FE chiamava `POST /medical/pain-assessment` ma BE espone `POST /medical/pain-checkin`.
- ❌ BE passava `mobility_score` a `PainAssessment` (campo non supportato) → crash runtime.
- ✅ Fix applicato: allineato endpoint/payload FE e rimosso `mobility_score` dal BE.
- ✅ Fix applicato: rimosso dead code `medicalApi.chat` (endpoint non esistente lato backend).
- ✅ Hardening: validazione input `pain-checkin` e ritorno `422` su input invalido (no `500`).

### `apps/frontend/src/lib/api/plans.ts`
**Finding critici (P0 - Medico / check-in piano settimanale):**
- ✅ Fix applicato: `submitPainCheckIn` invia snake_case (`pain_level`, `red_flags`) come richiesto dal backend.

### `apps/frontend/src/features/chat/hooks/useChat.ts`
**Finding critici (P0 - Medico / routing chat):**
- ❌ `mode="medical"` veniva trattato come check-in conversazionale (endpoint `/medical/checkin/*`) → flusso errato.
- ✅ Fix applicato: `medical` usa sempre `/medical/ask`, `checkin` usa `/medical/checkin/*`.

### `apps/frontend/src/routes/coach.lazy.tsx`
**Finding critici (P0 - Coach):**
- ❌ Mismatch dati: UI usava camelCase ma `plansApi` importato da `lib/api.ts` ritornava snake_case → campi `undefined`.
- ✅ Fix applicato: `CoachHub` ora usa `plansApi` trasformato (`src/lib/api/plans.ts`) + guardrail NO-SCROLL (max N sessioni visibili).
- ✅ Fix applicato: link "Inizia" passa contesto sessione a `/workout` (coachPlanId, coachSessionIndex).
 - ✅ Hardening: refresh piano su `focus`/`visibilitychange`.
 - ✅ Hardening: `loadCurrentPlan` stabilizzato con `useCallback` + deps corretti (evita stale closure e warning hooks).

### `apps/frontend/src/routes/workout.lazy.tsx`
**Finding critici (P0 - Coach → Workout):**
- ❌ Prima: `/workout` mostrava solo `workouts/today` (non la sessione della scheda).
- ✅ Fix applicato: `/workout` supporta avvio sessione da scheda coach e completamento sessione via `plansApi.completeWorkoutSession`.
- ✅ Hardening: invalidazione cache query `plans/coach/current` dopo completion per aggiornare subito lo stato in CoachHub.
 - ✅ UX: completion con `rating` (1–5) + `note` (opzionali) senza overflow.
 - ✅ Hardening: guardrail `coachSessionIndex` (solo interi >= 0) + redirect pulito a `/coach` se search invalida.
 - ✅ Hardening: gestione esplicita "piano non più corrente" con CTA refresh+back.

### `apps/frontend/src/lib/api/plans.ts`
**Finding critici (NO DUPLICATE CODE):**
- ❌ Duplicazione: creava un secondo `axios.create` con interceptor duplicato.
- ✅ Fix applicato: riusa il client unico `src/lib/api.ts`.

**Unificazione (P0 - Medico/Wizard):**
- ✅ `Medical` e `Wizard` usano `plansApi` da `src/lib/api/plans.ts` (wrapper medical + payload check-in).
- ✅ Rimosse API Medical duplicate da `src/lib/api.ts` per evitare call-site inconsistenti.

**Nota (Nutrition):**
- ⚠️ `routes/nutrition.lazy.tsx` resta temporaneamente su `plansApi` legacy (`src/lib/api.ts`) perché la UI usa ancora campi `snake_case` (`daily_calories`, `week_number`, ...). La migrazione richiede refactor/transform completo.

### `apps/frontend/src/features/workout/WorkoutSession.tsx`
**Finding critici (NO SCROLL):**
- ✅ Fix applicato: rimosso `overflow-y-auto` dal main.
- ✅ Guardrail temporaneo: note/textarea visibili solo su `lg`.

### `apps/frontend/src/features/workout/MobileWorkoutView.tsx`
**Finding critici (NO SCROLL):**
- ✅ Fix applicato: rimosso `overflow-y-auto` dalla lista.
- ✅ Guardrail temporaneo: lista esercizi limitata a N per sezione.

### `apps/frontend/src/components/ui/ExerciseDetailModal.tsx`
**Finding critici (NO SCROLL):**
- ✅ Fix applicato: rimosso `overflow-y-auto`/`max-h` nel modal; guardrail su liste lunghe (istruzioni/cues).

### `apps/frontend/src/components/ui/mobile/SwipeableCard.tsx`
**Finding critici:**
- ⚠️ `threshold` e `velocity` hardcoded.

### `apps/frontend/src/components/ui/mobile/TouchInput.tsx`
**Finding critici:**
- ✅ Touch input con altezza `h-12`.

---

## Checklist file-by-file (coverage 100%)

| File | Stato |
| --- | --- |
| `apps/frontend/src/main.tsx` | ANALIZZATO |
| `apps/frontend/src/router.tsx` | ANALIZZATO |
| `apps/frontend/src/routeTree.gen.ts` | ANALIZZATO (autogenerato) |
| `apps/frontend/src/routes/__root.tsx` | COMPLETATO (hardening onboarding) |
| `apps/frontend/src/routes/index.lazy.tsx` | COMPLETATO (NO-SCROLL) |
| `apps/frontend/src/routes/progress.lazy.tsx` | COMPLETATO (NO-SCROLL) |
| `apps/frontend/src/routes/medical.lazy.tsx` | COMPLETATO (NO-SCROLL) |
| `apps/frontend/src/features/layout/HubLayout.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/features/layout/types.ts` | ANALIZZATO |
| `apps/frontend/src/routes/login.lazy.tsx` | ANALIZZATO |
| `apps/frontend/src/routes/register.lazy.tsx` | ANALIZZATO |
| `apps/frontend/src/config/api.config.ts` | DA RIFATTORIZZARE |
| `apps/frontend/src/lib/api.ts` | BLOCCANTE |
| `apps/frontend/src/features/auth/AuthContext.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/components/layout/AppLayout.tsx` | ANALIZZATO |
| `apps/frontend/src/components/layout/BottomNav.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/components/layout/Sidebar.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/components/layout/MobileDrawer.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/components/layout/MobileHeader.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/features/chat/AgentSwitcher.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/features/tour/components/TourSpotlight.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/features/chat/ChatInterface.tsx` | COMPLETATO (NO-SCROLL) |
| `apps/frontend/src/features/chat/QuickActions.tsx` | COMPLETATO (NO-SCROLL) |
| `apps/frontend/src/features/chat/components/MessageList.tsx` | COMPLETATO (NO-SCROLL) |
| `apps/frontend/src/features/wizard/WizardChat.tsx` | COMPLETATO (NO-SCROLL) |
| `apps/frontend/src/features/wizard/steps/BaselineStrengthStep.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/features/wizard/steps/BiometricsStep.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/features/wizard/steps/InjuryDetailsStep.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/features/wizard/steps/FoodPreferencesStep.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/features/wizard/steps/LifestyleStep.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/features/wizard/steps/NutritionGoalsStep.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/features/wizard/steps/TrainingGoalsStep.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/features/auth/LoginForm.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/features/auth/RegisterForm.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/features/auth/index.ts` | ANALIZZATO |
| `apps/frontend/src/lib/navigation.ts` | DA RIFATTORIZZARE |
| `apps/frontend/src/lib/touch-targets.ts` | DA RIFATTORIZZARE |
| `apps/frontend/src/components/ui/Toast.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/components/ui/Modal.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/components/ui/Button.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/components/ui/PWAInstallBanner.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/components/ui/OfflineIndicator.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/components/ui/OptimizedImage.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/components/ui/Skeletons.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/components/ui/ExerciseDetailModal.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/components/ui/Input.tsx` | ANALIZZATO |
| `apps/frontend/src/components/ui/MobileInput.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/components/ui/Card.tsx` | ANALIZZATO |
| `apps/frontend/src/components/ui/sonner.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/components/ErrorBoundary.tsx` | BLOCCANTE |
| `apps/frontend/src/components/ui/mobile/index.ts` | ANALIZZATO |
| `apps/frontend/src/components/ui/mobile/GestureWrapper.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/components/ui/mobile/PullToRefresh.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/components/ui/mobile/SwipeableCard.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/components/ui/mobile/TouchInput.tsx` | ANALIZZATO |
| `apps/frontend/src/features/nutrition/components/MealPlanner/MealPlannerPage.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/features/nutrition/components/MealPlanner/WeeklyMealCalendar.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/features/workout/WorkoutSession.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/features/workout/MobileWorkoutView.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/components/ui/ExerciseDetailModal.tsx` | DA RIFATTORIZZARE |
| `apps/frontend/src/lib/logger.ts` | DA RIFATTORIZZARE |
| `apps/frontend/src/lib/apiErrorHandler.ts` | DA RIFATTORIZZARE |
| `apps/frontend/src/hooks/useAuthStorage.ts` | ANALIZZATO |

---

## Backlog miglioramenti

### P0 (BLOCCANTI)
- ⚠️ `apps/frontend/src/lib/api.ts`: spezzare per dominio + eliminare `any`.
- ✅ `apps/frontend/src/lib/api.ts`/`apps/frontend/src/lib/api/client.ts`: `httpClient` unico + `API_CONFIG.TIMEOUT` applicato (no doppio interceptor).
- ✅ PROD/Docker: `make rebuild-frontend` ora passa build-args coerenti (`VITE_API_URL=` vuoto, `VITE_API_BASE_URL=http://backend:8000`, `NODE_ENV=production`) per evitare regressioni tipo `baseURL=/api/api`.
- ✅ FatSecret (Food Search): localizzazione IT + NO MOCK + env prod (`FATSECRET_LANGUAGE`/`FATSECRET_REGION`) completati.

### Smoke test PROD (post-rebuild)
- ✅ Backend diretto: `curl -sf http://localhost:8000/health`
- ✅ Proxy via Nginx: `curl -sf -H "Host: ironrep.it" http://localhost/api/health`
- ✅ Sito: `curl -I https://ironrep.it` e `curl -sf https://ironrep.it/api/health`

---

## Requisito UX (mandato): NO SCROLL su mobile/tablet

Ho capito così: **su mobile e tablet non vuoi alcuno scroll verticale** (né body scroll né scroll interno in container). Quindi ogni pagina deve “stare” nella viewport e mostrare tutto *senza* overflow, usando alternative come:
- pagine/step dedicate (wizard/flow)
- sezioni collassabili/accordion
- tab che cambiano contenuto senza richiedere scroll
- paginazione (es. “Mostra altro” che naviga ad una route dedicata)

⚠️ Nota tecnica: per contenuti grandi (es. dashboard, progress, medical) “zero scroll assoluto” è un vincolo molto forte e richiede redesign (non solo CSS).

### Punti del codice che oggi creano scroll (verificati)
- `apps/frontend/src/components/layout/AppLayout.tsx`
  - container root: `h-[100dvh] ... overflow-hidden`.
  - main: ✅ fix applicato (non più `overflow-y-auto`); resta da far rientrare ogni route nel “viewport budget”.
- `apps/frontend/src/routes/progress.lazy.tsx` e `apps/frontend/src/routes/medical.lazy.tsx`
  - hub con sezioni lunghe e liste → oggi richiedono scroll.

### `apps/frontend/src/routes/__root.tsx`
**Finding critici (P1 - onboarding policy):**
- ✅ Fix applicato: rimosso fallback che assumeva `isOnboarded=true` su errore.
- ✅ Fix applicato: introdotta UI errore con pulsante "Riprova" per verifica onboarding.

### Direzione di implementazione (da fare)
- Definire e applicare **un modello unico** per mobile/tablet:
  - `no-scroll assoluto`: layout a pagine/step.
  - (alternativa meno drastica) `no nested scroll`: un solo scroll (body) e niente `overflow-y-auto` interni.
- Introdurre un “viewport budget” per ogni route: contenuto principale sempre fit + azioni secondarie su route dedicate.

### Stato implementazione (in corso)
- ✅ `apps/frontend/src/index.css`: applicato scroll-lock globale su mobile/tablet (`html/body/#root { overflow: hidden }`).
- ✅ `apps/frontend/src/components/layout/AppLayout.tsx`: rimosso `overflow-y-auto` dal main (main non scrollabile).
- ✅ `apps/frontend/src/components/layout/BottomNav.tsx`: rimosso `position: fixed` (nav ora nel flow del layout).

### Backlog specifico (UX no-scroll)
Queste attività sono aggiunte anche nella TODO list.

- P0: eliminare tutte le occorrenze di `overflow-y-auto`/`scrollIntoView` che presuppongono scroll (es. Chat/Wizard) o sostituirle con paginazione/step.
- P0: definire “layout contract” per route: altezza massima disponibile = viewport - header - bottomnav (no overflow).

### P1 (ALTA)
- ⚠️ `apps/frontend/src/routes/__root.tsx`: eliminare hardcoded routes e definire policy onboarding (evitare `setIsOnboarded(true)` su errore).
- ⚠️ `apps/frontend/src/routes/progress.lazy.tsx`: migrare fetch su TanStack Query e ridurre mega-file.
- ⚠️ `apps/frontend/src/routes/medical.lazy.tsx`: rimuovere magic `current_pain_level: 5` e chiarire/persistenza completion.

### P2 (MEDIA)
- ⚠️ `apps/frontend/src/lib/logger.ts`: rimuovere ANSI e integrare Sentry ufficialmente.
- ⚠️ `apps/frontend/src/lib/apiErrorHandler.ts`: type-guards axios e masking log.
