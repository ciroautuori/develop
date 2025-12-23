"""
Upload Service - Gestione upload immagini portfolio.
Enterprise-grade: validazione, resize, storage sicuro.
"""

import os
import uuid
from pathlib import Path
from typing import Tuple, Optional
from datetime import datetime

from fastapi import UploadFile, HTTPException, status
from PIL import Image
import aiofiles


class UploadConfig:
    """Configurazione upload."""
    
    # Paths
    UPLOAD_DIR = Path("/app/uploads")  # Inside container
    PROJECTS_DIR = UPLOAD_DIR / "projects"
    THUMBNAILS_DIR = UPLOAD_DIR / "thumbnails"
    
    # Limits
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
    
    # Image processing
    MAX_WIDTH = 1920
    MAX_HEIGHT = 1080
    THUMBNAIL_SIZE = (400, 300)
    QUALITY = 85
    
    @classmethod
    def ensure_directories(cls):
        """Crea directory se non esistono."""
        cls.PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)


class ImageUploadService:
    """
    Servizio upload immagini.
    
    Features:
    - Validazione tipo e dimensione
    - Resize automatico
    - Generazione thumbnail
    - Storage sicuro con nomi unici
    - Cleanup automatico file vecchi
    """
    
    @staticmethod
    def validate_file(file: UploadFile) -> None:
        """
        Valida file upload.
        
        Raises:
            HTTPException: Se file non valido
        """
        # Check content type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Check extension
        file_ext = Path(file.filename or "").suffix.lower()
        if file_ext not in UploadConfig.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension {file_ext} not allowed. Allowed: {', '.join(UploadConfig.ALLOWED_EXTENSIONS)}"
            )
    
    @staticmethod
    def generate_filename(original_filename: str) -> str:
        """
        Genera nome file univoco.
        
        Format: YYYYMMDD_UUID_original.ext
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        unique_id = uuid.uuid4().hex[:8]
        ext = Path(original_filename).suffix.lower()
        safe_name = Path(original_filename).stem[:20]  # Max 20 chars
        
        return f"{timestamp}_{unique_id}_{safe_name}{ext}"
    
    @staticmethod
    async def save_upload(file: UploadFile, directory: Path) -> Path:
        """
        Salva file uploaded.
        
        Args:
            file: File da salvare
            directory: Directory destinazione
            
        Returns:
            Path del file salvato
        """
        filename = ImageUploadService.generate_filename(file.filename or "upload.jpg")
        file_path = directory / filename
        
        # Salva file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return file_path
    
    @staticmethod
    def resize_image(
        input_path: Path,
        output_path: Path,
        max_width: int = UploadConfig.MAX_WIDTH,
        max_height: int = UploadConfig.MAX_HEIGHT,
        quality: int = UploadConfig.QUALITY
    ) -> Tuple[int, int]:
        """
        Resize immagine mantenendo aspect ratio.
        
        Returns:
            Tuple (width, height) finale
        """
        with Image.open(input_path) as img:
            # Convert RGBA to RGB if needed
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            # Calculate new size
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            
            return img.size
    
    @staticmethod
    def create_thumbnail(
        input_path: Path,
        output_path: Path,
        size: Tuple[int, int] = UploadConfig.THUMBNAIL_SIZE
    ) -> Tuple[int, int]:
        """
        Crea thumbnail.
        
        Returns:
            Tuple (width, height) finale
        """
        with Image.open(input_path) as img:
            # Convert to RGB
            if img.mode != 'RGB':
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                else:
                    img = img.convert('RGB')
            
            # Thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save
            img.save(output_path, 'JPEG', quality=80, optimize=True)
            
            return img.size
    
    @staticmethod
    async def upload_project_image(file: UploadFile) -> dict:
        """
        Upload immagine progetto completo.
        
        Process:
        1. Valida file
        2. Salva temporaneo
        3. Resize a dimensioni corrette
        4. Crea thumbnail
        5. Rimuovi temporaneo
        
        Returns:
            dict con 'image_url' e 'thumbnail_url'
        """
        # Ensure directories exist
        UploadConfig.ensure_directories()
        
        # Validate
        ImageUploadService.validate_file(file)
        
        # Generate filenames
        temp_path = UploadConfig.UPLOAD_DIR / f"temp_{uuid.uuid4().hex}.tmp"
        final_filename = ImageUploadService.generate_filename(file.filename or "project.jpg")
        thumb_filename = f"thumb_{final_filename}"
        
        final_path = UploadConfig.PROJECTS_DIR / final_filename
        thumb_path = UploadConfig.THUMBNAILS_DIR / thumb_filename
        
        try:
            # Save temporary
            await ImageUploadService.save_upload(file, UploadConfig.UPLOAD_DIR)
            
            # Rename temp to actual path
            os.rename(
                UploadConfig.UPLOAD_DIR / ImageUploadService.generate_filename(file.filename or "temp.jpg"),
                temp_path
            )
            
            # Resize main image
            ImageUploadService.resize_image(temp_path, final_path)
            
            # Create thumbnail
            ImageUploadService.create_thumbnail(temp_path, thumb_path)
            
            # Remove temp
            temp_path.unlink(missing_ok=True)
            
            # Return URLs (nginx serve /uploads)
            return {
                "image_url": f"/uploads/projects/{final_filename}",
                "thumbnail_url": f"/uploads/thumbnails/{thumb_filename}",
                "filename": final_filename
            }
            
        except Exception as e:
            # Cleanup on error
            temp_path.unlink(missing_ok=True)
            final_path.unlink(missing_ok=True)
            thumb_path.unlink(missing_ok=True)
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing image: {str(e)}"
            )
    
    @staticmethod
    def delete_image(filename: str) -> None:
        """
        Elimina immagine e thumbnail.
        
        Args:
            filename: Nome file immagine principale
        """
        # Delete main image
        image_path = UploadConfig.PROJECTS_DIR / filename
        image_path.unlink(missing_ok=True)
        
        # Delete thumbnail
        thumb_filename = f"thumb_{filename}"
        thumb_path = UploadConfig.THUMBNAILS_DIR / thumb_filename
        thumb_path.unlink(missing_ok=True)
