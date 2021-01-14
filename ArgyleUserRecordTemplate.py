from pydantic import BaseModel, ValidationError, validator

class ArgyleUserRecord(BaseModel) :

  id: str
  account: str
  employer: str
  full_name: str
  first_name: str
  last_name: str
  email: str
  phone_number: str
  birth_date: str
  picture_url: str
  ssn: str
  marital_status: str
  gender: str
  address: dict

  @validator('address')
  def address_must_contain_required_values(cls,value) :
    if "line1" not in value : raise ValueError("required line1 address component missing")
    if "line2" not in value : raise ValueError("required line2 address component missing")
    if "city" not in value : raise ValueError("required city address component missing")
    if "state" not in value : raise ValueError("required state address component missing")
    if "postal_code" not in value : raise ValueError("required postal code address component missing")
    if "country" not in value : raise ValueError("required country address component missing")

    return value

