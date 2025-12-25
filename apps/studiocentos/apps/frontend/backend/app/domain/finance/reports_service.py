"""
Finance Reports Service - Sistema report e export StudioCentOS
"""

from datetime import datetime, date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from io import BytesIO
import csv
import json

from .models import CompanyExpense, MonthlyBudget, ROITracking
from .schemas import ExpenseResponse, BudgetResponse, ROIResponse

import logging
logger = logging.getLogger(__name__)


class FinanceReportsService:
    """Service per report e export finanziari"""
    
    @staticmethod
    def generate_monthly_report(db: Session, year: int, month: int) -> Dict[str, Any]:
        """Genera report mensile completo"""
        
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
        
        # Spese del mese
        expenses = db.query(CompanyExpense).filter(
            and_(
                CompanyExpense.due_date >= start_date,
                CompanyExpense.due_date < end_date
            )
        ).all()
        
        # Budget del mese
        budgets = db.query(MonthlyBudget).filter(
            and_(
                MonthlyBudget.year == year,
                MonthlyBudget.month == month
            )
        ).all()
        
        # Statistiche
        total_expenses = sum(exp.amount for exp in expenses)
        total_budget = sum(budget.planned_amount for budget in budgets)
        paid_expenses = sum(exp.amount for exp in expenses if exp.status == 'paid')
        pending_expenses = sum(exp.amount for exp in expenses if exp.status == 'pending')
        
        return {
            "period": f"{month:02d}/{year}",
            "summary": {
                "total_expenses": float(total_expenses),
                "total_budget": float(total_budget),
                "paid_expenses": float(paid_expenses),
                "pending_expenses": float(pending_expenses),
                "budget_variance": float(total_expenses - total_budget),
                "budget_utilization": float((total_expenses / total_budget * 100) if total_budget > 0 else 0)
            },
            "expenses_count": len(expenses),
            "categories": FinanceReportsService._get_category_breakdown(expenses),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def export_expenses_csv(db: Session, year: int, category: Optional[str] = None) -> bytes:
        """Export spese in CSV"""
        
        query = db.query(CompanyExpense).filter(
            func.extract('year', CompanyExpense.due_date) == year
        )
        
        if category:
            query = query.filter(CompanyExpense.category == category)
        
        expenses = query.order_by(CompanyExpense.due_date).all()
        
        # Crea CSV
        output = BytesIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'ID', 'Titolo', 'Categoria', 'Importo', 'Valuta', 'Data Scadenza',
            'Status', 'Fornitore', 'Deducibile', 'Creato'
        ])
        
        # Dati
        for exp in expenses:
            writer.writerow([
                exp.id,
                exp.title,
                exp.category,
                float(exp.amount),
                exp.currency,
                exp.due_date.strftime('%Y-%m-%d'),
                exp.status,
                exp.supplier_name or '',
                'Sì' if exp.tax_deductible else 'No',
                exp.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        return output.getvalue()
    
    @staticmethod
    def _get_category_breakdown(expenses: List[CompanyExpense]) -> List[Dict[str, Any]]:
        """Breakdown per categoria"""
        
        categories = {}
        total = sum(exp.amount for exp in expenses)
        
        for exp in expenses:
            if exp.category not in categories:
                categories[exp.category] = {
                    "category": exp.category,
                    "amount": 0,
                    "count": 0
                }
            
            categories[exp.category]["amount"] += float(exp.amount)
            categories[exp.category]["count"] += 1
        
        # Aggiungi percentuali
        for cat in categories.values():
            cat["percentage"] = (cat["amount"] / float(total) * 100) if total > 0 else 0
        
        return list(categories.values())
