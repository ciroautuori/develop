/**
 * CustomerAIMarketing - Customer-facing AI Marketing Hub
 * Simplified version of admin AIMarketing with customer restrictions
 */

import { useState, lazy, Suspense } from 'react';
import { motion } from 'framer-motion';
import {
  Wand2,
  Image,
  Video,
  Calendar,
  Send,
  Sparkles,
} from 'lucide-react';
import { cn } from '../../../shared/lib/utils';
import { TokenBalance } from '../components/TokenBalance';

// Lazy load content generators from admin
const ContentGenerator = lazy(() => import('../../admin/pages/AIMarketing/components/ContentGenerator'));
const ImageGenerator = lazy(() => import('../../admin/pages/AIMarketing/components/ImageGenerator'));
const VideoGenerator = lazy(() => import('../../admin/pages/AIMarketing/components/VideoGenerator'));
const CalendarManager = lazy(() => import('../../admin/pages/AIMarketing/components/CalendarManager'));

type TabId = 'content' | 'image' | 'video' | 'calendar';

interface Tab {
  id: TabId;
  label: string;
  icon: React.ElementType;
  color: string;
  tokens: string;
}

const TABS: Tab[] = [
  { id: 'content', label: 'Genera Testo', icon: Wand2, color: 'from-blue-500 to-cyan-500', tokens: '5-40' },
  { id: 'image', label: 'Crea Immagine', icon: Image, color: 'from-purple-500 to-pink-500', tokens: '15-80' },
  { id: 'video', label: 'Genera Video', icon: Video, color: 'from-pink-500 to-rose-500', tokens: '80-400' },
  { id: 'calendar', label: 'Calendario', icon: Calendar, color: 'from-emerald-500 to-teal-500', tokens: '0' },
];

const LoadingFallback = () => (
  <div className="flex items-center justify-center h-64">
    <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full" />
  </div>
);

export function CustomerAIMarketing() {
  const [activeTab, setActiveTab] = useState<TabId>('content');

  // Mock token data
  const tokenData = {
    balance: 1247,
    used: 753,
    total: 2000,
    planName: 'Growth',
  };

  const currentTab = TABS.find(t => t.id === activeTab);

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6">
      {/* Header with Token Balance */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4"
      >
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-foreground flex items-center gap-2">
            <Sparkles className="h-7 w-7 text-primary" />
            AI Marketing
          </h1>
          <p className="text-muted-foreground mt-1">
            Genera contenuti con intelligenza artificiale
          </p>
        </div>

        <TokenBalance
          balance={tokenData.balance}
          used={tokenData.used}
          total={tokenData.total}
          compact
        />
      </motion.div>

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
                {tab.tokens !== '0' && (
                  <span className="text-[10px] opacity-70">~{tab.tokens} token</span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Content */}
      <Suspense fallback={<LoadingFallback />}>
        {activeTab === 'content' && <ContentGenerator />}
        {activeTab === 'image' && <ImageGenerator />}
        {activeTab === 'video' && <VideoGenerator />}
        {activeTab === 'calendar' && <CalendarManager />}
      </Suspense>
    </div>
  );
}
