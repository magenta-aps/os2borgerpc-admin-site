from ninja import Schema
from typing import Optional

class RegisterComputerSchema(Schema):
    mac: str
    name: str
    site: str
    configuration: dict

class SendStatusInfoSchema(Schema):
    pc_uid: str
    job_data: dict

class GetInstructionsSchema(Schema):
    pc_uid: str

class PushConfigKeysSchema(Schema):
    pc_uid: str
    config_dict: dict
    read_only: bool = False

class PushSecurityEventsSchema(Schema):
    pc_uid: str
    csv_data: list

class CitizenLoginSchema(Schema):
    username: str
    password: str
    pc_uid: str
    prevent_dual_login: bool = False

class CitizenLogoutSchema(Schema):
    citizen_hash: str

class GeneralCitizenLoginSchema(Schema):
    pc_uid: str
    integration: str
    value_dict: str

class GeneralCitizenLogoutSchema(Schema):
    citizen_hash: str
    log_id: int

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


class SmsLoginFinalizeSchema(Schema):
   phone_number: str
   pc_uid: str
   require_booking: bool
   save_log: bool
   allow_idle_login: bool = False
   login_duration: Optional[int] = None
   quarantine_duration: Optional[int] = None

class SmsLogoutSchema(Schema):
    citizen_hash: str
    log_id: str