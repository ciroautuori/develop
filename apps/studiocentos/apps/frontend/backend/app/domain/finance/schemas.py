"""
Finance Schemas - Pydantic models per API
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, validator


# ============================================================================
# ENUMS
# ============================================================================

class ExpenseFrequency(str, Enum):
    """Frequenza spese"""
    ONE_TIME = "one_time"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class ExpenseStatus(str, Enum):
    """Status spese"""
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELED = "canceled"
    SCHEDULED = "scheduled"


class ExpenseCategory(str, Enum):
    """Categorie spese"""
    INFRASTRUTTURA = "infrastruttura"
    MARKETING = "marketing"
    FORMAZIONE = "formazione"
    BUSINESS = "business"
    TOOLS = "tools"
    LEGALE = "legale"
    INVESTIMENTI = "investimenti"


class ROIStatus(str, Enum):
    """Status ROI tracking"""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELED = "canceled"


class AlertSeverity(str, Enum):
    """Livelli severità alert"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class CreateExpenseRequest(BaseModel):
    """Request per creare nuova spesa"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: ExpenseCategory
    subcategory: Optional[str] = None
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="EUR", max_length=3)
    vat_rate: Decimal = Field(default=22.0, ge=0, le=100)
    due_date: date
    frequency: ExpenseFrequency = ExpenseFrequency.ONE_TIME
    frequency_count: int = Field(default=1, gt=0)
    end_date: Optional[date] = None
    supplier_name: Optional[str] = None
    supplier_email: Optional[str] = None
    supplier_website: Optional[str] = None
    supplier_vat_id: Optional[str] = None
    payment_method: Optional[str] = None
    tax_deductible: bool = True
    tax_percentage: Decimal = Field(default=100.0, ge=0, le=100)
    project_id: Optional[int] = None
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'due_date' in values and v < values['due_date']:
            raise ValueError('end_date must be after due_date')
        return v


class UpdateExpenseRequest(BaseModel):
    """Request per aggiornare spesa"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[ExpenseCategory] = None
    subcategory: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    due_date: Optional[date] = None
    status: Optional[ExpenseStatus] = None
    payment_date: Optional[date] = None
    supplier_name: Optional[str] = None
    supplier_email: Optional[str] = None
    payment_method: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    approval_notes: Optional[str] = None


class CreateBudgetRequest(BaseModel):
    """Request per creare budget mensile"""
    year: int = Field(..., ge=2020, le=2050)
    month: int = Field(..., ge=1, le=12)
    category: ExpenseCategory
    subcategory: Optional[str] = None
    planned_amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="EUR", max_length=3)
    notes: Optional[str] = None
    alert_threshold: Decimal = Field(default=10.0, ge=0, le=100)


class CreateROIRequest(BaseModel):
    """Request per creare ROI tracking"""
    investment_name: str = Field(..., min_length=1, max_length=255)
    investment_description: Optional[str] = None
    investment_category: ExpenseCategory
    investment_amount: Decimal = Field(..., gt=0)
    expected_return: Optional[Decimal] = Field(None, ge=0)
    currency: str = Field(default="EUR", max_length=3)
    investment_date: date
    expected_return_date: Optional[date] = None
    return_period_months: int = Field(default=12, gt=0)
    success_criteria: Optional[str] = None
    expense_id: Optional[int] = None


