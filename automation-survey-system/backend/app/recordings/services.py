"""화면 녹화 파일 저장 및 조회 서비스"""
import os
import uuid
from datetime import datetime, timezone
from flask import current_app
from werkzeug.datastructures import FileStorage
from app.extensions import db
from .models import Recording
import logging

logger = logging.getLogger(__name__)

ALLOWED_MIME = {'video/webm', 'video/webm;codecs=vp8', 'video/webm;codecs=vp9', 'video/webm;codecs=h264'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB


class RecordingService:

    @staticmethod
    def _upload_dir() -> str:
        folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'recordings')
        os.makedirs(folder, exist_ok=True)
        return folder

    @classmethod
    def save_recording(
        cls,
        file: FileStorage,
        user_id: int,
        survey_response_id: int | None = None,
        duration_seconds: int | None = None,
    ) -> Recording:
        # MIME 체크 (Chrome WebM)
        mime = (file.content_type or '').split(';')[0].strip()
        if mime not in {'video/webm', 'video/mp4', 'application/octet-stream'}:
            raise ValueError(f"허용되지 않는 파일 형식입니다: {file.content_type}")

        # 파일 저장 (UUID 기반 이름으로 경로 조작 방지)
        safe_name = f"{uuid.uuid4().hex}.webm"
        save_path = os.path.join(cls._upload_dir(), safe_name)
        file.save(save_path)
        file_size = os.path.getsize(save_path)

        if file_size > MAX_FILE_SIZE:
            os.remove(save_path)
            raise ValueError(f"파일 크기가 제한(500MB)을 초과했습니다.")

        recording = Recording(
            user_id=user_id,
            survey_response_id=survey_response_id,
            filename=safe_name,
            original_filename=file.filename,
            file_size=file_size,
            duration_seconds=duration_seconds,
            status='ready',
        )
        db.session.add(recording)
        db.session.commit()
        logger.info(f"Recording saved: id={recording.id} user={user_id} size={file_size}")
        return recording

    @staticmethod
    def list_recordings(user_id: int, is_admin: bool = False) -> list:
        q = Recording.query.order_by(Recording.created_at.desc())
        if not is_admin:
            q = q.filter_by(user_id=user_id)
        return q.all()

    @staticmethod
    def get_recording(recording_id: int) -> Recording | None:
        return Recording.query.get(recording_id)

    @classmethod
    def get_file_path(cls, recording: Recording) -> str:
        return os.path.join(cls._upload_dir(), recording.filename)

    @classmethod
    def delete_recording(cls, recording: Recording) -> None:
        path = cls.get_file_path(recording)
        if os.path.exists(path):
            os.remove(path)
        db.session.delete(recording)
        db.session.commit()
        logger.info(f"Recording deleted: id={recording.id}")

    @staticmethod
    def to_dict(recording: Recording) -> dict:
        return {
            'id': recording.id,
            'user_id': recording.user_id,
            'survey_response_id': recording.survey_response_id,
            'filename': recording.filename,
            'original_filename': recording.original_filename,
            'file_size': recording.file_size,
            'duration_seconds': recording.duration_seconds,
            'status': recording.status,
            'created_at': recording.created_at.isoformat(),
        }
