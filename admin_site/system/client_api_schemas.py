from ninja import Schema

class RegisterComputerSchema(Schema):
    mac: str
    name: str
    site: str
    configuration: str