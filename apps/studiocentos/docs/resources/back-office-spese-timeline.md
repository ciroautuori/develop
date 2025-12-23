# 🏢 BACK-OFFICE STUDIOCENTOS - TIMELINE SPESE AZIENDALI

## 📋 **SISTEMA COMPLETO GESTIONE FINANZIARIA**

### 🎯 **OBIETTIVO:**
Integrare nel back-office esistente una sezione completa per:
- **Timeline spese mensili/annuali**
- **Calendarizzazione budget**
- **Tracking ROI investimenti**
- **Dashboard finanziario real-time**

---

## 💰 **ESEMPI SPESE STUDIOCENTOS 2025**

### **📅 CALENDARIO SPESE RICORRENTI:**

#### **🔄 MENSILI (€1.420/mese):**
```
📊 INFRASTRUTTURA & TOOLS:
- Server AWS/DigitalOcean: €120/mese
- Domain & DNS (studiocentos.it + ciroautuori.*): €15/mese
- GitHub Enterprise: €21/mese  
- Figma Professional: €15/mese
- Adobe Creative Suite: €60/mese

🤖 AI & API:
- OpenAI API (GPT-4): €200/mese
- Google Cloud (Analytics, Maps): €50/mese
- Anthropic Claude API: €100/mese

📧 MARKETING & SALES:
- Email Marketing (Mailgun): €30/mese
- CRM Hubspot Starter: €45/mese
- LinkedIn Sales Navigator: €80/mese
- Google Ads budget: €500/mese

📋 BUSINESS & LEGALE:
- Commercialista: €150/mese
- Assicurazione RC Professionale: €24/mese (€288/anno)
```

#### **📈 TRIMESTRALI (€2.100 ogni 3 mesi):**
```
🎓 FORMAZIONE & CERTIFICAZIONI:
- Corsi tecnologici (React, AI, etc.): €800/trimestre
- Conferenze tech (React Summit, AI Europe): €600/trimestre
- Certificazioni cloud (AWS, Google): €300/trimestre
- Libri e risorse: €150/trimestre
- Training marketing/sales: €250/trimestre
```

#### **📅 ANNUALI (€8.500/anno):**
```
💼 BUSINESS & LEGALE:
- Registro imprese Camera Commercio: €300
- F24 e tasse varie: €2.500
- Audit sicurezza IT: €800
- Backup e disaster recovery: €400

🚀 MARKETING & BRAND:
- Redesign brand/website: €2.000
- Video promozionali: €1.500
- Partecipazioni fiere IT: €1.000
```

#### **🎯 INVESTIMENTI STRATEGICI (variabili):**
```
💻 HARDWARE & SETUP:
- MacBook Pro/PC development: €3.000 (ogni 3 anni)
- Monitor, setup ergonomico: €1.200 (ogni 2 anni)
- Server dedicati: €2.400/anno

🤝 PARTNERSHIPS & COLLABORAZIONI:
- Freelance specializzati: €5.000-15.000/anno
- Partnership tecnologiche: €2.000-8.000/anno
- Consulenze esterne: €3.000-10.000/anno
```

---

## 📊 **IMPLEMENTAZIONE TECNICA**

### **1️⃣ DATABASE SCHEMA:**

