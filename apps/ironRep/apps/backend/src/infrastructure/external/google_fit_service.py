"""
Google Fit Service - Biometric data sync from Google Fit.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


class GoogleFitService:
    """Google Fit API for biometric data."""

    def __init__(self, credentials: Credentials):
        self.credentials = credentials
        self.service = build("fitness", "v1", credentials=credentials)

    def _nanoseconds_to_datetime(self, nanos: int) -> datetime:
        return datetime.fromtimestamp(nanos / 1_000_000_000)

    def _datetime_to_nanoseconds(self, dt: datetime) -> int:
        return int(dt.timestamp() * 1_000_000_000)

    def get_weight_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get weight measurements from Google Fit."""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        dataset_id = f"{self._datetime_to_nanoseconds(start_time)}-{self._datetime_to_nanoseconds(end_time)}"

        try:
            response = self.service.users().dataSources().datasets().get(
                userId="me", dataSourceId="derived:com.google.weight:com.google.android.gms:merge_weight",
                datasetId=dataset_id,
            ).execute()

            weights = []
            for point in response.get("point", []):
                weight_kg = point.get("value", [{}])[0].get("fpVal", 0)
                if weight_kg > 0:
                    weights.append({
                        "date": self._nanoseconds_to_datetime(int(point.get("startTimeNanos", 0))).isoformat(),
                        "weight_kg": round(weight_kg, 1),
                    })
            return sorted(weights, key=lambda x: x["date"], reverse=True)
        except Exception as e:
            logger.error(f"Failed to get weight history: {e}")
            return []

    def get_daily_steps(self, date: Optional[datetime] = None) -> int:
        """Get step count for a specific day."""
        target_date = date or datetime.now()
        start_time = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)
        dataset_id = f"{self._datetime_to_nanoseconds(start_time)}-{self._datetime_to_nanoseconds(end_time)}"

        try:
            response = self.service.users().dataSources().datasets().get(
                userId="me", dataSourceId="derived:com.google.step_count.delta:com.google.android.gms:estimated_steps",
                datasetId=dataset_id,
            ).execute()
            return sum(point.get("value", [{}])[0].get("intVal", 0) for point in response.get("point", []))
        except Exception as e:
            logger.error(f"Failed to get daily steps: {e}")
            return 0

    def get_steps_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily step counts for multiple days."""
        return [{"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                 "steps": self.get_daily_steps(datetime.now() - timedelta(days=i))} for i in range(days)]

    def get_heart_rate_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get heart rate data from Google Fit."""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        dataset_id = f"{self._datetime_to_nanoseconds(start_time)}-{self._datetime_to_nanoseconds(end_time)}"

        try:
            response = self.service.users().dataSources().datasets().get(
                userId="me", dataSourceId="derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm",
                datasetId=dataset_id,
            ).execute()

            daily_hr: Dict[str, List[float]] = {}
            for point in response.get("point", []):
                hr = point.get("value", [{}])[0].get("fpVal", 0)
                if hr > 0:
                    date_str = self._nanoseconds_to_datetime(int(point.get("startTimeNanos", 0))).strftime("%Y-%m-%d")
                    daily_hr.setdefault(date_str, []).append(hr)

            return sorted([{"date": d, "avg_hr": round(sum(hrs) / len(hrs), 0), "min_hr": round(min(hrs), 0), "max_hr": round(max(hrs), 0)}
                          for d, hrs in daily_hr.items()], key=lambda x: x["date"], reverse=True)
        except Exception as e:
            logger.error(f"Failed to get heart rate history: {e}")
            return []

    def get_calories_burned(self, date: Optional[datetime] = None) -> int:
        """Get calories burned for a specific day."""
        target_date = date or datetime.now()
        start_time = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)
        dataset_id = f"{self._datetime_to_nanoseconds(start_time)}-{self._datetime_to_nanoseconds(end_time)}"

        try:
            response = self.service.users().dataSources().datasets().get(
                userId="me", dataSourceId="derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended",
                datasetId=dataset_id,
            ).execute()
            return int(sum(point.get("value", [{}])[0].get("fpVal", 0) for point in response.get("point", [])))
        except Exception as e:
            logger.error(f"Failed to get calories burned: {e}")
            return 0

    def sync_all_biometrics(self, days: int = 7) -> Dict[str, Any]:
        """Sync all available biometric data."""
        return {
            "weight": self.get_weight_history(days),
            "steps": self.get_steps_history(days),
            "heart_rate": self.get_heart_rate_history(days),
            "calories_today": self.get_calories_burned(),
            "synced_at": datetime.now().isoformat(),
        }
