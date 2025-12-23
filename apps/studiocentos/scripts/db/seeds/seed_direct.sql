-- Seed Portfolio Data - SQL Diretto
-- Inserisce 2 progetti e 6 servizi dalla landing originale

-- PROGETTI
INSERT INTO projects (
    title, slug, description, year, category,
    live_url, technologies, metrics,
    status, is_featured, is_public, "order",
    images, created_at, updated_at
) VALUES 
(
    'CV-Lab Pro',
    'cv-lab-pro',
    'Portfolio builder con AI per professionisti',
    2024,
    'SaaS Platform',
    'https://cv-lab.pro',
    '["React 19", "FastAPI", "PostgreSQL 16", "AI Agents"]'::jsonb,
    '{"File production-ready": "850+", "Domini business": "11", "Time to market": "45gg"}'::jsonb,
    'active',
    true,
    true,
    1,
    '[]'::jsonb,
    NOW(),
    NOW()
),
(
    'Phoenix AI',
    'phoenix-ai',
    'Piattaforma multi-agent per automazione enterprise',
    2024,
    'AI Platform',
    'https://phoenix-ai.duckdns.org',
    '["Python 3.12", "LangChain", "ChromaDB", "GPT-4"]'::jsonb,
    '{"Enterprise AI tools": "78", "Vector search": "RAG", "Monitoring": "24/7"}'::jsonb,
    'active',
    true,
    true,
    2,
    '[]'::jsonb,
    NOW(),
    NOW()
)
ON CONFLICT (slug) DO NOTHING;

-- SERVIZI
INSERT INTO services (
    title, slug, description, icon, category,
    features, benefits, value_indicator, cta_text, cta_url,
    is_active, is_featured, "order", created_at, updated_at
) VALUES
(
    'STUDIOCENTOS Framework',
    'studiocentos-framework',
    'Enterprise full-stack framework production-ready con 850+ file e 11 domini business.',
    '⚡',
    'framework',
    '["React 19 + FastAPI", "PostgreSQL 16 + Redis 7", "DDD Architecture", "Docker + CI/CD ready", "MVP in 45 giorni"]'::jsonb,
    '[]'::jsonb,
    '€100K valore codice',
    'Scopri di più →',
    '#contatti',
    true,
    true,
    1,
    NOW(),
    NOW()
),
(
    'AgentVanilla',
    'agentvanilla',
    'Suite di 78 enterprise AI tools con monitoring Prometheus e Grafana integrato.',
    '🤖',
    'ai_tools',
    '["78 AI Tools pronti", "Multi-provider support", "Real-time monitoring", "Orchestrazione agents", "Production-tested"]'::jsonb,
    '[]'::jsonb,
    '€50K valore tools',
    'Scopri di più →',
    '#contatti',
    true,
    true,
    2,
    NOW(),
    NOW()
),
(
    'fastBank',
    'fastbank',
    'Component library con 50+ componenti React + FastAPI riutilizzabili e production-ready.',
    '🧩',
    'components',
    '["50+ Componenti UI", "TypeScript + Storybook", "30+ Makefile commands", "Automation completa", "Enterprise-tested"]'::jsonb,
    '[]'::jsonb,
    '-90% dev time',
    'Scopri di più →',
    '#contatti',
    true,
    true,
    3,
    NOW(),
    NOW()
),
(
    'Sviluppo Custom',
    'sviluppo-custom',
    'Siti web, app mobile e soluzioni su misura con tecnologie moderne.',
    '🌐',
    'custom_dev',
    '["Landing page & Corporate", "E-commerce completi", "Web app custom", "SEO ottimizzato"]'::jsonb,
    '[]'::jsonb,
    NULL,
    'Richiedi Preventivo →',
    '#contatti',
    true,
    false,
    4,
    NOW(),
    NOW()
),
(
    'App Mobile',
    'app-mobile',
    'Applicazioni iOS e Android con React Native ed Expo 52.',
    '📱',
    'mobile',
    '["iOS + Android native", "Offline-first", "Push notifications", "Backend integration"]'::jsonb,
    '[]'::jsonb,
    NULL,
    'Richiedi Preventivo →',
    '#contatti',
    true,
    false,
    5,
    NOW(),
    NOW()
),
(
    'AI Integration',
    'ai-integration',
    'Integrazione AI nei tuoi prodotti con ChatGPT, agents custom e RAG.',
    '🔮',
    'ai_integration',
    '["Chatbot intelligenti", "AI Agents custom", "Document analysis (RAG)", "Automation workflows"]'::jsonb,
    '[]'::jsonb,
    NULL,
    'Richiedi Preventivo →',
    '#contatti',
    true,
    false,
    6,
    NOW(),
    NOW()
)
ON CONFLICT (slug) DO NOTHING;

-- Verifica
SELECT 'PROGETTI INSERITI:' as status, COUNT(*) as count FROM projects;
SELECT 'SERVIZI INSERITI:' as status, COUNT(*) as count FROM services;
