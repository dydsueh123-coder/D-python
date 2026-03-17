"""화면 녹화 API"""
import os
from flask import request, jsonify, send_file
from flask_login import current_user
from . import recordings_bp
from .services import RecordingService
from app.auth.decorators import login_required, admin_required


@recordings_bp.route('/', methods=['GET'])
@login_required
def list_recordings():
    """녹화 목록 (관리자: 전체, 일반: 본인 것만)"""
    recordings = RecordingService.list_recordings(
        user_id=current_user.id,
        is_admin=current_user.is_admin,
    )
    return jsonify([RecordingService.to_dict(r) for r in recordings])


@recordings_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """WebM 녹화 파일 업로드"""
    if 'file' not in request.files:
        return jsonify({'error': 'file 필드가 없습니다.'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400

    survey_response_id = request.form.get('survey_response_id', type=int)
    duration_seconds = request.form.get('duration_seconds', type=int)

    try:
        recording = RecordingService.save_recording(
            file=file,
            user_id=current_user.id,
            survey_response_id=survey_response_id,
            duration_seconds=duration_seconds,
        )
        return jsonify(RecordingService.to_dict(recording)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Recording upload error")
        return jsonify({'error': '업로드 중 오류가 발생했습니다.'}), 500


@recordings_bp.route('/<int:recording_id>/file', methods=['GET'])
@login_required
def get_file(recording_id):
    """녹화 파일 스트리밍 (본인 또는 관리자만)"""
    recording = RecordingService.get_recording(recording_id)
    if not recording:
        return jsonify({'error': '녹화를 찾을 수 없습니다.'}), 404
    if recording.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': '접근 권한이 없습니다.'}), 403

    file_path = RecordingService.get_file_path(recording)
    if not os.path.exists(file_path):
        return jsonify({'error': '파일이 존재하지 않습니다.'}), 404

    return send_file(
        file_path,
        mimetype='video/webm',
        as_attachment=False,
        download_name=recording.original_filename or recording.filename,
        conditional=True,  # Range 요청 지원 (브라우저 seek)
    )


@recordings_bp.route('/<int:recording_id>', methods=['DELETE'])
@login_required
def delete_recording(recording_id):
    """녹화 삭제 (본인 또는 관리자만)"""
    recording = RecordingService.get_recording(recording_id)
    if not recording:
        return jsonify({'error': '녹화를 찾을 수 없습니다.'}), 404
    if recording.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': '접근 권한이 없습니다.'}), 403

    RecordingService.delete_recording(recording)
    return jsonify({'message': '삭제되었습니다.'})
