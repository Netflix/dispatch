from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.exceptions import InvalidConfiguration
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
    sort_by: List[str] = Query([], alias="sortBy[]"),
    descending: List[bool] = Query([], alias="descending[]"),
    fields: List[str] = Query([], alias="field[]"),
    ops: List[str] = Query([], alias="op[]"),
    values: List[str] = Query([], alias="value[]"),
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


@router.get("/{plugin_type}", response_model=PluginPagination)
def get_plugins_by_type(
    plugin_type: str,
    db_session: Session = Depends(get_db),
    page: int = 1,
    items_per_page: int = Query(5, alias="itemsPerPage"),
    query_str: str = Query(None, alias="q"),
    sort_by: List[str] = Query([], alias="sortBy[]"),
    descending: List[bool] = Query([], alias="descending[]"),
    fields: List[str] = Query([], alias="field[]"),
    ops: List[str] = Query([], alias="op[]"),
    values: List[str] = Query([], alias="value[]"),
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
        fields=["type"],
        values=[plugin_type],
        ops=["=="],
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

    try:
        plugin = update(db_session=db_session, plugin=plugin, plugin_in=plugin_in)
    except InvalidConfiguration as e:
        raise HTTPException(status_code=400, detail=str(e))

    return plugin
