from fastapi import APIRouter, Depends, Query, status

from src.db.models import User
from src.db.connect import get_db
from src.repository import contacts

from src.schemas import contacts as schemas_contact
from src.services.auth import auth_service

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post(
    "/",
    response_model=schemas_contact.ContactResponse,
    name="API for create contact",
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(
    body: schemas_contact.ContactModel,
    db=Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    contact = await contacts.create_contact(body, db, user)
    return contact


@router.get("/search", name="Search contacts")
async def search_contacts(
    first_name: str | None = Query(default=None),
    last_name: str | None = Query(default=None),
    email: str | None = Query(default=None),
    db=Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    return await contacts.search_contacts(first_name, last_name, email, db, user)


@router.get("/birthdays", name="Upcoming birthdays (7 days)")
async def get_upcoming_birthdays(
    db=Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    return await contacts.upcoming_birthdays(db, user)


@router.get(
    "/",
    name="List of contacts",
    status_code=200,
)
async def get_contacts(db=Depends(get_db), user=Depends(auth_service.get_current_user)):
    all_contacts = await contacts.get_contacts(db, user)
    return all_contacts


@router.get(
    "/{contact_id}",
    name="Get contact by id",
    response_model=schemas_contact.ContactResponse,
    status_code=200,
)
async def get_contact_by_id(
    contact_id: int,
    db=Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    return await contacts.get_contact_by_id(contact_id, db, user)


@router.delete(
    "/{contact_id}",
    name="Delete contact by id",
    status_code=200,
)
async def delete_contact(
    contact_id: int,
    db=Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    return await contacts.delete_contact(contact_id, db, user)


@router.patch(
    "/{contact_id}",
    name="Update contact",
    status_code=200,
)
async def update_contact(
    contact_id: int,
    body: schemas_contact.ContactUpdate,
    db=Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    return await contacts.update_contact(contact_id, body, db, user)