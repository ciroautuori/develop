"""
Seed iModels - Modelli AI FREE
GROQ, OpenRouter, Google Gemini, HuggingFace
"""

import asyncio
from sqlalchemy import text

# SQL per creare tabelle
CREATE_TABLES_SQL = """
-- AI Models table
CREATE TABLE IF NOT EXISTS ai_models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE,
    slug VARCHAR(200) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    
    provider VARCHAR(50) NOT NULL,
    model_id VARCHAR(200) NOT NULL,
    
    capabilities JSON NOT NULL DEFAULT '[]'::json,
    config JSON NOT NULL DEFAULT '{}'::json,
    default_params JSON NOT NULL DEFAULT '{}'::json,
    
    context_window INTEGER NOT NULL,
    max_output_tokens INTEGER NOT NULL,
    rpm_limit INTEGER,
    tpm_limit INTEGER,
    
    input_price INTEGER,
    output_price INTEGER,
    
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_featured BOOLEAN NOT NULL DEFAULT false,
    
    tags JSON NOT NULL DEFAULT '[]'::json,
    use_cases JSON NOT NULL DEFAULT '[]'::json,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_ai_models_id ON ai_models(id);
CREATE INDEX IF NOT EXISTS ix_ai_models_slug ON ai_models(slug);
"""

# Modelli FREE da seed
FREE_MODELS = [
    # GROQ Models
    {
        "name": "Llama 3.3 70B Versatile (GROQ)",
        "slug": "llama-3.3-70b-versatile",
        "description": "Meta Llama 3.3 70B su GROQ - Il più veloce (300+ tok/sec). Ottimo per chat, code, RAG. FREE 100k tokens/giorno.",
        "provider": "openai",  # GROQ usa OpenAI-compatible API
        "model_id": "llama-3.3-70b-versatile",
        "capabilities": '["text_generation", "chat", "code_generation", "function_calling"]'::json,
        "config": '{"api_base": "https://api.groq.com/openai/v1", "api_key_env": "GROQ_API_KEY"}'::json,
        "default_params": '{"temperature": 0.7, "max_tokens": 8000}'::json,
        "context_window": 128000,
        "max_output_tokens": 8000,
        "rpm_limit": 30,
        "tpm_limit": 6000,
        "input_price": 0,
        "output_price": 0,
        "is_active": True,
        "is_featured": True,
        "tags": '["fast", "free", "code", "chat"]'::json,
        "use_cases": '["chat", "code", "analysis", "rag"]'::json
    },
    
    # OpenRouter FREE Models
    {
        "name": "Llama 4 Maverick FREE (OpenRouter)",
        "slug": "llama-4-maverick-free",
        "description": "Meta Llama 4 Maverick 400B MoE (17B attivi) su OpenRouter. FREE UNLIMITED con training opt-in. Potente e veloce.",
        "provider": "openai",
        "model_id": "meta-llama/llama-4-maverick:free",
        "capabilities": '["text_generation", "chat", "code_generation", "function_calling"]'::json,
        "config": '{"api_base": "https://openrouter.ai/api/v1", "api_key_env": "OPENROUTER_API_KEY"}'::json,
        "default_params": '{"temperature": 0.7, "max_tokens": 4000}'::json,
        "context_window": 128000,
        "max_output_tokens": 4000,
        "rpm_limit": None,
        "tpm_limit": None,
        "input_price": 0,
        "output_price": 0,
        "is_active": True,
        "is_featured": True,
        "tags": '["free", "unlimited", "powerful"]'::json,
        "use_cases": '["chat", "code", "reasoning"]'::json
    },
    
    {
        "name": "DeepSeek R1 FREE (OpenRouter)",
        "slug": "deepseek-r1-free",
        "description": "DeepSeek R1 reasoning model su OpenRouter. FREE UNLIMITED. Ottimo per problemi complessi e matematica.",
        "provider": "openai",
        "model_id": "deepseek/deepseek-r1:free",
        "capabilities": '["text_generation", "chat", "reasoning"]'::json,
        "config": '{"api_base": "https://openrouter.ai/api/v1", "api_key_env": "OPENROUTER_API_KEY"}'::json,
        "default_params": '{"temperature": 0.3, "max_tokens": 4000}'::json,
        "context_window": 64000,
        "max_output_tokens": 4000,
        "rpm_limit": None,
        "tpm_limit": None,
        "input_price": 0,
        "output_price": 0,
        "is_active": True,
        "is_featured": False,
        "tags": '["free", "reasoning", "math"]'::json,
        "use_cases": '["reasoning", "math", "analysis"]'::json
    },
    
    # Google Gemini
    {
        "name": "Gemini 2.0 Flash (Google)",
        "slug": "gemini-2.0-flash",
        "description": "Google Gemini 2.0 Flash - Velocissimo, multimodale (text, image, video). FREE con 1M tokens/min. Eccellente!",
        "provider": "google",
        "model_id": "gemini-2.0-flash-exp",
        "capabilities": '["text_generation", "chat", "image_analysis", "function_calling", "rag"]'::json,
        "config": '{"api_key_env": "GOOGLE_API_KEY"}'::json,
        "default_params": '{"temperature": 0.7, "max_tokens": 8000}'::json,
        "context_window": 1000000,
        "max_output_tokens": 8000,
        "rpm_limit": 15,
        "tpm_limit": 1000000,
        "input_price": 0,
        "output_price": 0,
        "is_active": True,
        "is_featured": True,
        "tags": '["free", "multimodal", "fast", "google"]'::json,
        "use_cases": '["chat", "multimodal", "rag", "image"]'::json
    },
    
    # HuggingFace
    {
        "name": "DeepSeek V3 (HuggingFace)",
        "slug": "deepseek-v3-hf",
        "description": "DeepSeek V3 su HuggingFace Inference API. Potentissimo MoE. FREE 200 req/ora.",
        "provider": "custom",
        "model_id": "deepseek-ai/DeepSeek-V3",
        "capabilities": '["text_generation", "chat", "code_generation"]'::json,
        "config": '{"api_base": "https://api-inference.huggingface.co/models", "api_key_env": "HUGGINGFACE_API_KEY"}'::json,
        "default_params": '{"temperature": 0.7, "max_tokens": 4000}'::json,
        "context_window": 64000,
        "max_output_tokens": 4000,
        "rpm_limit": 200,
        "tpm_limit": None,
        "input_price": 0,
        "output_price": 0,
        "is_active": True,
        "is_featured": False,
        "tags": '["free", "powerful", "code"]'::json,
        "use_cases": '["code", "chat", "analysis"]'::json
    }
]


