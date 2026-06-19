from bs4 import BeautifulSoup, Tag
from typing import Optional
from datetime import datetime

from src.models.profile import LinkedInProfile, Experience, Education, Skill
from src.utils.logger import logger


class ProfileScrapper:
    """
    Parses a fully rendered LinkedIn profile page using BeautifulSoup.

    LinkedIn's HTML structure changes frequently — class names here
    were correct as of mid-2024. If selectors break, inspect the live
    page with browser DevTools and update the class fragments below.

    Usage:
        scraper = ProfileScraper()
        profile = scraper.parse(html, "https://linkedin.com/in/someone/")
    """


    def parse(self, html: str, profile_url: str) -> LinkedInProfile:
        soup = BeautifulSoup(html, 'lxml')

        return LinkedInProfile(
            profile_url=profile_url,
            full_name=self._get_name(soup),
            headline=self._get_headline(soup),
            location=self._get_location(soup),
            about=self._get_about(soup),
            connections=self._get_connections(soup),
            profile_image_url=self._get_avatar(soup),
            experience=self._get_experience(soup),
            education=self._get_education(soup),
            skills=self._get_skills(soup),
            scraped_at=datetime.now().isoformat(),
            source="scrapper",

        )

    # =============================================================
    #                       Helpers
    # =============================================================

    def _text(self, el:Optional[Tag]) -> Optional[str]:
        return el.get_text(strip=True) if el else None

    def _find_section(self, soup: BeautifulSoup, section_id: str) -> Optional[Tag]:
        return soup.find("section", {"id": section_id})

    # =============================================================
    #                    Header Fields
    # =============================================================

    def _get_name(self, soup: BeautifulSoup) -> str:
        el = soup.find("h1", class_= lambda c: c and "text-heading-xlarge" in c )
        return self._text(el) or "Unknown"

    def _get_headline(self, soup:BeautifulSoup) -> Optional[str]:
        el = soup.find("div", class_=lambda c:c and "text-body-medium" in c and "break-words" in c)
        return self._text(el)

    def _get_location(self, soup:BeautifulSoup) -> Optional[str]:
        el = soup.find(
            "span",
            class_= lambda c: c and "text-body-small" in c and "inline" in c and "t-black--light" in c,
        )
        return self._text(el)

    def _get_connections(self,soup: BeautifulSoup) -> Optional[str]:
        el = soup.find("span", string=lambda t: t and "connection" in t.lower()  )
        return self._text(el)

    def _get_avatar(self, soup: BeautifulSoup) -> Optional[str]:
        img = soup.find("img", class_=lambda c: c and "profile-photo-edit__preview" in c)
        if img:
            return img.get("src")
        return None

    # =========================================================
    #                         About
    # =========================================================

    def _get_about(self, soup: BeautifulSoup) -> Optional[str]:
        section = self._find_section(soup, "about")
        if section:
            el = section.find("span" , {"aria-hidden" : "true"})
            return self._text(el)
        return None


#      ==========================================================
#                         Experience
#      ==========================================================

    def _get_experience(self, soup: BeautifulSoup) -> list[Experience]:
        results = []
        section = self._find_section(soup , "experience")

        if not section:
            logger.debug("No 'Experience' section found")
            return results


        items = section.find_all("li", class_ = lambda c: c and "artdeco-list__item" in c)
        for item in items:
            spans = item.find_all("span" , {"aria-hidden" : "true"})
            if not spans:
                continue

            title = self._text(spans[0]) or "Unknown"
            company = self._text(spans[1]) if len(spans) > 1 else "Unknown"

            date_range = item.find("span", class_=lambda c:c and "date-range" in c)
            dates = date_range.find_all("time") if date_range else []
            start_date = self._text(dates[0]) if dates else None
            end_date = self._text(dates[1]) if len(dates) > 1 else None
            location_el = item.find("span" , class_=lambda c: c and "bullet" in c)
            location = self._text(location_el)

            results.append(
                Experience(
                    title=title,
                    company=company,
                    start_date=start_date,
                    end_date=end_date,
                    location=location,
                    is_current=end_date is None or "present" in (end_date or "").lower(),
                )
            )

        logger.debug(f"Found {len(results)} experience entries.")
        return results


#     ====================================================================
#                            Education
#     ====================================================================


    def _get_education(self, soup: BeautifulSoup) -> list[Education]:
        results = []
        section = self._find_section(soup, "education")

        if not section:
            return results


        items = section.find_all("li" , class_=lambda c:c and "artdeco-list__item" in c)
        for item in items:
            spans = item.find_all("span" , {"aria-hidden" : "true"})
            institution = self._text(spans[0]) or "Unknown"
            degree = self._text(spans[1]) if len(spans) > 1 else None
            field = self._text(spans[2]) if len(spans) > 2 else None

            results.append(
                Education(
                    institution=institution,
                    degree=degree,
                    field_of_study=field
                )
            )

        return results

#     ==========================================================
#                         Skills
#     ==========================================================

    def _get_skills(self, soup: BeautifulSoup) -> list[Skill]:
        results = []
        section = self._find_section(soup, "skills")
        if not section:
            return results

        items = section.find_all("li" , class_=lambda c: c and "artdeco-list__item" in c )

        for item in items[:20]:
            name_el = item.find("span", {"aria-hidden": "true"})
            name = self._text(name_el)
            if name:
                results.append(Skill(name=name))

        return results








