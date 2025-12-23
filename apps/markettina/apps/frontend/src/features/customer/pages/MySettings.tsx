/**
 * MySettings - Customer account settings
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  User,
  Mail,
  Lock,
  Bell,
  CreditCard,
  Link2,
  Shield,
  Save,
  Instagram,
  Facebook,
  Linkedin,
  Twitter,
  Check,
  X,
} from 'lucide-react';
import { cn } from '../../../shared/lib/utils';

export function MySettings() {
  const [activeTab, setActiveTab] = useState<'profile' | 'social' | 'notifications' | 'billing'>('profile');

  const tabs = [
    { id: 'profile', label: 'Profilo', icon: User },
    { id: 'social', label: 'Social', icon: Link2 },
    { id: 'notifications', label: 'Notifiche', icon: Bell },
    { id: 'billing', label: 'Fatturazione', icon: CreditCard },
  ];

  // Mock connected social accounts
  const socialAccounts = [
    { id: 'instagram', name: 'Instagram', icon: Instagram, connected: true, username: '@azienda_srl' },
    { id: 'facebook', name: 'Facebook', icon: Facebook, connected: true, username: 'Azienda Srl' },
    { id: 'linkedin', name: 'LinkedIn', icon: Linkedin, connected: false },
    { id: 'twitter', name: 'Twitter/X', icon: Twitter, connected: false },
  ];

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl sm:text-3xl font-bold text-foreground">Impostazioni</h1>
        <p className="text-muted-foreground mt-1">Gestisci il tuo account e preferenze</p>
      </motion.div>

      {/* Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={cn(
                'flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium whitespace-nowrap transition-colors',
                activeTab === tab.id
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80'
              )}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      {activeTab === 'profile' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-card border border-border rounded-2xl p-6 space-y-6"
        >
          <h3 className="font-semibold text-foreground">Informazioni Profilo</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-muted-foreground mb-2">Nome</label>
              <input
                type="text"
                defaultValue="Mario Rossi"
                className="w-full px-4 py-2.5 rounded-xl border border-border bg-background text-foreground"
              />
            </div>
            <div>
              <label className="block text-sm text-muted-foreground mb-2">Azienda</label>
              <input
                type="text"
                defaultValue="Azienda Srl"
                className="w-full px-4 py-2.5 rounded-xl border border-border bg-background text-foreground"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm text-muted-foreground mb-2">Email</label>
              <input
                type="email"
                defaultValue="mario@azienda.it"
                className="w-full px-4 py-2.5 rounded-xl border border-border bg-background text-foreground"
              />
            </div>
          </div>

          <button className="flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:bg-primary/90 transition-colors">
            <Save className="h-4 w-4" />
            Salva Modifiche
          </button>
        </motion.div>
      )}

      {activeTab === 'social' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-card border border-border rounded-2xl p-6 space-y-4"
        >
          <h3 className="font-semibold text-foreground">Account Social Collegati</h3>
          <p className="text-sm text-muted-foreground">
            Collega i tuoi account social per abilitare la pubblicazione automatica
          </p>

          <div className="space-y-3">
            {socialAccounts.map((account) => {
              const Icon = account.icon;
              return (
                <div
                  key={account.id}
                  className="flex items-center justify-between p-4 rounded-xl border border-border"
                >
                  <div className="flex items-center gap-3">
                    <Icon className="h-6 w-6 text-muted-foreground" />
                    <div>
                      <p className="font-medium text-foreground">{account.name}</p>
                      {account.connected && (
                        <p className="text-sm text-muted-foreground">{account.username}</p>
                      )}
                    </div>
                  </div>

                  {account.connected ? (
                    <div className="flex items-center gap-2">
                      <span className="flex items-center gap-1 text-sm text-green-500">
                        <Check className="h-4 w-4" /> Connesso
                      </span>
                      <button className="text-sm text-red-500 hover:underline">Disconnetti</button>
                    </div>
                  ) : (
                    <button className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors">
                      Connetti
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </motion.div>
      )}

      {activeTab === 'notifications' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-card border border-border rounded-2xl p-6 space-y-4"
        >
          <h3 className="font-semibold text-foreground">Preferenze Notifiche</h3>

          {[
            { label: 'Email per nuovi contenuti generati', enabled: true },
            { label: 'Email per post pubblicati', enabled: true },
            { label: 'Report settimanale performance', enabled: false },
            { label: 'Avvisi saldo token basso', enabled: true },
          ].map((pref, index) => (
            <div key={index} className="flex items-center justify-between py-3 border-b border-border last:border-0">
              <span className="text-foreground">{pref.label}</span>
              <button
                className={cn(
                  'w-12 h-6 rounded-full transition-colors',
                  pref.enabled ? 'bg-primary' : 'bg-muted'
                )}
              >
                <div
                  className={cn(
                    'w-5 h-5 bg-white rounded-full shadow-sm transition-transform',
                    pref.enabled ? 'translate-x-6' : 'translate-x-0.5'
                  )}
                />
              </button>
            </div>
          ))}
        </motion.div>
      )}

      {activeTab === 'billing' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-4"
        >
          <div className="bg-card border border-border rounded-2xl p-6">
            <h3 className="font-semibold text-foreground mb-4">Piano Attuale</h3>
            <div className="flex items-center justify-between p-4 rounded-xl bg-primary/10 border border-primary/20">
              <div>
                <p className="font-bold text-foreground text-lg">Growth</p>
                <p className="text-sm text-muted-foreground">5.000 token/mese • €99.99</p>
              </div>
              <button className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors">
                Upgrade
              </button>
            </div>
          </div>

          <div className="bg-card border border-border rounded-2xl p-6">
            <h3 className="font-semibold text-foreground mb-4">Metodo di Pagamento</h3>
            <div className="flex items-center gap-3 p-4 rounded-xl border border-border">
              <CreditCard className="h-8 w-8 text-muted-foreground" />
              <div>
                <p className="font-medium text-foreground">•••• •••• •••• 4242</p>
                <p className="text-sm text-muted-foreground">Scade 12/26</p>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