async def seed_free_models():
    """Seed modelli AI FREE nel database."""
    from app.infrastructure.database.session import async_engine
    from sqlalchemy.ext.asyncio import AsyncSession
    
    async with async_engine.begin() as conn:
        # Create tables
        print("✅ Creating ai_models table...")
        await conn.execute(text(CREATE_TABLES_SQL))
        
        # Insert models
        print(f"\n📦 Seeding {len(FREE_MODELS)} FREE AI models...")
        
        for model in FREE_MODELS:
            insert_sql = """
                INSERT INTO ai_models (
                    name, slug, description, provider, model_id,
                    capabilities, config, default_params,
                    context_window, max_output_tokens,
                    rpm_limit, tpm_limit, input_price, output_price,
                    is_active, is_featured, tags, use_cases
                ) VALUES (
                    :name, :slug, :description, :provider, :model_id,
                    :capabilities, :config, :default_params,
                    :context_window, :max_output_tokens,
                    :rpm_limit, :tpm_limit, :input_price, :output_price,
                    :is_active, :is_featured, :tags, :use_cases
                )
                ON CONFLICT (slug) DO UPDATE SET
                    description = EXCLUDED.description,
                    is_active = EXCLUDED.is_active,
                    updated_at = NOW()
            """
            
            await conn.execute(text(insert_sql), model)
            print(f"  ✅ {model['name']}")
        
        print(f"\n🎉 Seeded {len(FREE_MODELS)} FREE models successfully!")
        print("\n📊 Models available:")
        print("  - GROQ: llama-3.3-70b-versatile (FASTEST)")
        print("  - OpenRouter: llama-4-maverick-free (UNLIMITED)")
        print("  - OpenRouter: deepseek-r1-free (REASONING)")
        print("  - Google: gemini-2.0-flash (MULTIMODAL)")
        print("  - HuggingFace: deepseek-v3-hf (POWERFUL)")


if __name__ == "__main__":
    print("🚀 iModels FREE Seeder")
    print("=" * 50)
    asyncio.run(seed_free_models())
