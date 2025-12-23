/**
 * ExerciseVideoEmbed - YouTube video embed for exercises
 */
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Play, ExternalLink, Loader2, Youtube, ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "../../lib/utils";

const API_BASE =
  import.meta.env.VITE_API_URL ||
  (typeof window !== "undefined" ? window.location.origin : "");

interface VideoResult { video_id: string; title: string; description: string; thumbnail: string; channel: string; embed_url: string; watch_url: string; }

async function searchExerciseVideos(query: string): Promise<{ videos: VideoResult[] }> {
  const response = await fetch(`${API_BASE}/api/google/youtube/search?query=${encodeURIComponent(query)}&max_results=5`);
  if (!response.ok) throw new Error("Video search failed");
  return response.json();
}

interface Props { exerciseName: string; showSearch?: boolean; autoPlay?: boolean; className?: string; }

export function ExerciseVideoEmbed({ exerciseName, autoPlay = false, className }: Props) {
  const [selectedVideo, setSelectedVideo] = useState<VideoResult | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);

  const { data, isLoading, error } = useQuery({
    queryKey: ["youtube-search", exerciseName],
    queryFn: () => searchExerciseVideos(exerciseName),
    enabled: !!exerciseName && exerciseName.length > 2,
    staleTime: 5 * 60 * 1000,
  });

  const videos = data?.videos || [];

  if (isLoading) return <div className={cn("flex items-center justify-center p-8 bg-muted/50 rounded-xl", className)}><Loader2 className="w-6 h-6 animate-spin text-muted-foreground" /><span className="ml-2 text-muted-foreground">Cercando video...</span></div>;
  if (error || videos.length === 0) return <div className={cn("flex flex-col items-center justify-center p-8 bg-muted/50 rounded-xl", className)}><Youtube className="w-8 h-8 text-muted-foreground mb-2" /><span className="text-muted-foreground text-sm text-center">Nessun video per "{exerciseName}"</span></div>;

  if (selectedVideo) {
    return (
      <div className={cn("rounded-xl overflow-hidden bg-black", className)}>
        <div className="relative aspect-video"><iframe src={`${selectedVideo.embed_url}${autoPlay ? "?autoplay=1" : ""}`} title={selectedVideo.title} allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen className="absolute inset-0 w-full h-full" /></div>
        <div className="p-3 bg-gray-900 text-white">
          <div className="font-medium text-sm line-clamp-1">{selectedVideo.title}</div>
          <div className="flex items-center justify-between mt-1">
            <span className="text-xs text-gray-400">{selectedVideo.channel}</span>
            <div className="flex items-center gap-2">
              <a href={selectedVideo.watch_url} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1">YouTube <ExternalLink className="w-3 h-3" /></a>
              <button onClick={() => setSelectedVideo(null)} className="text-xs text-gray-400 hover:text-white">Chiudi</button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const currentVideo = videos[currentIndex];
  return (
    <div className={cn("rounded-xl overflow-hidden", className)}>
      <div className="relative aspect-video bg-gray-900">
        <img src={currentVideo.thumbnail} alt={currentVideo.title} className="w-full h-full object-cover" />
        <button onClick={() => setSelectedVideo(currentVideo)} className="absolute inset-0 flex items-center justify-center bg-black/40 hover:bg-black/50 transition-colors group">
          <div className="w-16 h-16 bg-red-600 rounded-full flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform"><Play className="w-8 h-8 text-white fill-white ml-1" /></div>
        </button>
        {videos.length > 1 && (<><button onClick={() => setCurrentIndex(i => i > 0 ? i - 1 : videos.length - 1)} className="absolute left-2 top-1/2 -translate-y-1/2 p-2 bg-black/50 rounded-full text-white hover:bg-black/70"><ChevronLeft className="w-5 h-5" /></button><button onClick={() => setCurrentIndex(i => i < videos.length - 1 ? i + 1 : 0)} className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-black/50 rounded-full text-white hover:bg-black/70"><ChevronRight className="w-5 h-5" /></button></>)}
        {videos.length > 1 && <div className="absolute bottom-2 right-2 px-2 py-1 bg-black/70 rounded text-white text-xs">{currentIndex + 1} / {videos.length}</div>}
      </div>
      <div className="p-3 bg-secondary/50"><div className="font-medium text-sm line-clamp-2">{currentVideo.title}</div><div className="flex items-center gap-2 mt-1"><Youtube className="w-4 h-4 text-red-600" /><span className="text-xs text-muted-foreground">{currentVideo.channel}</span></div></div>
      {videos.length > 1 && <div className="flex justify-center gap-1 p-2 bg-secondary/30">{videos.map((_, idx) => <button key={idx} onClick={() => setCurrentIndex(idx)} className={cn("w-2 h-2 rounded-full transition-colors", idx === currentIndex ? "bg-primary" : "bg-muted-foreground/30")} />)}</div>}
    </div>
  );
}

export default ExerciseVideoEmbed;
