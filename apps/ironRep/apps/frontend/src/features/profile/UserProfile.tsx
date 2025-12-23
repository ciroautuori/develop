import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { toast } from "sonner";
import { User, Mail, Calendar, Activity, Target, Link2 } from "lucide-react";
import { hapticFeedback } from "../../lib/haptics";
import { useProfile } from "./hooks/useProfile";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/Card";
import { cn } from "../../lib/utils";
import { GoogleConnectButton } from "../../components/integrations/GoogleConnectButton";
import { GoogleFitSync } from "../../components/integrations/GoogleFitSync";

const profileSchema = z.object({
  name: z.string().min(2, "Nome troppo corto"),
  email: z.string().email("Email non valida"),
  age: z.number().min(10).max(120).optional(),
  sex: z.enum(["M", "F", "O", ""]).optional(),
  diagnosis: z.string().optional(),
  injury_date: z.string().optional(),
  activity_level: z
    .enum([
      "sedentario",
      "leggermente_attivo",
      "moderatamente_attivo",
      "molto_attivo",
      "atleta",
      "",
    ])
    .optional(),
  primary_goal: z.string().optional(),
  goals_description: z.string().optional(),
  injury_description: z.string().optional(),
});

type ProfileFormData = z.infer<typeof profileSchema>;

interface UserProfileProps {
  userId?: string;
}