```sql
-- Tabella spese aziendali
CREATE TABLE company_expenses (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL, -- infrastruttura, marketing, formazione, etc.
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    due_date DATE NOT NULL,
    payment_date DATE,
    frequency VARCHAR(50), -- monthly, quarterly, yearly, one_time
    status VARCHAR(50) DEFAULT 'pending', -- pending, paid, overdue, canceled
    payment_method VARCHAR(100),
    supplier_name VARCHAR(255),
    supplier_email VARCHAR(255),
    invoice_number VARCHAR(100),
    tax_deductible BOOLEAN DEFAULT true,
    project_id BIGINT REFERENCES projects(id),
    created_by BIGINT REFERENCES admin_users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella budget mensili
CREATE TABLE monthly_budgets (
    id BIGSERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month >= 1 AND month <= 12),
    category VARCHAR(100) NOT NULL,
    planned_amount DECIMAL(10,2) NOT NULL,
    actual_amount DECIMAL(10,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'EUR',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, month, category)
);

-- Tabella tracking ROI
CREATE TABLE roi_tracking (
    id BIGSERIAL PRIMARY KEY,
    investment_name VARCHAR(255) NOT NULL,
    investment_amount DECIMAL(10,2) NOT NULL,
    investment_date DATE NOT NULL,
    expected_return DECIMAL(10,2),
    actual_return DECIMAL(10,2) DEFAULT 0,
    return_period_months INTEGER DEFAULT 12,
    status VARCHAR(50) DEFAULT 'active', -- active, completed, failed
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **2️⃣ BACKEND API ENDPOINTS:**

```python
# apps/backend/app/domain/finance/models.py
class CompanyExpense(Base):
    __tablename__ = "company_expenses"
    
    id = Column(BigInteger, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="EUR")
    due_date = Column(Date, nullable=False)
    payment_date = Column(Date)
    frequency = Column(String(50))  # monthly, quarterly, yearly, one_time
    status = Column(String(50), default="pending")
    supplier_name = Column(String(255))
    tax_deductible = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# apps/backend/app/domain/finance/router.py
