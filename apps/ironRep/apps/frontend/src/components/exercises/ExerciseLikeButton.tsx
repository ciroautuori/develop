/**
 * ExerciseLikeButton Component
 *
 * Provides like/dislike functionality for exercises.
 * Uses shadcn/ui design system.
 */
import { useState, useEffect, type ChangeEvent } from 'react';
import { Heart, HeartOff, Star, X } from 'lucide-react';
import { Button } from '../../shared/components/ui/button';
import { Input } from '../../shared/components/ui/input';
import { cn } from '../../lib/utils';
import { exercisePreferencesApi, type ExercisePreference } from '../../lib/api';
import { toast } from 'sonner';

interface ExerciseLikeButtonProps {
  exerciseId: string;
  exerciseName: string;
  variant?: 'default' | 'compact' | 'icon-only';
  className?: string;
  onPreferenceChange?: (preference: ExercisePreference | null) => void;
}

export function ExerciseLikeButton({
  exerciseId,
  exerciseName,
  variant = 'default',
  className,
  onPreferenceChange,
}: ExerciseLikeButtonProps) {
  const [preference, setPreference] = useState<ExercisePreference | null>(null);
  const [loading, setLoading] = useState(false);
  const [showRating, setShowRating] = useState(false);
  const [rating, setRating] = useState<number>(0);
  const [reason, setReason] = useState('');

  // Load existing preference
  useEffect(() => {
    const loadPreference = async () => {
      try {
        const pref = await exercisePreferencesApi.get(exerciseId);
        setPreference(pref);
        if (pref?.rating) setRating(pref.rating);
        if (pref?.reason) setReason(pref.reason);
      } catch {
        // No preference exists
      }
    };
    loadPreference();
  }, [exerciseId]);

  const handleLike = async () => {
    setLoading(true);
    try {
      const newPref = await exercisePreferencesApi.like(
        exerciseId,
        exerciseName,
        rating || undefined,
        reason || undefined
      );
      setPreference(newPref);
      onPreferenceChange?.(newPref);
      toast.success(`${exerciseName} aggiunto ai preferiti!`);
    } catch (error) {
      toast.error('Errore nel salvare la preferenza');
    } finally {
      setLoading(false);
    }
  };

  const handleDislike = async () => {
    setLoading(true);
    try {
      const newPref = await exercisePreferencesApi.dislike(
        exerciseId,
        exerciseName,
        reason || undefined
      );
      setPreference(newPref);
      onPreferenceChange?.(newPref);
      toast.success(`${exerciseName} aggiunto ai non preferiti`);
    } catch (error) {
      toast.error('Errore nel salvare la preferenza');
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async () => {
    setLoading(true);
    try {
      await exercisePreferencesApi.delete(exerciseId);
      setPreference(null);
      setRating(0);
      setReason('');
      onPreferenceChange?.(null);
      toast.success('Preferenza rimossa');
    } catch (error) {
      toast.error('Errore nel rimuovere la preferenza');
    } finally {
      setLoading(false);
    }
  };

  const isLiked = preference?.preference === 'like';
  const isDisliked = preference?.preference === 'dislike';

  if (variant === 'icon-only') {
    return (
      <div className={cn('flex gap-1', className)}>
        <Button
          variant="ghost"
          size="icon"
          onClick={isLiked ? handleRemove : handleLike}
          disabled={loading}
          className={cn(
            'h-10 w-10 touch-manipulation',
            isLiked && 'text-red-500 hover:text-red-600'
          )}
        >
          <Heart
            className={cn('h-5 w-5', isLiked && 'fill-current')}
          />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={isDisliked ? handleRemove : handleDislike}
          disabled={loading}
          className={cn(
            'h-10 w-10 touch-manipulation',
            isDisliked && 'text-gray-500'
          )}
        >
          <HeartOff
            className={cn('h-5 w-5', isDisliked && 'fill-current')}
          />
        </Button>
      </div>
    );
  }

  if (variant === 'compact') {
    return (
      <div className={cn('flex items-center gap-2', className)}>
        <Button
          variant={isLiked ? 'default' : 'outline'}
          size="sm"
          onClick={isLiked ? handleRemove : handleLike}
          disabled={loading}
          className={cn(
            'h-9 px-3 touch-manipulation',
            isLiked && 'bg-red-500 hover:bg-red-600'
          )}
        >
          <Heart className={cn('h-4 w-4 mr-1.5', isLiked && 'fill-current')} />
          {isLiked ? 'Liked' : 'Like'}
        </Button>
        <Button
          variant={isDisliked ? 'default' : 'outline'}
          size="sm"
          onClick={isDisliked ? handleRemove : handleDislike}
          disabled={loading}
          className={cn(
            'h-9 px-3 touch-manipulation',
            isDisliked && 'bg-gray-500 hover:bg-gray-600'
          )}
        >
          <HeartOff className={cn('h-4 w-4', isDisliked && 'fill-current')} />
        </Button>
      </div>
    );
  }

  // Default variant with modal for rating
  return (
    <div className={cn('relative', className)}>
      <div className="flex items-center gap-2">
        <Button
          variant={isLiked ? 'default' : 'outline'}
          size="sm"
          onClick={() => {
            if (isLiked) {
              handleRemove();
            } else {
              setShowRating(true);
            }
          }}
          disabled={loading}
          className={cn(
            'touch-manipulation',
            isLiked && 'bg-red-500 hover:bg-red-600 text-white'
          )}
        >
          <Heart className={cn('h-4 w-4 mr-2', isLiked && 'fill-current')} />
          {isLiked ? 'Mi piace' : 'Mi piace'}
        </Button>

        <Button
          variant={isDisliked ? 'default' : 'outline'}
          size="sm"
          onClick={isDisliked ? handleRemove : handleDislike}
          disabled={loading}
          className={cn(
            'touch-manipulation',
            isDisliked && 'bg-gray-500 hover:bg-gray-600 text-white'
          )}
        >
          <HeartOff className={cn('h-4 w-4 mr-2', isDisliked && 'fill-current')} />
          Non mi piace
        </Button>
      </div>

      {/* Rating Modal */}
      {showRating && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-background rounded-xl shadow-xl w-full max-w-sm p-5 space-y-4 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between">
              <h4 className="font-semibold text-lg">Valuta esercizio</h4>
              <button
                onClick={() => setShowRating(false)}
                className="p-1 rounded-full hover:bg-muted transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Rating</p>
              <div className="flex gap-1 justify-center">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => setRating(star)}
                    className="p-2 hover:scale-110 transition-transform touch-manipulation"
                  >
                    <Star
                      className={cn(
                        'h-8 w-8 transition-colors',
                        star <= rating
                          ? 'fill-yellow-400 text-yellow-400'
                          : 'text-gray-300'
                      )}
                    />
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm text-muted-foreground">
                Perché ti piace? (opzionale)
              </label>
              <Input
                value={reason}
                onChange={(e: ChangeEvent<HTMLInputElement>) => setReason(e.target.value)}
                placeholder="Es: Ottimo per la schiena..."
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowRating(false)}
              >
                Annulla
              </Button>
              <Button
                size="sm"
                onClick={() => {
                  handleLike();
                  setShowRating(false);
                }}
                disabled={loading}
              >
                Salva
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ExerciseLikeButton;
