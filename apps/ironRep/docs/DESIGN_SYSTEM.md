# 🎨 IronRep Design System - Mobile First

## 📊 Usage Distribution

| Device | Percentage | Priority |
|--------|------------|----------|
| **Mobile** | 70% | 🥇 Primary |
| **Tablet** | 28% | 🥈 Secondary |
| **Desktop** | 2% | 🥉 Enhancement |

---

## 📐 Core Principles

### 1. Mobile First

Tutti gli stili base sono per mobile. Breakpoints solo per enhancement.

```tsx
// ✅ CORRETTO - Mobile first
className="text-sm md:text-base lg:text-lg"

// ❌ SBAGLIATO - Desktop first
className="text-lg md:text-base sm:text-sm"
```

### 2. Touch Targets

Minimo **44px** (iOS HIG) per tutti gli elementi interattivi.

```tsx
// ✅ CORRETTO
className="min-h-[44px] min-w-[44px] p-3"

// ❌ SBAGLIATO
className="p-1" // Troppo piccolo per touch
```

### 3. Input Font Size

Sempre **16px minimo** per prevenire zoom su iOS.

```tsx
// ✅ CORRETTO
className="text-[16px]" // Previene zoom

// ❌ SBAGLIATO
className="text-sm" // 14px causa zoom su iOS
```

---

## 📏 Breakpoints

### Breakpoints (28% Tablet + 2% Desktop)
- **sm: 640px** - Tablet portrait (TABLET - 28% usage)
- **md: 768px** - Tablet landscape (TABLET - 28% usage)
- **lg: 1024px** - Desktop small (DESKTOP - 2% usage)
- **xl: 1280px** - Desktop large (< 1% usage - NEVER USE)

---

## 📦 Componenti Standard

### Buttons

```tsx
// Primary CTA (sempre full width su mobile)
<button className="w-full h-12 bg-primary text-primary-foreground rounded-xl font-semibold active:scale-[0.98] transition-transform touch-manipulation">
  Continua
</button>

// Secondary
<button className="w-full h-12 bg-secondary text-secondary-foreground rounded-xl font-medium active:scale-[0.98] transition-transform touch-manipulation">
  Annulla
</button>

// Icon Button
<button className="p-3 rounded-xl bg-secondary/50 active:scale-95 transition-transform touch-manipulation min-h-[44px] min-w-[44px] flex items-center justify-center">
  <Icon className="w-5 h-5" />
</button>
```

### Cards

```tsx
// Card base
<div className="bg-card border rounded-2xl p-4 shadow-sm">
  {/* content */}
</div>

// Card interattiva
<button className="bg-card border rounded-2xl p-4 shadow-sm active:scale-[0.98] transition-transform touch-manipulation w-full text-left">
  {/* content */}
</button>
```

### Inputs

```tsx
<input
  className="w-full min-h-[48px] px-4 py-3 text-[16px] bg-secondary/50 border rounded-xl focus:ring-2 focus:ring-primary/20 focus:outline-none transition-all"
  placeholder="..."
/>

<textarea
  className="w-full min-h-[100px] px-4 py-3 text-[16px] bg-secondary/50 border rounded-xl focus:ring-2 focus:ring-primary/20 focus:outline-none transition-all resize-none"
/>
```

### Lists

```tsx
<ul className="divide-y">
  <li className="flex items-center gap-3 p-4 active:bg-accent/50 transition-colors touch-manipulation min-h-[60px]">
    <Icon className="w-5 h-5 text-muted-foreground" />
    <span>Item text</span>
    <ChevronRight className="w-4 h-4 ml-auto text-muted-foreground" />
  </li>
</ul>
```

---

## 🎭 Layout Patterns

### Page con Bottom Nav

```tsx
<div className="min-h-[100dvh] pb-20 safe-area-bottom">
  {/* Content */}
</div>
```

### Sticky Header

```tsx
<header className="sticky top-0 z-20 bg-background/95 backdrop-blur-sm border-b safe-area-top">
  {/* Header content */}
</header>
```

### Sticky Bottom (Input area)

```tsx
<div className="sticky bottom-0 z-20 bg-background border-t p-4 safe-area-bottom">
  {/* Input or CTA */}
</div>
```

### Hub Layout con Tabs

```tsx
<div className="flex flex-col min-h-[100dvh]">
  <nav className="sticky top-0 z-20 flex border-b safe-area-top">
    {/* Tab buttons */}
  </nav>
  <main className="flex-1 overflow-y-auto overscroll-contain">
    {/* Content */}
  </main>
</div>
```

---

## 🎨 Colors

Usare sempre variabili CSS per supportare dark mode:

```tsx
// ✅ CORRETTO
className="bg-background text-foreground"
className="bg-primary text-primary-foreground"
className="text-muted-foreground"

// ❌ SBAGLIATO
className="bg-white text-black"
className="bg-blue-500"
```

### Semantic Colors

| Variable | Usage |
|----------|-------|
| `primary` | CTA, brand elements |
| `secondary` | Backgrounds, disabled |
| `muted` | Subtle backgrounds |
| `accent` | Hover states |
| `destructive` | Errors, delete |

---

## ✨ Animations

### Touch Feedback

```tsx
className="active:scale-[0.98] transition-transform"
className="active:scale-95 transition-transform"
className="active:opacity-80 transition-opacity"
```

### Reduced Motion

Rispetta le preferenze utente:

```tsx
// Framer Motion
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{
    duration: 0.3,
    // Rispetta reduced motion
    ...(prefersReducedMotion && { duration: 0 })
  }}
/>
```

---

## ♿ Accessibility

### Focus States

```tsx
className="focus:ring-2 focus:ring-primary/20 focus:outline-none"
```

### ARIA Labels

```tsx
<button aria-label="Chiudi menu">
  <X className="w-5 h-5" />
</button>
```

### Semantic HTML

```tsx
<nav role="tablist">
  <button role="tab" aria-selected={active}>
    Tab
  </button>
</nav>
<main role="tabpanel">
  Content
</main>
```

---

## 📱 Safe Areas

Per dispositivi con notch/home indicator:

```tsx
// Top (status bar, notch)
className="safe-area-top" // o pt-[env(safe-area-inset-top)]

// Bottom (home indicator)
className="safe-area-bottom" // o pb-[env(safe-area-inset-bottom)]
```

---

## 📄 Import Design System

```tsx
import { components, touchTargets, typography, ds } from '@/lib/design-system';

// Uso
<button className={ds(components.buttonPrimary, "mt-4")}>
  Click me
</button>
```

---

## ✅ Checklist Pre-Deploy

- [ ] Touch targets ≥ 44px
- [ ] Input font size ≥ 16px
- [ ] Mobile-first breakpoints
- [ ] Safe area handling
- [ ] Dark mode support
- [ ] Reduced motion support
- [ ] Focus states visibili
- [ ] ARIA labels per icon buttons

---

*Last Updated: November 2025*
