import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from typing import Tuple, Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

class FileUploadService:
    def __init__(self):
        self.allowed_extensions = {
            'images': {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'},
            'documents': {'pdf', 'doc', 'docx', 'txt', 'rtf'},
            'archives': {'zip', 'rar', '7z'},
            'videos': {'mp4', 'avi', 'mov', 'wmv', 'flv'},
            'audio': {'mp3', 'wav', 'ogg', 'm4a'}
        }
        
        # File signature magic numbers (first few bytes)
        self.file_signatures = {
            'images': {
                'jpeg': b'\xFF\xD8\xFF',
                'png': b'\x89PNG\r\n\x1a\n',
                'gif': b'GIF8',
                'bmp': b'BM',
                'webp': b'RIFF....WEBP'
            },
            'pdf': b'%PDF',
            'zip': b'PK\x03\x04',
            'rar': b'Rar!\x1a\x07\x00'
        }
        
        self.max_sizes = {
            'images': 5 * 1024 * 1024,  # 5MB
            'documents': 10 * 1024 * 1024,  # 10MB
            'archives': 20 * 1024 * 1024,  # 20MB
            'videos': 50 * 1024 * 1024,  # 50MB
            'audio': 10 * 1024 * 1024  # 10MB
        }
    
    def validate_file_type(self, file_stream, filename: str) -> bool:
        """Validate file type using file signatures"""
        try:
            # Read first 20 bytes for signature detection
            file_start = file_stream.read(20)
            file_stream.seek(0)  # Reset stream position
            
            file_category = self.get_file_category(filename)
            
            if file_category == 'images':
                # Check image signatures
                if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
                    return file_start.startswith(b'\xFF\xD8\xFF')
                elif filename.lower().endswith('.png'):
                    return file_start.startswith(b'\x89PNG\r\n\x1a\n')
                elif filename.lower().endswith('.gif'):
                    return file_start.startswith(b'GIF8')
                elif filename.lower().endswith('.bmp'):
                    return file_start.startswith(b'BM')
                elif filename.lower().endswith('.webp'):
                    return file_start.startswith(b'RIFF') and b'WEBP' in file_start
            
            elif file_category == 'documents':
                if filename.lower().endswith('.pdf'):
                    return file_start.startswith(b'%PDF')
            
            elif file_category == 'archives':
                if filename.lower().endswith('.zip'):
                    return file_start.startswith(b'PK\x03\x04')
                elif filename.lower().endswith('.rar'):
                    return file_start.startswith(b'Rar!\x1a\x07\x00')
            
            # For other file types, rely on extension validation only
            return True
            
        except Exception as e:
            logger.error(f"Error validating file type: {e}")
            return False
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """Generate a unique filename to prevent conflicts"""
        ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        unique_id = uuid.uuid4().hex[:8]
        base_name = secure_filename(original_filename.rsplit('.', 1)[0])
        
        if ext:
            return f"{base_name}_{unique_id}.{ext}"
        else:
            return f"{base_name}_{unique_id}"
    
    def create_thumbnail(self, image_path: str, thumbnail_size: Tuple[int, int] = (200, 200)) -> Optional[str]:
        """Create thumbnail for images"""
        try:
            with Image.open(image_path) as img:
                img.thumbnail(thumbnail_size)
                
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                
                # Save thumbnail
                base, ext = os.path.splitext(image_path)
                thumbnail_path = f"{base}_thumb{ext}"
                img.save(thumbnail_path, 'JPEG', quality=85)
                
                return thumbnail_path
                
        except Exception as e:
            logger.error(f"Error creating thumbnail: {e}")
            return None
    
    def upload_file(self, file, folder: str, allowed_categories: List[str] = None, 
                   create_thumbnail: bool = False) -> Dict[str, any]:
        """Upload file with comprehensive validation"""
        try:
            if not file or file.filename == '':
                return {'success': False, 'error': 'No file selected'}
            
            # Validate filename
            filename = secure_filename(file.filename)
            if not filename:
                return {'success': False, 'error': 'Invalid filename'}
            
            # Check allowed extensions
            if not self.allowed_file(filename, allowed_categories):
                return {'success': False, 'error': 'File type not allowed'}
            
            # Determine file category
            file_category = self.get_file_category(filename)
            
            # Validate file size
            if not self.validate_file_size(file.stream, file_category):
                max_size_mb = self.max_sizes[file_category] / (1024 * 1024)
                return {'success': False, 'error': f'File too large. Maximum size: {max_size_mb}MB'}
            
            # Validate file type using magic numbers
            if not self.validate_file_type(file.stream, filename):
                return {'success': False, 'error': 'File type mismatch detected'}
            
            # Generate unique filename
            unique_filename = self.generate_unique_filename(filename)
            
            # Create upload directory
            upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
            os.makedirs(upload_folder, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            
            result = {
                'success': True,
                'filename': unique_filename,
                'original_filename': filename,
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'file_category': file_category,
                'url': f"/uploads/{folder}/{unique_filename}"
            }
            
            # Create thumbnail for images
            if create_thumbnail and file_category == 'images':
                thumbnail_path = self.create_thumbnail(file_path)
                if thumbnail_path:
                    result['thumbnail_url'] = f"/uploads/{folder}/{os.path.basename(thumbnail_path)}"
            
            logger.info(f"File uploaded successfully: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return {'success': False, 'error': str(e)}
    
    def upload_multiple_files(self, files, folder: str, allowed_categories: List[str] = None) -> Dict[str, any]:
        """Upload multiple files"""
        results = {
            'total': len(files),
            'successful': [],
            'failed': []
        }
        
        for file in files:
            result = self.upload_file(file, folder, allowed_categories)
            if result['success']:
                results['successful'].append(result)
            else:
                results['failed'].append({
                    'filename': file.filename,
                    'error': result['error']
                })
        
        return results
    
    def delete_file(self, file_path: str) -> bool:
        """Delete uploaded file and its thumbnail"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                
                # Delete thumbnail if exists
                base, ext = os.path.splitext(file_path)
                thumbnail_path = f"{base}_thumb{ext}"
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
                
                logger.info(f"File deleted: {file_path}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, any]]:
        """Get information about uploaded file"""
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            filename = os.path.basename(file_path)
            
            return {
                'filename': filename,
                'file_path': file_path,
                'file_size': stat.st_size,
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime,
                'file_category': self.get_file_category(filename)
            }
            
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None

# Global file upload service instance
file_upload_service = FileUploadService()

# Legacy functions for backward compatibility
def allowed_file(filename, allowed_extensions=None):
    if allowed_extensions is None:
        allowed_extensions = file_upload_service.allowed_extensions['images'].union(
            file_upload_service.allowed_extensions['documents']
        )
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def upload_file(file, folder, allowed_extensions=None):
    if allowed_extensions is None:
        allowed_extensions = file_upload_service.allowed_extensions['images'].union(
            file_upload_service.allowed_extensions['documents']
        )
    
    # Convert allowed_extensions to categories
    allowed_categories = []
    for category, exts in file_upload_service.allowed_extensions.items():
        if any(ext in allowed_extensions for ext in exts):
            allowed_categories.append(category)
    
    result = file_upload_service.upload_file(file, folder, allowed_categories)
    return result['file_path'] if result['success'] else None