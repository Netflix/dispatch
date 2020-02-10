from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dispatch.database import get_db, paginate
from dispatch.search.service import search

from .models import Policy, PolicyCreate, PolicyPagination, PolicyRead, PolicyUpdate
from .service import create, delete, get, get_all, update

router = APIRouter()


@router.get("/", response_model=PolicyPagination)
def get_policies(
    db_session: Session = Depends(get_db), page: int = 0, itemsPerPage: int = 5, q: str = None
):
    """
    Retrieve policies.
    """
    if q:
        query = search(db_session=db_session, query_str=q, model=Policy)
    else:
        query = get_all(db_session=db_session)

    items, total = paginate(query=query, page=page, items_per_page=itemsPerPage)

    return {"items": items, "total": total}


@router.post("/", response_model=PolicyRead)
def create_policy(*, db_session: Session = Depends(get_db), policy_in: PolicyCreate):
    """
    Create a new policy.
    """
    # TODO check for similarity
    policy = create(db_session=db_session, policy_in=policy_in)
    return policy


@router.put("/{policy_id}", response_model=PolicyRead)
def update_policy(
    *, db_session: Session = Depends(get_db), policy_id: int, policy_in: PolicyUpdate
):
    """
    Update a policy.
    """
    policy = get(db_session=db_session, policy_id=policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="A policy with this id does not exist.")
    policy = update(db_session=db_session, policy=policy, policy_in=policy_in)
    return policy


@router.delete("/{policy_id}")
def delete_individual(*, db_session: Session = Depends(get_db), policy_id: int):
    """
    Delete a policy.
    """
    policy = get(db_session=db_session, policy_id=policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="A policy with this id does not exist.")

    delete(db_session=db_session, policy_id=policy_id)
