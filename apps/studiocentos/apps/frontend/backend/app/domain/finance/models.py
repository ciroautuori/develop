"""
Finance Models - Gestione finanziaria StudioCentOS
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import (
    Column, BigInteger, String, Text, Numeric, Date, DateTime, 
    Boolean, Integer, ForeignKey, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.ext.hybrid import hybrid_property

from app.infrastructure.database.session import Base


class CompanyExpense(Base):
    """
    Spese aziendali StudioCentOS.
    
    Gestisce tutte le spese: ricorrenti, una tantum, investimenti.
    """
    __tablename__ = "company_expenses"
    
    id = Column(BigInteger, primary_key=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Categorizzazione
    category = Column(String(100), nullable=False, index=True)  # infrastruttura, marketing, formazione, etc.
    subcategory = Column(String(100))  # aws, google_ads, react_course, etc.
    
    # Importi
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="EUR", nullable=False)
    vat_rate = Column(Numeric(5, 2), default=22.0)  # 22% IVA italiana
    net_amount = Column(Numeric(10, 2))  # Calcolato automaticamente
    
    # Date
    due_date = Column(Date, nullable=False, index=True)
    payment_date = Column(Date, index=True)
    
    # Ricorrenza
    frequency = Column(String(50))  # monthly, quarterly, yearly, one_time
    frequency_count = Column(Integer, default=1)  # ogni X mesi/anni
    end_date = Column(Date)  # quando finisce la ricorrenza
    
    # Status
    status = Column(String(50), default="pending", nullable=False, index=True)  
    # pending, paid, overdue, canceled, scheduled
    
    # Fornitore
    supplier_name = Column(String(255), index=True)
    supplier_email = Column(String(255))
    supplier_website = Column(String(255))
    supplier_vat_id = Column(String(50))  # P.IVA fornitore
    
    # Fatturazione
    invoice_number = Column(String(100), index=True)
    invoice_date = Column(Date)
    invoice_file_path = Column(String(500))  # Path file PDF fattura
    
    # Metodo pagamento
    payment_method = Column(String(100))  # bank_transfer, credit_card, paypal, etc.
    payment_reference = Column(String(255))  # IBAN, numero carta, etc.
    
    # Fiscale
    tax_deductible = Column(Boolean, default=True, nullable=False)
    tax_percentage = Column(Numeric(5, 2), default=100.0)  # % deducibilità
    
    # Progetti (opzionale) - RELAZIONE UNIDIREZIONALE
    project_id = Column(BigInteger, ForeignKey("projects.id"), nullable=True)
    
    # Approvazione
    approved_by = Column(BigInteger, ForeignKey("admin_users.id"))
    approved_at = Column(DateTime)
    approval_notes = Column(Text)
    
    # Audit
    created_by = Column(BigInteger, ForeignKey("admin_users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("AdminUser", foreign_keys=[created_by])
    approver = relationship("AdminUser", foreign_keys=[approved_by])
    
    # Constraints
    __table_args__ = (
        CheckConstraint('amount > 0', name='positive_amount'),
        CheckConstraint('vat_rate >= 0 AND vat_rate <= 100', name='valid_vat_rate'),
        CheckConstraint('tax_percentage >= 0 AND tax_percentage <= 100', name='valid_tax_percentage'),
    )
    
    @hybrid_property
    def net_amount_calculated(self) -> Decimal:
        """Calcola importo netto (senza IVA)"""
        if self.vat_rate and self.vat_rate > 0:
            return self.amount / (1 + (self.vat_rate / 100))
        return self.amount
    
    @hybrid_property
    def vat_amount(self) -> Decimal:
        """Calcola importo IVA"""
        if self.vat_rate and self.vat_rate > 0:
            net = self.net_amount_calculated
            return self.amount - net
        return Decimal('0.00')
    
    @hybrid_property
    def is_overdue(self) -> bool:
        """Verifica se la spesa è scaduta"""
        if self.status != 'pending':
            return False
        return self.due_date < date.today()
    
    @hybrid_property
    def days_until_due(self) -> int:
        """Giorni rimanenti alla scadenza"""
        if self.status != 'pending':
            return 0
        delta = self.due_date - date.today()
        return delta.days


class MonthlyBudget(Base):
    """
    Budget mensili per categoria.
    
    Pianificazione e controllo budget StudioCentOS.
    """
    __tablename__ = "monthly_budgets"
    
    id = Column(BigInteger, primary_key=True)
    
    # Periodo
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False, index=True)
    
    # Categoria
    category = Column(String(100), nullable=False, index=True)
    subcategory = Column(String(100))
    
    # Budget
    planned_amount = Column(Numeric(10, 2), nullable=False)
    actual_amount = Column(Numeric(10, 2), default=0)
    currency = Column(String(3), default="EUR", nullable=False)
    
    # Varianza
    variance_amount = Column(Numeric(10, 2), default=0)  # actual - planned
    variance_percentage = Column(Numeric(5, 2), default=0)  # (actual/planned - 1) * 100
    
    # Note
    notes = Column(Text)
    alert_threshold = Column(Numeric(5, 2), default=10.0)  # Alert se varianza > X%
    
    # Audit
    created_by = Column(BigInteger, ForeignKey("admin_users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("AdminUser")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('year', 'month', 'category', 'subcategory', name='unique_budget_period'),
        CheckConstraint('month >= 1 AND month <= 12', name='valid_month'),
        CheckConstraint('year >= 2020 AND year <= 2050', name='valid_year'),
        CheckConstraint('planned_amount > 0', name='positive_planned_amount'),
    )
    
    @hybrid_property
    def budget_utilization(self) -> Decimal:
        """Percentuale utilizzo budget"""
        if self.planned_amount > 0:
            return (self.actual_amount / self.planned_amount) * 100
        return Decimal('0.00')
    
    @hybrid_property
    def remaining_budget(self) -> Decimal:
        """Budget rimanente"""
        return self.planned_amount - self.actual_amount
    
    @hybrid_property
    def is_over_budget(self) -> bool:
        """Verifica se ha superato il budget"""
        return self.actual_amount > self.planned_amount
    
    @hybrid_property
    def alert_needed(self) -> bool:
        """Verifica se serve un alert"""
        if self.alert_threshold and self.planned_amount > 0:
            variance_pct = abs((self.actual_amount / self.planned_amount - 1) * 100)
            return variance_pct > self.alert_threshold
        return False


class ROITracking(Base):
    """
    Tracking ROI investimenti.
    
    Monitora il ritorno degli investimenti StudioCentOS.
    """
    __tablename__ = "roi_tracking"
    
    id = Column(BigInteger, primary_key=True)
    
    # Investimento
    investment_name = Column(String(255), nullable=False, index=True)
    investment_description = Column(Text)
    investment_category = Column(String(100), nullable=False, index=True)  # marketing, tools, training, etc.
    
    # Importi
    investment_amount = Column(Numeric(10, 2), nullable=False)
    expected_return = Column(Numeric(10, 2))
    actual_return = Column(Numeric(10, 2), default=0)
    currency = Column(String(3), default="EUR", nullable=False)
    
    # Date
    investment_date = Column(Date, nullable=False, index=True)
    expected_return_date = Column(Date)
    measurement_start_date = Column(Date)
    measurement_end_date = Column(Date)
    
    # Periodo
    return_period_months = Column(Integer, default=12)
    measurement_frequency = Column(String(50), default="monthly")  # daily, weekly, monthly, quarterly
    
    # Status
    status = Column(String(50), default="active", nullable=False, index=True)  
    # active, completed, failed, paused, canceled
    
    # Metriche
    roi_percentage = Column(Numeric(10, 2), default=0)  # (actual_return - investment) / investment * 100
    payback_period_days = Column(Integer)  # Giorni per rientrare investimento
    break_even_date = Column(Date)
    
    # KPI specifici
    conversion_rate = Column(Numeric(5, 2))  # % conversione se applicabile
    customer_acquisition_cost = Column(Numeric(10, 2))  # CAC se marketing
    lifetime_value = Column(Numeric(10, 2))  # LTV se cliente
    
    # Note e tracking
    notes = Column(Text)
    success_criteria = Column(Text)  # Criteri di successo definiti
    lessons_learned = Column(Text)  # Cosa abbiamo imparato
    
    # Link a spese
    expense_id = Column(BigInteger, ForeignKey("company_expenses.id"), nullable=True)
    expense = relationship("CompanyExpense")
    
    # Audit
    created_by = Column(BigInteger, ForeignKey("admin_users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("AdminUser")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('investment_amount > 0', name='positive_investment'),
        CheckConstraint('actual_return >= 0', name='non_negative_return'),
        CheckConstraint('return_period_months > 0', name='positive_period'),
    )
    
    @hybrid_property
    def roi_calculated(self) -> Decimal:
        """Calcola ROI percentage"""
        if self.investment_amount > 0:
            return ((self.actual_return - self.investment_amount) / self.investment_amount) * 100
        return Decimal('0.00')
    
    @hybrid_property
    def net_profit(self) -> Decimal:
        """Profitto netto"""
        return self.actual_return - self.investment_amount
    
    @hybrid_property
    def roi_multiple(self) -> Decimal:
        """Multiplo dell'investimento"""
        if self.investment_amount > 0:
            return self.actual_return / self.investment_amount
        return Decimal('0.00')
    
    @hybrid_property
    def is_profitable(self) -> bool:
        """Verifica se l'investimento è profittevole"""
        return self.actual_return > self.investment_amount
    
    @hybrid_property
    def days_active(self) -> int:
        """Giorni attivi dell'investimento"""
        if self.measurement_end_date:
            end_date = self.measurement_end_date
        else:
            end_date = date.today()
        
        start_date = self.measurement_start_date or self.investment_date
        return (end_date - start_date).days


