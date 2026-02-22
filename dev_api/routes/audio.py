from flask import Blueprint, jsonify, current_app, send_file, request

from ..services.email_loader import EmailLoader
from ..services.parser_service import ParserService
from ..services.storage import AudioCache

audio_bp = Blueprint("audio", __name__)


def get_email_loader() -> EmailLoader:
    """Get EmailLoader from dependencies."""
    return current_app.deps.get(EmailLoader)


def get_parser_service() -> ParserService:
    """Get ParserService from dependencies."""
    return current_app.deps.get(ParserService)


def get_audio_cache() -> AudioCache:
    """Get AudioCache from dependencies."""
    return current_app.deps.get(AudioCache)


@audio_bp.route("/cache/clear", methods=["POST"])
def clear_cache():
    """Clear the audio cache."""
    cache = get_audio_cache()
    cache.clear_cache()
    return jsonify({"success": True})


@audio_bp.route("/chunk/<email_id>/<int:chunk_index>", methods=["POST"])
def generate_chunk_audio(email_id: str, chunk_index: int):
    """Generate audio for a specific SSML chunk of an email."""
    loader = get_email_loader()
    parser_service = get_parser_service()

    inbox_item = loader.get_email(email_id)
    if inbox_item is None:
        return jsonify({"error": "Email not found"}), 404

    result = parser_service.parse_email(inbox_item)

    if not result.success:
        return jsonify({"error": "Failed to parse email", "details": result.error}), 500

    if chunk_index < 0 or chunk_index >= len(result.ssml_chunks):
        return jsonify({"error": "Chunk index out of range"}), 400

    chunk = result.ssml_chunks[chunk_index]
    voice = result.voice

    cache = get_audio_cache()

    # Check cache first
    cached_path = cache.get_audio_path(chunk.ssml, voice)
    if cached_path:
        return jsonify({
            "success": True,
            "cached": True,
            "audioUrl": f"/api/audio/chunk/{email_id}/{chunk_index}/file"
        })

    # Generate audio
    try:
        from email_exporter.cloud import TextToSpeech

        t2s = current_app.deps.get(TextToSpeech)

        audio_result = t2s.t2s(chunk.ssml, voice)

        # Cache the result
        cache.store_audio(chunk.ssml, voice, audio_result.audio_content, audio_result.extension)

        return jsonify({
            "success": True,
            "cached": False,
            "audioUrl": f"/api/audio/chunk/{email_id}/{chunk_index}/file"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@audio_bp.route("/chunk/<email_id>/<int:chunk_index>/file", methods=["GET"])
def get_chunk_audio_file(email_id: str, chunk_index: int):
    """Serve an audio file for a specific chunk with Range request support for seeking."""
    import os
    import mimetypes
    from flask import Response
    
    loader = get_email_loader()
    parser_service = get_parser_service()

    inbox_item = loader.get_email(email_id)
    if inbox_item is None:
        return jsonify({"error": "Email not found"}), 404

    result = parser_service.parse_email(inbox_item)

    if not result.success:
        return jsonify({"error": "Failed to parse email"}), 500

    if chunk_index < 0 or chunk_index >= len(result.ssml_chunks):
        return jsonify({"error": "Chunk index out of range"}), 400

    chunk = result.ssml_chunks[chunk_index]
    voice = result.voice

    cache = get_audio_cache()
    path = cache.get_audio_path(chunk.ssml, voice)
    
    if not path or not os.path.exists(path):
        return jsonify({"error": "Audio not found - generate it first"}), 404

    # Get file size and mime type
    file_size = os.path.getsize(path)
    mime_type = mimetypes.guess_type(path)[0] or 'audio/mpeg'
    
    # Handle Range requests for seeking
    range_header = request.headers.get('Range')
    
    if range_header:
        # Parse range header (e.g., "bytes=0-1024")
        byte_start = 0
        byte_end = file_size - 1
        
        if range_header.startswith('bytes='):
            range_spec = range_header[6:]
            if '-' in range_spec:
                parts = range_spec.split('-')
                if parts[0]:
                    byte_start = int(parts[0])
                if parts[1]:
                    byte_end = int(parts[1])
        
        # Ensure valid range
        byte_end = min(byte_end, file_size - 1)
        content_length = byte_end - byte_start + 1
        
        def generate():
            with open(path, 'rb') as f:
                f.seek(byte_start)
                remaining = content_length
                while remaining > 0:
                    chunk_size = min(8192, remaining)
                    data = f.read(chunk_size)
                    if not data:
                        break
                    remaining -= len(data)
                    yield data
        
        response = Response(
            generate(),
            status=206,  # Partial Content
            mimetype=mime_type,
            direct_passthrough=True
        )
        response.headers['Content-Range'] = f'bytes {byte_start}-{byte_end}/{file_size}'
        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['Content-Length'] = content_length
        return response
    
    # No Range header - serve entire file
    response = send_file(path, mimetype=mime_type)
    response.headers['Accept-Ranges'] = 'bytes'
    response.headers['Content-Length'] = file_size
    return response
