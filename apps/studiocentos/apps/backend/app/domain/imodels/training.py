"""
iModels Training - Dataset Generation + Fine-tuning
Crea dataset da conversazioni customer service per training modelli
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import json
import os


class TrainingService:
    """Service per training e fine-tuning modelli AI."""

    @staticmethod
    def extract_customer_conversations(
        db: Session,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Estrae conversazioni customer service dal database.

        Formato dataset per fine-tuning:
        {
            "messages": [
                {"role": "system", "content": "Sei customer service di StudioCentOS..."},
                {"role": "user", "content": "Come posso prenotare una consulenza?"},
                {"role": "assistant", "content": "Puoi prenotare tramite..."}
            ]
        }
        """

        # Get conversations from booking/messages tables
        query = text("""
            SELECT
                b.id as booking_id,
                b.customer_name,
                b.customer_email,
                b.service_type,
                b.notes,
                b.status,
                b.created_at
            FROM bookings b
            WHERE b.status IN ('confirmed', 'completed')
            ORDER BY b.created_at DESC
            LIMIT :limit
        """)

        result = db.execute(query, {"limit": limit})
        rows = result.fetchall()

        dataset = []

        # System prompt per StudioCentOS
        system_prompt = """Sei l'assistente virtuale di StudioCentOS, software house di Salerno specializzata in:
- 🤖 AI Integration (ChatGPT, RAG, Agents)
- 💻 Sviluppo Software (React 19, FastAPI, PostgreSQL)
- 📱 App Mobile (React Native, Expo 52)
- 🌐 Web Development (Siti e webapp enterprise)

Rispondi in modo:
- Professionale ma amichevole
- Chiaro e conciso
- Focalizzato su benefici concreti
- Con call-to-action per consulenza gratuita

Info azienda:
- Location: Salerno, Campania
- Email: info@studiocentos.it
- Website: https://studiocentos.it
- Time to market: 45 giorni
- Made in Italy 🇮🇹
"""

        for row in rows:
            # Genera conversazione da booking
            user_message = f"Vorrei prenotare una consulenza per {row[3]}. {row[4] or ''}"

            assistant_message = f"""Certo! Sarò felice di aiutarti per {row[3]}.

Offriamo consulenza gratuita di 30 minuti per:
- Analizzare il tuo progetto
- Proporre soluzioni tecniche
- Stimare tempi e costi

Puoi prenotare su: https://studiocentos.it#prenota

Il tuo nome è {row[1]} e email {row[2]}, corretto?

Rispondo entro 24 ore. Made in Salerno 🇮🇹"""

            dataset.append({
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": assistant_message}
                ],
                "metadata": {
                    "booking_id": row[0],
                    "service_type": row[3],
                    "created_at": row[6].isoformat()
                }
            })

        return dataset

    @staticmethod
    def create_training_dataset_jsonl(
        db: Session,
        output_path: str = "/tmp/studiocentos_training.jsonl"
    ) -> str:
        """
        Crea file JSONL per fine-tuning OpenAI/HuggingFace.

        Returns: path del file generato
        """

        dataset = TrainingService.extract_customer_conversations(db)

        # Write JSONL
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in dataset:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')

        print(f"✅ Dataset created: {output_path}")
        print(f"📊 Total conversations: {len(dataset)}")

        return output_path

    @staticmethod
    def validate_dataset(dataset_path: str) -> Dict[str, Any]:
        """Valida dataset per training."""

        with open(dataset_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        total = len(lines)
        valid = 0
        errors = []

        for i, line in enumerate(lines):
            try:
                data = json.loads(line)

                # Check required fields
                if "messages" not in data:
                    errors.append(f"Line {i+1}: Missing 'messages' field")
                    continue

                messages = data["messages"]

                # Check roles
                roles = [m.get("role") for m in messages]
                if "system" not in roles or "user" not in roles or "assistant" not in roles:
                    errors.append(f"Line {i+1}: Missing required roles")
                    continue

                valid += 1

            except json.JSONDecodeError:
                errors.append(f"Line {i+1}: Invalid JSON")

        return {
            "total": total,
            "valid": valid,
            "invalid": total - valid,
            "errors": errors[:10],  # First 10 errors
            "is_valid": valid == total
        }

    @staticmethod
    async def fine_tune_openai(
        dataset_path: str,
        model: str = "gpt-3.5-turbo",
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fine-tune modello OpenAI.

        Steps:
        1. Upload dataset
        2. Create fine-tuning job
        3. Monitor status
        4. Get fine-tuned model ID
        """

        # OpenAI fine-tuning requires additional setup
        # See: https://platform.openai.com/docs/guides/fine-tuning

        return {
            "status": "pending",
            "message": "Fine-tuning requires OpenAI API configuration. Contact admin.",
            "dataset_path": dataset_path,
            "base_model": model
        }

    @staticmethod
    def generate_synthetic_qa_pairs(
        db: Session,
        num_pairs: int = 100
    ) -> List[Dict[str, str]]:
        """
        Genera coppie Q&A sintetiche per augmentation dataset.

        Usa servizi esistenti come base.
        """

        # Get services from database
        query = text("""
            SELECT title, description, features, benefits
            FROM services
            WHERE is_active = true
        """)

        result = db.execute(query)
        services = result.fetchall()

        qa_pairs = []

        # Template domande
        question_templates = [
            "Cosa offrite per {}?",
            "Quanto costa {}?",
            "Come funziona {}?",
            "Che vantaggi ha {}?",
            "Posso avere info su {}?",
            "Supportate {}?",
            "Fate anche {}?",
        ]

        for service in services:
            title = service[0]
            description = service[1]
            features = service[2] or []
            benefits = service[3] or []

            for template in question_templates[:3]:  # 3 domande per servizio
                question = template.format(title.lower())

                answer = f"""{title}: {description}

Caratteristiche:
{chr(10).join(f"- {f}" for f in features[:3])}

Vantaggi:
{chr(10).join(f"- {b}" for b in benefits[:2])}

Prenota consulenza gratuita: https://studiocentos.it#prenota"""

                qa_pairs.append({
                    "question": question,
                    "answer": answer,
                    "service": title
                })

        return qa_pairs[:num_pairs]
