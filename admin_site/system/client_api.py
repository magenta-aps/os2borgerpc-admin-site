from ninja import Router
from .client_api_schemas import (
    CitizenLoginSchema,
    CitizenLogoutSchema,
    ConfirmJobsReceiptSchema,
    GeneralCitizenLoginSchema,
    GeneralCitizenLogoutSchema,
    GetInstructionsSchema,
    PushConfigKeysSchema,
    PushSecurityEventsSchema,
    RegisterComputerSchema,
    SendStatusInfoSchema,
    SmsLoginFinalizeSchema,
    SmsLoginSchema,
    SmsLogoutSchema,
)
from .rpc import (
    citizen_login,
    citizen_logout,
    confirm_jobs_receipt,
    general_citizen_login,
    general_citizen_logout,
    get_instructions,
    push_config_keys,
    push_security_events,
    register_new_computer_v2,
    send_status_info_v2,
    sms_login,
    sms_login_finalize,
    sms_logout,
)

router = Router()


@router.post("/register_new_computer", response={200: str, 400: str})
def register_computer_route(request, data: RegisterComputerSchema):
    return register_new_computer_v2(**data.dict(), api_call=True)


@router.post("/send_status_info")
def send_status_info_route(request, data: SendStatusInfoSchema):
    return send_status_info_v2(**data.dict())


@router.post("/get_instructions")
def get_instructions_route(request, data: GetInstructionsSchema):
    return get_instructions(**data.dict())


@router.post("/confirm_jobs_receipt")
def confirm_jobs_receipt_route(request, data: ConfirmJobsReceiptSchema):
    return confirm_jobs_receipt(**data.dict())


@router.post("/push_config_keys", response={200: str, 400: str})
def push_config_keys_route(request, data: PushConfigKeysSchema):
    return push_config_keys(**data.dict(), api_call=True)


@router.post("/push_security_events")
def push_security_events_route(request, data: PushSecurityEventsSchema):
    return push_security_events(**data.dict())


# This function is deprecated and only exists because one customer still has old
# computers that call it. The newer versions of the Cicero integration
# use general_citizen_login instead.
@router.post("/citizen_login")
def citizen_login_route(request, data: CitizenLoginSchema):
    # This needs to be handled this way as the API
    # will interpret time_allowed as a status code
    # if we simply use return citizen_login(**data.dict())
    time_allowed, citizen_hash = citizen_login(**data.dict())
    return [time_allowed, citizen_hash]


# This function is deprecated and only exists because one customer still has old
# computers that call it. The newer versions of the Cicero integration
# use general_citizen_logout instead.
@router.post("/citizen_logout")
def citizen_logout_route(request, data: CitizenLogoutSchema):
    return citizen_logout(**data.dict())


@router.post("/general_citizen_login")
def general_citizen_login_route(request, data: GeneralCitizenLoginSchema):
    # This needs to be handled this way as the API
    # will interpret time_allowed as a status code
    # if we simply use return general_citizen_login(**data.dict())
    time_allowed, citizen_hash, log_id = general_citizen_login(**data.dict())
    return [time_allowed, citizen_hash, log_id]


@router.post("/general_citizen_logout")
def general_citizen_logout_route(request, data: GeneralCitizenLogoutSchema):
    return general_citizen_logout(**data.dict())


@router.post("/sms_login")
def sms_login_route(request, data: SmsLoginSchema):
    # This needs to be handled this way as the API
    # will interpret time_allowed as a status code
    # if we simply use return sms_login(**data.dict())
    time_allowed, citizen_hash = sms_login(**data.dict())
    return [time_allowed, citizen_hash]


@router.post("/sms_login_finalize")
def sms_login_finalize_route(request, data: SmsLoginFinalizeSchema):
    return sms_login_finalize(**data.dict())


@router.post("/sms_logout")
def sms_logout_route(request, data: SmsLogoutSchema):
    return sms_logout(**data.dict())
