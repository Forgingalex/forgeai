"""Workspace application service."""

from __future__ import annotations

from typing import Optional

from app.core.exceptions import NotFoundError
from app.repositories.workspace_repository import WorkspaceRepository


class WorkspaceService:
    """Service for knowledge workspace workflows."""

    def __init__(self, workspace_repository: WorkspaceRepository) -> None:
        self.workspace_repository = workspace_repository

    def create_workspace(self, owner_id: int, name: str, description: Optional[str] = None):
        """Create a workspace."""
        return self.workspace_repository.create(owner_id=owner_id, name=name, description=description)

    def list_workspaces(self, owner_id: int):
        """List workspaces owned by a user."""
        return self.workspace_repository.list_owned(owner_id=owner_id)

    def get_workspace(self, workspace_id: int, owner_id: int):
        """Return a workspace or raise not found."""
        workspace = self.workspace_repository.get_owned(workspace_id=workspace_id, owner_id=owner_id)
        if not workspace:
            raise NotFoundError("Workspace", workspace_id)
        return workspace