class UpdateROIRequest(BaseModel):
    """Request per aggiornare ROI"""
    actual_return: Optional[Decimal] = Field(None, ge=0)
    status: Optional[ROIStatus] = None
    measurement_end_date: Optional[date] = None
    conversion_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    customer_acquisition_cost: Optional[Decimal] = Field(None, ge=0)
    lifetime_value: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None
    lessons_learned: Optional[str] = None


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class ExpenseResponse(BaseModel):
    """Response spesa"""
    id: int
    title: str
    description: Optional[str]
    category: str
    subcategory: Optional[str]
    amount: Decimal
    currency: str
    vat_rate: Decimal
    net_amount: Decimal
    vat_amount: Decimal
    due_date: date
    payment_date: Optional[date]
    frequency: Optional[str]
    status: str
    supplier_name: Optional[str]
    supplier_email: Optional[str]
    invoice_number: Optional[str]
    tax_deductible: bool
    project_id: Optional[int]
    is_overdue: bool
    days_until_due: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class BudgetResponse(BaseModel):
    """Response budget"""
    id: int
    year: int
    month: int
    category: str
    subcategory: Optional[str]
    planned_amount: Decimal
    actual_amount: Decimal
    currency: str
    variance_amount: Decimal
    variance_percentage: Decimal
    budget_utilization: Decimal
    remaining_budget: Decimal
    is_over_budget: bool
    alert_needed: bool
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ROIResponse(BaseModel):
    """Response ROI tracking"""
    id: int
    investment_name: str
    investment_description: Optional[str]
    investment_category: str
    investment_amount: Decimal
    expected_return: Optional[Decimal]
    actual_return: Decimal
    currency: str
    investment_date: date
    expected_return_date: Optional[date]
    return_period_months: int
    status: str
    roi_calculated: Decimal
    net_profit: Decimal
    roi_multiple: Decimal
    is_profitable: bool
    days_active: int
    conversion_rate: Optional[Decimal]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    """Response alert"""
    id: int
    alert_type: str
    title: str
    message: str
    severity: str
    trigger_date: datetime
    due_date: Optional[datetime]
    status: str
    is_overdue: bool
    is_snoozed: bool
    expense_id: Optional[int]
    budget_id: Optional[int]
    roi_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# DASHBOARD SCHEMAS
# ============================================================================

class ExpenseTimelineItem(BaseModel):
    """Item timeline spese"""
    id: int
    title: str
    amount: Decimal
    currency: str
    due_date: date
    status: str
    category: str
    is_overdue: bool
    days_until_due: int


class ExpenseTimelineResponse(BaseModel):
    """Response timeline spese"""
    year: int
    total_year: Decimal
    total_pending: Decimal
    total_paid: Decimal
    upcoming_count: int
    overdue_count: int
    expenses: List[ExpenseTimelineItem]


class BudgetOverviewItem(BaseModel):
    """Item overview budget"""
    month: int
    month_name: str
    planned: Decimal
    actual: Decimal
    variance: Decimal
    variance_percentage: Decimal


class BudgetOverviewResponse(BaseModel):
    """Response overview budget"""
    year: int
    monthly_average: Decimal
    total_planned: Decimal
    total_actual: Decimal
    total_variance: Decimal
    monthly_data: List[BudgetOverviewItem]


class CategoryStatsItem(BaseModel):
    """Statistiche per categoria"""
    category: str
    total_amount: Decimal
    count: int
    percentage: Decimal


class DashboardStatsResponse(BaseModel):
    """Response statistiche dashboard"""
    total_expenses_year: Decimal
    total_budget_year: Decimal
    active_alerts: int
    overdue_expenses: int
    roi_investments: int
    avg_roi_percentage: Decimal
    categories_stats: List[CategoryStatsItem]
    monthly_trend: List[Dict[str, Any]]


class PaymentMethodStatsResponse(BaseModel):
    """Statistiche metodi pagamento"""
    method: str
    count: int
    total_amount: Decimal
    percentage: Decimal


class TaxDeductibilityResponse(BaseModel):
    """Riepilogo deducibilità fiscale"""
    total_deductible: Decimal
    total_non_deductible: Decimal
    vat_recoverable: Decimal
    estimated_tax_savings: Decimal


# ============================================================================
# FILTERS SCHEMAS
# ============================================================================

class ExpenseFilters(BaseModel):
    """Filtri per spese"""
    category: Optional[str] = None
    status: Optional[str] = None
    supplier_name: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    amount_min: Optional[Decimal] = None
    amount_max: Optional[Decimal] = None
    is_overdue: Optional[bool] = None
    tax_deductible: Optional[bool] = None
    project_id: Optional[int] = None


class BudgetFilters(BaseModel):
    """Filtri per budget"""
    year: Optional[int] = None
    month: Optional[int] = None
    category: Optional[str] = None
    is_over_budget: Optional[bool] = None


class ROIFilters(BaseModel):
    """Filtri per ROI"""
    category: Optional[str] = None
    status: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    is_profitable: Optional[bool] = None


# ============================================================================
# PAGINATION SCHEMAS
# ============================================================================

class PaginatedExpensesResponse(BaseModel):
    """Response paginata spese"""
    items: List[ExpenseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedBudgetsResponse(BaseModel):
    """Response paginata budget"""
    items: List[BudgetResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedROIResponse(BaseModel):
    """Response paginata ROI"""
    items: List[ROIResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedAlertsResponse(BaseModel):
    """Response paginata alert"""
    items: List[AlertResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
