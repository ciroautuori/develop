-- Seed Bookings Demo Data
-- Aggiunge alcuni appuntamenti demo per testare il sistema

-- BOOKINGS
INSERT INTO bookings (
    client_name, client_email, client_phone,
    service_type, consultation_type, booking_date, booking_time,
    duration_hours, status, notes,
    metadata, created_at, updated_at
) VALUES 
(
    'Marco Rossi',
    'marco.rossi@example.com',
    '+39 345 678 9012',
    'custom_dev',
    'initial',
    '2025-11-15',
    '14:00:00',
    2,
    'confirmed',
    'Richiesta sviluppo e-commerce per azienda tessile',
    '{"budget_range": "5000-10000", "priority": "high", "expected_delivery": "30gg"}'::jsonb,
    NOW(),
    NOW()
),
(
    'Laura Bianchi',
    'laura.bianchi@startup.io',
    '+39 347 123 4567',
    'ai_integration',
    'technical',
    '2025-11-18',
    '10:30:00',
    1.5,
    'pending',
    'Integrazione ChatGPT in piattaforma SaaS esistente',
    '{"current_tech": "React + Node.js", "ai_features": ["chatbot", "document_analysis"]}'::jsonb,
    NOW(),
    NOW()
),
(
    'Giuseppe Verde',
    'g.verde@consulting.com',
    '+39 340 987 6543',
    'mobile',
    'discovery',
    '2025-11-20',
    '16:00:00',
    2,
    'confirmed',
    'App mobile per gestione clienti - iOS e Android',
    '{"platforms": ["iOS", "Android"], "features": "CRM mobile", "team_size": 3}'::jsonb,
    NOW(),
    NOW()
),
(
    'Anna Gialli',
    'anna@digitalagenzia.it',
    '+39 389 456 7890',
    'framework',
    'consultation',
    '2025-11-14',
    '09:00:00',
    1,
    'completed',
    'Consulenza STUDIOCENTOS Framework per nuovo progetto',
    '{"project_scope": "MVP", "deadline": "Q1 2025", "completed": true}'::jsonb,
    NOW() - INTERVAL '2 days',
    NOW()
),
(
    'Roberto Neri',
    'roberto.neri@enterprise.com',
    '+39 335 111 2233',
    'ai_tools',
    'technical',
    '2025-11-25',
    '15:30:00',
    3,
    'pending',
    'Implementazione suite AgentVanilla per automazione processi',
    '{"current_tools": "legacy", "processes": ["customer_service", "data_analysis"], "team_training": true}'::jsonb,
    NOW(),
    NOW()
)
ON CONFLICT DO NOTHING;

-- AVAILABILITY SLOTS (alcuni slot disponibili)
INSERT INTO availability_slots (
    day_of_week, start_time, end_time, slot_type,
    is_active, created_at, updated_at
) VALUES
(1, '09:00:00', '12:00:00', 'consultation', true, NOW(), NOW()),  -- Lunedì mattina
(1, '14:00:00', '18:00:00', 'technical', true, NOW(), NOW()),     -- Lunedì pomeriggio
(2, '09:00:00', '12:00:00', 'consultation', true, NOW(), NOW()),  -- Martedì mattina
(3, '10:00:00', '16:00:00', 'discovery', true, NOW(), NOW()),     -- Mercoledì
(4, '14:00:00', '17:00:00', 'technical', true, NOW(), NOW()),     -- Giovedì pomeriggio
(5, '09:00:00', '13:00:00', 'consultation', true, NOW(), NOW())   -- Venerdì mattina
ON CONFLICT DO NOTHING;

-- Verifica
SELECT 'BOOKINGS INSERITI:' as status, COUNT(*) as count FROM bookings;
SELECT 'SLOT DISPONIBILITÀ:' as status, COUNT(*) as count FROM availability_slots;
