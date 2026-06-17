from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class Experience(BaseModel):
    """A single entry in the Experience section."""

    title: str
    company: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    is_current: bool = False


class Education(BaseModel):
    """A single entry in the Education section."""

    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    activities: Optional[str] = None


class Skill(BaseModel):
    """A skill listed on the profile."""

    name: str
    endorsements: int = 0


class LinkedInProfile(BaseModel):
    """
    The top-level model for a scraped/fetched LinkedIn profile.
    All fields are optional except profile_url and full_name.
    """

    profile_url: str
    full_name: str
    headline: Optional[str] = None
    location: Optional[str] = None
    about: Optional[str] = None
    connections: Optional[str] = None       # LinkedIn shows "500+" etc.
    followers: Optional[int] = None
    profile_image_url: Optional[str] = None
    experience: list[Experience] = []
    education: list[Education] = []
    skills: list[Skill] = []
    scraped_at: str = datetime.now().isoformat()
    source: str = "scraper"                 # "api" | "scraper"

    @field_validator("full_name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("full_name cannot be empty")
        return v.strip()

    def to_flat_dict(self) -> dict:
        """
        Returns a flat dictionary suitable for CSV export.
        Nested fields (experience, education, skills) are simplified.
        """
        return {
            "profile_url": self.profile_url,
            "full_name": self.full_name,
            "headline": self.headline,
            "location": self.location,
            "about": (self.about or "")[:300],        # Truncate for CSV
            "connections": self.connections,
            "current_title": self.experience[0].title if self.experience else None,
            "current_company": self.experience[0].company if self.experience else None,
            "top_3_skills": ", ".join(s.name for s in self.skills[:3]),
            "num_experiences": len(self.experience),
            "num_skills": len(self.skills),
            "scraped_at": self.scraped_at,
            "source": self.source,
        }
