# TODO: Make sure this also works on the client - see if the data format is the same as before
# TODO: Convert all the rpc calls on the client to HTTP calls - consider whether json body or query params are best (probably json body)

from ninja import Router
from .client_api_schemas import *
from .rpc import register_new_computer_v2, send_status_info_v2, get_instructions, push_config_keys, \
    push_security_events, sms_logout, sms_login, general_citizen_logout, general_citizen_login, citizen_logout, \
    citizen_login

router = Router()

@router.post("/register_new_computer")
def register_computer_route(request, data: RegisterComputerSchema):
    return register_new_computer_v2(**data.dict())

@router.post("/send_status_info")
def send_status_info_route(request, data: SendStatusInfoSchema):
    return send_status_info_v2(**data.dict())

@router.post("/get_instructions")
def get_instructions_route(request, data: GetInstructionsSchema):
    return get_instructions(**data.dict())

@router.post("/push_config_keys")
def push_config_keys_route(request, data: PushConfigKeysSchema):
    return push_config_keys(**data.dict())

@router.post("/push_security_events")
def push_security_events_route(request, data: PushSecurityEventsSchema):
    return push_security_events(**data.dict())

@router.post("/citizen_login")
def citizen_login_route(request, data: CitizenLoginSchema):
    return citizen_login(**data.dict())

@router.post("/citizen_logout")
def citizen_logout_route(request, data: CitizenLogoutSchema):
    return citizen_logout(**data.dict())

@router.post("/general_citizen_login")
def general_citizen_login_route(request, data: GeneralCitizenLoginSchema):
    return general_citizen_login(**data.dict())

@router.post("/general_citizen_logout")
def general_citizen_logout_route(request, data: GeneralCitizenLogoutSchema):
    return general_citizen_logout(**data.dict())

@router.post("/sms_login")
def sms_login_route(request, data: SmsLoginSchema):
    return sms_login(**data.dict())

@router.post("/sms_login_finalize")
def sms_login_finalize_route(request, data: SmsLoginFinalizeSchema):
    return sms_login_finalize_route(**data.dict())

@router.post("/sms_logout")
def sms_logout_route(request, data: SmsLogoutSchema):
    return sms_logout(**data.dict())