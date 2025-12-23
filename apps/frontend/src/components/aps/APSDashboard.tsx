import React, { useState, useEffect } from 'react';
import { 
  Building2, FileText, Star, Brain, Calendar, TrendingUp, 
  Users, Target, AlertCircle, CheckCircle, Clock, Plus,
  Eye, ThumbsUp, ThumbsDown, ExternalLink, Filter
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/utils/cn';

interface APSDashboardProps {
  userId: number;
  className?: string;
}

interface DashboardData {
  user: {
    id: number;
    organization_name: string;
    organization_type: string;
    sectors: string[];
    city?: string;
    created_at: string;
  };
  stats: {
    total_applications: number;
    successful_applications: number;
    pending_applications: number;
    success_rate: number;
    active_watchlist_count: number;
    unviewed_recommendations_count: number;
    upcoming_deadlines_count: number;
  };
  recent_applications: Application[];
  top_recommendations: Recommendation[];
  upcoming_deadlines: Deadline[];
}

interface Application {
  id: number;
  bando_id: number;
  status: 'submitted' | 'in_review' | 'approved' | 'rejected';
  application_date: string;
  project_title?: string;
  success_probability?: number;
  bando: {
    title: string;
    ente: string;
    scadenza?: string;
  };
}

interface Recommendation {
  id: number;
  bando_id: number;
  recommendation_score: number;
  reasoning: string;
  match_factors: Record<string, boolean>;
  created_at: string;
  viewed: boolean;
  bando: {
    title: string;
    ente: string;
    scadenza?: string;
    importo?: string;
  };
}

interface Deadline {
  bando: {
    id: number;
    title: string;
    ente: string;
    scadenza: string;
  };
  days_left: number;
  priority: 'high' | 'medium' | 'low';
}

const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const variants = {
    submitted: { variant: 'default' as const, icon: Clock, text: 'Inviata' },
    in_review: { variant: 'secondary' as const, icon: Eye, text: 'In Valutazione' },
    approved: { variant: 'default' as const, icon: CheckCircle, text: 'Approvata', className: 'bg-green-100 text-green-800' },
    rejected: { variant: 'destructive' as const, icon: AlertCircle, text: 'Respinta' }
  };

  const config = variants[status as keyof typeof variants];
  if (!config) return <Badge variant="outline">{status}</Badge>;

  const Icon = config.icon;
  return (
    <Badge variant={config.variant} className={config.className}>
      <Icon className="w-3 h-3 mr-1" />
      {config.text}
    </Badge>
  );
};

const PriorityBadge: React.FC<{ priority: string; daysLeft: number }> = ({ priority, daysLeft }) => {
  if (daysLeft <= 7) {
    return <Badge variant="destructive">Urgente</Badge>;
  } else if (daysLeft <= 30) {
    return <Badge className="bg-orange-100 text-orange-800">Prossimo</Badge>;
  } else {
    return <Badge variant="outline">Monitorato</Badge>;
  }
};

