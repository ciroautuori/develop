-- SQL Script per aggiungere traduzioni a progetti e servizi
-- Da eseguire manualmente sul database PostgreSQL

-- PROGETTI: Aggiungi traduzioni EN/ES

-- Innovazione Sociale Salernitana
UPDATE projects
SET translations = '{
  "en": {
    "title": "Salerno Social Innovation",
    "description": "Complete platform for managing social welfare services with AI integration for document management and user assistance. Handles over 20,000 citizens with automated workflows and intelligent routing."
  },
  "es": {
    "title": "Innovación Social Salerno",
    "description": "Plataforma completa para la gestión de servicios sociales con integración de IA para gestión documental y asistencia al usuario. Gestiona más de 20,000 ciudadanos con flujos de trabajo automatizados y enrutamiento inteligente."
  }
}'::jsonb
WHERE title = 'Innovazione Sociale Salernitana';

-- CV-Lab Pro
UPDATE projects
SET translations = '{
  "en": {
    "title": "CV-Lab Pro",
    "description": "Professional CV generation platform with AI-powered templates and multilingual support. Create stunning resumes in minutes with intelligent content suggestions."
  },
  "es": {
    "title": "CV-Lab Pro",
    "description": "Plataforma profesional de generación de CV con plantillas impulsadas por IA y soporte multilingüe. Crea currículums impresionantes en minutos con sugerencias de contenido inteligentes."
  }
}'::jsonb
WHERE title = 'CV-Lab Pro';

-- ironRep
UPDATE projects
SET translations = '{
  "en": {
    "title": "ironRep",
    "description": "Advanced fitness tracking and workout management system with AI-powered training recommendations. Track your progress, plan workouts, and achieve your fitness goals."
  },
  "es": {
    "title": "ironRep",
    "description": "Sistema avanzado de seguimiento de fitness y gestión de entrenamientos con recomendaciones de entrenamiento impulsadas por IA. Rastrea tu progreso, planifica entrenamientos y alcanza tus objetivos de fitness."
  }
}'::jsonb
WHERE title = 'ironRep';

-- SERVIZI: Aggiungi traduzioni EN/ES

-- Assistente Virtuale AI
UPDATE services
SET translations = '{
  "en": {
    "title": "AI Virtual Assistant",
    "description": "Intelligent virtual assistant powered by advanced AI models. Automates customer support, handles inquiries 24/7, and provides human-like interactions.",
    "features": [
      "Natural language processing",
      "Multi-channel support (web, email, chat)",
      "Learns from interactions",
      "24/7 availability",
      "Easy integration"
    ],
    "cta_text": "Discover more →"
  },
  "es": {
    "title": "Asistente Virtual IA",
    "description": "Asistente virtual inteligente impulsado por modelos avanzados de IA. Automatiza el soporte al cliente, maneja consultas 24/7 y proporciona interacciones similares a humanos.",
    "features": [
      "Procesamiento de lenguaje natural",
      "Soporte multicanal (web, email, chat)",
      "Aprende de las interacciones",
      "Disponibilidad 24/7",
      "Fácil integración"
    ],
    "cta_text": "Descubre más →"
  }
}'::jsonb
WHERE title = 'Assistente Virtuale AI';

-- Knowledge Base AI
UPDATE services
SET translations = '{
  "en": {
    "title": "AI Knowledge Base",
    "description": "Smart knowledge management system with AI-powered search and content recommendations. Centralize information and make it instantly accessible.",
    "features": [
      "Intelligent semantic search",
      "Automatic categorization",
      "Content recommendations",
      "Version control",
      "Team collaboration"
    ],
    "cta_text": "Learn more →"
  },
  "es": {
    "title": "Base de Conocimiento IA",
    "description": "Sistema inteligente de gestión del conocimiento con búsqueda y recomendaciones de contenido impulsadas por IA. Centraliza la información y hazla accesible al instante.",
    "features": [
      "Búsqueda semántica inteligente",
      "Categorización automática",
      "Recomendaciones de contenido",
      "Control de versiones",
      "Colaboración en equipo"
    ],
    "cta_text": "Aprende más →"
  }
}'::jsonb
WHERE title = 'Knowledge Base AI';

-- Dashboard Analytics
UPDATE services
SET translations = '{
  "en": {
    "title": "Analytics Dashboard",
    "description": "Real-time analytics dashboard with AI-powered insights and predictive analytics. Make data-driven decisions with confidence.",
    "features": [
      "Real-time data visualization",
      "Predictive analytics",
      "Custom reports",
      "Multi-source integration",
      "Alert system"
    ],
    "cta_text": "See demo →"
  },
  "es": {
    "title": "Panel de Análisis",
    "description": "Panel de análisis en tiempo real con información e análisis predictivo impulsados por IA. Toma decisiones basadas en datos con confianza.",
    "features": [
      "Visualización de datos en tiempo real",
      "Análisis predictivo",
      "Informes personalizados",
      "Integración multifuente",
      "Sistema de alertas"
    ],
    "cta_text": "Ver demo →"
  }
}'::jsonb
WHERE title = 'Dashboard Analytics';

-- Verifica aggiornamenti
SELECT id, title,
  translations->'en'->>'title' as title_en,
  translations->'es'->>'title' as title_es
FROM projects;

SELECT id, title,
  translations->'en'->>'title' as title_en,
  translations->'es'->>'title' as title_es
FROM services
LIMIT 5;
