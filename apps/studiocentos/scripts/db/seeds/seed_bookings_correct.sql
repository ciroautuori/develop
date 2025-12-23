-- Seed Bookings Demo Data - Schema Corretto
-- Aggiunge alcuni appuntamenti demo per testare il sistema

-- BOOKINGS
INSERT INTO bookings (
    client_name, client_email, client_phone, client_company,
    service_type, title, description, 
    scheduled_at, duration_minutes, timezone, status,
    meeting_provider, admin_notes, client_notes,
    reminder_sent, created_at, updated_at
) VALUES 
(
    'Marco Rossi',
    'marco.rossi@example.com',
    '+39 345 678 9012',
    'Rossi Textile SpA',
    'custom_dev',
    'Consulenza E-commerce',
    'Richiesta sviluppo e-commerce per azienda tessile con gestione magazzino',
    '2025-11-15 14:00:00',
    120,
    'Europe/Rome',
    'confirmed',
    'zoom',
    'Cliente interessato a soluzione completa con CRM integrato',
    'Budget indicativo 5-10K, urgenza media',
    false,
    NOW(),
    NOW()
),
(
    'Laura Bianchi',
    'laura.bianchi@startup.io',
    '+39 347 123 4567',
    'AI Startup Ltd',
    'ai_integration',
    'Integrazione ChatGPT',
    'Integrazione ChatGPT in piattaforma SaaS esistente con analisi documenti',
    '2025-11-18 10:30:00',
    90,
    'Europe/Rome',
    'pending',
    'google_meet',
    'Stack tecnico: React + Node.js, richiede chatbot e document analysis',
    'Startup in fase di crescita, tecnologia prioritaria',
    false,
    NOW(),
    NOW()
),
(
    'Giuseppe Verde',
    'g.verde@consulting.com',
    '+39 340 987 6543',
    'Verde Consulting',
    'mobile',
    'App Mobile CRM',
    'Applicazione iOS e Android per gestione clienti con sincronizzazione offline',
    '2025-11-20 16:00:00',
    120,
    'Europe/Rome',
    'confirmed',
    'zoom',
    'Team di 3 sviluppatori, esperienza con React Native',
    'CRM mobile con funzionalità offline-first',
    false,
    NOW(),
    NOW()
),
(
    'Anna Gialli',
    'anna@digitalagenzia.it',
    '+39 389 456 7890',
    'Digital Agency Pro',
    'framework',
    'STUDIOCENTOS Framework',
    'Consulenza su framework STUDIOCENTOS per nuovo progetto enterprise',
    '2025-11-14 09:00:00',
    60,
    'Europe/Rome',
    'completed',
    'zoom',
    'Consulenza completata - cliente soddisfatto, possibile progetto futuro',
    'MVP per Q1 2025, framework ideale per velocità sviluppo',
    true,
    NOW() - INTERVAL '2 days',
    NOW()
),
(
    'Roberto Neri',
    'roberto.neri@enterprise.com',
    '+39 335 111 2233',
    'Enterprise Solutions Corp',
    'ai_tools',
    'AgentVanilla Implementation',
    'Implementazione suite AgentVanilla per automazione processi aziendali',
    '2025-11-25 15:30:00',
    180,
    'Europe/Rome',
    'pending',
    'google_meet',
    'Grande azienda, processi legacy da modernizzare con AI',
    'Automazione customer service e data analysis, training team necessario',
    false,
    NOW(),
    NOW()
)
ON CONFLICT DO NOTHING;

-- AVAILABILITY SLOTS
INSERT INTO availability_slots (
    day_of_week, start_time, end_time,
    is_active, created_at, updated_at
) VALUES
(1, '09:00:00', '12:00:00', true, NOW(), NOW()),  -- Lunedì mattina
(1, '14:00:00', '18:00:00', true, NOW(), NOW()),  -- Lunedì pomeriggio
(2, '09:00:00', '12:00:00', true, NOW(), NOW()),  -- Martedì mattina
(3, '10:00:00', '16:00:00', true, NOW(), NOW()),  -- Mercoledì
(4, '14:00:00', '17:00:00', true, NOW(), NOW()),  -- Giovedì pomeriggio
(5, '09:00:00', '13:00:00', true, NOW(), NOW())   -- Venerdì mattina
ON CONFLICT DO NOTHING;

-- Verifica
SELECT 'BOOKINGS INSERITI:' as status, COUNT(*) as count FROM bookings;
SELECT 'SLOT DISPONIBILITÀ:' as status, COUNT(*) as count FROM availability_slots;
