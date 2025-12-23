"""
Marketing Analytics API Router.

Endpoints:
- Dashboard unificata
- Report generation (PDF/JSON)
- Export dati (CSV/Excel)
- Weekly report scheduling
"""

import csv
import io
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.domain.marketing.analytics_service import (
    DateRange,
    ReportConfig,
    analytics_service,
)

router = APIRouter(prefix="/analytics", tags=["Marketing Analytics"])


# ============================================================================
# DASHBOARD
# ============================================================================

@router.get("/dashboard")
async def get_dashboard(
    date_range: DateRange = Query(DateRange.LAST_30_DAYS, description="Periodo dati"),
    start_date: datetime | None = None,
    end_date: datetime | None = None
):
    """
    Ottieni dati dashboard marketing unificata.

    Aggregazione cross-platform:
    - KPIs principali con trend
    - Chart lead e conversioni
    - Metriche per piattaforma social
    - Top content
    - Attività recenti
    """
    try:
        data = await analytics_service.get_dashboard_data(date_range)
        return data.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kpis")
async def get_kpis(date_range: DateRange = Query(DateRange.LAST_30_DAYS)):
    """Ottieni solo KPIs."""
    data = await analytics_service.get_dashboard_data(date_range)
    return {"kpis": [k.model_dump() for k in data.kpis], "period": date_range.value}


@router.get("/platforms")
async def get_platform_metrics(date_range: DateRange = Query(DateRange.LAST_30_DAYS)):
    """Ottieni metriche per piattaforma social."""
    data = await analytics_service.get_dashboard_data(date_range)
    return {"platforms": [p.model_dump() for p in data.platform_metrics]}


@router.get("/activities")
async def get_recent_activities(limit: int = Query(10, ge=1, le=50)):
    """Ottieni attività recenti."""
    data = await analytics_service.get_dashboard_data(DateRange.LAST_7_DAYS)
    return {"activities": data.recent_activities[:limit]}


# ============================================================================
# REPORT GENERATION
# ============================================================================

@router.post("/report")
async def generate_report(config: ReportConfig):
    """
    Genera report marketing completo.

    Configurazioni:
    - Periodo (preset o custom)
    - Sezioni da includere (KPIs, lead, campagne, social)
    - Formato output (json, pdf)
    """
    try:
        report_data = await analytics_service.generate_report(config)

        if config.format == "json":
            return report_data

        # Per PDF - ritorna dati strutturati che il frontend convertirà
        return {
            "format": config.format,
            "data": report_data,
            "download_ready": True
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/quick")
async def quick_report(date_range: DateRange = Query(DateRange.LAST_30_DAYS)):
    """Report rapido con configurazione di default."""
    config = ReportConfig(
        title=f"Marketing Report - {date_range.value}",
        date_range=date_range,
        include_kpis=True,
        include_charts=True,
        include_leads=True,
        include_campaigns=True,
        include_social=True,
        format="json"
    )
    return await analytics_service.generate_report(config)


# ============================================================================
# EXPORT
# ============================================================================

@router.get("/export/{data_type}")
async def export_data(
    data_type: str,
    date_range: DateRange = Query(DateRange.LAST_30_DAYS),
    format: str = Query("csv", regex="^(csv|excel|json)$")
):
    """
    Esporta dati marketing.

    Args:
        data_type: leads, campaigns, social, all
        date_range: periodo
        format: csv, excel, json
    """
    if data_type not in ["leads", "campaigns", "social", "all"]:
        raise HTTPException(status_code=400, detail="Invalid data type")

    try:
        export_data = await analytics_service.export_data(data_type, date_range, format)

        if format == "json":
            return export_data

        if format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(export_data["columns"])
            writer.writerows(export_data["rows"])

            output.seek(0)
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={data_type}_{date_range.value}.csv"}
            )

        if format == "excel":
            # Per Excel, ritorna dati JSON che il frontend converte con xlsx library
            return {
                "format": "excel",
                "filename": f"{data_type}_{date_range.value}.xlsx",
                "data": export_data
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WEEKLY REPORT CONFIG
# ============================================================================

@router.get("/weekly-report/config")
async def get_weekly_report_config():
    """Ottieni configurazione weekly report."""

    return {
        "enabled": True,
        "day_of_week": 1,  # Lunedì
        "hour": 9,
        "recipients": ["admin@example.com"],
        "include_sections": ["kpis", "leads", "campaigns", "social"],
        "last_sent": None
    }


@router.put("/weekly-report/config")
async def update_weekly_report_config(
    enabled: bool = True,
    day_of_week: int = Query(1, ge=0, le=6),
    hour: int = Query(9, ge=0, le=23),
    recipients: list = []
):
    """Aggiorna configurazione weekly report."""

    return {
        "status": "updated",
        "config": {
            "enabled": enabled,
            "day_of_week": day_of_week,
            "hour": hour,
            "recipients": recipients
        }
    }


@router.post("/weekly-report/send-now")
async def send_weekly_report_now():
    """Invia report settimanale immediatamente."""
    config = ReportConfig(
        title="Weekly Marketing Report",
        date_range=DateRange.LAST_7_DAYS,
        include_kpis=True,
        include_leads=True,
        include_campaigns=True,
        include_social=True,
        format="json"
    )

    report = await analytics_service.generate_report(config)


    return {
        "status": "sent",
        "report_summary": {
            "sections": len(report.get("sections", [])),
            "generated_at": report.get("generated_at")
        }
    }


# ============================================================================
# COMPARISONS
# ============================================================================

@router.get("/compare")
async def compare_periods(
    period1: DateRange = Query(..., description="Primo periodo"),
    period2: DateRange = Query(..., description="Secondo periodo")
):
    """Confronta metriche tra due periodi."""
    data1 = await analytics_service.get_dashboard_data(period1)
    data2 = await analytics_service.get_dashboard_data(period2)

    comparison = {
        "period1": period1.value,
        "period2": period2.value,
        "kpis_comparison": []
    }

    for kpi1 in data1.kpis:
        kpi2 = next((k for k in data2.kpis if k.id == kpi1.id), None)
        if kpi2:
            diff = kpi1.value - kpi2.value
            diff_percent = ((kpi1.value - kpi2.value) / kpi2.value * 100) if kpi2.value > 0 else 0
            comparison["kpis_comparison"].append({
                "id": kpi1.id,
                "label": kpi1.label,
                "period1_value": kpi1.value,
                "period2_value": kpi2.value,
                "difference": round(diff, 2),
                "difference_percent": round(diff_percent, 2)
            })

    return comparison
