"""File persistence repository."""

from __future__ import annotations

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.file import File


class FileRepository:
    """Repository for uploaded file records."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        metadata: Dict[str, object],
        owner_id: int,
        workspace_id: Optional[int] = None,
    ) -> File:
        """Create a file row from storage metadata."""
        db_file = File(
            filename=str(metadata["filename"]),
            original_filename=str(metadata["original_filename"]),
            file_path=str(metadata["file_path"]),
            file_type=str(metadata["file_type"]),
            file_size=int(metadata["file_size"]),
            owner_id=owner_id,
            workspace_id=workspace_id,
        )
        self.db.add(db_file)
        self.db.commit()
        self.db.refresh(db_file)
        return db_file

    def list_owned(self, owner_id: int, workspace_id: Optional[int] = None) -> List[File]:
        """Return uploaded files owned by a user."""
        query = self.db.query(File).filter(File.owner_id == owner_id)
        if workspace_id is not None:
            query = query.filter(File.workspace_id == workspace_id)
        return query.order_by(File.created_at.desc()).all()

    def get_owned(self, file_id: int, owner_id: int) -> Optional[File]:
        """Return a file only when owned by the user."""
        return self.db.query(File).filter(File.id == file_id, File.owner_id == owner_id).first()

    def mark_processed(self, file: File, summary: str, extracted_text: str) -> File:
        """Persist successful document processing output."""
        file.summary = summary
        file.extracted_text = extracted_text
        file.is_processed = True
        self.db.commit()
        self.db.refresh(file)
        return file

    def mark_processing_failed(self, file: File, message: str) -> File:
        """Persist a processing failure without deleting the upload."""
        file.summary = message
        file.is_processed = False
        self.db.commit()
        self.db.refresh(file)
        return file

    def mark_indexed(self, file: File) -> File:
        """Persist successful vector indexing status."""
        file.is_indexed = True
        self.db.commit()
        self.db.refresh(file)
        return file

