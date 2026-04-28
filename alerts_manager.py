import time
import threading
import logging
from datetime import datetime
from storage_unit import get_db_connection

#  Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("alerts.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

#  Severity → urgency mapping
SEVERITY_CONFIG = {
    "HIGH":        {"color": "\033[91m", "notify": True,  "repeat_interval": 30},   # red
    "MEDIUM":      {"color": "\033[93m", "notify": True,  "repeat_interval": 60},   # yellow
    "LOW":         {"color": "\033[94m", "notify": False, "repeat_interval": 120},  # blue
    "NON VIOLENCE":{"color": "\033[92m", "notify": False, "repeat_interval": None}, # green
}
RESET_COLOR = "\033[0m"




class AlertManager:

    def __init__(self, cooldown_seconds: int = 60):
#Sets the minimum interval between repeated alerts from the same camera to prevent excessive notifications.
        self.cooldown_seconds = cooldown_seconds
        self._last_alert: dict[str, float] = {}
        self._lock = threading.Lock()
        logger.info("AlertsManager initialised (cooldown=%ds)", cooldown_seconds)


  #  Public API
    def send_alert(
        self,
        camera_url: str,
        severity: str,
        score: float,
        weapon_type: str = "none",
        frame_id: int = -1,
    ) -> bool:
        #Returns True if the alert was dispatched, False if suppressed by the cooldown guard.
        
        if severity == "NON VIOLENCE":
            return False  # never alert on clean frames
 
        if self._is_suppressed(camera_url, severity):
            logger.debug(
                "Alert suppressed for %s (cooldown active)", camera_url
            )
            return False
        timestamp = datetime.now()
 
        # 1 persist to db
        self._save_to_db(camera_url, severity, score, weapon_type, frame_id, timestamp)
 
        # 2 console or file log
        self._log_alert(camera_url, severity, score, weapon_type, frame_id, timestamp)
 
        # 3 Optional downstream notification (email, SMS)
        if SEVERITY_CONFIG[severity]["notify"]:
            self._dispatch_notification(camera_url, severity, score, weapon_type, timestamp)
 
        # 4 update cooldown 
        with self._lock:
            self._last_alert[camera_url] = time.time()
        return True 


    def get_recent_alerts(self, limit: int = 50) -> list[dict]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute((limit,))
        rows = cursor.fetchall()
        conn.close()
 
        keys = ("camera_url", "severity", "score", "weapon_type", "frame_id", "detected_at")
        return [dict(zip(keys, row)) for row in rows] 

    def get_alert_summary(self) -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute()
        rows = cursor.fetchall()
        conn.close()
 
        summary = {sev: 0 for sev in SEVERITY_CONFIG}
        for severity, count in rows:
            summary[severity] = count
        return summary

#  Internal helpers
    def _is_suppressed(self, camera_url: str, severity: str) -> bool:
        interval = SEVERITY_CONFIG[severity].get("repeat_interval") or self.cooldown_seconds
        with self._lock:
            last = self._last_alert.get(camera_url)
        if last is None:
            return False
        return (time.time() - last) < interval
    
    def _save_to_db(self,camera_url: str,severity: str,score: float,weapon_type: str,frame_id: int,timestamp: datetime,) -> None:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                (
                    camera_url,
                    severity,
                    round(score, 4),
                    weapon_type,
                    frame_id,
                    timestamp.isoformat(sep=" ", timespec="seconds"),
                ),
            )
            conn.commit()
            conn.close()
        except Exception as exc:
            logger.error("DB write failed for alert [%s]: %s", camera_url, exc)
        
        
    def _log_alert(self,camera_url: str,severity: str,score: float,weapon_type: str,frame_id: int,timestamp: datetime,) -> None:
        cfg = SEVERITY_CONFIG.get(severity, {})
        color = cfg.get("color", "")
        ts_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
 
        message = (
            f"{color}"
            f"[ALERT] {ts_str} | Severity: {severity:<12} | "
            f"Score: {score:.2f} | Weapon: {weapon_type:<10} | "
            f"Frame: {frame_id:>6} | Camera: {camera_url}"
            f"{RESET_COLOR}"
        )
        if severity == "HIGH":
            logger.warning(message)
        else:
            logger.info(message)
    
    def _dispatch_notification(self,camera_url: str,severity: str,score: float,weapon_type: str,timestamp: datetime,) -> None:
        logger.info(
            "NOTIFICATION dispatched → severity=%s camera=%s score=%.2f weapon=%s @ %s",
            severity,
            camera_url,
            score,
            weapon_type,
            timestamp.strftime("%H:%M:%S"),
        )
alerts_manager = AlertManager(cooldown_seconds=60)