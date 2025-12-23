# 🎨 **ISS - BRAND COLORS UFFICIALI**

## 📋 **PALETTE COLORI UFFICIALE**

Estratta dal logo SVG ufficiale di **Innovazione Sociale Salernitana APS**.

### **🏛️ COLORI PRIMARI**

#### **Bordeaux ISS** 
- **HEX**: `#7a2426`
- **HSL**: `hsl(355, 52%, 31%)`
- **RGB**: `rgb(122, 36, 38)`
- **Uso**: Colore principale per testi, bordi, elementi di primo piano

#### **Oro ISS**
- **HEX**: `#f4af00` 
- **HSL**: `hsl(46, 100%, 48%)`
- **RGB**: `rgb(244, 175, 0)`
- **Uso**: Colore accento, highlights, call-to-action

#### **Bianco**
- **HEX**: `#ffffff`
- **HSL**: `hsl(0, 0%, 100%)`
- **RGB**: `rgb(255, 255, 255)`
- **Uso**: Background, testi su sfondo scuro

---

## 🌈 **SCALE TONALITÀ TAILWIND**

### **ISS Bordeaux Scale**
```css
'iss-bordeaux': {
  50: '#fdf2f3',   /* Molto chiaro */
  100: '#fce7e8',  /* Chiaro */
  200: '#facecd',  /* Chiaro */
  300: '#f5a3a8',  /* Medio chiaro */
  400: '#ec6d75',  /* Medio */
  500: '#df3a47',  /* Medio scuro */
  600: '#c51f2f',  /* Scuro */
  700: '#a4182a',  /* Molto scuro */
  800: '#7a2426',  /* 🏛️ UFFICIALE */
  900: '#6b1f21',  /* Ultra scuro */
}
```

### **ISS Oro Scale**
```css
'iss-gold': {
  50: '#fffef7',   /* Molto chiaro */
  100: '#fffbe0',  /* Chiaro */
  200: '#fff7c2',  /* Chiaro */
  300: '#fff08a',  /* Medio chiaro */
  400: '#ffe74f',  /* Medio */
  500: '#f4af00',  /* 🏛️ UFFICIALE */
  600: '#e89900',  /* Scuro */
  700: '#c07302',  /* Molto scuro */
  800: '#9e5a08',  /* Ultra scuro */
  900: '#82480b',  /* Nero dorato */
}
```

---

## 🎯 **GUIDE D'USO**

### **✅ DO - Cosa Fare**
- Usa **Bordeaux 800** per testi principali e navigation
- Usa **Oro 500** per bottoni primari e CTA
- Usa **Bianco** per background e contrast text
- Combina Bordeaux + Oro per gradienti eleganti
- Mantieni sempre alto contrasto per accessibilità

### **❌ DON'T - Cosa Evitare**
- Non mischiare con altri colori brand
- Non usare tonalità troppo chiare per testi importanti
- Non usare oro su sfondo bianco senza bordi
- Non creare combinazioni con basso contrasto

---

## 📊 **ESEMPI DI UTILIZZO**

### **Headers & Navigation**
```css
background: iss-bordeaux-800
color: white
accent: iss-gold-500
```

### **Buttons Primary**
```css
background: iss-gold-500
color: iss-bordeaux-800
border: iss-bordeaux-800
```

### **Cards & Components**
```css
border: iss-bordeaux-200
background: white
text: iss-bordeaux-800
```

### **Status & Alerts**
- **Priorità Alta**: iss-bordeaux-600
- **Priorità Media**: iss-gold-500
- **Priorità Bassa**: gray-400

---

## 🛠️ **IMPLEMENTAZIONE TECNICA**

### **CSS Variables (globals.css)**
```css
--primary: 46 100% 48%;        /* ISS Gold */
--primary-foreground: 0 0% 100%;
--ring: 355 52% 31%;           /* ISS Bordeaux */
```

### **Tailwind Classes**
- `text-iss-bordeaux-800`
- `bg-iss-gold-500` 
- `border-iss-bordeaux-600`
- `hover:bg-iss-gold-600`

### **Gradients**
```css
.text-gradient {
  @apply bg-gradient-to-r from-iss-bordeaux-600 to-iss-gold-500 bg-clip-text text-transparent;
}
```

---

## ✨ **BRAND IDENTITY COMPLETA**

Questa palette rappresenta l'identità visiva ufficiale di:

**🏛️ INNOVAZIONE SOCIALE SALERNITANA APS**
- **Bordeaux**: Istituzionale, professionale, affidabile
- **Oro**: Innovazione, eccellenza, valore
- **Bianco**: Purezza, chiarezza, accessibilità

**Il design rispetta completamente il logo ufficiale fornito!** 🎨✨
