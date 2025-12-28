from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid
import os
from PIL import Image
from io import BytesIO


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_file(request):
    """
    Upload a file and return the URL
    """
    # Debug: Log request details
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Upload request - FILES keys: {list(request.FILES.keys())}, POST keys: {list(request.POST.keys())}")
    
    if 'file' not in request.FILES:
        logger.warning("No file in request.FILES")
        return Response({
            'error': 'No file provided',
            'debug': {
                'files_keys': list(request.FILES.keys()),
                'post_keys': list(request.POST.keys()),
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    logger.info(f"File received - name: {file.name}, size: {file.size}, content_type: {file.content_type}")
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/webp']
    if file.content_type not in allowed_types:
        logger.warning(f"Invalid file type: {file.content_type}")
        return Response({
            'error': 'File type not supported. Please use JPG, PNG, or WebP format.',
            'received_type': file.content_type,
            'allowed_types': allowed_types
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate file size (5MB limit)
    if file.size > 5 * 1024 * 1024:
        return Response({
            'error': 'File size too large. Maximum size is 5MB.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Generate unique filename
        file_extension = os.path.splitext(file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Save file to media directory
        file_path = default_storage.save(f'uploads/{unique_filename}', file)
        file_url = default_storage.url(file_path)
        
        return Response({
            'url': file_url,
            'filename': unique_filename
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'File upload failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
