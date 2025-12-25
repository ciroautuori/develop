"""
Finance Service - Business logic gestione finanziaria
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc, extract
from fastapi import HTTPException, status

from .models import (
    CompanyExpense, MonthlyBudget, ROITracking, ExpenseRecurrence, FinanceAlert
)
from .schemas import (
    CreateExpenseRequest, UpdateExpenseRequest, ExpenseResponse,
    CreateBudgetRequest, BudgetResponse, CreateROIRequest, UpdateROIRequest, ROIResponse,
    ExpenseTimelineResponse, BudgetOverviewResponse, DashboardStatsResponse,
    ExpenseFilters, BudgetFilters, ROIFilters, PaginatedExpensesResponse,
    CategoryStatsItem, PaymentMethodStatsResponse, TaxDeductibilityResponse
)


class FinanceService:
    """Service per gestione finanziaria StudioCentOS"""

    # ========================================================================
    # EXPENSE MANAGEMENT
    # ========================================================================

    @staticmethod
    def create_expense(
        db: Session,
        request: CreateExpenseRequest,
        created_by: int
    ) -> ExpenseResponse:
        """Crea nuova spesa"""

        # Calcola net_amount
        net_amount = request.amount
        if request.vat_rate and request.vat_rate > 0:
            net_amount = request.amount / (1 + (request.vat_rate / 100))

        expense = CompanyExpense(
            title=request.title,
            description=request.description,
            category=request.category.value,
            subcategory=request.subcategory,
            amount=request.amount,
            currency=request.currency,
            vat_rate=request.vat_rate,
            net_amount=net_amount,
            due_date=request.due_date,
            frequency=request.frequency.value if request.frequency != "one_time" else None,
            frequency_count=request.frequency_count,
            end_date=request.end_date,
            supplier_name=request.supplier_name,
            supplier_email=request.supplier_email,
            supplier_website=request.supplier_website,
            supplier_vat_id=request.supplier_vat_id,
            payment_method=request.payment_method,
            tax_deductible=request.tax_deductible,
            tax_percentage=request.tax_percentage,
            project_id=request.project_id,
            created_by=created_by
        )

        db.add(expense)
        db.commit()
        db.refresh(expense)

        # Crea ricorrenza se necessaria
        if request.frequency != "one_time":
            FinanceService._create_recurrence(db, expense, created_by)

        # Crea alert se scadenza vicina
        FinanceService._check_and_create_due_alert(db, expense)

        return ExpenseResponse.model_validate(expense)

    @staticmethod
    def get_expenses(
        db: Session,
        filters: ExpenseFilters,
        page: int = 1,
        page_size: int = 50,
        sort_by: str = "due_date",
        sort_order: str = "asc"
    ) -> PaginatedExpensesResponse:
        """Lista spese con filtri e paginazione"""

        query = db.query(CompanyExpense)

        # Applica filtri
        if filters.category:
            query = query.filter(CompanyExpense.category == filters.category)

        if filters.status:
            query = query.filter(CompanyExpense.status == filters.status)

        if filters.supplier_name:
            query = query.filter(
                CompanyExpense.supplier_name.ilike(f"%{filters.supplier_name}%")
            )

        if filters.date_from:
            query = query.filter(CompanyExpense.due_date >= filters.date_from)

        if filters.date_to:
            query = query.filter(CompanyExpense.due_date <= filters.date_to)

        if filters.amount_min:
            query = query.filter(CompanyExpense.amount >= filters.amount_min)

        if filters.amount_max:
            query = query.filter(CompanyExpense.amount <= filters.amount_max)

        if filters.is_overdue is not None:
            if filters.is_overdue:
                query = query.filter(
                    and_(
                        CompanyExpense.status == "pending",
                        CompanyExpense.due_date < date.today()
                    )
                )
            else:
                query = query.filter(
                    or_(
                        CompanyExpense.status != "pending",
                        CompanyExpense.due_date >= date.today()
                    )
                )

        if filters.tax_deductible is not None:
            query = query.filter(CompanyExpense.tax_deductible == filters.tax_deductible)

        if filters.project_id:
            query = query.filter(CompanyExpense.project_id == filters.project_id)

        # Count totale
        total = query.count()

        # Sorting
        if sort_by == "due_date":
            order_col = CompanyExpense.due_date
        elif sort_by == "amount":
            order_col = CompanyExpense.amount
        elif sort_by == "created_at":
            order_col = CompanyExpense.created_at
        else:
            order_col = CompanyExpense.due_date

        if sort_order == "desc":
            query = query.order_by(desc(order_col))
        else:
            query = query.order_by(asc(order_col))

        # Paginazione
        offset = (page - 1) * page_size
        expenses = query.offset(offset).limit(page_size).all()

        return PaginatedExpensesResponse(
            items=[ExpenseResponse.model_validate(exp) for exp in expenses],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )

    @staticmethod
    def update_expense(
        db: Session,
        expense_id: int,
        request: UpdateExpenseRequest,
        updated_by: int
    ) -> ExpenseResponse:
        """Aggiorna spesa esistente"""

        expense = db.query(CompanyExpense).filter(
            CompanyExpense.id == expense_id
        ).first()

        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Spesa non trovata"
            )

        # Aggiorna campi
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(expense, field, value)

        expense.updated_at = datetime.utcnow()

        # Ricalcola net_amount se amount o vat_rate sono cambiati
        if request.amount is not None or hasattr(request, 'vat_rate'):
            if expense.vat_rate and expense.vat_rate > 0:
                expense.net_amount = expense.amount / (1 + (expense.vat_rate / 100))
            else:
                expense.net_amount = expense.amount

        # Se pagata, marca come paid
        if request.payment_date and expense.status == "pending":
            expense.status = "paid"

        db.commit()
        db.refresh(expense)

        return ExpenseResponse.model_validate(expense)

    @staticmethod
    def delete_expense(db: Session, expense_id: int) -> bool:
        """Elimina una spesa esistente"""

        expense = db.query(CompanyExpense).filter(
            CompanyExpense.id == expense_id
        ).first()

        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Spesa non trovata"
            )

        # Elimina alert associati
        db.query(FinanceAlert).filter(
            FinanceAlert.expense_id == expense_id
        ).delete()

        # Elimina ricorrenza associata se esiste
        db.query(ExpenseRecurrence).filter(
            ExpenseRecurrence.id == expense.id  # Potrebbero esserci legami
        ).delete()

        db.delete(expense)
        db.commit()

        return True

    @staticmethod
    def get_expenses_timeline(db: Session, year: int) -> ExpenseTimelineResponse:
        """Ottieni timeline spese per anno"""

        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

        expenses = db.query(CompanyExpense).filter(
            and_(
                CompanyExpense.due_date >= start_date,
                CompanyExpense.due_date <= end_date
            )
        ).order_by(CompanyExpense.due_date).all()

        # Calcola totali
        total_year = sum(exp.amount for exp in expenses)
        total_pending = sum(exp.amount for exp in expenses if exp.status == "pending")
        total_paid = sum(exp.amount for exp in expenses if exp.status == "paid")

        # Conta upcoming e overdue
        today = date.today()
        upcoming_count = len([
            exp for exp in expenses
            if exp.status == "pending" and exp.due_date >= today and exp.due_date <= today + timedelta(days=30)
        ])
        overdue_count = len([
            exp for exp in expenses
            if exp.status == "pending" and exp.due_date < today
        ])

        return ExpenseTimelineResponse(
            year=year,
            total_year=total_year,
            total_pending=total_pending,
            total_paid=total_paid,
            upcoming_count=upcoming_count,
            overdue_count=overdue_count,
            expenses=[
                {
                    "id": exp.id,
                    "title": exp.title,
                    "amount": exp.amount,
                    "currency": exp.currency,
                    "due_date": exp.due_date,
                    "status": exp.status,
                    "category": exp.category,
                    "is_overdue": exp.is_overdue,
                    "days_until_due": exp.days_until_due
                }
                for exp in expenses
            ]
        )

    # ========================================================================
    # BUDGET MANAGEMENT
    # ========================================================================

    @staticmethod
    def create_budget(
        db: Session,
        request: CreateBudgetRequest,
        created_by: int
    ) -> BudgetResponse:
        """Crea nuovo budget mensile"""

        # Verifica se esiste già
        existing = db.query(MonthlyBudget).filter(
            and_(
                MonthlyBudget.year == request.year,
                MonthlyBudget.month == request.month,
                MonthlyBudget.category == request.category.value,
                MonthlyBudget.subcategory == request.subcategory
            )
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Budget per questo periodo già esistente"
            )

        budget = MonthlyBudget(
            year=request.year,
            month=request.month,
            category=request.category.value,
            subcategory=request.subcategory,
            planned_amount=request.planned_amount,
            currency=request.currency,
            notes=request.notes,
            alert_threshold=request.alert_threshold,
            created_by=created_by
        )

        db.add(budget)
        db.commit()
        db.refresh(budget)

        # Aggiorna actual_amount con spese esistenti
        FinanceService._update_budget_actual(db, budget)

        return BudgetResponse.model_validate(budget)

    @staticmethod
    def get_budget_overview(db: Session, year: int) -> BudgetOverviewResponse:
        """Overview budget vs actual per anno"""

        budgets = db.query(MonthlyBudget).filter(
            MonthlyBudget.year == year
        ).order_by(MonthlyBudget.month).all()

        # Raggruppa per mese
        monthly_data = {}
        for budget in budgets:
            month = budget.month
            if month not in monthly_data:
                monthly_data[month] = {
                    "month": month,
                    "month_name": date(year, month, 1).strftime("%B"),
                    "planned": Decimal('0'),
                    "actual": Decimal('0'),
                    "variance": Decimal('0'),
                    "variance_percentage": Decimal('0')
                }

            monthly_data[month]["planned"] += budget.planned_amount
            monthly_data[month]["actual"] += budget.actual_amount

        # Calcola varianze
        for month_data in monthly_data.values():
            if month_data["planned"] > 0:
                month_data["variance"] = month_data["actual"] - month_data["planned"]
                month_data["variance_percentage"] = (
                    (month_data["actual"] / month_data["planned"] - 1) * 100
                )

        # Calcola totali
        total_planned = sum(data["planned"] for data in monthly_data.values())
        total_actual = sum(data["actual"] for data in monthly_data.values())
        total_variance = total_actual - total_planned
        monthly_average = total_planned / 12 if total_planned > 0 else Decimal('0')

        return BudgetOverviewResponse(
            year=year,
            monthly_average=monthly_average,
            total_planned=total_planned,
            total_actual=total_actual,
            total_variance=total_variance,
            monthly_data=list(monthly_data.values())
        )

    # ========================================================================
    # ROI TRACKING
    # ========================================================================

    @staticmethod
    def create_roi_tracking(
        db: Session,
        request: CreateROIRequest,
        created_by: int
    ) -> ROIResponse:
        """Crea nuovo ROI tracking"""

        roi = ROITracking(
            investment_name=request.investment_name,
            investment_description=request.investment_description,
            investment_category=request.investment_category.value,
            investment_amount=request.investment_amount,
            expected_return=request.expected_return,
            currency=request.currency,
            investment_date=request.investment_date,
            expected_return_date=request.expected_return_date,
            return_period_months=request.return_period_months,
            success_criteria=request.success_criteria,
            expense_id=request.expense_id,
            created_by=created_by,
            measurement_start_date=request.investment_date
        )

        db.add(roi)
        db.commit()
        db.refresh(roi)

        return ROIResponse.model_validate(roi)

    @staticmethod
    def update_roi_tracking(
        db: Session,
        roi_id: int,
        request: UpdateROIRequest
    ) -> ROIResponse:
        """Aggiorna ROI tracking"""

        roi = db.query(ROITracking).filter(ROITracking.id == roi_id).first()

        if not roi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ROI tracking non trovato"
            )

        # Aggiorna campi
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(roi, field, value)

        roi.updated_at = datetime.utcnow()

        # Ricalcola metriche
        if request.actual_return is not None:
            roi.roi_percentage = roi.roi_calculated

            # Calcola break even date se profittevole
            if roi.actual_return > roi.investment_amount:
                days_to_break_even = (
                    roi.investment_amount / roi.actual_return * roi.days_active
                )
                roi.break_even_date = roi.investment_date + timedelta(days=int(days_to_break_even))

        db.commit()
        db.refresh(roi)

        return ROIResponse.model_validate(roi)

    # ========================================================================
    # DASHBOARD & ANALYTICS
    # ========================================================================

    @staticmethod
    def get_dashboard_stats(db: Session, year: int) -> DashboardStatsResponse:
        """Statistiche dashboard finanziario"""

        # Totali anno
        total_expenses = db.query(func.sum(CompanyExpense.amount)).filter(
            extract('year', CompanyExpense.due_date) == year
        ).scalar() or Decimal('0')

        total_budget = db.query(func.sum(MonthlyBudget.planned_amount)).filter(
            MonthlyBudget.year == year
        ).scalar() or Decimal('0')

        # Alert attivi
        active_alerts = db.query(FinanceAlert).filter(
            FinanceAlert.status == "active"
        ).count()

        # Spese scadute
        overdue_expenses = db.query(CompanyExpense).filter(
            and_(
                CompanyExpense.status == "pending",
                CompanyExpense.due_date < date.today()
            )
        ).count()

        # ROI investimenti
        roi_investments = db.query(ROITracking).filter(
            ROITracking.status == "active"
        ).count()

        # ROI medio
        avg_roi = db.query(func.avg(ROITracking.roi_percentage)).filter(
            ROITracking.status.in_(["active", "completed"])
        ).scalar() or Decimal('0')

        # Statistiche per categoria
        category_stats = db.query(
            CompanyExpense.category,
            func.sum(CompanyExpense.amount).label('total_amount'),
            func.count(CompanyExpense.id).label('count')
        ).filter(
            extract('year', CompanyExpense.due_date) == year
        ).group_by(CompanyExpense.category).all()

        total_for_percentage = sum(stat.total_amount for stat in category_stats)

        categories_list = [
            CategoryStatsItem(
                category=stat.category,
                total_amount=stat.total_amount,
                count=stat.count,
                percentage=(stat.total_amount / total_for_percentage * 100) if total_for_percentage > 0 else 0
            )
            for stat in category_stats
        ]

        # Trend mensile
        monthly_trend = []
        for month in range(1, 13):
            month_expenses = db.query(func.sum(CompanyExpense.amount)).filter(
                and_(
                    extract('year', CompanyExpense.due_date) == year,
                    extract('month', CompanyExpense.due_date) == month
                )
            ).scalar() or Decimal('0')

            month_budget = db.query(func.sum(MonthlyBudget.planned_amount)).filter(
                and_(
                    MonthlyBudget.year == year,
                    MonthlyBudget.month == month
                )
            ).scalar() or Decimal('0')

            monthly_trend.append({
                "month": month,
                "month_name": date(year, month, 1).strftime("%B"),
                "expenses": float(month_expenses),
                "budget": float(month_budget)
            })

        return DashboardStatsResponse(
            total_expenses_year=total_expenses,
            total_budget_year=total_budget,
            active_alerts=active_alerts,
            overdue_expenses=overdue_expenses,
            roi_investments=roi_investments,
            avg_roi_percentage=avg_roi,
            categories_stats=categories_list,
            monthly_trend=monthly_trend
        )

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    @staticmethod
    def _create_recurrence(db: Session, expense: CompanyExpense, created_by: int):
        """Crea ricorrenza per spesa"""

        recurrence = ExpenseRecurrence(
            title_template=expense.title,
            description_template=expense.description,
            category=expense.category,
            subcategory=expense.subcategory,
            amount=expense.amount,
            currency=expense.currency,
            frequency=expense.frequency,
            frequency_count=expense.frequency_count,
            start_date=expense.due_date,
            end_date=expense.end_date,
            supplier_name=expense.supplier_name,
            supplier_email=expense.supplier_email,
            payment_method=expense.payment_method,
            next_generation_date=FinanceService._calculate_next_recurrence_date(
                expense.due_date, expense.frequency, expense.frequency_count
            ),
            created_by=created_by
        )

        db.add(recurrence)
        db.commit()

    @staticmethod
    def _calculate_next_recurrence_date(
        current_date: date,
        frequency: str,
        frequency_count: int
    ) -> date:
        """Calcola prossima data ricorrenza"""

        if frequency == "monthly":
            next_date = current_date + timedelta(days=30 * frequency_count)
        elif frequency == "quarterly":
            next_date = current_date + timedelta(days=90 * frequency_count)
        elif frequency == "yearly":
            next_date = current_date + timedelta(days=365 * frequency_count)
        else:
            next_date = current_date

        return next_date

    @staticmethod
    def _check_and_create_due_alert(db: Session, expense: CompanyExpense):
        """Crea alert se scadenza vicina"""

        days_until_due = (expense.due_date - date.today()).days

        if days_until_due <= 7 and expense.status == "pending":
            alert = FinanceAlert(
                alert_type="expense_due",
                expense_id=expense.id,
                title=f"Scadenza pagamento: {expense.title}",
                message=f"La spesa '{expense.title}' di €{expense.amount} scade il {expense.due_date.strftime('%d/%m/%Y')}",
                severity="high" if days_until_due <= 3 else "medium",
                trigger_date=datetime.utcnow(),
                due_date=datetime.combine(expense.due_date, datetime.min.time())
            )

            db.add(alert)
            db.commit()

    @staticmethod
    def _update_budget_actual(db: Session, budget: MonthlyBudget):
        """Aggiorna actual_amount del budget"""

        start_date = date(budget.year, budget.month, 1)
        if budget.month == 12:
            end_date = date(budget.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(budget.year, budget.month + 1, 1) - timedelta(days=1)

        actual_amount = db.query(func.sum(CompanyExpense.amount)).filter(
            and_(
                CompanyExpense.category == budget.category,
                CompanyExpense.due_date >= start_date,
                CompanyExpense.due_date <= end_date,
                CompanyExpense.status.in_(["paid", "pending"])
            )
        ).scalar() or Decimal('0')

        budget.actual_amount = actual_amount
        budget.variance_amount = actual_amount - budget.planned_amount

        if budget.planned_amount > 0:
            budget.variance_percentage = (
                (actual_amount / budget.planned_amount - 1) * 100
            )

        db.commit()