class ExpenseRecurrence(Base):
    """
    Gestione ricorrenze spese.
    
    Automatizza la creazione di spese ricorrenti.
    """
    __tablename__ = "expense_recurrences"
    
    id = Column(BigInteger, primary_key=True)
    
    # Template spesa
    title_template = Column(String(255), nullable=False)
    description_template = Column(Text)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100))
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="EUR", nullable=False)
    
    # Ricorrenza
    frequency = Column(String(50), nullable=False)  # monthly, quarterly, yearly
    frequency_count = Column(Integer, default=1)  # ogni X periodi
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)  # quando finisce la ricorrenza
    
    # Supplier info
    supplier_name = Column(String(255))
    supplier_email = Column(String(255))
    payment_method = Column(String(100))
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_generated_date = Column(Date)
    next_generation_date = Column(Date, nullable=False, index=True)
    
    # Approvazione automatica
    auto_approve = Column(Boolean, default=False)
    auto_approve_threshold = Column(Numeric(10, 2))  # Auto-approva se importo <= threshold
    
    # Audit
    created_by = Column(BigInteger, ForeignKey("admin_users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("AdminUser")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('amount > 0', name='positive_recurrence_amount'),
        CheckConstraint('frequency_count > 0', name='positive_frequency_count'),
    )


class FinanceAlert(Base):
    """
    Alert e notifiche finanziarie.
    
    Sistema di notifiche per scadenze, budget, ROI.
    """
    __tablename__ = "finance_alerts"
    
    id = Column(BigInteger, primary_key=True)
    
    # Tipo alert
    alert_type = Column(String(50), nullable=False, index=True)  
    # expense_due, budget_exceeded, roi_milestone, payment_overdue
    
    # Riferimenti
    expense_id = Column(BigInteger, ForeignKey("company_expenses.id"), nullable=True)
    budget_id = Column(BigInteger, ForeignKey("monthly_budgets.id"), nullable=True)
    roi_id = Column(BigInteger, ForeignKey("roi_tracking.id"), nullable=True)
    
    # Alert info
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(50), default="medium")  # low, medium, high, critical
    
    # Date
    trigger_date = Column(DateTime, nullable=False, index=True)
    due_date = Column(DateTime)  # quando deve essere risolto
    
    # Status
    status = Column(String(50), default="active", nullable=False, index=True)  
    # active, dismissed, resolved, snoozed
    
    resolved_at = Column(DateTime)
    resolved_by = Column(BigInteger, ForeignKey("admin_users.id"))
    resolution_notes = Column(Text)
    
    # Notifiche
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime)
    push_sent = Column(Boolean, default=False)
    push_sent_at = Column(DateTime)
    
    # Snooze
    snoozed_until = Column(DateTime)
    snooze_count = Column(Integer, default=0)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    expense = relationship("CompanyExpense")
    budget = relationship("MonthlyBudget")
    roi = relationship("ROITracking")
    resolver = relationship("AdminUser")
    
    @hybrid_property
    def is_active(self) -> bool:
        """Verifica se l'alert è ancora attivo"""
        return self.status == "active"
    
    @hybrid_property
    def is_overdue(self) -> bool:
        """Verifica se l'alert è scaduto"""
        if self.due_date and self.status == "active":
            return datetime.utcnow() > self.due_date
        return False
    
    @hybrid_property
    def is_snoozed(self) -> bool:
        """Verifica se l'alert è posticipato"""
        if self.snoozed_until:
            return datetime.utcnow() < self.snoozed_until
        return False
