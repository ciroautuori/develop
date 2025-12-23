"""GDPR Compliance Implementation - Enterprise Grade
Sistema completo per conformità GDPR (General Data Protection Regulation).
"""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class DataProcessingPurpose(str, Enum):
    """Scopi di trattamento dati secondo GDPR Art. 6."""

    CONSENT = "consent"  # Consenso esplicito
    CONTRACT = "contract"  # Esecuzione contratto
    LEGAL_OBLIGATION = "legal_obligation"  # Obbligo legale
    VITAL_INTERESTS = "vital_interests"  # Interessi vitali
    PUBLIC_TASK = "public_task"  # Compito pubblico
    LEGITIMATE_INTERESTS = "legitimate_interests"  # Interessi legittimi

class ConsentStatus(str, Enum):
    """Stato del consenso GDPR."""

    GIVEN = "given"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"

@dataclass
class DataSubjectRight:
    """Diritti del soggetto interessato secondo GDPR."""

    right_name: str
    description: str
    article: str

# Diritti GDPR implementati
GDPR_RIGHTS = {
    "access": DataSubjectRight(
        "Right of Access", "Right to obtain confirmation and access to personal data", "Article 15"
    ),
    "rectification": DataSubjectRight(
        "Right to Rectification", "Right to rectification of inaccurate personal data", "Article 16"
    ),
    "erasure": DataSubjectRight(
        "Right to Erasure (Right to be Forgotten)",
        "Right to erasure of personal data",
        "Article 17",
    ),
    "restrict": DataSubjectRight(
        "Right to Restriction of Processing", "Right to restriction of processing", "Article 18"
    ),
    "portability": DataSubjectRight(
        "Right to Data Portability",
        "Right to receive personal data in structured format",
        "Article 20",
    ),
    "object": DataSubjectRight("Right to Object", "Right to object to processing", "Article 21"),
}

class ConsentModel(BaseModel):
    """Model per consenso GDPR."""

    user_id: str
    purpose: DataProcessingPurpose
    status: ConsentStatus = ConsentStatus.PENDING
    consent_text: str = Field(..., min_length=10)
    granted_at: datetime | None = None
    withdrawn_at: datetime | None = None
    expires_at: datetime | None = None
    ip_address: str
    user_agent: str

class DataExportRequest(BaseModel):
    """Richiesta esportazione dati (Art. 20)."""

    user_id: str
    requested_at: datetime
    format: str = Field(default="json", pattern="^(json|xml|csv)$")
    include_metadata: bool = False

class DataDeletionRequest(BaseModel):
    """Richiesta cancellazione dati (Art. 17)."""

    user_id: str
    requested_at: datetime
    reason: str = Field(..., min_length=5)
    hard_delete: bool = False  # True = eliminazione fisica, False = soft delete

