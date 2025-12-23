/**
 * AI Marketing Hub - PRODUCTION READY v2.0
 * =============================================
 * ARCHITETTURA: Tab Navigation + Full Components
 *
 * TABS:
 * - Dashboard: KPIs + Calendar + Quick Actions
 * - Trova Clienti: AcquisitionWizard (1-click funnel)
 * - Crea Contenuti: Video + Social + Email creation
 * - Analytics: MarketingAnalyticsPro (GA4 + Social)
 * - Impostazioni: Brand DNA + Connections
 */

import React, { useState, Suspense, lazy } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Zap, Target, Sparkles, BarChart3, Settings, Send, Video,
  Mail, LayoutDashboard, Loader2, Wand2,
  MessageSquare, Calendar, Layers, Database, FlaskConical, Eye, Webhook,
  Globe, Search, Activity
} from 'lucide-react';
import { useTheme } from '../../../../shared/contexts/ThemeContext';
import { cn } from '../../../../shared/utils/cn';
import { SPACING } from '../../../../shared/config/constants';
import { ErrorBoundary } from '../../../../shared/components/error/ErrorBoundary';
import { Button } from '../../../../shared/components/ui/button';

// Dashboard Components (always loaded)
import { WeeklyCalendar } from './components/dashboard';
import { ConversionDashboard } from './components/ConversionDashboard';

// Modals (lightweight quick actions)
import { SettingsModal } from './components/modals';

// Full Power Components (lazy loaded per tab)
const SocialPublisherPro = lazy(() => import('./components/SocialPublisherPro'));
const EmailCampaignPro = lazy(() => import('./components/EmailCampaignPro'));
const VideoStoryCreator = lazy(() => import('./components/VideoStoryCreator').then(m => ({ default: m.VideoStoryCreator })));
const MarketingAnalyticsPro = lazy(() => import('./components/MarketingAnalyticsPro'));
const BusinessDNAGenerator = lazy(() => import('./components/BusinessDNAGenerator').then(m => ({ default: m.BusinessDNAGenerator })));
// ContentGenerator non usato - ContentStudio è il componente principale
const ContentStudio = lazy(() => import('./components/ContentStudio'));
const CalendarManager = lazy(() => import('./components/CalendarManager'));
const BatchContentModal = lazy(() => import('./components/BatchContentModal').then(m => ({ default: m.BatchContentModal })));
const KnowledgeBaseManager = lazy(() => import('./components/KnowledgeBaseManager'));
const WorkflowBuilder = lazy(() => import('./components/WorkflowBuilder'));
const ABTestingManager = lazy(() => import('./components/ABTestingManager'));
const CompetitorMonitor = lazy(() => import('./components/CompetitorMonitor'));
const WebhookManager = lazy(() => import('./components/WebhookManager'));
const LeadFinderInline = lazy(() => import('./components/LeadFinderInline'));

// Analytics Components (integrati da pages/)
const AnalyticsGA4 = lazy(() => import('../AnalyticsGA4').then(m => ({ default: m.AnalyticsGA4 })));
const AnalyticsSEO = lazy(() => import('../AnalyticsSEO'));

// ============================================================================
// TYPES
// ============================================================================

type TabId = 'dashboard' | 'acquisition' | 'content' | 'analytics' | 'settings';
type ContentSubTab = 'templates' | 'video' | 'social' | 'email';
type AnalyticsSubTab = 'performance' | 'ga4' | 'seo' | 'abtesting' | 'competitors';
type SettingsSubTab = 'brand' | 'knowledge' | 'workflows' | 'webhooks' | 'calendar';

interface Tab {
  id: TabId;
  label: string;
  icon: React.ElementType;
  description: string;
  color: string;
}

// ============================================================================
// CONSTANTS - 6 TAB PRINCIPALI
// ============================================================================

const TABS: Tab[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: LayoutDashboard,
    description: 'KPIs e panoramica generale',
    color: 'from-amber-500 to-yellow-500', // Gold-like
  },
  {
    id: 'acquisition',
    label: 'Trova Clienti',
    icon: Target,
    description: 'Lead finder + Email automation',
    color: 'from-emerald-500 to-teal-500',
  },
  {
    id: 'content',
    label: 'Crea Contenuti',
    icon: Sparkles,
    description: 'Video, Social, Email con AI',
    color: 'from-purple-500 to-indigo-500',
  },
  {
    id: 'analytics',
    label: 'Analytics',
    icon: BarChart3,
    description: 'Performance, A/B Test, Competitor',
    color: 'from-blue-500 to-cyan-500',
  },
  {
    id: 'settings',
    label: 'Impostazioni',
    icon: Settings,
    description: 'Brand, Automazioni, Integrazioni',
    color: 'from-gray-500 to-gray-600',
  },
];

