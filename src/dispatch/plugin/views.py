from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.auth.permissions import SensitiveProjectActionPermission, PermissionsDependency
from dispatch.models import PrimaryKey

from .models import (
    PluginInstanceRead,
    PluginInstanceCreate,
    PluginInstanceUpdate,
    PluginInstancePagination,
    PluginPagination,
)
from .service import get_instance, update_instance, create_instance, delete_instance


router = APIRouter()


@router.get("", response_model=PluginPagination)
def get_plugins(*, common: dict = Depends(common_parameters)):
    """Get all plugins."""
    return search_filter_sort_paginate(model="Plugin", **common)


@router.get(
    "/instances",
    response_model=PluginInstancePagination,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def get_plugin_instances(*, common: dict = Depends(common_parameters)):
    """Get all plugin instances."""
    return search_filter_sort_paginate(model="PluginInstance", **common)


@router.get(
    "/instances/{plugin_instance_id}",
    response_model=PluginInstanceRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def get_plugin_instance(*, db_session: Session = Depends(get_db), plugin_instance_id: PrimaryKey):
    """Get a plugin instance."""
    plugin = get_instance(db_session=db_session, plugin_instance_id=plugin_instance_id)
    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A plugin instance with this id does not exist."}],
        )
    return plugin


@router.post(
    "/instances",
    response_model=PluginInstanceRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def create_plugin_instance(
    *, db_session: Session = Depends(get_db), plugin_instance_in: PluginInstanceCreate
):
    """Create a new plugin instance."""
    return create_instance(db_session=db_session, plugin_instance_in=plugin_instance_in)


@router.put(
    "/instances/{plugin_instance_id}",
    response_model=PluginInstanceCreate,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def update_plugin_instance(
    *,
    db_session: Session = Depends(get_db),
    plugin_instance_id: PrimaryKey,
    plugin_instance_in: PluginInstanceUpdate,
):
    """Update a plugin instance."""
    plugin_instance = get_instance(db_session=db_session, plugin_instance_id=plugin_instance_id)
    if not plugin_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A plugin instance with this id does not exist."}],
        )

    plugin_instance = update_instance(
        db_session=db_session,
        plugin_instance=plugin_instance,
        plugin_instance_in=plugin_instance_in,
    )

    return plugin_instance


@router.delete(
    "/instances/{plugin_instance_id}",
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def delete_plugin_instances(
    *,
    db_session: Session = Depends(get_db),
    plugin_instance_id: PrimaryKey,
):
    """Deletes an existing plugin instance."""
    plugin_instance = get_instance(db_session=db_session, plugin_instance_id=plugin_instance_id)
    if not plugin_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A plugin instance with this id does not exist."}],
        )

    delete_instance(db_session=db_session, plugin_instance_id=plugin_instance_id)
