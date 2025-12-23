-- Aggiungo progetto del 2020 per testare timeline
INSERT INTO projects (
    title, slug, description, year, category,
    live_url, technologies, metrics,
    status, is_featured, is_public, "order",
    images, created_at, updated_at
) VALUES (
    'E-Commerce Platform',
    'e-commerce-platform',
    'Primo progetto enterprise: piattaforma e-commerce completa con catalogo prodotti, carrello, pagamenti e dashboard admin. Realizzata per un cliente nel settore moda con oltre 10.000 prodotti.',
    2020,
    'E-Commerce',
    'https://demo-shop.example.com',
    '["React", "Node.js", "MongoDB", "Stripe"]'::jsonb,
    '{"Prodotti": "10.000+", "Ordini": "50.000", "Clienti": "25.000"}'::jsonb,
    'active',
    true,
    true,
    3,
    '[]'::jsonb,
    NOW(),
    NOW()
)
ON CONFLICT (slug) DO NOTHING;
