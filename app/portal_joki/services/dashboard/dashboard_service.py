"""
Portal Joki - Dashboard Service

Service untuk data dashboard portal joki.
"""

from typing import Optional, List, Dict, Any
from datetime import date, datetime, timedelta

from app.portal_joki.repositories.dashboard.dashboard_repo import (
    PortalJokiDashboardRepository,
)
from app.utils.logger import log


# ==========================================================
# RESULT CLASS
# ==========================================================
class DashboardResult:
    """
    Result object untuk dashboard data.
    """
    
    def __init__(
        self,
        summary: Dict[str, Any],
        today: List[Dict[str, Any]],
        calendar: List[Dict[str, Any]],
        recent_uploads: List[Dict[str, Any]],
        progress: Dict[str, Any],
        top_joki: Optional[List[Dict[str, Any]]] = None,
        latest_review: Optional[List[Dict[str, Any]]] = None,
        weekly_stats: Optional[Dict[str, Any]] = None,
        additional_data: Optional[Dict[str, Any]] = None,
    ):
        self.summary = summary or {}
        self.today = today or []
        self.calendar = calendar or []
        self.recent_uploads = recent_uploads or []
        self.progress = progress or {}
        self.top_joki = top_joki or []
        self.latest_review = latest_review or []
        self.weekly_stats = weekly_stats or {}
        self.additional_data = additional_data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "summary": self.summary,
            "today": self.today,
            "calendar": self.calendar,
            "recent_uploads": self.recent_uploads,
            "progress": self.progress,
            "top_joki": self.top_joki,
            "latest_review": self.latest_review,
            "weekly_stats": self.weekly_stats,
            "additional_data": self.additional_data,
        }
    
    @property
    def total_today(self) -> int:
        """Total tugas hari ini."""
        return len(self.today)
    
    @property
    def completed_today(self) -> int:
        """Total tugas selesai hari ini."""
        return sum(1 for item in self.today if item.get("status") == 3)
    
    @property
    def pending_today(self) -> int:
        """Total tugas pending hari ini."""
        return sum(1 for item in self.today if item.get("status") == 0)
    
    @property
    def completion_rate(self) -> float:
        """Completion rate dari progress."""
        return self.progress.get("persen", 0.0)
    
    @property
    def total_tasks(self) -> int:
        """Total tugas dari summary."""
        return self.summary.get("total", 0)
    
    @property
    def total_completed(self) -> int:
        """Total tugas selesai dari summary."""
        return self.summary.get("selesai", 0)


