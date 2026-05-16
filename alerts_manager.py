import time
import threading
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import mysql.connector
from storage_unit import get_db_connection, save_violence_event


WS_ENABLED = True   
WS_PORT    = 8765
EMAIL_ENABLED   = True  
EMAIL_SENDER    = "fager1029g@gmail.com"   
EMAIL_PASSWORD  = "sqgb hphz kqdc chmv"      
EMAIL_RECEIVERS = [                        
    "fajralinajmi@gmail.com",
    # "security@example.com",             
]


SEVERITY_CONFIG = {
    "HIGH":         {"color": "\033[91m", "notify": True,  "repeat_interval": 30},
    "MEDIUM":       {"color": "\033[93m", "notify": True,  "repeat_interval": 60},
    "LOW":          {"color": "\033[94m", "notify": False, "repeat_interval": 120},
    "NON VIOLENCE": {"color": "\033[92m", "notify": False, "repeat_interval": None},
}
RESET_COLOR = "\033[0m"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("alerts.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)



class AlertsManager:

    def __init__(self, cooldown_seconds: int = 60):
        self.cooldown_seconds = cooldown_seconds
        self._last_alert: dict[str, float] = {}
        self._lock = threading.Lock()
        logger.info("AlertsManager initialised (cooldown=%ds | Email=True)", cooldown_seconds)


    def send_alert(self, camera_url, severity, score, weapon_type="none", frame_id=-1):
        if severity == "NON VIOLENCE":
            return False

        if self._is_suppressed(camera_url, severity):
            logger.debug("Alert suppressed for %s (cooldown active)", camera_url)
            return False

        timestamp = datetime.now()
        self._save_to_db(camera_url, severity, score, weapon_type, frame_id, timestamp)
        self._log_alert(camera_url, severity, score, weapon_type, frame_id, timestamp)

        if SEVERITY_CONFIG[severity]["notify"]:
            threading.Thread(
                target=self._send_email,
                args=(camera_url, severity, score, weapon_type, frame_id, timestamp),
                daemon=True
            ).start()

        with self._lock:
            self._last_alert[camera_url] = time.time()
        return True

    def get_recent_alerts(self, limit=50):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.stream_url, v.Severity, v.Confidence, 
                'weapon' as weapon_type, v.ID, v.Timestamp
            FROM violence_events v
            JOIN cameras c ON v.Camera_ID = c.camera_id
            ORDER BY v.Timestamp DESC
            LIMIT %s
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        keys = ("camera_url", "severity", "score", "weapon_type", "frame_id", "detected_at")
        return [dict(zip(keys, row)) for row in rows]
    
    def get_alert_summary(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Severity, COUNT(*) 
            FROM violence_events 
            GROUP BY Severity
        """)
        rows = cursor.fetchall()
        conn.close()
        summary = {sev: 0 for sev in SEVERITY_CONFIG}
        for sev, count in rows:
            if sev in summary:
                summary[sev] = count
        return summary



    def _send_email(self, camera_url, severity, score, weapon_type, frame_id, timestamp):
        try:
            subject = f"[{'🔴' if severity == 'HIGH' else '🟠'}] Violence Alert [{severity}] — {camera_url}"

            body_html = f"""
            <div dir="rtl" style="font-family:Arial,sans-serif;font-size:14px;max-width:600px">

              <div style="background:{'#c53030' if severity=='HIGH' else '#c05621'};
                          color:white;padding:16px 20px;border-radius:8px 8px 0 0">
                <h2 style="margin:0;font-size:18px">
                  {'🔴' if severity=='HIGH' else '🟠'} Violence Detection Alert — {severity}
                </h2>
              </div>
              <div style="border:1px solid #e2e8f0;border-top:none;
                          border-radius:0 0 8px 8px;padding:20px">
                <table style="width:100%;border-collapse:collapse;font-size:14px">
                  <tr style="background:#f7fafc">
                    <td style="padding:10px 14px;border:1px solid #e2e8f0;
                               font-weight:bold;width:35%">Camera Source</td>
                    <td style="padding:10px 14px;border:1px solid #e2e8f0">{camera_url}</td>
                  </tr>
                  <tr>
                    <td style="padding:10px 14px;border:1px solid #e2e8f0;font-weight:bold">Severity Level</td>
                    <td style="padding:10px 14px;border:1px solid #e2e8f0;
                               color:{'#c53030' if severity=='HIGH' else '#c05621'};
                               font-weight:bold">{severity}</td>
                  </tr>
                  <tr style="background:#f7fafc">
                    <td style="padding:10px 14px;border:1px solid #e2e8f0;font-weight:bold">Analysis Result</td>
                    <td style="padding:10px 14px;border:1px solid #e2e8f0">{score:.1%}</td>
                  </tr>
                  <tr>
                    <td style="padding:10px 14px;border:1px solid #e2e8f0;font-weight:bold">Detected Weapon</td>
                    <td style="padding:10px 14px;border:1px solid #e2e8f0">{weapon_type}</td>
                  </tr>
                  <tr style="background:#f7fafc">
                    <td style="padding:10px 14px;border:1px solid #e2e8f0;font-weight:bold">Frame ID</td>
                    <td style="padding:10px 14px;border:1px solid #e2e8f0">{frame_id}</td>
                  </tr>
                  <tr>
                    <td style="padding:10px 14px;border:1px solid #e2e8f0;font-weight:bold">Detection Time</td>
                    <td style="padding:10px 14px;border:1px solid #e2e8f0">
                      {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
                    </td>
                  </tr>
                </table>
                <p style="margin-top:16px;font-size:12px;color:#718096">
                  This alert was automatically sent from the violence detection system.
                </p>
              </div>
            </div>
            """

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"]    = EMAIL_SENDER
            msg["To"]      = ", ".join(EMAIL_RECEIVERS)
            msg.attach(MIMEText(body_html, "html", "utf-8"))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.sendmail(EMAIL_SENDER, EMAIL_RECEIVERS, msg.as_string())

            logger.info("Email sent → %s | severity=%s", EMAIL_RECEIVERS, severity)

        except smtplib.SMTPAuthenticationError:
            logger.error("Email: Authentication error — please check EMAIL_SENDER and EMAIL_PASSWORD")
        except smtplib.SMTPException as e:
            logger.error("Email SMTP error: %s", e)
        except Exception as e:
            logger.error("Email error: %s", e)


    def _is_suppressed(self, camera_url, severity):
        interval = SEVERITY_CONFIG[severity].get("repeat_interval") or self.cooldown_seconds
        with self._lock:
            last = self._last_alert.get(camera_url)
        if last is None:
            return False
        return (time.time() - last) < interval

    def _save_to_db(self, camera_url, severity, score, weapon_type, frame_id, timestamp):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE violence_events
                SET Severity = %s, Confidence = %s
                WHERE Camera_ID = (
                    SELECT camera_id FROM cameras
                    WHERE stream_url = %s
                    LIMIT 1
                )
                ORDER BY Timestamp DESC
                LIMIT 1
            """, (
                severity,
                f"{score:.0%}",
                camera_url
            ))
            conn.commit()
            conn.close()
        except Exception as exc:
            logger.error("DB write failed: %s", exc)

    def _log_alert(self, camera_url, severity, score, weapon_type, frame_id, timestamp):
        color = SEVERITY_CONFIG.get(severity, {}).get("color", "")
        msg = (
            f"{color}[ALERT] {timestamp:%Y-%m-%d %H:%M:%S} | "
            f"Severity: {severity:<12} | Score: {score:.2f} | "
            f"Weapon: {weapon_type:<10} | Frame: {frame_id:>6} | Camera: {camera_url}{RESET_COLOR}"
        )
        logger.warning(msg) if severity == "HIGH" else logger.info(msg)

alerts_manager = AlertsManager(cooldown_seconds=60)