@router.get("/expenses/timeline")
def get_expenses_timeline(
    year: int = Query(2025),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get expenses timeline for calendar view"""
    return FinanceService.get_expenses_timeline(db, year)

@router.get("/budget/overview")
def get_budget_overview(
    year: int = Query(2025),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get budget vs actual overview"""
    return FinanceService.get_budget_overview(db, year)

@router.post("/expenses", response_model=ExpenseResponse)
def create_expense(
    expense: CreateExpenseRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Create new expense"""
    return FinanceService.create_expense(db, expense, admin.id)
```

### **3️⃣ FRONTEND COMPONENTI:**

```tsx
// apps/frontend/src/features/admin/pages/FinanceDashboard.tsx
export function FinanceDashboard() {
  const { data: timeline } = useQuery({
    queryKey: ['finance', 'timeline', 2025],
    queryFn: () => financeApi.getExpensesTimeline(2025)
  });

  const { data: budget } = useQuery({
    queryKey: ['finance', 'budget', 2025], 
    queryFn: () => financeApi.getBudgetOverview(2025)
  });

  return (
    <div className="space-y-8">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <KPICard 
          title="Spese Totali 2025"
          value={`€${timeline?.total_year || 0}`}
          trend="+5.2%"
          icon={Euro}
        />
        <KPICard 
          title="Budget Mensile"
          value={`€${budget?.monthly_average || 0}`}
          trend="-2.1%"
          icon={Calendar}
        />
        <KPICard 
          title="ROI Investimenti"
          value="127%"
          trend="+12.3%"
          icon={TrendingUp}
        />
        <KPICard 
          title="Scadenze Prossime"
          value={timeline?.upcoming_count || 0}
          trend="3 giorni"
          icon={AlertTriangle}
        />
      </div>

      {/* Timeline Calendar */}
      <Card className="p-6">
        <h2 className="text-2xl font-bold mb-6">Timeline Spese 2025</h2>
        <ExpensesCalendar 
          expenses={timeline?.expenses || []}
          onDateClick={handleDateClick}
        />
      </Card>

      {/* Budget vs Actual Chart */}
      <Card className="p-6">
        <h2 className="text-2xl font-bold mb-6">Budget vs Spese Reali</h2>
        <BudgetChart data={budget?.monthly_data || []} />
      </Card>
    </div>
  );
}
```

---

## 📅 **ESEMPI PRATICI TIMELINE 2025**

### **🗓️ GENNAIO 2025:**
```
📅 5 Gen: Server hosting AWS (€120) - MENSILE
📅 8 Gen: Google Ads budget (€500) - MENSILE  
📅 15 Gen: Commercialista (€150) - MENSILE
📅 20 Gen: OpenAI API (€200) - MENSILE
📅 31 Gen: F24 trimestrale (€800) - TRIMESTRALE
```

### **🗓️ FEBBRAIO 2025:**
```
📅 5 Feb: Server hosting AWS (€120) - MENSILE
📅 8 Feb: Google Ads budget (€500) - MENSILE
📅 12 Feb: Adobe Creative Suite (€60) - MENSILE
📅 15 Feb: Commercialista (€150) - MENSILE
📅 28 Feb: Assicurazione RC (€24) - MENSILE
```

### **🗓️ MARZO 2025:**
```
📅 5 Mar: Server hosting AWS (€120) - MENSILE
📅 8 Mar: Google Ads budget (€500) - MENSILE
📅 15 Mar: Commercialista (€150) - MENSILE
📅 31 Mar: Formazione React Summit (€600) - TRIMESTRALE
```

### **🗓️ DICEMBRE 2025:**
```
📅 5 Dic: Server hosting AWS (€120) - MENSILE
📅 15 Dic: Commercialista (€150) - MENSILE
📅 20 Dic: Tasse annuali (€2.500) - ANNUALE
📅 31 Dic: Chiusura bilancio - PLANNING 2026
```

---

## 🎯 **DASHBOARD FEATURES**

### **📊 ANALYTICS FINANZIARIE:**
- **Cash flow forecast** 12 mesi
- **Trend spese** per categoria
- **Alert scadenze** 7/15/30 giorni
- **ROI calculator** investimenti
- **Export PDF** report mensili

### **📱 NOTIFICHE SMART:**
```
🔔 "Scadenza pagamento OpenAI API tra 3 giorni (€200)"
🔔 "Budget Google Ads superato del 15% questo mese"
🔔 "Nuova fattura da pagare: Adobe Creative Suite"
🔔 "ROI investimento LinkedIn Ads: +127% vs previsto"
```

### **📈 REPORTS AUTOMATICI:**
- **Report mensile** spese vs budget
- **Analisi ROI** trimestrale investimenti
- **Previsioni** cash flow 6 mesi
- **Benchmark** settore IT

---

## 🚀 **IMPLEMENTAZIONE ROADMAP**

### **✅ SETTIMANA 1-2:**
1. Database schema + migrations
2. Backend API endpoints
3. Frontend componenti base

### **✅ SETTIMANA 3-4:**
1. Calendar timeline component
2. Budget vs actual charts
3. KPI dashboard integration

### **✅ SETTIMANA 5-6:**
1. Notifiche e alert system
2. Export PDF reports
3. Mobile responsive design

### **✅ SETTIMANA 7-8:**
1. ROI tracking avanzato
2. Previsioni AI-powered
3. Integration con commercialista

---

## 💡 **VALORE AGGIUNTO**

### **🎯 DECISION MAKING:**
- **Visibilità completa** su tutte le spese
- **Previsioni accurate** cash flow
- **Ottimizzazione** investimenti marketing
- **Control budgetario** real-time

### **📋 COMPLIANCE:**
- **Tracking fiscale** automatico
- **Documenti** organizzati per commercialista
- **Report** pronti per audit
- **Backup** sicurezza dati

### **🚀 SCALING:**
- **Template** spese ricorrenti
- **Workflow** approvazione spese team
- **Integration** banche/PayPal
- **API** contabilità esterna

---

## 📞 **NEXT STEPS**

1. **✅ Approvazione** schema database
2. **🔧 Implementazione** backend APIs
3. **🎨 Design** componenti frontend
4. **📊 Test** con dati reali StudioCentOS
5. **🚀 Deploy** e training utilizzo

**Tempo stimato implementazione completa: 6-8 settimane** 

**ROI atteso: Risparmio 20-30% spese + ottimizzazione cash flow**