export const APSDashboard: React.FC<APSDashboardProps> = ({ userId, className }) => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<DashboardData | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadDashboardData();
  }, [userId]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/aps-users/${userId}/dashboard`);
      if (response.ok) {
        const dashboardData = await response.json();
        setData(dashboardData);
      }
    } catch (error) {
      console.error('Errore caricamento dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const markRecommendationViewed = async (recommendationId: number) => {
    try {
      await fetch(`/api/v1/aps-users/recommendations/${recommendationId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ viewed: true })
      });
      // Aggiorna data locale
      if (data) {
        setData({
          ...data,
          top_recommendations: data.top_recommendations.map(r => 
            r.id === recommendationId ? { ...r, viewed: true } : r
          ),
          stats: {
            ...data.stats,
            unviewed_recommendations_count: Math.max(0, data.stats.unviewed_recommendations_count - 1)
          }
        });
      }
    } catch (error) {
      console.error('Errore aggiornamento raccomandazione:', error);
    }
  };

  const generateNewRecommendations = async () => {
    try {
      await fetch(`/api/v1/aps-users/${userId}/generate-recommendations`, {
        method: 'POST'
      });
      // Ricarica dashboard dopo qualche secondo
      setTimeout(loadDashboardData, 3000);
    } catch (error) {
      console.error('Errore generazione raccomandazioni:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">Errore caricamento dashboard</p>
      </div>
    );
  }

  return (
    <div className={cn("max-w-7xl mx-auto p-6", className)}>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Building2 className="h-8 w-8 text-blue-600" />
              {data.user.organization_name}
            </h1>
            <p className="text-gray-600 mt-1">
              {data.user.organization_type.toUpperCase()} • {data.user.city || 'Campania'} • 
              Membro dal {new Date(data.user.created_at).toLocaleDateString('it-IT')}
            </p>
          </div>
          <Button onClick={generateNewRecommendations} className="gap-2">
            <Brain className="h-4 w-4" />
            Aggiorna AI
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Candidature Totali</p>
                <p className="text-3xl font-bold text-gray-900">{data.stats.total_applications}</p>
              </div>
              <FileText className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Tasso Successo</p>
                <p className="text-3xl font-bold text-green-600">{data.stats.success_rate.toFixed(1)}%</p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-600" />
            </div>
            <div className="mt-2">
              <Progress value={data.stats.success_rate} className="h-2" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">In Watchlist</p>
                <p className="text-3xl font-bold text-gray-900">{data.stats.active_watchlist_count}</p>
              </div>
              <Star className="h-8 w-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Raccomandazioni AI</p>
                <p className="text-3xl font-bold text-purple-600">{data.stats.unviewed_recommendations_count}</p>
              </div>
              <Brain className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Panoramica</TabsTrigger>
          <TabsTrigger value="applications">Candidature</TabsTrigger>
          <TabsTrigger value="recommendations">AI Consigli</TabsTrigger>
          <TabsTrigger value="deadlines">Scadenze</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Applications */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Candidature Recenti
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {data.recent_applications.slice(0, 5).map((app) => (
                    <div key={app.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex-1">
                        <h4 className="font-medium text-sm">{app.bando.title.substring(0, 60)}...</h4>
                        <p className="text-xs text-gray-600">{app.bando.ente}</p>
                        <p className="text-xs text-gray-500">
                          {new Date(app.application_date).toLocaleDateString('it-IT')}
                        </p>
                      </div>
                      <div className="flex flex-col items-end gap-2">
                        <StatusBadge status={app.status} />
                        {app.success_probability && (
                          <div className="text-xs text-gray-600">
                            AI: {(app.success_probability * 100).toFixed(0)}%
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  {data.recent_applications.length === 0 && (
                    <p className="text-gray-500 text-center py-4">Nessuna candidatura ancora</p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Top AI Recommendations */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5" />
                  Raccomandazioni AI
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {data.top_recommendations.slice(0, 3).map((rec) => (
                    <div 
                      key={rec.id} 
                      className={cn(
                        "p-3 rounded-lg border transition-colors",
                        rec.viewed ? "bg-gray-50 border-gray-200" : "bg-blue-50 border-blue-200"
                      )}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium text-sm">{rec.bando.title.substring(0, 50)}...</h4>
                          <p className="text-xs text-gray-600 mb-2">{rec.bando.ente}</p>
                          <p className="text-xs text-blue-600">{rec.reasoning}</p>
                          
                          {/* Match Factors */}
                          <div className="flex flex-wrap gap-1 mt-2">
                            {Object.entries(rec.match_factors).map(([factor, matches]) => 
                              matches && (
                                <Badge key={factor} variant="outline" className="text-xs">
                                  {factor.replace('_match', '').replace('_', ' ')}
                                </Badge>
                              )
                            )}
                          </div>
                        </div>
                        <div className="flex flex-col items-end gap-2">
                          <Badge className="bg-purple-100 text-purple-800">
                            {(rec.recommendation_score * 100).toFixed(0)}%
                          </Badge>
                          {!rec.viewed && (
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => markRecommendationViewed(rec.id)}
                            >
                              <Eye className="h-3 w-3" />
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                  {data.top_recommendations.length === 0 && (
                    <div className="text-center py-4">
                      <Brain className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                      <p className="text-gray-500 text-sm">Nessuna raccomandazione AI disponibile</p>
                      <Button size="sm" className="mt-2" onClick={generateNewRecommendations}>
                        Genera Raccomandazioni
                      </Button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Upcoming Deadlines */}
          {data.upcoming_deadlines.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  Scadenze Imminenti
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {data.upcoming_deadlines.map((deadline, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-medium text-sm">{deadline.bando.title.substring(0, 40)}...</h4>
                        <PriorityBadge priority={deadline.priority} daysLeft={deadline.days_left} />
                      </div>
                      <p className="text-xs text-gray-600 mb-2">{deadline.bando.ente}</p>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-red-600">
                          {deadline.days_left} giorni rimasti
                        </span>
                        <Button size="sm" variant="outline">
                          <ExternalLink className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Applications Tab */}
        <TabsContent value="applications">
          <Card>
            <CardHeader>
              <CardTitle>Tutte le Candidature</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {data.recent_applications.map((app) => (
                  <div key={app.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <h4 className="font-medium">{app.project_title || 'Candidatura'}</h4>
                      <p className="text-sm text-gray-600">{app.bando.title}</p>
                      <p className="text-xs text-gray-500">
                        Inviata: {new Date(app.application_date).toLocaleDateString('it-IT')}
                      </p>
                    </div>
                    <div className="flex items-center gap-4">
                      {app.success_probability && (
                        <div className="text-center">
                          <p className="text-xs text-gray-600">Probabilità</p>
                          <p className="font-semibold">{(app.success_probability * 100).toFixed(0)}%</p>
                        </div>
                      )}
                      <StatusBadge status={app.status} />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Recommendations Tab */}
        <TabsContent value="recommendations">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Raccomandazioni AI Personalizzate</CardTitle>
                <Button onClick={generateNewRecommendations} size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Genera Nuove
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {data.top_recommendations.map((rec) => (
                  <div key={rec.id} className="p-4 border rounded-lg">
                    <div className="flex items-start justify-between mb-3">
                      <h4 className="font-medium">{rec.bando.title}</h4>
                      <Badge className="bg-purple-100 text-purple-800">
                        {(rec.recommendation_score * 100).toFixed(0)}% Match
                      </Badge>
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-2">{rec.bando.ente}</p>
                    
                    {rec.bando.importo && (
                      <p className="text-sm text-green-600 mb-2">💰 {rec.bando.importo}</p>
                    )}
                    
                    <p className="text-sm text-blue-600 mb-3">{rec.reasoning}</p>
                    
                    <div className="flex flex-wrap gap-2 mb-3">
                      {Object.entries(rec.match_factors).map(([factor, matches]) => 
                        matches && (
                          <Badge key={factor} variant="outline" className="text-xs">
                            ✓ {factor.replace('_match', '').replace('_', ' ')}
                          </Badge>
                        )
                      )}
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">
                        {new Date(rec.created_at).toLocaleDateString('it-IT')}
                      </span>
                      <div className="flex gap-2">
                        {!rec.viewed && (
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => markRecommendationViewed(rec.id)}
                          >
                            <Eye className="h-3 w-3 mr-1" />
                            Visto
                          </Button>
                        )}
                        <Button size="sm">
                          Vai al Bando
                          <ExternalLink className="h-3 w-3 ml-1" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Deadlines Tab */}
        <TabsContent value="deadlines">
          <Card>
            <CardHeader>
              <CardTitle>Gestione Scadenze</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {data.upcoming_deadlines.map((deadline, index) => (
                  <div key={index} className="p-4 border rounded-lg">
                    <div className="flex items-start justify-between mb-3">
                      <h4 className="font-medium">{deadline.bando.title}</h4>
                      <PriorityBadge priority={deadline.priority} daysLeft={deadline.days_left} />
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-2">{deadline.bando.ente}</p>
                    
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-red-600">
                          {deadline.days_left} giorni rimasti
                        </p>
                        <p className="text-xs text-gray-500">
                          Scade: {new Date(deadline.bando.scadenza).toLocaleDateString('it-IT')}
                        </p>
                      </div>
                      
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline">
                          <Star className="h-3 w-3" />
                        </Button>
                        <Button size="sm">
                          <ExternalLink className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
                
                {data.upcoming_deadlines.length === 0 && (
                  <div className="col-span-full text-center py-8">
                    <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">Nessuna scadenza imminente</p>
                    <p className="text-sm text-gray-500">Le scadenze dei bandi in watchlist appariranno qui</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};
