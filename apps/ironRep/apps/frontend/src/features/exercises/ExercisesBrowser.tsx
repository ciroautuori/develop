import { useState, useEffect } from "react";
import { Search } from "lucide-react";
import { exercisesApi, type ExerciseDetail } from "../../lib/api";
import { ExerciseDetailModal } from "../../components/ui/ExerciseDetailModal";
import { toast } from "sonner";

const PHASES = ["warm_up", "technical_work", "conditioning", "cool_down"];

export function ExercisesBrowser() {
  const [exercises, setExercises] = useState<ExerciseDetail[]>([]);
  const [filteredExercises, setFilteredExercises] = useState<ExerciseDetail[]>(
    []
  );
  const [selectedExercise, setSelectedExercise] =
    useState<ExerciseDetail | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedPhase, setSelectedPhase] = useState<string>("all");

  useEffect(() => {
    loadExercises();
  }, []);

  useEffect(() => {
    filterExercises();
  }, [searchQuery, selectedPhase, exercises]);

  const loadExercises = async () => {
    try {
      setIsLoading(true);
      const response = await exercisesApi.getAll(500, 0);
      const exercisesList = response.exercises || [];
      setExercises(exercisesList);
      setFilteredExercises(exercisesList);
    } catch (error) {
      console.error("Error loading exercises:", error);
      toast.error("Errore nel caricamento degli esercizi");
    } finally {
      setIsLoading(false);
    }
  };

  const filterExercises = () => {
    let filtered = exercises;

    // Filter by phase
    if (selectedPhase !== "all") {
      filtered = filtered.filter((ex) => ex.phase === selectedPhase);
    }

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (ex) =>
          ex.name.toLowerCase().includes(query) ||
          ex.category.toLowerCase().includes(query) ||
          ex.target_muscles.some((m) => m.toLowerCase().includes(query))
      );
    }

    setFilteredExercises(filtered);
  };

  const handleExerciseClick = (exercise: ExerciseDetail) => {
    setSelectedExercise(exercise);
    setIsModalOpen(true);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold mb-1 sm:mb-2">Database Esercizi</h1>
        <p className="text-sm sm:text-base text-muted-foreground">
          {filteredExercises?.length || 0} esercizi disponibili
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col gap-3 sm:gap-4">
        {/* Search */}
        <div className="relative">
          <Search
            className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground"
            size={20}
          />
          <input
            type="text"
            placeholder="Cerca esercizi, muscoli..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-11 pr-4 py-3.5 sm:py-3 border rounded-xl sm:rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary text-base touch-manipulation"
          />
        </div>

        {/* Phase Filter - Horizontal scroll on mobile */}
        <div className="flex gap-2 overflow-x-auto pb-1 -mx-3 px-3 sm:mx-0 sm:px-0 no-scrollbar">
          <button
            onClick={() => setSelectedPhase("all")}
            className={`flex-shrink-0 px-4 py-2.5 rounded-xl text-sm font-medium transition-all touch-manipulation ${
              selectedPhase === "all"
                ? "bg-primary text-primary-foreground"
                : "bg-secondary text-secondary-foreground"
            }`}
          >
            Tutte
          </button>
          {PHASES.map((phase) => (
            <button
              key={phase}
              onClick={() => setSelectedPhase(phase)}
              className={`flex-shrink-0 px-4 py-2.5 rounded-xl text-sm font-medium transition-all whitespace-nowrap touch-manipulation ${
                selectedPhase === phase
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary text-secondary-foreground"
              }`}
            >
              {phase.replace("_", " ").replace(/\b\w/g, l => l.toUpperCase())}
            </button>
          ))}
        </div>
      </div>

      {/* Exercise Grid */}
      {!filteredExercises || filteredExercises.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">
            Nessun esercizio trovato con i filtri selezionati
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
          {filteredExercises.map((exercise) => (
            <div
              key={exercise.id}
              onClick={() => handleExerciseClick(exercise)}
              className="border rounded-xl p-4 sm:p-4 hover:shadow-lg active:scale-[0.98] transition-all cursor-pointer bg-card touch-manipulation"
            >
              <h3 className="font-semibold text-base sm:text-lg mb-1.5 sm:mb-2 leading-tight">{exercise.name}</h3>
              <p className="text-sm text-muted-foreground mb-2 sm:mb-3">
                {exercise.category}
              </p>

              {/* Phase Badge */}
              <span className="inline-block px-2 py-1 bg-primary/10 text-primary text-xs rounded-full mb-3">
                {exercise.phase.replace("_", " ").toUpperCase()}
              </span>

              {/* Target Muscles */}
              {exercise.target_muscles.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {exercise.target_muscles.slice(0, 3).map((muscle, i) => (
                    <span
                      key={i}
                      className="text-xs px-2 py-1 bg-muted rounded-full"
                    >
                      {muscle}
                    </span>
                  ))}
                  {exercise.target_muscles.length > 3 && (
                    <span className="text-xs px-2 py-1 bg-muted rounded-full">
                      +{exercise.target_muscles.length - 3}
                    </span>
                  )}
                </div>
              )}

              {/* Equipment */}
              {exercise.equipment.length > 0 && (
                <p className="text-xs text-muted-foreground mt-2">
                  🏋️ {exercise.equipment.join(", ")}
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Exercise Detail Modal */}
      <ExerciseDetailModal
        exercise={selectedExercise}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  );
}
