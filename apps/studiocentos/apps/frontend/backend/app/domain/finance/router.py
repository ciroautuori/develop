"""
Finance Router - API endpoints gestione finanziaria
"""

from datetime import datetime, date
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.infrastructure.database.session import get_db
from app.core.api.dependencies.auth_deps import get_current_admin_user
from app.domain.auth.admin_models import AdminUser

from .service import FinanceService
from .schemas import (
    CreateExpenseRequest, UpdateExpenseRequest, ExpenseResponse,
    CreateBudgetRequest, BudgetResponse, CreateROIRequest, UpdateROIRequest, ROIResponse,
    ExpenseTimelineResponse, BudgetOverviewResponse, DashboardStatsResponse,
    ExpenseFilters, BudgetFilters, ROIFilters, 
    PaginatedExpensesResponse, PaginatedBudgetsResponse, PaginatedROIResponse,
    TaxDeductibilityResponse, PaymentMethodStatsResponse, AlertResponse
)


router = APIRouter(prefix="/api/v1/admin/finance", tags=["admin-finance"])


# ============================================================================
# EXPENSES ENDPOINTS
# ============================================================================

@router.post("/expenses", response_model=ExpenseResponse)
def create_expense(
    request: CreateExpenseRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Crea nuova spesa aziendale.
    
    Supporta spese una tantum e ricorrenti con gestione automatica delle ricorrenze.
    """
    return FinanceService.create_expense(db, request, admin.id)


@router.get("/expenses", response_model=PaginatedExpensesResponse)
def get_expenses(
    page: int = Query(1, ge=1, description="Numero pagina"),
    page_size: int = Query(50, ge=1, le=100, description="Elementi per pagina"),
    sort_by: str = Query("due_date", description="Campo per ordinamento"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Direzione ordinamento"),
    # Filtri
    category: Optional[str] = Query(None, description="Filtra per categoria"),
    status: Optional[str] = Query(None, description="Filtra per status"),
    supplier_name: Optional[str] = Query(None, description="Filtra per fornitore"),
    date_from: Optional[date] = Query(None, description="Data scadenza da"),
    date_to: Optional[date] = Query(None, description="Data scadenza a"),
    amount_min: Optional[float] = Query(None, ge=0, description="Importo minimo"),
    amount_max: Optional[float] = Query(None, ge=0, description="Importo massimo"),
    is_overdue: Optional[bool] = Query(None, description="Solo spese scadute"),
    tax_deductible: Optional[bool] = Query(None, description="Solo spese deducibili"),
    project_id: Optional[int] = Query(None, description="Filtra per progetto"),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Lista spese con filtri avanzati e paginazione.
    
    Supporta ordinamento per: due_date, amount, created_at
    """
    filters = ExpenseFilters(
        category=category,
        status=status,
        supplier_name=supplier_name,
        date_from=date_from,
        date_to=date_to,
        amount_min=amount_min,
        amount_max=amount_max,
        is_overdue=is_overdue,
        tax_deductible=tax_deductible,
        project_id=project_id
    )
    
    return FinanceService.get_expenses(
        db, filters, page, page_size, sort_by, sort_order
    )


@router.get("/expenses/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Ottieni dettagli spesa specifica"""
    expense = FinanceService.get_expense_by_id(db, expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spesa non trovata"
        )
    return expense


@router.put("/expenses/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    request: UpdateExpenseRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Aggiorna spesa esistente.
    
    Permette di modificare tutti i campi eccetto quelli di audit.
    """
    return FinanceService.update_expense(db, expense_id, request, admin.id)


@router.delete("/expenses/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Elimina spesa (soft delete)"""
    success = FinanceService.delete_expense(db, expense_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spesa non trovata"
        )
    return {"message": "Spesa eliminata con successo"}


@router.post("/expenses/{expense_id}/approve")
def approve_expense(
    expense_id: int,
    approval_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Approva spesa per pagamento"""
    success = FinanceService.approve_expense(db, expense_id, admin.id, approval_notes)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spesa non trovata"
        )
    return {"message": "Spesa approvata con successo"}


@router.post("/expenses/{expense_id}/pay")
def mark_expense_paid(
    expense_id: int,
    payment_date: Optional[date] = None,
    payment_reference: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Marca spesa come pagata"""
    success = FinanceService.mark_expense_paid(
        db, expense_id, payment_date or date.today(), payment_reference
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spesa non trovata"
        )
    return {"message": "Spesa marcata come pagata"}


@router.post("/expenses/{expense_id}/upload-invoice")
def upload_invoice(
    expense_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Upload fattura PDF per spesa"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo file PDF sono supportati"
        )
    
    file_path = FinanceService.upload_invoice_file(db, expense_id, file)
    return {"message": "Fattura caricata con successo", "file_path": file_path}


# ============================================================================
# TIMELINE & CALENDAR ENDPOINTS  
# ============================================================================

@router.get("/expenses/timeline/{year}", response_model=ExpenseTimelineResponse)
def get_expenses_timeline(
    year: int = Path(..., ge=2020, le=2050, description="Anno timeline"),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Timeline spese per anno.
    
    Utilizzato per il calendario spese e dashboard overview.
    """
    return FinanceService.get_expenses_timeline(db, year)


@router.get("/expenses/calendar/{year}/{month}")
def get_monthly_calendar(
    year: int = Path(..., ge=2020, le=2050),
    month: int = Path(..., ge=1, le=12),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Dati calendario per mese specifico"""
    return FinanceService.get_monthly_calendar(db, year, month)


@router.get("/expenses/upcoming")
def get_upcoming_expenses(
    days: int = Query(30, ge=1, le=365, description="Giorni in anticipo"),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Spese in scadenza nei prossimi X giorni"""
    return FinanceService.get_upcoming_expenses(db, days)


@router.get("/expenses/overdue")
def get_overdue_expenses(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Spese scadute e non pagate"""
    return FinanceService.get_overdue_expenses(db)


# ============================================================================
# BUDGET ENDPOINTS
# ============================================================================

@router.post("/budgets", response_model=BudgetResponse)
def create_budget(
    request: CreateBudgetRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Crea nuovo budget mensile per categoria.
    
    Calcola automaticamente actual_amount basato su spese esistenti.
    """
    return FinanceService.create_budget(db, request, admin.id)


@router.get("/budgets", response_model=PaginatedBudgetsResponse)
def get_budgets(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    year: Optional[int] = Query(None, ge=2020, le=2050),
    month: Optional[int] = Query(None, ge=1, le=12),
    category: Optional[str] = Query(None),
    is_over_budget: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Lista budget con filtri"""
    filters = BudgetFilters(
        year=year,
        month=month,
        category=category,
        is_over_budget=is_over_budget
    )
    
    return FinanceService.get_budgets(db, filters, page, page_size)


@router.get("/budgets/overview/{year}", response_model=BudgetOverviewResponse)
def get_budget_overview(
    year: int = Path(..., ge=2020, le=2050),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Overview budget vs actual per anno.
    
    Mostra confronto mensile e trend annuale.
    """
    return FinanceService.get_budget_overview(db, year)


@router.put("/budgets/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    request: CreateBudgetRequest,  # Riusa lo stesso schema
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Aggiorna budget esistente"""
    return FinanceService.update_budget(db, budget_id, request)


@router.post("/budgets/refresh-actual")
def refresh_budget_actual(
    year: Optional[int] = Query(None, ge=2020, le=2050),
    month: Optional[int] = Query(None, ge=1, le=12),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Ricalcola actual_amount per tutti i budget"""
    count = FinanceService.refresh_budget_actual(db, year, month)
    return {"message": f"Aggiornati {count} budget"}


# ============================================================================
# ROI TRACKING ENDPOINTS
# ============================================================================

@router.post("/roi", response_model=ROIResponse)
def create_roi_tracking(
    request: CreateROIRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Crea nuovo ROI tracking per investimento.
    
    Monitora il ritorno di investimenti marketing, tools, formazione.
    """
    return FinanceService.create_roi_tracking(db, request, admin.id)


@router.get("/roi", response_model=PaginatedROIResponse)
def get_roi_trackings(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    is_profitable: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Lista ROI tracking con filtri"""
    filters = ROIFilters(
        category=category,
        status=status,
        date_from=date_from,
        date_to=date_to,
        is_profitable=is_profitable
    )
    
    return FinanceService.get_roi_trackings(db, filters, page, page_size)


@router.put("/roi/{roi_id}", response_model=ROIResponse)
def update_roi_tracking(
    roi_id: int,
    request: UpdateROIRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Aggiorna ROI tracking con risultati reali.
    
    Calcola automaticamente ROI%, net profit, payback period.
    """
    return FinanceService.update_roi_tracking(db, roi_id, request)


@router.get("/roi/summary")
def get_roi_summary(
    year: Optional[int] = Query(None, ge=2020, le=2050),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Riepilogo performance ROI"""
    return FinanceService.get_roi_summary(db, year, category)


# ============================================================================
# DASHBOARD & ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    year: int = Query(datetime.now().year, ge=2020, le=2050),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Statistiche dashboard finanziario.
    
    KPI principali, trend mensili, breakdown per categoria.
    """
    return FinanceService.get_dashboard_stats(db, year)


@router.get("/analytics/categories")
def get_category_analytics(
    year: int = Query(datetime.now().year, ge=2020, le=2050),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Analisi spese per categoria"""
    return FinanceService.get_category_analytics(db, year)


@router.get("/analytics/suppliers")
def get_supplier_analytics(
    year: int = Query(datetime.now().year, ge=2020, le=2050),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Top fornitori per volume spesa"""
    return FinanceService.get_supplier_analytics(db, year, limit)


@router.get("/analytics/payment-methods", response_model=List[PaymentMethodStatsResponse])
def get_payment_method_stats(
    year: int = Query(datetime.now().year, ge=2020, le=2050),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Distribuzione metodi di pagamento"""
    return FinanceService.get_payment_method_stats(db, year)


@router.get("/analytics/tax-deductibility", response_model=TaxDeductibilityResponse)
def get_tax_deductibility_summary(
    year: int = Query(datetime.now().year, ge=2020, le=2050),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Riepilogo deducibilità fiscale.
    
    Calcola totali deducibili, IVA recuperabile, stima risparmio fiscale.
    """
    return FinanceService.get_tax_deductibility_summary(db, year)


@router.get("/analytics/cashflow-forecast")
def get_cashflow_forecast(
    months: int = Query(12, ge=1, le=24, description="Mesi di previsione"),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Previsione cashflow basata su spese ricorrenti"""
    return FinanceService.get_cashflow_forecast(db, months)


# ============================================================================
# ALERTS & NOTIFICATIONS ENDPOINTS
# ============================================================================

@router.get("/alerts")
def get_finance_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None, regex="^(active|dismissed|resolved|snoozed)$"),
    severity: Optional[str] = Query(None, regex="^(low|medium|high|critical)$"),
    alert_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Lista alert finanziari attivi"""
    return FinanceService.get_finance_alerts(db, page, page_size, status, severity, alert_type)


@router.post("/alerts/{alert_id}/dismiss")
def dismiss_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Dismissi alert"""
    success = FinanceService.dismiss_alert(db, alert_id, admin.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert non trovato"
        )
    return {"message": "Alert dismisso"}


@router.post("/alerts/{alert_id}/snooze")
def snooze_alert(
    alert_id: int,
    hours: int = Query(..., ge=1, le=168, description="Ore di snooze"),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Posticipa alert per X ore"""
    success = FinanceService.snooze_alert(db, alert_id, hours)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert non trovato"
        )
    return {"message": f"Alert posticipato di {hours} ore"}


# ============================================================================
# EXPORT & REPORTS ENDPOINTS
# ============================================================================

@router.get("/export/expenses")
def export_expenses_csv(
    year: int = Query(datetime.now().year, ge=2020, le=2050),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Export spese in formato CSV"""
    return FinanceService.export_expenses_csv(db, year, category)


@router.get("/export/budget-report")
def export_budget_report_pdf(
    year: int = Query(datetime.now().year, ge=2020, le=2050),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Export report budget in PDF"""
    return FinanceService.export_budget_report_pdf(db, year)


@router.get("/export/roi-report")
def export_roi_report_pdf(
    year: int = Query(datetime.now().year, ge=2020, le=2050),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Export report ROI in PDF"""
    return FinanceService.export_roi_report_pdf(db, year, category)


@router.get("/export/tax-summary")
def export_tax_summary_pdf(
    year: int = Query(datetime.now().year, ge=2020, le=2050),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Export riepilogo fiscale per commercialista"""
    return FinanceService.export_tax_summary_pdf(db, year)
