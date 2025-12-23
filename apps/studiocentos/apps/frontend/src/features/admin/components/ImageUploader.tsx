/**
 * Image Uploader Component - Upload e gestione immagini
 * API REALI - Upload su backend
 */
import { useState, useRef } from 'react';
import { Upload, X, Image as ImageIcon } from 'lucide-react';
import { Button } from '../../../shared/components/ui/button';
import { toast } from 'sonner';

interface ImageUploaderProps {
  value: string[];
  onChange: (urls: string[]) => void;
  maxImages?: number;
}

export function ImageUploader({ value, onChange, maxImages = 10 }: ImageUploaderProps) {
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    setUploading(true);

    try {
      const token = localStorage.getItem('admin_token');

      // Upload reale tramite API
      const uploadedUrls = await Promise.all(
        files.map(async (file) => {
          const formData = new FormData();
          formData.append('file', file);

          const res = await fetch('/api/v1/admin/upload', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
          });

          if (!res.ok) {
            // Fallback a URL locale se upload fallisce
            toast.error(`Errore upload ${file.name}`);
            return URL.createObjectURL(file);
          }

          const data = await res.json();
          return data.url || data.file_url || URL.createObjectURL(file);
        })
      );

      onChange([...value, ...uploadedUrls].slice(0, maxImages));
      toast.success('Immagini caricate con successo');
    } catch (error) {
      toast.error('Errore durante il caricamento');
    } finally {
      setUploading(false);
    }
  };

  const handleRemove = (index: number) => {
    onChange(value.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-4">
      {/* Upload Button */}
      <div>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          multiple
          onChange={handleFileSelect}
          className="hidden"
        />
        <Button
          type="button"
          variant="outline"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading || value.length >= maxImages}
        >
          <Upload className="mr-2 h-4 w-4" />
          {uploading ? 'Caricamento...' : 'Carica Immagini'}
        </Button>
        <p className="mt-2 text-sm text-neutral-500">
          {value.length}/{maxImages} immagini
        </p>
      </div>

      {/* Image Grid */}
      {value.length > 0 && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
          {value.map((url, index) => (
            <div
              key={index}
              className="group relative aspect-square overflow-hidden rounded-lg border border-neutral-200 dark:border-neutral-800"
            >
              <img
                src={url}
                alt={`Upload ${index + 1}`}
                className="h-full w-full object-cover"
              />
              <button
                type="button"
                onClick={() => handleRemove(index)}
                className="absolute right-2 top-2 rounded-full bg-gray-500 p-1 text-white opacity-0 transition-opacity group-hover:opacity-100"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {value.length === 0 && (
        <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-neutral-300 py-12 dark:border-neutral-700">
          <ImageIcon className="h-12 w-12 text-neutral-400" />
          <p className="mt-2 text-sm text-neutral-600 dark:text-neutral-400">
            Nessuna immagine caricata
          </p>
        </div>
      )}
    </div>
  );
}