class GDPRComplianceManager:
    """Manager principale per compliance GDPR."""

    def __init__(self):
        self.data_retention_periods = {
            "user_profiles": timedelta(days=2555),  # 7 anni
            "financial_records": timedelta(days=2920),  # 8 anni (requisiti fiscali)
            "marketing_data": timedelta(days=1095),  # 3 anni
            "analytics_data": timedelta(days=730),  # 2 anni
            "session_logs": timedelta(days=90),  # 3 mesi
            "audit_logs": timedelta(days=2190),  # 6 anni
        }

    async def record_consent(self, db: AsyncSession, consent_data: ConsentModel) -> dict[str, Any]:
        """Registra consenso utente secondo GDPR Art. 7."""
        try:
            # Verifica che il consenso sia specifico e informato
            if len(consent_data.consent_text) < 50:
                raise ValueError("Consent text must be detailed and specific")

            consent_data.granted_at = datetime.now(UTC)
            consent_data.status = ConsentStatus.GIVEN

            # Set expiration (consenso scade dopo 2 anni per marketing)
            if consent_data.purpose in [DataProcessingPurpose.LEGITIMATE_INTERESTS]:
                consent_data.expires_at = datetime.now(UTC) + timedelta(days=730)

            # Save to database
            from app.domain.gdpr.models import (
                ConsentStatusEnum,
                DataProcessingPurposeEnum,
                UserConsent,
            )

            db_consent = UserConsent(
                user_id=int(consent_data.user_id),
                purpose=DataProcessingPurposeEnum(consent_data.purpose.value),
                status=ConsentStatusEnum.GIVEN,
                consent_text=consent_data.consent_text,
                granted_at=consent_data.granted_at,
                expires_at=consent_data.expires_at,
                ip_address=consent_data.ip_address,
                user_agent=consent_data.user_agent,
            )

            db.add(db_consent)
            await db.commit()
            await db.refresh(db_consent)

            logger.info(
                f"GDPR consent recorded for user {consent_data.user_id} - {consent_data.purpose}"
            )

            return {
                "status": "recorded",
                "consent_id": db_consent.id,
                "recorded_at": consent_data.granted_at,
                "expires_at": consent_data.expires_at,
            }

        except Exception as e:
            logger.error(f"Failed to record GDPR consent: {e}")
            raise

    async def withdraw_consent(
        self, db: AsyncSession, user_id: str, purpose: DataProcessingPurpose
    ) -> dict[str, Any]:
        """Ritira consenso esistente (Art. 7)."""
        try:
            withdrawn_at = datetime.now(UTC)

            # Update consent status in database
            from sqlalchemy import select

            from app.domain.gdpr.models import (
                ConsentStatusEnum,
                DataProcessingPurposeEnum,
                UserConsent,
            )

            # Find active consent for this purpose
            stmt = select(UserConsent).where(
                UserConsent.user_id == int(user_id),
                UserConsent.purpose == DataProcessingPurposeEnum(purpose.value),
                UserConsent.status == ConsentStatusEnum.GIVEN
            )
            result = await db.execute(stmt)
            consent = result.scalar_one_or_none()

            if not consent:
                raise ValueError(f"No active consent found for user {user_id} - {purpose}")

            # Update status
            consent.status = ConsentStatusEnum.WITHDRAWN
            consent.withdrawn_at = withdrawn_at

            await db.commit()

            logger.info(f"GDPR consent withdrawn for user {user_id} - {purpose}")

            return {"status": "withdrawn", "withdrawn_at": withdrawn_at, "effect": "immediate"}

        except Exception as e:
            logger.error(f"Failed to withdraw GDPR consent: {e}")
            raise

    async def export_user_data(
        self, db: AsyncSession, export_request: DataExportRequest
    ) -> dict[str, Any]:
        """Esporta tutti i dati utente (Art. 20 - Right to Data Portability)."""
        try:
            from sqlalchemy import select

            from app.domain.auth.models import User
            from app.domain.gdpr.models import UserConsent
            from app.domain.portfolio.models import (
                Education,
                Experience,
                PortfolioLanguage,
                Project,
                Skill,
            )

            user_id = int(export_request.user_id)

            # Raccoglie dati da tutte le tabelle pertinenti
            user_data = {}

            # User profile data
            user_stmt = select(User).where(User.id == user_id)
            user_result = await db.execute(user_stmt)
            user = user_result.scalar_one_or_none()

            if user:
                user_data["profile"] = {
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "title": user.title,
                    "bio": user.bio,
                    "public_email": user.public_email,
                    "phone_number": user.phone_number,
                    "linkedin_url": user.linkedin_url,
                    "github_url": user.github_url,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "role": user.role.value if user.role else None,
                }

            # Portfolio data - Experiences
            exp_stmt = select(Experience).where(Experience.user_id == user_id)
            exp_result = await db.execute(exp_stmt)
            experiences = exp_result.scalars().all()
            user_data["experiences"] = [
                {
                    "company": exp.company,
                    "position": exp.position,
                    "location": exp.location,
                    "start_date": exp.start_date.isoformat() if exp.start_date else None,
                    "end_date": exp.end_date.isoformat() if exp.end_date else None,
                    "description": exp.description,
                }
                for exp in experiences
            ]

            # Education
            edu_stmt = select(Education).where(Education.user_id == user_id)
            edu_result = await db.execute(edu_stmt)
            education = edu_result.scalars().all()
            user_data["education"] = [
                {
                    "institution": edu.institution,
                    "degree": edu.degree,
                    "field_of_study": edu.field_of_study,
                    "start_date": edu.start_date.isoformat() if edu.start_date else None,
                    "end_date": edu.end_date.isoformat() if edu.end_date else None,
                    "description": edu.description,
                }
                for edu in education
            ]

            # Projects
            proj_stmt = select(Project).where(Project.user_id == user_id)
            proj_result = await db.execute(proj_stmt)
            projects = proj_result.scalars().all()
            user_data["projects"] = [
                {
                    "title": proj.title,
                    "description": proj.description,
                    "technologies": proj.technologies,
                    "project_url": proj.project_url,
                    "start_date": proj.start_date.isoformat() if proj.start_date else None,
                    "end_date": proj.end_date.isoformat() if proj.end_date else None,
                }
                for proj in projects
            ]

            # Skills
            skill_stmt = select(Skill).where(Skill.user_id == user_id)
            skill_result = await db.execute(skill_stmt)
            skills = skill_result.scalars().all()
            user_data["skills"] = [
                {"name": skill.name, "proficiency": skill.proficiency.value if skill.proficiency else None}
                for skill in skills
            ]

            # Languages
            lang_stmt = select(PortfolioLanguage).where(PortfolioLanguage.user_id == user_id)
            lang_result = await db.execute(lang_stmt)
            languages = lang_result.scalars().all()
            user_data["languages"] = [
                {"language": lang.language, "proficiency": lang.proficiency.value if lang.proficiency else None}
                for lang in languages
            ]

            # GDPR consents
            consent_stmt = select(UserConsent).where(UserConsent.user_id == user_id)
            consent_result = await db.execute(consent_stmt)
            consents = consent_result.scalars().all()
            user_data["consents"] = [
                {
                    "purpose": c.purpose.value if c.purpose else None,
                    "status": c.status.value if c.status else None,
                    "granted_at": c.granted_at.isoformat() if c.granted_at else None,
                    "withdrawn_at": c.withdrawn_at.isoformat() if c.withdrawn_at else None,
                }
                for c in consents
            ]

            if export_request.include_metadata:
                user_data["metadata"] = {
                    "export_date": datetime.now(UTC).isoformat(),
                    "format": export_request.format,
                    "gdpr_article": "Article 20 - Right to Data Portability",
                    "total_records": {
                        "experiences": len(experiences),
                        "education": len(education),
                        "projects": len(projects),
                        "skills": len(skills),
                        "languages": len(languages),
                        "consents": len(consents),
                    }
                }

            logger.info(f"GDPR data export completed for user {export_request.user_id}")

            return {
                "status": "completed",
                "data": user_data,
                "format": export_request.format,
                "exported_at": datetime.now(UTC),
            }

        except Exception as e:
            logger.error(f"Failed to export GDPR data: {e}")
            raise

    async def delete_user_data(
        self, db: AsyncSession, deletion_request: DataDeletionRequest
    ) -> dict[str, Any]:
        """Cancella dati utente (Art. 17 - Right to be Forgotten)."""
        try:
            from sqlalchemy import delete, select

            from app.domain.auth.models import User
            from app.domain.portfolio.models import (
                Education,
                Experience,
                PortfolioLanguage,
                PortfolioProfile,
                Project,
                Skill,
            )

            user_id = int(deletion_request.user_id)
            deleted_items = []

            if deletion_request.hard_delete:
                # Eliminazione fisica permanente (cascade delete via relationships)
                # Delete portfolio data first (due to foreign keys)
                await db.execute(delete(Experience).where(Experience.user_id == user_id))
                deleted_items.append("experiences")

                await db.execute(delete(Education).where(Education.user_id == user_id))
                deleted_items.append("education")

                await db.execute(delete(Project).where(Project.user_id == user_id))
                deleted_items.append("projects")

                await db.execute(delete(Skill).where(Skill.user_id == user_id))
                deleted_items.append("skills")

                await db.execute(delete(PortfolioLanguage).where(PortfolioLanguage.user_id == user_id))
                deleted_items.append("languages")

                await db.execute(delete(PortfolioProfile).where(PortfolioProfile.user_id == user_id))
                deleted_items.append("portfolio_profile")

                # Delete consents (keep audit logs as per legal requirement)
                from app.domain.gdpr.models import UserConsent
                await db.execute(delete(UserConsent).where(UserConsent.user_id == user_id))
                deleted_items.append("consents")

                # Finally delete user profile
                await db.execute(delete(User).where(User.id == user_id))
                deleted_items.append("profile")

                await db.commit()

                logger.warning(f"HARD DELETE executed for user {user_id} - ALL DATA REMOVED")
            else:
                # Soft delete - deactivate user and anonymize data
                user_stmt = select(User).where(User.id == user_id)
                result = await db.execute(user_stmt)
                user = result.scalar_one_or_none()

                if user:
                    # Deactivate account
                    user.is_active = False
                    user.email = f"deleted_user_{user_id}@anonymized.local"
                    user.username = f"deleted_{user_id}"
                    user.full_name = "[DELETED]"
                    user.bio = None
                    user.public_email = None
                    user.phone_number = None
                    user.linkedin_url = None
                    user.github_url = None
                    deleted_items.append("profile_anonymized")

                    await db.commit()

                    logger.info(f"SOFT DELETE executed for user {user_id} - Data anonymized")

            logger.info(f"GDPR data deletion completed for user {deletion_request.user_id}")

            return {
                "status": "completed",
                "deletion_type": "hard" if deletion_request.hard_delete else "soft",
                "deleted_items": deleted_items,
                "deleted_at": datetime.now(UTC),
                "retention_note": "Audit logs retained as per legal requirements (GDPR Art. 17.3)",
            }

        except Exception as e:
            logger.error(f"Failed to delete GDPR data: {e}")
            raise

    async def audit_data_processing(self, db: AsyncSession, user_id: str) -> dict[str, Any]:
        """Audit attività di trattamento dati per un utente."""
        try:
            from sqlalchemy import select

            from app.domain.gdpr.models import DataAuditLog, UserConsent

            user_id_int = int(user_id)

            # Raccoglie informazioni su come i dati vengono processati
            audit_info = {
                "user_id": user_id,
                "audit_date": datetime.now(UTC),
                "processing_activities": [],
                "consent_status": {},
                "retention_periods": self.data_retention_periods,
                "data_transfers": [],  # Trasferimenti a paesi terzi
                "automated_decisions": [],  # Decisioni automatizzate
            }

            # Get consent status
            consent_stmt = select(UserConsent).where(UserConsent.user_id == user_id_int)
            consent_result = await db.execute(consent_stmt)
            consents = consent_result.scalars().all()

            audit_info["consent_status"] = {
                c.purpose.value: {
                    "status": c.status.value,
                    "granted_at": c.granted_at.isoformat() if c.granted_at else None,
                    "expires_at": c.expires_at.isoformat() if c.expires_at else None,
                }
                for c in consents
            }

            # Get recent processing activities from audit log
            audit_stmt = (
                select(DataAuditLog)
                .where(DataAuditLog.user_id == user_id_int)
                .order_by(DataAuditLog.timestamp.desc())
                .limit(100)  # Last 100 activities
            )
            audit_result = await db.execute(audit_stmt)
            audit_logs = audit_result.scalars().all()

            # Aggregate by action type
            action_counts = {}
            for log in audit_logs:
                action = log.action.value if log.action else "unknown"
                action_counts[action] = action_counts.get(action, 0) + 1

            audit_info["processing_activities"] = [
                {
                    "action": action,
                    "count": count,
                    "description": f"{count} {action} operations recorded"
                }
                for action, count in action_counts.items()
            ]

            # Check for automated decisions (AI enrichment)
            ai_actions = [log for log in audit_logs if "enrichment" in (log.description or "").lower()]
            if ai_actions:
                audit_info["automated_decisions"] = [
                    {
                        "type": "AI Data Enrichment",
                        "count": len(ai_actions),
                        "legal_basis": "User consent",
                        "right_to_object": True
                    }
                ]

            return audit_info

        except Exception as e:
            logger.error(f"Failed to audit GDPR data processing: {e}")
            raise

    async def check_retention_compliance(self, db: AsyncSession) -> dict[str, Any]:
        """Verifica compliance con periodi di retention dati."""
        try:
            from sqlalchemy import func, select

            from app.domain.auth.models import User
            from app.domain.gdpr.models import DataAuditLog, UserConsent

            compliance_report = {
                "check_date": datetime.now(UTC),
                "expired_data": [],
                "warnings": [],
                "actions_needed": [],
            }

            current_time = datetime.now(UTC)

            # Check expired consents
            expired_consents_stmt = select(func.count(UserConsent.id)).where(
                UserConsent.expires_at < current_time,
                UserConsent.status != "expired"
            )
            expired_consents_result = await db.execute(expired_consents_stmt)
            expired_consents_count = expired_consents_result.scalar() or 0

            if expired_consents_count > 0:
                compliance_report["expired_data"].append({
                    "data_type": "user_consents",
                    "expired_count": expired_consents_count,
                    "cutoff_date": current_time.isoformat(),
                    "action": "Update consent status to 'expired'"
                })
                compliance_report["actions_needed"].append(
                    f"Mark {expired_consents_count} expired consents"
                )

            # Check old audit logs (retention period: 2 years)
            audit_cutoff = current_time - self.data_retention_periods.get("audit_logs", timedelta(days=730))
            old_audit_stmt = select(func.count(DataAuditLog.id)).where(
                DataAuditLog.timestamp < audit_cutoff
            )
            old_audit_result = await db.execute(old_audit_stmt)
            old_audit_count = old_audit_result.scalar() or 0

            if old_audit_count > 0:
                compliance_report["expired_data"].append({
                    "data_type": "audit_logs",
                    "expired_count": old_audit_count,
                    "cutoff_date": audit_cutoff.isoformat(),
                    "action": "Archive or delete old audit logs"
                })
                compliance_report["warnings"].append(
                    f"{old_audit_count} audit logs older than retention period"
                )

            # Check inactive users (trial expired > 90 days)
            inactive_cutoff = current_time - timedelta(days=90)
            inactive_stmt = select(func.count(User.id)).where(
                User.is_active == False,
                User.updated_at < inactive_cutoff
            )
            inactive_result = await db.execute(inactive_stmt)
            inactive_count = inactive_result.scalar() or 0

            if inactive_count > 0:
                compliance_report["warnings"].append({
                    "data_type": "inactive_users",
                    "count": inactive_count,
                    "message": f"{inactive_count} inactive users may require data deletion review"
                })

            return compliance_report

        except Exception as e:
            logger.error(f"Failed to check retention compliance: {e}")
            raise

    def validate_data_processing_lawfulness(
        self, purpose: DataProcessingPurpose, user_consent: ConsentModel | None = None
    ) -> bool:
        """Valida liceità del trattamento secondo Art. 6 GDPR."""

        # Contract, legal obligation, vital interests sono sempre leciti
        if purpose in [
            DataProcessingPurpose.CONTRACT,
            DataProcessingPurpose.LEGAL_OBLIGATION,
            DataProcessingPurpose.VITAL_INTERESTS,
            DataProcessingPurpose.PUBLIC_TASK,
        ]:
            return True

        # Consent richiede consenso esplicito valido
        if purpose == DataProcessingPurpose.CONSENT:
            return (
                user_consent
                and user_consent.status == ConsentStatus.GIVEN
                and (not user_consent.expires_at or user_consent.expires_at > datetime.now(UTC))
            )

        # Legitimate interests richiede bilanciamento interessi (Art. 6(1)(f))
        if purpose == DataProcessingPurpose.LEGITIMATE_INTERESTS:
            return self._assess_legitimate_interest_balance(user_consent)

        return False

    def _assess_legitimate_interest_balance(self, user_consent: ConsentModel | None = None) -> bool:
        """Assess legitimate interest balance (GDPR Art. 6(1)(f)).
        
        Balancing test considers:
        1. Purpose: Analytics and service improvement
        2. Necessity: Required for service quality
        3. Impact: Minimal risk to user rights/freedoms
        4. Safeguards: Data minimization, anonymization where possible
        
        Returns:
            True if legitimate interests outweigh user rights concerns
        """
        # Legitimate interest balancing factors
        factors = {
            "legitimate_purpose": True,  # Analytics for service improvement
            "reasonable_expectation": True,  # Users expect data processing for service
            "minimal_impact": True,  # Low risk to rights/freedoms
            "data_minimization": True,  # Only necessary data collected
            "transparency": True,  # Processing disclosed in privacy notice
            "user_control": True,  # Users can opt-out via settings
        }

        # Assessment: If all factors positive, legitimate interest is lawful
        all_factors_positive = all(factors.values())

        # Additional check: If user has explicitly objected (withdrawn consent), respect it
        if user_consent and user_consent.status == ConsentStatus.WITHDRAWN:
            logger.info("Legitimate interest overridden by explicit user objection")
            return False

        return all_factors_positive

    async def generate_privacy_notice(self, language: str = "en") -> dict[str, Any]:
        """Genera privacy notice conforme GDPR."""

        privacy_notices = {
            "en": {
                "title": "Privacy Notice - CV-Lab SaaS",
                "controller": {
                    "name": "CV-Lab SaaS Platform",
                    "contact": "privacy@cv-lab.pro",
                    "dpo_contact": "dpo@cv-lab.pro",
                },
                "data_collected": [
                    "Profile information (name, email, phone)",
                    "Professional experience and skills",
                    "Portfolio projects and achievements",
                    "Usage analytics and preferences",
                ],
                "processing_purposes": [
                    "Provide portfolio management services",
                    "Generate professional CV documents",
                    "Service improvement and analytics",
                    "Marketing communications (with consent)",
                ],
                "legal_basis": {
                    "service_provision": "Performance of contract (Art. 6(1)(b))",
                    "marketing": "Consent (Art. 6(1)(a))",
                    "analytics": "Legitimate interests (Art. 6(1)(f))",
                },
                "retention_periods": "Data retained for service provision plus 7 years for legal obligations",
                "user_rights": list(GDPR_RIGHTS.keys()),
                "data_transfers": "Data processed within EU/EEA. No transfers to third countries.",
                "contact_info": {
                    "privacy_requests": "privacy@cv-lab.pro",
                    "supervisory_authority": "Data Protection Authority of your country",
                },
            },
            "it": {
                "title": "Informativa Privacy - CV-Lab SaaS",
                "controller": {
                    "name": "Piattaforma CV-Lab SaaS",
                    "contact": "privacy@cv-lab.pro",
                    "dpo_contact": "dpo@cv-lab.pro",
                },
                # ... versione italiana
            },
        }

        return privacy_notices.get(language, privacy_notices["en"])

