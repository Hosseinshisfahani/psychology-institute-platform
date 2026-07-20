import logging
import secrets
from dataclasses import dataclass
from typing import Any, Optional

import requests
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password

logger = logging.getLogger(__name__)


@dataclass
class SmsSendResult:
    ok: bool
    message_id: Optional[str] = None
    error_code: Optional[str] = None
    raw: Optional[Any] = None


def generate_otp_code(length: int = 6) -> str:
    digits = "0123456789"
    return "".join(secrets.choice(digits) for _ in range(length))


def hash_otp(code: str) -> str:
    return make_password(code)


def verify_otp(code: str, code_hash: str) -> bool:
    return check_password(code, code_hash)


def _mask_phone(phone: str) -> str:
    if not phone or len(phone) < 4:
        return "***"
    return f"{phone[:4]}***{phone[-2:]}"


def _send_url() -> str:
    base = getattr(settings, "SEPAHANGOSTAR_API_BASE", "https://api.sepahansms.com").rstrip("/")
    return f"{base}/api/Sms/Send"


def _normalize_phone(phone: str) -> str:
    phone = str(phone).replace("+98", "0").replace("0098", "0").replace("-", "").replace(" ", "").strip()
    if not phone.startswith("0"):
        phone = "0" + phone
    return phone


def send_single_sms(*, to_phone: str, text: str) -> SmsSendResult:
    token = getattr(settings, "SEPAHANGOSTAR_API_TOKEN", "")
    sender = getattr(settings, "SEPAHANGOSTAR_SENDER_NUMBER", "")

    if not token or not sender:
        logger.error("SepahanGostar config missing (token/sender).")
        return SmsSendResult(
            ok=False,
            error_code="config_missing",
            raw={"token_set": bool(token), "sender_set": bool(sender)},
        )

    normalized_phone = _normalize_phone(to_phone)
    payload = {
        "smsText": text,
        "receiverNumbers": [normalized_phone],
        "senderNumber": sender,
    }
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(_send_url(), json=payload, headers=headers, timeout=15)
    except requests.RequestException as exc:
        logger.error("SepahanGostar request failed for %s: %s", _mask_phone(normalized_phone), str(exc))
        return SmsSendResult(ok=False, error_code="request_failed", raw=str(exc))

    try:
        data = response.json()
    except ValueError:
        data = {"raw_text": response.text}

    success = bool(data.get("isSuccess")) if isinstance(data, dict) else False

    if success:
        message_id = None
        value = data.get("value") if isinstance(data, dict) else None
        if isinstance(value, dict):
            ids = value.get("ids")
            if isinstance(ids, list) and ids:
                message_id = str(ids[0])

        logger.info("SepahanGostar SMS sent to %s (msg_id=%s)", _mask_phone(normalized_phone), message_id)
        return SmsSendResult(ok=True, message_id=message_id, raw=data)

    error_code = None
    if isinstance(data, dict):
        err = data.get("error")
        if isinstance(err, dict) and err.get("code") is not None:
            error_code = str(err.get("code"))

    logger.warning(
        "SepahanGostar SMS failed for %s (status=%s, error_code=%s)",
        _mask_phone(normalized_phone),
        response.status_code,
        error_code,
    )
    return SmsSendResult(ok=False, error_code=error_code or str(response.status_code), raw=data)


def send_otp_sms(phone: str, code: str) -> SmsSendResult:
    # Keep OTP generation/verification local in Django; provider only transports message.
    text = f"کد تایید شما: {code}"
    return send_single_sms(to_phone=phone, text=text)


def verify_otp_sms(phone: str, code: str) -> bool:
    # Not used in app-generated OTP flow.
    return False