// Sub-tabs per sezioni con sotto-opzioni
const CONTENT_SUB_TABS = [
  { id: 'templates' as ContentSubTab, label: 'Template Veloci', icon: Wand2 },
  { id: 'video' as ContentSubTab, label: 'Video & Stories', icon: Video },
  { id: 'social' as ContentSubTab, label: 'Social Post', icon: Send },
  { id: 'email' as ContentSubTab, label: 'Email Marketing', icon: Mail },
];

const ANALYTICS_SUB_TABS = [
  { id: 'performance' as AnalyticsSubTab, label: 'Performance', icon: Activity },
  { id: 'ga4' as AnalyticsSubTab, label: 'Google Analytics', icon: Globe },
  { id: 'seo' as AnalyticsSubTab, label: 'SEO', icon: Search },
  { id: 'abtesting' as AnalyticsSubTab, label: 'A/B Testing', icon: FlaskConical },
  { id: 'competitors' as AnalyticsSubTab, label: 'Competitor', icon: Eye },
];


const SETTINGS_SUB_TABS = [
  { id: 'brand' as SettingsSubTab, label: 'Brand DNA', icon: Layers },
  { id: 'knowledge' as SettingsSubTab, label: 'Knowledge Base', icon: Database },
  { id: 'workflows' as SettingsSubTab, label: 'Automazioni', icon: Zap },
  { id: 'webhooks' as SettingsSubTab, label: 'Webhooks', icon: Webhook },
  { id: 'calendar' as SettingsSubTab, label: 'Calendario', icon: Calendar },
];

// ============================================================================
// LOADING COMPONENT
// ============================================================================