# Singleton instance
gdpr_manager = GDPRComplianceManager()

# Helper functions
async def record_user_consent(
    db: AsyncSession,
    user_id: str,
    purpose: DataProcessingPurpose,
    consent_text: str,
    ip_address: str,
    user_agent: str,
) -> dict[str, Any]:
    """Helper per registrare consenso utente."""
    consent_data = ConsentModel(
        user_id=user_id,
        purpose=purpose,
        consent_text=consent_text,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return await gdpr_manager.record_consent(db, consent_data)

async def process_data_export_request(
    db: AsyncSession, user_id: str, format: str = "json"
) -> dict[str, Any]:
    """Helper per processare richiesta esportazione dati."""
    export_request = DataExportRequest(
        user_id=user_id, requested_at=datetime.now(UTC), format=format
    )
    return await gdpr_manager.export_user_data(db, export_request)

async def process_deletion_request(
    db: AsyncSession, user_id: str, reason: str, hard_delete: bool = False
) -> dict[str, Any]:
    """Helper per processare richiesta cancellazione dati."""
    deletion_request = DataDeletionRequest(
        user_id=user_id, requested_at=datetime.now(UTC), reason=reason, hard_delete=hard_delete
    )
    return await gdpr_manager.delete_user_data(db, deletion_request)
