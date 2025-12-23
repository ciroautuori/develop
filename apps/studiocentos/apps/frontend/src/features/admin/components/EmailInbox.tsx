/**
 * EmailInbox Component - Webmail Reader
 * Legge email da info@studiocentos.it via IMAP
 */

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Mail,
  Inbox,
  Send,
  Trash2,
  Star,
  StarOff,
  RefreshCw,
  Search,
  ChevronLeft,
  ChevronRight,
  Paperclip,
  Clock,
  CheckCircle2,
  Circle,
  Loader2,
  AlertCircle,
  X,
  ExternalLink,
  Folder,
  MailOpen,
} from 'lucide-react';
import { Button } from '../../../shared/components/ui/button';
import { cn } from '../../../shared/lib/utils';
import { toast } from 'sonner';

// Types
interface EmailAttachment {
  filename: string;
  content_type: string;
  size: number;
}

interface Email {
  id: string;
  subject: string;
  from_email: string;
  from_name: string | null;
  to_email: string;
  date: string;
  body_text: string | null;
  body_html: string | null;
  is_read: boolean;
  is_starred: boolean;
  attachments: EmailAttachment[];
  folder: string;
}

interface EmailFolder {
  name: string;
  display_name: string;
  total: number;
  unread: number;
}

interface ConnectionStatus {
  connected: boolean;
  server?: string;
  username?: string;
  inbox_total?: number;
  inbox_unread?: number;
  error?: string;
}

// API functions
const getAuthHeaders = () => {
  const token = localStorage.getItem('admin_token');
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  };
};

async function fetchConnectionStatus(): Promise<ConnectionStatus> {
  const res = await fetch('/api/v1/admin/inbox/status', { headers: getAuthHeaders() });
  if (!res.ok) throw new Error('Failed to fetch status');
  return res.json();
}

async function fetchFolders(): Promise<EmailFolder[]> {
  const res = await fetch('/api/v1/admin/inbox/folders', { headers: getAuthHeaders() });
  if (!res.ok) throw new Error('Failed to fetch folders');
  return res.json();
}