# ==========================================================
# DASHBOARD SERVICE
# ==========================================================
class PortalJokiDashboardService:
    """
    Service Dashboard Portal Joki.
    
    Menyediakan fungsi untuk:
    - Joki dashboard
    - Admin dashboard
    - Weekly stats
    - Custom dashboard queries
    """

    # ==========================================================
    # JOKI DASHBOARD
    # ==========================================================

    @staticmethod
    def execute(
        joki_id: int,
        include_weekly: bool = True,
        include_details: bool = True,
    ) -> DashboardResult:
        """
        Execute dashboard untuk joki.
        
        Args:
            joki_id: ID joki
            include_weekly: Sertakan statistik mingguan
            include_details: Sertakan detail tambahan
            
        Returns:
            DashboardResult: Data dashboard joki
        """
        log.info(f"Execute dashboard for joki: {joki_id}")
        
        try:
            # Get all dashboard data
            summary = PortalJokiDashboardRepository.get_summary(joki_id)
            today = PortalJokiDashboardRepository.get_today_tasks(joki_id)
            calendar = PortalJokiDashboardRepository.get_calendar(joki_id)
            recent_uploads = PortalJokiDashboardRepository.get_recent_uploads(joki_id)
            progress = PortalJokiDashboardRepository.get_progress(joki_id)
            
            # Optional weekly stats
            weekly_stats = {}
            if include_weekly:
                weekly_stats = PortalJokiDashboardRepository.get_weekly_stats(joki_id)
            
            # Optional additional data
            additional_data = {}
            if include_details:
                additional_data = {
                    "upload_count": len(recent_uploads),
                    "today_count": len(today),
                    "calendar_days": len(calendar),
                }
            
            log.debug(f"Dashboard data: summary={summary.get('total', 0)}, today={len(today)}")
            
            return DashboardResult(
                summary=summary,
                today=today,
                calendar=calendar,
                recent_uploads=recent_uploads,
                progress=progress,
                weekly_stats=weekly_stats,
                additional_data=additional_data,
            )
            
        except Exception as e:
            log.error(f"Failed to execute dashboard for joki {joki_id}: {e}")
            # Return empty result
            return DashboardResult({}, [], [], [], {})

    # ==========================================================
    # JOKI - DETAILED
    # ==========================================================

    @staticmethod
    def execute_detailed(
        joki_id: int,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Execute detailed dashboard untuk joki.
        
        Args:
            joki_id: ID joki
            days: Jumlah hari untuk calendar
            
        Returns:
            dict: Detailed dashboard data
        """
        log.info(f"Execute detailed dashboard for joki: {joki_id}, days={days}")
        
        try:
            result = PortalJokiDashboardService.execute(joki_id)
            
            # Get detailed calendar
            calendar_detail = PortalJokiDashboardRepository.get_calendar(
                joki_id, days=days
            )
            
            # Get performance
            performance = PortalJokiDashboardRepository.get_joki_performance(
                joki_id, days=days
            )
            
            # Get daily activity
            daily_activity = PortalJokiDashboardRepository.get_daily_activity(
                joki_id, days=7
            )
            
            return {
                "summary": result.summary,
                "today": result.today,
                "calendar": calendar_detail,
                "recent_uploads": result.recent_uploads,
                "progress": result.progress,
                "weekly_stats": result.weekly_stats,
                "performance": performance,
                "daily_activity": daily_activity,
            }
            
        except Exception as e:
            log.error(f"Failed to execute detailed dashboard for joki {joki_id}: {e}")
            return {}

    # ==========================================================
    # ADMIN DASHBOARD
    # ==========================================================

    @staticmethod
    def execute_admin(
        include_top: bool = True,
        include_review: bool = True,
    ) -> DashboardResult:
        """
        Execute dashboard untuk admin.
        
        Args:
            include_top: Sertakan top joki
            include_review: Sertakan latest review
            
        Returns:
            DashboardResult: Data dashboard admin
        """
        log.info("Execute admin dashboard")
        
        try:
            # Get all dashboard data
            summary = PortalJokiDashboardRepository.get_admin_summary()
            today = PortalJokiDashboardRepository.get_admin_today_tasks()
            calendar = PortalJokiDashboardRepository.get_admin_calendar()
            recent_uploads = PortalJokiDashboardRepository.get_admin_recent_uploads()
            progress = PortalJokiDashboardRepository.get_admin_progress()
            
            # Optional data
            top_joki = []
            latest_review = []
            
            if include_top:
                top_joki = PortalJokiDashboardRepository.get_admin_top_joki()
            
            if include_review:
                latest_review = PortalJokiDashboardRepository.get_admin_latest_review()
            
            # Additional stats
            additional_data = {
                "total_joki": summary.get("total_joki", 0),
                "total_penugasan": summary.get("total_penugasan", 0),
                "total_today": len(today),
                "total_uploads": len(recent_uploads),
            }
            
            log.debug(f"Admin dashboard: summary={summary.get('total_penugasan', 0)}, today={len(today)}")
            
            return DashboardResult(
                summary=summary,
                today=today,
                calendar=calendar,
                recent_uploads=recent_uploads,
                progress=progress,
                top_joki=top_joki,
                latest_review=latest_review,
                additional_data=additional_data,
            )
            
        except Exception as e:
            log.error(f"Failed to execute admin dashboard: {e}")
            return DashboardResult({}, [], [], [], {})

    # ==========================================================
    # ADMIN - DETAILED
    # ==========================================================

    @staticmethod
    def execute_admin_detailed(
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Execute detailed dashboard untuk admin.
        
        Args:
            days: Jumlah hari untuk calendar
            
        Returns:
            dict: Detailed dashboard data
        """
        log.info(f"Execute detailed admin dashboard: days={days}")
        
        try:
            result = PortalJokiDashboardService.execute_admin()
            
            # Get detailed calendar
            calendar_detail = PortalJokiDashboardRepository.get_admin_calendar()
            
            # Get top joki with more details
            top_joki = PortalJokiDashboardRepository.get_admin_top_joki(limit=10)
            
            return {
                "summary": result.summary,
                "today": result.today,
                "calendar": calendar_detail,
                "recent_uploads": result.recent_uploads,
                "progress": result.progress,
                "top_joki": top_joki,
                "latest_review": result.latest_review,
                "additional_data": result.additional_data,
            }
            
        except Exception as e:
            log.error(f"Failed to execute detailed admin dashboard: {e}")
            return {}

    # ==========================================================
    # QUICK STATS
    # ==========================================================

    @staticmethod
    def get_quick_stats(joki_id: int) -> Dict[str, Any]:
        """
        Mendapatkan quick stats untuk joki.
        
        Args:
            joki_id: ID joki
            
        Returns:
            dict: Quick stats
        """
        log.debug(f"Get quick stats for joki: {joki_id}")
        
        try:
            summary = PortalJokiDashboardRepository.get_summary(joki_id)
            progress = PortalJokiDashboardRepository.get_progress(joki_id)
            
            return {
                "total_tasks": summary.get("total", 0),
                "completed": summary.get("selesai", 0),
                "pending": summary.get("pending", 0),
                "revision": summary.get("revisi", 0),
                "completion_rate": progress.get("persen", 0.0),
                "today_tasks": len(PortalJokiDashboardRepository.get_today_tasks(joki_id)),
            }
            
        except Exception as e:
            log.error(f"Failed to get quick stats for joki {joki_id}: {e}")
            return {}

    @staticmethod
    def get_admin_quick_stats() -> Dict[str, Any]:
        """
        Mendapatkan quick stats untuk admin.
        
        Returns:
            dict: Quick stats admin
        """
        log.debug("Get admin quick stats")
        
        try:
            summary = PortalJokiDashboardRepository.get_admin_summary()
            progress = PortalJokiDashboardRepository.get_admin_progress()
            today = PortalJokiDashboardRepository.get_admin_today_tasks()
            
            return {
                "total_joki": summary.get("total_joki", 0),
                "total_tasks": summary.get("total_penugasan", 0),
                "completed": summary.get("selesai", 0),
                "pending": summary.get("pending", 0),
                "revision": summary.get("revisi", 0),
                "completion_rate": progress.get("persen", 0.0),
                "today_tasks": len(today),
            }
            
        except Exception as e:
            log.error(f"Failed to get admin quick stats: {e}")
            return {}

    # ==========================================================
    # CHART DATA
    # ==========================================================

    @staticmethod
    def get_chart_data(
        joki_id: Optional[int] = None,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Mendapatkan data untuk chart.
        
        Args:
            joki_id: ID joki (opsional, untuk admin jika None)
            days: Jumlah hari
            
        Returns:
            dict: Data chart
        """
        log.info(f"Get chart data: joki_id={joki_id}, days={days}")
        
        try:
            if joki_id:
                calendar = PortalJokiDashboardRepository.get_calendar(joki_id, days)
            else:
                calendar = PortalJokiDashboardRepository.get_admin_calendar()
            
            # Prepare chart data
            dates = []
            totals = []
            completed = []
            pending = []
            
            for day in calendar:
                dates.append(day.get("tanggal").isoformat() if day.get("tanggal") else "")
                totals.append(day.get("total", 0))
                completed.append(day.get("selesai", 0))
                pending.append(day.get("pending", 0))
            
            return {
                "labels": dates,
                "datasets": {
                    "total": totals,
                    "completed": completed,
                    "pending": pending,
                },
                "summary": {
                    "total": sum(totals),
                    "completed": sum(completed),
                    "pending": sum(pending),
                    "days": len(dates),
                }
            }
            
        except Exception as e:
            log.error(f"Failed to get chart data: {e}")
            return {
                "labels": [],
                "datasets": {"total": [], "completed": [], "pending": []},
                "summary": {"total": 0, "completed": 0, "pending": 0, "days": 0},
            }


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================
dashboard_service = PortalJokiDashboardService()