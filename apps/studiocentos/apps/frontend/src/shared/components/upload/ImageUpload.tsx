/**
 * ImageUpload Component - Drag & drop image upload with preview.
 * Enterprise-grade: progress bar, validation, error handling.
 */

import { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { Upload, X, Image as ImageIcon, AlertCircle } from 'lucide-react';
import { cn } from '../../lib/utils';

interface ImageUploadProps {
  onUpload: (file: File) => Promise<{ image_url: string; thumbnail_url: string }>;
  currentImage?: string;
  onRemove?: () => void;
  maxSizeMB?: number;
  accept?: string;
  className?: string;
}

export function ImageUpload({
  onUpload,
  currentImage,
  onRemove,
  maxSizeMB = 10,
  accept = 'image/jpeg,image/png,image/webp',
  className
}: ImageUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [preview, setPreview] = useState<string | null>(currentImage || null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): string | null => {
    // Check file type
    const acceptedTypes = accept.split(',').map(t => t.trim());
    if (!acceptedTypes.some(type => file.type.match(type.replace('*', '.*')))) {
      return `File type not supported. Accepted: ${accept}`;
    }

    // Check file size
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      return `File too large. Maximum size: ${maxSizeMB}MB`;
    }

    return null;
  };

  const handleFile = async (file: File) => {
    setError(null);

    // Validate
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);

    // Upload
    try {
      setUploading(true);
      setProgress(0);

      // Simulate progress (real progress would come from upload API)
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const result = await onUpload(file);

      clearInterval(progressInterval);
      setProgress(100);

      // Set final preview from uploaded URL
      if (result.image_url) {
        setPreview(result.image_url);
      }

      setTimeout(() => {
        setUploading(false);
        setProgress(0);
      }, 500);

    } catch (err: any) {
      setError(err.message || 'Upload failed');
      setPreview(null);
      setUploading(false);
      setProgress(0);
    }
  };

  const handleDragEnter = (e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileInput = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleRemove = () => {
    setPreview(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    onRemove?.();
  };

  return (
    <div className={cn('space-y-4', className)}>
      {/* Upload area */}
      {!preview && (
        <div
          onDragEnter={handleDragEnter}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={cn(
            'relative border-2 border-dashed rounded-xl p-8 transition-all duration-200 cursor-pointer',
            'hover:border-gold hover:bg-gold/5',
            isDragging && 'border-gold bg-gold/10 scale-105',
            error && 'border-gray-500 bg-gray-50 dark:bg-gray-700/10',
            'bg-gray-50 dark:bg-[#0A0A0A]',
            'border-gray-300 dark:border-gray-700'
          )}
        >
          <div className="flex flex-col items-center justify-center gap-4 text-center">
            <div className={cn(
              'p-4 rounded-full transition-colors',
              isDragging ? 'bg-gold/20' : 'bg-gray-200 dark:bg-gray-800'
            )}>
              <Upload className={cn(
                'h-8 w-8 transition-colors',
                isDragging ? 'text-gold' : 'text-gray-600 dark:text-gray-400'
              )} />
            </div>

            <div>
              <p className="text-lg font-medium text-gray-900 dark:text-white">
                {isDragging ? 'Drop image here' : 'Drag & drop image'}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                or click to browse
              </p>
            </div>

            <p className="text-xs text-gray-400 dark:text-gray-600">
              Accepted: JPG, PNG, WEBP • Max {maxSizeMB}MB
            </p>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept={accept}
            onChange={handleFileInput}
            className="hidden"
          />
        </div>
      )}

      {/* Preview */}
      {preview && (
        <div className="relative rounded-xl overflow-hidden border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-[#0A0A0A]">
          <img
            src={preview}
            alt="Preview"
            className="w-full h-64 object-cover"
          />

          <button
            onClick={handleRemove}
            disabled={uploading}
            className="absolute top-3 right-3 p-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg shadow-lg transition-colors disabled:opacity-50"
          >
            <X className="h-5 w-5" />
          </button>

          {/* Upload progress */}
          {uploading && (
            <div className="absolute bottom-0 left-0 right-0 bg-black/50 backdrop-blur-sm p-4">
              <div className="flex items-center gap-3">
                <div className="flex-1">
                  <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gold transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
                <span className="text-sm text-white font-medium">
                  {progress}%
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error message */}
      {error && (
        <div className="flex items-start gap-3 p-4 bg-gray-50 dark:bg-gray-700/20 border border-gray-300 dark:border-gray-700 rounded-lg">
          <AlertCircle className="h-5 w-5 text-gray-500 dark:text-gray-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-300">
              Upload failed
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {error}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