async function fetchEmails(
  folder: string,
  limit: number,
  offset: number,
  search?: string,
  unreadOnly?: boolean
): Promise<{ emails: Email[]; total: number; unread: number }> {
  const params = new URLSearchParams({
    folder,
    limit: limit.toString(),
    offset: offset.toString(),
  });
  if (search) params.append('search', search);
  if (unreadOnly) params.append('unread_only', 'true');

  const res = await fetch(`/api/v1/admin/inbox/emails?${params}`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error('Failed to fetch emails');
  return res.json();
}

async function fetchEmail(msgId: string, folder: string): Promise<Email> {
  const res = await fetch(`/api/v1/admin/inbox/emails/${msgId}?folder=${folder}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Failed to fetch email');
  return res.json();
}

async function markEmailRead(msgId: string, folder: string, read: boolean): Promise<void> {
  const res = await fetch('/api/v1/admin/inbox/emails/mark-read', {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ msg_id: msgId, folder, read }),
  });
  if (!res.ok) throw new Error('Failed to update email');
}

async function starEmail(msgId: string, folder: string, starred: boolean): Promise<void> {
  const res = await fetch('/api/v1/admin/inbox/emails/star', {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ msg_id: msgId, folder, starred }),
  });
  if (!res.ok) throw new Error('Failed to star email');
}

async function deleteEmail(msgId: string, folder: string): Promise<void> {
  const res = await fetch(`/api/v1/admin/inbox/emails/${msgId}?folder=${folder}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Failed to delete email');
}

// Format date
function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (days === 0) {
    return date.toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' });
  } else if (days === 1) {
    return 'Ieri';
  } else if (days < 7) {
    return date.toLocaleDateString('it-IT', { weekday: 'short' });
  } else {
    return date.toLocaleDateString('it-IT', { day: '2-digit', month: 'short' });
  }
}

// Format file size
function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function EmailInbox() {
  // State
  const [status, setStatus] = useState<ConnectionStatus | null>(null);
  const [folders, setFolders] = useState<EmailFolder[]>([]);
  const [emails, setEmails] = useState<Email[]>([]);
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [currentFolder, setCurrentFolder] = useState('INBOX');
  const [loading, setLoading] = useState(true);
  const [loadingEmail, setLoadingEmail] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);
  const [unread, setUnread] = useState(0);
  const [showUnreadOnly, setShowUnreadOnly] = useState(false);
  const limit = 20;

  // Load connection status
  const loadStatus = useCallback(async () => {
    try {
      const data = await fetchConnectionStatus();
      setStatus(data);
    } catch (error) {
      console.error('Failed to load status:', error);
      setStatus({ connected: false, error: 'Connessione fallita' });
    }
  }, []);

  // Load folders
  const loadFolders = useCallback(async () => {
    try {
      const data = await fetchFolders();
      setFolders(data);
    } catch (error) {
      console.error('Failed to load folders:', error);
    }
  }, []);

  // Load emails
  const loadEmails = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchEmails(
        currentFolder,
        limit,
        page * limit,
        searchQuery || undefined,
        showUnreadOnly
      );
      setEmails(data.emails);
      setTotal(data.total);
      setUnread(data.unread);
    } catch (error) {
      console.error('Failed to load emails:', error);
      toast.error('Errore nel caricamento email');
    } finally {
      setLoading(false);
    }
  }, [currentFolder, page, searchQuery, showUnreadOnly]);

  // Initial load
  useEffect(() => {
    loadStatus();
    loadFolders();
  }, [loadStatus, loadFolders]);

  // Load emails when folder/page changes
  useEffect(() => {
    if (status?.connected) {
      loadEmails();
    }
  }, [status?.connected, loadEmails]);

  // Open email
  const openEmail = async (email: Email) => {
    setLoadingEmail(true);
    try {
      const fullEmail = await fetchEmail(email.id, currentFolder);
      setSelectedEmail(fullEmail);

      // Mark as read if unread
      if (!email.is_read) {
        await markEmailRead(email.id, currentFolder, true);
        setEmails(prev =>
          prev.map(e => (e.id === email.id ? { ...e, is_read: true } : e))
        );
        setUnread(prev => Math.max(0, prev - 1));
      }
    } catch (error) {
      console.error('Failed to open email:', error);
      toast.error('Errore apertura email');
    } finally {
      setLoadingEmail(false);
    }
  };

  // Toggle star
  const toggleStar = async (email: Email, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await starEmail(email.id, currentFolder, !email.is_starred);
      setEmails(prev =>
        prev.map(e => (e.id === email.id ? { ...e, is_starred: !e.is_starred } : e))
      );
      if (selectedEmail?.id === email.id) {
        setSelectedEmail(prev => prev ? { ...prev, is_starred: !prev.is_starred } : null);
      }
    } catch (error) {
      toast.error('Errore aggiornamento');
    }
  };

  // Delete email
  const handleDelete = async (email: Email) => {
    if (!confirm('Eliminare questa email?')) return;
    try {
      await deleteEmail(email.id, currentFolder);
      setEmails(prev => prev.filter(e => e.id !== email.id));
      if (selectedEmail?.id === email.id) {
        setSelectedEmail(null);
      }
      toast.success('Email eliminata');
    } catch (error) {
      toast.error('Errore eliminazione');
    }
  };

  // Refresh
  const handleRefresh = () => {
    loadStatus();
    loadFolders();
    loadEmails();
  };

  // Not connected state
  if (status && !status.connected) {
    return (
      <div className="bg-card border border-border rounded-xl p-8 text-center">
        <AlertCircle className="w-12 h-12 text-destructive mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-foreground mb-2">
          Connessione Email Non Configurata
        </h3>
        <p className="text-muted-foreground mb-4">
          {status.error || 'Configura le credenziali IMAP per accedere alla posta.'}
        </p>
        <p className="text-sm text-muted-foreground">
          Variabili ambiente richieste: IMAP_HOST, IMAP_USERNAME, IMAP_PASSWORD
        </p>
      </div>
    );
  }

  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        <div className="flex items-center gap-3">
          <Mail className="w-5 h-5 text-primary" />
          <div>
            <h3 className="font-semibold text-foreground">Posta in Arrivo</h3>
            <p className="text-xs text-muted-foreground">
              {status?.username || 'info@studiocentos.it'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {unread > 0 && (
            <span className="px-2 py-1 rounded-full bg-primary text-primary-foreground text-xs font-medium">
              {unread} non lette
            </span>
          )}
          <Button variant="ghost" size="icon" onClick={handleRefresh} disabled={loading}>
            <RefreshCw className={cn('w-4 h-4', loading && 'animate-spin')} />
          </Button>
        </div>
      </div>

      <div className="flex h-[600px]">
        {/* Sidebar - Folders */}
        <div className="w-48 border-r border-border p-2 hidden md:block">
          {folders.map(folder => (
            <button
              key={folder.name}
              onClick={() => {
                setCurrentFolder(folder.name);
                setPage(0);
                setSelectedEmail(null);
              }}
              className={cn(
                'w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors',
                currentFolder === folder.name
                  ? 'bg-primary/10 text-primary'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground'
              )}
            >
              <div className="flex items-center gap-2">
                {folder.name === 'INBOX' ? (
                  <Inbox className="w-4 h-4" />
                ) : folder.name === 'Sent' ? (
                  <Send className="w-4 h-4" />
                ) : folder.name === 'Trash' ? (
                  <Trash2 className="w-4 h-4" />
                ) : (
                  <Folder className="w-4 h-4" />
                )}
                <span className="truncate">{folder.display_name}</span>
              </div>
              {folder.unread > 0 && (
                <span className="text-xs font-medium">{folder.unread}</span>
              )}
            </button>
          ))}
        </div>

        {/* Email List */}
        <div className={cn('flex-1 flex flex-col', selectedEmail && 'hidden md:flex')}>
          {/* Search */}
          <div className="p-2 border-b border-border">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Cerca email..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && loadEmails()}
                className="w-full pl-9 pr-4 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
          </div>

          {/* Email List */}
          <div className="flex-1 overflow-y-auto">
            {loading ? (
              <div className="flex items-center justify-center h-full">
                <Loader2 className="w-6 h-6 animate-spin text-primary" />
              </div>
            ) : emails.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                <MailOpen className="w-12 h-12 mb-2 opacity-50" />
                <p>Nessuna email</p>
              </div>
            ) : (
              emails.map(email => (
                <div
                  key={email.id}
                  onClick={() => openEmail(email)}
                  className={cn(
                    'flex items-start gap-3 p-3 border-b border-border cursor-pointer transition-colors',
                    !email.is_read && 'bg-primary/5',
                    'hover:bg-muted/50'
                  )}
                >
                  {/* Read indicator */}
                  <div className="pt-1">
                    {email.is_read ? (
                      <Circle className="w-2 h-2 text-muted-foreground" />
                    ) : (
                      <Circle className="w-2 h-2 fill-primary text-primary" />
                    )}
                  </div>

                  {/* Star */}
                  <button
                    onClick={e => toggleStar(email, e)}
                    className="pt-1"
                  >
                    {email.is_starred ? (
                      <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    ) : (
                      <StarOff className="w-4 h-4 text-muted-foreground hover:text-yellow-400" />
                    )}
                  </button>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <span className={cn(
                        'text-sm truncate',
                        !email.is_read ? 'font-semibold text-foreground' : 'text-foreground'
                      )}>
                        {email.from_name || email.from_email}
                      </span>
                      <span className="text-xs text-muted-foreground whitespace-nowrap">
                        {formatDate(email.date)}
                      </span>
                    </div>
                    <p className={cn(
                      'text-sm truncate',
                      !email.is_read ? 'font-medium text-foreground' : 'text-muted-foreground'
                    )}>
                      {email.subject}
                    </p>
                    {email.attachments.length > 0 && (
                      <div className="flex items-center gap-1 mt-1 text-xs text-muted-foreground">
                        <Paperclip className="w-3 h-3" />
                        <span>{email.attachments.length} allegat{email.attachments.length > 1 ? 'i' : 'o'}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Pagination */}
          {total > limit && (
            <div className="flex items-center justify-between p-2 border-t border-border">
              <span className="text-xs text-muted-foreground">
                {page * limit + 1}-{Math.min((page + 1) * limit, total)} di {total}
              </span>
              <div className="flex items-center gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setPage(p => Math.max(0, p - 1))}
                  disabled={page === 0}
                >
                  <ChevronLeft className="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setPage(p => p + 1)}
                  disabled={(page + 1) * limit >= total}
                >
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* Email Detail */}
        <AnimatePresence>
          {selectedEmail && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="flex-1 flex flex-col border-l border-border md:w-1/2"
            >
              {/* Detail Header */}
              <div className="flex items-center justify-between p-4 border-b border-border">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedEmail(null)}
                  className="md:hidden"
                >
                  <ChevronLeft className="w-4 h-4 mr-1" />
                  Indietro
                </Button>

                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => toggleStar(selectedEmail, { stopPropagation: () => { } } as React.MouseEvent)}
                  >
                    {selectedEmail.is_starred ? (
                      <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    ) : (
                      <StarOff className="w-4 h-4" />
                    )}
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDelete(selectedEmail)}
                    className="text-destructive hover:text-destructive"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setSelectedEmail(null)}
                    className="hidden md:flex"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              {/* Email Content */}
              {loadingEmail ? (
                <div className="flex-1 flex items-center justify-center">
                  <Loader2 className="w-6 h-6 animate-spin text-primary" />
                </div>
              ) : (
                <div className="flex-1 overflow-y-auto p-4">
                  <h2 className="text-lg font-semibold text-foreground mb-4">
                    {selectedEmail.subject}
                  </h2>

                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <p className="font-medium text-foreground">
                        {selectedEmail.from_name || selectedEmail.from_email}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {selectedEmail.from_email}
                      </p>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {new Date(selectedEmail.date).toLocaleString('it-IT')}
                    </p>
                  </div>

                  {/* Attachments */}
                  {selectedEmail.attachments.length > 0 && (
                    <div className="mb-4 p-3 rounded-lg bg-muted/50">
                      <p className="text-sm font-medium text-foreground mb-2">
                        Allegati ({selectedEmail.attachments.length})
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {selectedEmail.attachments.map((att, i) => (
                          <div
                            key={i}
                            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-background border border-border text-sm"
                          >
                            <Paperclip className="w-3 h-3 text-muted-foreground" />
                            <span className="truncate max-w-[150px]">{att.filename}</span>
                            <span className="text-xs text-muted-foreground">
                              ({formatSize(att.size)})
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Body */}
                  <div className="prose prose-sm max-w-none dark:prose-invert">
                    {selectedEmail.body_html ? (
                      <div
                        dangerouslySetInnerHTML={{ __html: selectedEmail.body_html }}
                        className="email-content"
                      />
                    ) : (
                      <pre className="whitespace-pre-wrap font-sans text-foreground">
                        {selectedEmail.body_text || '(Nessun contenuto)'}
                      </pre>
                    )}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default EmailInbox;
