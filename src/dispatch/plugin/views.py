from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.database import get_db, search_filter_sort_paginate

from .models import PluginCreate, PluginPagination, PluginRead, PluginUpdate
from .service import get, update

router = APIRouter()


@router.get("/", response_model=PluginPagination)
def get_plugins(
    db_session: Session = Depends(get_db),
    page: int = 1,
    items_per_page: int = Query(5, alias="itemsPerPage"),
    query_str: str = Query(None, alias="q"),
    sort_by: List[str] = Query(None, alias="sortBy[]"),
    descending: List[bool] = Query(None, alias="descending[]"),
    fields: List[str] = Query(None, alias="field[]"),
    ops: List[str] = Query(None, alias="op[]"),
    values: List[str] = Query(None, alias="value[]"),
):
    """
    Get all plugins.
    """
    return search_filter_sort_paginate(
        db_session=db_session,
        model="Plugin",
        query_str=query_str,
        page=page,
        items_per_page=items_per_page,
        sort_by=sort_by,
        descending=descending,
        fields=fields,
        values=values,
        ops=ops,
    )


@router.get("/{plugin_id}", response_model=PluginRead)
def get_plugin(*, db_session: Session = Depends(get_db), plugin_id: int):
    """
    Get a plugin.
    """
    plugin = get(db_session=db_session, plugin_id=plugin_id)
    if not plugin:
        raise HTTPException(status_code=404, detail="The plugin with this id does not exist.")
    return plugin


@router.put("/{plugin_id}", response_model=PluginCreate)
def update_plugin(
    *, db_session: Session = Depends(get_db), plugin_id: int, plugin_in: PluginUpdate
):
    """
    Update a plugin.
    """
    plugin = get(db_session=db_session, plugin_id=plugin_id)
    if not plugin:
        raise HTTPException(status_code=404, detail="The plugin with this id does not exist.")
    plugin = update(db_session=db_session, plugin=plugin, plugin_in=plugin_in)
    return plugin