function TabLoader() {
  return (
    <div className="flex items-center justify-center py-20">
      <Loader2 className="w-8 h-8 animate-spin text-primary" />
      <span className="ml-3 text-muted-foreground">Caricamento...</span>
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function AIMarketing() {
  const { theme } = useTheme();

  // Tab State
  const [activeTab, setActiveTab] = useState<TabId>('dashboard');
  const [contentSubTab, setContentSubTab] = useState<ContentSubTab>('templates');
  const [analyticsSubTab, setAnalyticsSubTab] = useState<AnalyticsSubTab>('performance');
  const [settingsSubTab, setSettingsSubTab] = useState<SettingsSubTab>('brand');

  // Modal States
  const [isPostModalOpen, setIsPostModalOpen] = useState(false);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);
  const [isBatchModalOpen, setIsBatchModalOpen] = useState(false);

  // ============================================================================
  // RENDER DASHBOARD TAB
  // ============================================================================

  const renderDashboard = () => (
    <div className="space-y-6">
      {/* Weekly Calendar - Principale */}
      <motion.section
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <WeeklyCalendar
          onAddItem={() => { setActiveTab('content'); setContentSubTab('social'); }}
          onItemClick={() => { setActiveTab('content'); }}
        />
      </motion.section>

      {/* Conversion Dashboard - Pipeline Reale */}
      <motion.section
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <ConversionDashboard />
      </motion.section>

      {/* 🚀 BATCH CONTENT - Genera Campagna Completa */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="p-6 rounded-2xl border bg-gradient-to-r from-purple-500/10 to-indigo-500/10 border-purple-500/20"
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-r from-purple-500 to-indigo-500 flex items-center justify-center flex-shrink-0">
              <Layers className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="font-bold text-foreground">🚀 Genera Campagna AI Completa</h3>
              <p className="text-sm text-muted-foreground">
                1 topic → 4 post social + 3 stories + 1 video script
              </p>
            </div>
          </div>
          <Button
            onClick={() => setIsBatchModalOpen(true)}
            className="w-full sm:w-auto bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600 text-white"
          >
            <Sparkles className="w-4 h-4 mr-2" />
            Genera Tutto
          </Button>
        </div>
      </motion.div>
    </div>
  );

  // ============================================================================
  // RENDER SUB-TAB NAVIGATION (riutilizzabile)
  // ============================================================================

  const renderSubTabNav = <T extends string>(
    tabs: { id: T; label: string; icon: React.ElementType }[],
    activeSubTab: T,
    setActiveSubTab: (tab: T) => void
  ) => (
    <div className="flex gap-2 p-1 rounded-xl bg-muted/50 mb-6 overflow-x-auto scrollbar-hide">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        return (
          <button
            key={tab.id}
            onClick={() => setActiveSubTab(tab.id)}
            className={cn(
              'flex-shrink-0 min-w-max flex items-center justify-center gap-2 py-3 px-4 rounded-lg text-sm font-medium transition-all whitespace-nowrap',
              activeSubTab === tab.id
                ? 'bg-background text-foreground shadow-sm border border-border'
                : 'text-muted-foreground hover:text-foreground hover:bg-background/50'
            )}
          >
            <Icon className="w-4 h-4" />
            {tab.label}
          </button>
        );
      })}
    </div>
  );

  // ============================================================================
  // RENDER TABS
  // ============================================================================

  const renderAnalyticsTab = () => (
    <div>
      {renderSubTabNav(ANALYTICS_SUB_TABS, analyticsSubTab, (tab) => setAnalyticsSubTab(tab as AnalyticsSubTab))}
      <Suspense fallback={<TabLoader />}>
        <AnimatePresence mode="wait">
          {analyticsSubTab === 'performance' && (
            <motion.div key="perf" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <MarketingAnalyticsPro />
            </motion.div>
          )}
          {analyticsSubTab === 'ga4' && (
            <motion.div key="ga4" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <AnalyticsGA4 />
            </motion.div>
          )}
          {analyticsSubTab === 'seo' && (
            <motion.div key="seo" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <AnalyticsSEO />
            </motion.div>
          )}
          {analyticsSubTab === 'abtesting' && (
            <motion.div key="ab" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <ABTestingManager />
            </motion.div>
          )}
          {analyticsSubTab === 'competitors' && (
            <motion.div key="comp" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <CompetitorMonitor />
            </motion.div>
          )}
        </AnimatePresence>
      </Suspense>
    </div>
  );

  const renderSettingsTab = () => (
    <div>
      {renderSubTabNav(SETTINGS_SUB_TABS, settingsSubTab, (tab) => setSettingsSubTab(tab as SettingsSubTab))}
      <Suspense fallback={<TabLoader />}>
        <AnimatePresence mode="wait">
          {settingsSubTab === 'brand' && (
            <motion.div key="brand" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <BusinessDNAGenerator />
            </motion.div>
          )}
          {settingsSubTab === 'knowledge' && (
            <motion.div key="kb" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <KnowledgeBaseManager />
            </motion.div>
          )}
          {settingsSubTab === 'workflows' && (
            <motion.div key="wf" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <WorkflowBuilder />
            </motion.div>
          )}
          {settingsSubTab === 'webhooks' && (
            <motion.div key="wh" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <WebhookManager />
            </motion.div>
          )}
          {settingsSubTab === 'calendar' && (
            <motion.div key="cal" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <CalendarManager />
            </motion.div>
          )}
        </AnimatePresence>
      </Suspense>
    </div>
  );

  const renderContentTab = () => (
    <Suspense fallback={<TabLoader />}>
      <ContentStudio />
    </Suspense>
  );

  // ============================================================================
  // MAIN RENDER
  // ============================================================================

  return (
    <ErrorBoundary>
      <div className={cn(SPACING.padding.full, 'space-y-4 sm:space-y-6')}>
        {/* Header with Tab Navigation */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          {/* Title Row */}
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center shadow-lg shadow-primary/20">
              <Zap className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-foreground">
                Marketing Hub AI
              </h1>
              <p className="text-sm text-muted-foreground">
                {TABS.find(t => t.id === activeTab)?.description}
              </p>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="bg-card border border-border rounded-2xl p-2 shadow-sm">
            <div className="flex gap-1 overflow-x-auto">
              {TABS.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;

                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={cn(
                      'flex-1 min-w-[120px] flex flex-col items-center gap-1 py-3 px-4 rounded-xl transition-all',
                      isActive
                        ? `bg-gradient-to-r ${tab.color} text-white shadow-lg`
                        : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                    )}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="text-xs font-medium whitespace-nowrap">{tab.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </motion.div>

        {/* Tab Content */}
        <Suspense fallback={<TabLoader />}>
          <AnimatePresence mode="wait">
            {activeTab === 'dashboard' && (
              <motion.div
                key="dashboard"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                {renderDashboard()}
              </motion.div>
            )}

            {activeTab === 'acquisition' && (
              <motion.div
                key="acquisition"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="bg-card border border-border rounded-2xl p-6 shadow-sm"
              >
                <Suspense fallback={<TabLoader />}>
                  <LeadFinderInline
                    onCreateEmailCampaign={() => { setActiveTab('content'); setContentSubTab('email'); }}
                  />
                </Suspense>
              </motion.div>
            )}

            {activeTab === 'content' && (
              <motion.div
                key="content"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                {renderContentTab()}
              </motion.div>
            )}

            {activeTab === 'analytics' && (
              <motion.div
                key="analytics"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                {renderAnalyticsTab()}
              </motion.div>
            )}

            {activeTab === 'settings' && (
              <motion.div
                key="settings"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                {renderSettingsTab()}
              </motion.div>
            )}
          </AnimatePresence>
        </Suspense>
      </div>

      {/* Quick Action Modals */}
      <SettingsModal isOpen={isSettingsModalOpen} onClose={() => setIsSettingsModalOpen(false)} />

      {/* Batch Content Modal */}
      <Suspense fallback={null}>
        {isBatchModalOpen && (
          <BatchContentModal
            isOpen={isBatchModalOpen}
            onClose={() => setIsBatchModalOpen(false)}
            onSuccess={() => {
              setIsBatchModalOpen(false);
            }}
          />
        )}
      </Suspense>
    </ErrorBoundary>
  );
}
