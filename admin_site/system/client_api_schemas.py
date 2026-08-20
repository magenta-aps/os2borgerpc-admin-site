from ninja import Schema
from typing import Optional


class RegisterComputerSchema(Schema):
    mac: str
    name: str
    site: str
    configuration: dict
    client_key: str = ""


class SendStatusInfoSchema(Schema):
    pc_uid: str
    job_data: list
    client_key: str = ""


class GetInstructionsSchema(Schema):
    pc_uid: str
    jobs_received_check: bool = False
    client_key: str = ""


class ConfirmJobsReceiptSchema(Schema):
    pc_uid: str
    job_ids: list
    client_key: str = ""


class PushConfigKeysSchema(Schema):
    pc_uid: str
    config_dict: dict
    read_only: bool = False
    client_key: str = ""


class PushSecurityEventsSchema(Schema):
    pc_uid: str
    events_csv: list
    client_key: str = ""


### LOGIN ENDPOINTS - NOT CALLED BY JOBMANAGER ###


class CitizenLoginSchema(Schema):
    username: str
    password: str
    pc_uid: str
    prevent_dual_login: bool = False
    client_key: str = ""


class CitizenLogoutSchema(Schema):
    citizen_hash: str


class GeneralCitizenLoginSchema(Schema):
    pc_uid: str
    integration: str
    value_dict: dict
    client_key: str = ""


class GeneralCitizenLogoutSchema(Schema):
    citizen_hash: str
    log_id: str


class SmsLoginSchema(Schema):
    phone_number: str
    message: str
    pc_uid: str
    require_booking: bool = False
    pc_name: Optional[str] = None
    allow_idle_login: bool = False
    login_duration: Optional[int] = None
    quarantine_duration: Optional[int] = None
    unlimited_access: bool = False
    client_key: str = ""


class SmsLoginFinalizeSchema(Schema):
    phone_number: str
    pc_uid: str
    require_booking: bool
    save_log: bool
    allow_idle_login: bool = False
    login_duration: Optional[int] = None
    quarantine_duration: Optional[int] = None
    client_key: str = ""


class SmsLogoutSchema(Schema):
    citizen_hash: str
    log_id: str
