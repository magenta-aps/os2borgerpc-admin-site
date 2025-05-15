# TODO: Make sure this also works on the client - see if the data format is the same as before
# TODO: Convert all the rpc calls on the client to HTTP calls - consider whether json body or query params are best (probably json body)

from datetime import date, datetime, timedelta
from typing import List
from django.db.models import Q

from ninja import Router
from ninja.pagination import paginate
from ninja.errors import ValidationError

from .client_api_schemas import RegisterComputerSchema
from .models import (
    APIKey,
    Configuration,
    ConfigurationEntry,
    Job,
    PC,
    SecurityEvent,
)
from .api_schemas import (
    ConfigurationEntrySchema,
    JobSchema,
    PCSchema,
    PCLoginsSchema,
    SecurityEventSchema,
)
from .rpc import register_new_computer_v2, send_status_info_v2, get_instructions, push_config_keys, \
    push_security_events, sms_logout, sms_login, general_citizen_logout, general_citizen_login, citizen_logout, \
    citizen_login

router = Router()

@router.post("/register_new_computer")
def register_computer_route(request, data: RegisterComputerSchema):
    return register_new_computer_v2(**data.dict())

@router.post("/send_status_info")
def send_status_info_route(request, data: RegisterComputerSchema):
    # pc_uid, job_data
    return send_status_info_v2(**data.dict())

@router.post("/get_instructions")
def get_instructions_route(request, data: RegisterComputerSchema):
    #pc_uid
    return get_instructions(**data.dict())

@router.post("/push_config_keys")
def push_config_keys_route(request, data: RegisterComputerSchema):
    #pc_uid, config_dict, read_only=False)
    return push_config_keys(**data.dict())

@router.post("/push_security_events")
def push_security_events_route(request, data: RegisterComputerSchema):
    #pc_uid, csv_data
    return push_security_events(**data.dict())

@router.post("/citizen_login")
def citizen_login_route(request, data: RegisterComputerSchema):
    #username, password, pc_uid, prevent_dual_login=False)
    return citizen_login(**data.dict())

@router.post("/citizen_logout")
def citizen_logout_route(request, data: RegisterComputerSchema):
    #citizen_hash
    return citizen_logout(**data.dict())

@router.post("/general_citizen_login")
def general_citizen_login_route(request, data: RegisterComputerSchema):
    #pc_uid, integration, value_dict
    return general_citizen_login(**data.dict())

@router.post("/general_citizen_logout")
def general_citizen_logout_route(request, data: RegisterComputerSchema):
    #citizen_hash, log_id
    return general_citizen_logout(**data.dict())

@router.post("/sms_login")
def sms_login_route(request, data: RegisterComputerSchema):
    #          phone_number,
    #          message,
    #          pc_uid,
    #          require_booking,
    #          pc_name,
    #          allow_idle_login,
    #          login_duration,
    #          quarantine_duration,
    #          unlimited_access,
    return sms_login(**data.dict())

@router.post("/sms_login_finalize")
def sms_login_finalize_route(request, data: RegisterComputerSchema):
#   #          phone_number,
   #          pc_uid,
   #          require_booking,
   #          save_log,
   #          allow_idle_login,
   #          login_duration,
   #          quarantine_duration,
    return sms_login_finalize_route(**data.dict())

@router.post("/sms_logout")
def sms_logout_route(request, data: RegisterComputerSchema):
    #citizen_hash, log_id
    return sms_logout(**data.dict())