export function UserProfile({ userId }: UserProfileProps) {
  const { profile, isLoading, updateProfile, isUpdating } = useProfile(userId);
  const [isEditing, setIsEditing] = useState(false);

  const form = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
  });

  useEffect(() => {
    if (profile) {
      form.reset({
        name: profile.name,
        email: profile.email,
        age: profile.age,
        sex: (profile.sex as any) || "",
        diagnosis: profile.diagnosis || "",
        injury_date: profile.injury_date || "",
        activity_level: (profile.activity_level as any) || "",
        primary_goal: profile.primary_goal || "",
        goals_description: profile.goals_description || "",
        injury_description: profile.injury_description || "",
      });
    }
  }, [profile, form]);

  const onSubmit = async (values: ProfileFormData) => {
    try {
      hapticFeedback.impact("medium");
      await updateProfile(values);
      hapticFeedback.notification("success");
      toast.success("Profilo aggiornato con successo!");
      setIsEditing(false);
    } catch (error) {
      hapticFeedback.notification("error");
      toast.error("Errore nell'aggiornamento del profilo");
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Profilo non trovato</p>
      </div>
    );
  }

  return (
    <div className="space-y-4 sm:space-y-5 pb-20">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold">Profilo Utente</h2>
          <p className="text-sm text-muted-foreground">Gestisci le tue informazioni</p>
        </div>
        {!isEditing && (
          <Button
            onClick={() => {
              hapticFeedback.selection();
              setIsEditing(true);
            }}
            size="lg"
            className="w-full sm:w-auto"
          >
            Modifica Profilo
          </Button>
        )}
      </div>

      {/* Profile View */}
      {!isEditing ? (
        <div className="space-y-6">
          {/* Basic Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Informazioni Base</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 gap-4">
              <div className="flex items-center gap-3">
                <User className="text-muted-foreground" size={20} />
                <div>
                  <p className="text-sm text-muted-foreground">Nome</p>
                  <p className="font-medium">{profile.name}</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <Mail className="text-muted-foreground" size={20} />
                <div>
                  <p className="text-sm text-muted-foreground">Email</p>
                  <p className="font-medium">{profile.email}</p>
                </div>
              </div>

              {profile.age && (
                <div className="flex items-center gap-3">
                  <Calendar className="text-muted-foreground" size={20} />
                  <div>
                    <p className="text-sm text-muted-foreground">Età</p>
                    <p className="font-medium">{profile.age} anni</p>
                  </div>
                </div>
              )}

              {profile.sex && (
                <div className="flex items-center gap-3">
                  <User className="text-muted-foreground" size={20} />
                  <div>
                    <p className="text-sm text-muted-foreground">Sesso</p>
                    <p className="font-medium capitalize">{profile.sex}</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Fitness Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Fitness & Salute</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {profile.diagnosis && (
                <div className="flex items-start gap-3">
                  <Activity className="text-muted-foreground mt-1" size={20} />
                  <div>
                    <p className="text-sm text-muted-foreground">Diagnosi</p>
                    <p className="font-medium">{profile.diagnosis}</p>
                    {profile.injury_date && (
                      <p className="text-xs text-muted-foreground mt-1">
                        Dal:{" "}
                        {new Date(profile.injury_date).toLocaleDateString(
                          "it-IT"
                        )}
                      </p>
                    )}
                  </div>
                </div>
              )}

              {profile.activity_level && (
                <div className="flex items-center gap-3">
                  <Activity className="text-muted-foreground" size={20} />
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Livello Attività
                    </p>
                    <p className="font-medium capitalize">
                      {profile.activity_level.replace("_", " ")}
                    </p>
                  </div>
                </div>
              )}

              {(profile.primary_goal || profile.goals_description) && (
                <div className="flex items-start gap-3">
                  <Target className="text-muted-foreground mt-1" size={20} />
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">
                      Obiettivi
                    </p>
                    {profile.primary_goal && (
                      <p className="font-medium mb-1">{profile.primary_goal}</p>
                    )}
                    {profile.goals_description && (
                      <p className="text-sm text-muted-foreground">
                        {profile.goals_description}
                      </p>
                    )}
                  </div>
                </div>
              )}

              {profile.injury_description && (
                <div>
                  <p className="text-sm text-muted-foreground mb-2">
                    Descrizione Infortunio
                  </p>
                  <p className="text-sm bg-muted p-3 rounded-lg">
                    {profile.injury_description}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Google Integrations */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Link2 className="h-5 w-5" />
                Integrazioni Google
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground mb-4">
                Collega il tuo account Google per sincronizzare dati da Google Fit,
                aggiungere allenamenti al calendario e accedere a video tutorial.
              </p>
              <GoogleConnectButton />
              <GoogleFitSync />
            </CardContent>
          </Card>
        </div>
      ) : (
        /* Edit Form */
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Informazioni Base</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Nome *</label>
                  <Input
                    {...form.register("name")}
                    placeholder="Il tuo nome"
                  />
                  {form.formState.errors.name && (
                    <p className="text-sm text-destructive">
                      {form.formState.errors.name.message}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Email *</label>
                  <Input
                    type="email"
                    {...form.register("email")}
                    placeholder="email@example.com"
                  />
                  {form.formState.errors.email && (
                    <p className="text-sm text-destructive">
                      {form.formState.errors.email.message}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Età</label>
                  <Input
                    type="number"
                    {...form.register("age", { valueAsNumber: true })}
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Sesso</label>
                  <select
                    {...form.register("sex")}
                    className="flex h-11 w-full rounded-xl border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <option value="">Seleziona...</option>
                    <option value="M">Maschio</option>
                    <option value="F">Femmina</option>
                    <option value="O">Altro</option>
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Fitness & Salute</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Diagnosi</label>
                  <Input
                    {...form.register("diagnosis")}
                    placeholder="es. Ernia, Tendinite"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Data Infortunio</label>
                  <Input
                    type="date"
                    {...form.register("injury_date")}
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Livello Attività</label>
                  <select
                    {...form.register("activity_level")}
                    className="flex h-11 w-full rounded-xl border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <option value="">Seleziona...</option>
                    <option value="sedentario">Sedentario</option>
                    <option value="leggermente_attivo">Leggermente Attivo</option>
                    <option value="moderatamente_attivo">
                      Moderatamente Attivo
                    </option>
                    <option value="molto_attivo">Molto Attivo</option>
                    <option value="atleta">Atleta</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">
                    Obiettivo Principale
                  </label>
                  <Input
                    {...form.register("primary_goal")}
                    placeholder="es. Ritorno allo sport"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Descrizione Obiettivi
                </label>
                <textarea
                  {...form.register("goals_description")}
                  rows={2}
                  className="flex w-full rounded-xl border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
                  placeholder="Dettagli sui tuoi obiettivi..."
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Descrizione Infortunio
                </label>
                <textarea
                  {...form.register("injury_description")}
                  rows={4}
                  className="flex w-full rounded-xl border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
                  placeholder="Descrivi eventuali condizioni mediche rilevanti..."
                />
              </div>
            </CardContent>
          </Card>

          <div className="flex gap-3 pt-4">
            <Button
              type="submit"
              disabled={isUpdating}
              size="lg"
              className="flex-1"
            >
              {isUpdating ? "Salvataggio..." : "Salva Modifiche"}
            </Button>
            <Button
              type="button"
              variant="outline"
              size="lg"
              onClick={() => {
                setIsEditing(false);
                if (profile) {
                  form.reset({
                    name: profile.name,
                    email: profile.email,
                    age: profile.age,
                    sex: (profile.sex as any) || "",
                    diagnosis: profile.diagnosis || "",
                    injury_date: profile.injury_date || "",
                    activity_level: (profile.activity_level as any) || "",
                    primary_goal: profile.primary_goal || "",
                    goals_description: profile.goals_description || "",
                    injury_description: profile.injury_description || "",
                  });
                }
              }}
            >
              Annulla
            </Button>
          </div>
        </form>
      )}
    </div>
  );
}
