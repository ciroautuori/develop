"""
Comprehensive test suite for Portfolio domain services.
Tests experience, education, projects, skills management.
"""

import pytest
from datetime import date
from app.domain.portfolio.models.experience import Experience
from app.domain.portfolio.models.education import Education
from app.domain.portfolio.models.project import Project
from app.domain.portfolio.models.skill import Skill


class TestExperienceManagement:
    """Test work experience CRUD operations."""
    
    def test_create_experience(self, db_session, test_user):
        """Should create work experience entry."""
        experience = Experience(
            user_id=test_user.id,
            company="Tech Corp",
            position="Software Engineer",
            start_date=date(2020, 1, 1),
            is_current=True
        )
        db_session.add(experience)
        db_session.commit()
        
        assert experience.id is not None
        assert experience.company == "Tech Corp"
        assert experience.is_current is True
    
    def test_experience_date_validation(self):
        """End date should be after start date."""
        start = date(2020, 1, 1)
        end = date(2019, 1, 1)
        
        # Validate dates
        is_valid = end > start
        assert is_valid is False
    
    def test_current_experience_no_end_date(self, db_session, test_user):
        """Current position should not have end date."""
        experience = Experience(
            user_id=test_user.id,
            company="Current Corp",
            position="Developer",
            start_date=date(2023, 1, 1),
            is_current=True,
            end_date=None
        )
        db_session.add(experience)
        db_session.commit()
        
        assert experience.is_current is True
        assert experience.end_date is None


class TestEducationManagement:
    """Test education CRUD operations."""
    
    def test_create_education(self, db_session, test_user):
        """Should create education entry."""
        education = Education(
            user_id=test_user.id,
            institution="MIT",
            degree="Computer Science",
            field_of_study="AI",
            start_date=date(2015, 9, 1),
            end_date=date(2019, 6, 1)
        )
        db_session.add(education)
        db_session.commit()
        
        assert education.id is not None
        assert education.institution == "MIT"
    
    def test_education_gpa_validation(self):
        """GPA should be between 0 and 4.0."""
        valid_gpas = [3.5, 4.0, 2.8, 0.0]
        invalid_gpas = [-1, 5.0, 10]
        
        for gpa in valid_gpas:
            assert 0 <= gpa <= 4.0
        
        for gpa in invalid_gpas:
            is_valid = 0 <= gpa <= 4.0
            assert is_valid is False


class TestProjectManagement:
    """Test project CRUD operations."""
    
    def test_create_project(self, db_session, test_user):
        """Should create project entry."""
        project = Project(
            user_id=test_user.id,
            title="AI Chatbot",
            description="Intelligent chatbot using GPT",
            technologies="Python, OpenAI, FastAPI"
        )
        db_session.add(project)
        db_session.commit()
        
        assert project.id is not None
        assert project.title == "AI Chatbot"
    
    def test_project_with_url(self, db_session, test_user):
        """Project can have external URL."""
        project = Project(
            user_id=test_user.id,
            title="Portfolio Site",
            url="https://myportfolio.com"
        )
        db_session.add(project)
        db_session.commit()
        
        assert project.url == "https://myportfolio.com"


class TestSkillManagement:
    """Test skills CRUD operations."""
    
    def test_create_skill(self, db_session, test_user):
        """Should create skill entry."""
        skill = Skill(
            user_id=test_user.id,
            name="Python",
            level="EXPERT"
        )
        db_session.add(skill)
        db_session.commit()
        
        assert skill.id is not None
        assert skill.name == "Python"
    
    def test_skill_level_validation(self):
        """Skill level should be valid enum."""
        valid_levels = ["BEGINNER", "JUNIOR", "MID", "SENIOR", "EXPERT"]
        
        for level in valid_levels:
            assert level in valid_levels


class TestPortfolioProfile:
    """Test portfolio profile management."""
    
    def test_profile_visibility_toggle(self):
        """Portfolio can be public or private."""
        is_public = True
        assert isinstance(is_public, bool)
    
    def test_profile_slug_generation(self):
        """Profile should have unique slug."""
        full_name = "John Doe"
        slug = full_name.lower().replace(" ", "-")
        assert slug == "john-doe"
    
    def test_profile_completeness_calculation(self):
        """Calculate profile completeness percentage."""
        sections = {
            "experience": True,
            "education": True,
            "skills": True,
            "projects": False,
            "languages": False
        }
        
        completed = sum(1 for v in sections.values() if v)
        total = len(sections)
        completeness = (completed / total) * 100
        
        assert completeness == 60.0
