import httpx

from config.settings import settings
from src.utils.logger import logger
from src.utils.rate_limiter import rate_limiter

LINKEDIN_API_BASE = "https://api.linkedin.com/v2"
LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

class LinkedInAPIClient:
    """
    Official LinkedIn REST API client using OAuth 2.0.

    Without LinkedIn Partner Programme approval, the API only gives you:
        - r_liteprofile  → name, headline, profile photo
        - r_emailaddress → email address of the authenticated user

    This is useful for your own profile or building tools where users
    authenticate themselves. For scraping others' profiles, use the
    browser-based scraper instead.

    Setup:
        1. Create an app at https://www.linkedin.com/developers/
        2. Add your Client ID / Secret to .env
        3. Call get_auth_url() → direct user there → capture ?code=
        4. Call exchange_code_for_token(code) → stores the access token
    """

    def __init__(self,access_token : str = None):
        self.access_token =access_token
        self._client = httpx.Client(
            base_url=LINKEDIN_API_BASE,
            headers={
                "X-Restli-Protocol-Version": "2.0.0",
                "LinkedIn-Version" : "202401",
            },
            timeout=15.0,
        )
        if access_token:
            self._set_auth_header(access_token)


    def _set_auth_header(self, token:str):
        self._client.headers["Authorization"] = f"Bearer {token}"


#     ==================================================
#                    OAuth 2.0 Flow
#     ==================================================


    def get_auth_url(self, extra_scopes: list[str] = None) -> str:
        """
        Generate the OAuth 2.0 authorisation URL.
        Directs the user here; they'll be redirected back with ?code=
        """

        scopes = ["r_liteprofile", "r_emailaddress"]
        if extra_scopes:
            scopes.extend(extra_scopes)

        params = {
            "response_type": "code",
            "client_id" : settings.LINKEDIN_CLIENT_ID,
            "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
            "scope" : " ".join(scopes),
        }

        query = "&".join(f"{k}={v}" for k , v in params.items())
        url = f"{LINKEDIN_AUTH_URL}?{query}"
        logger.info(f"Auth URL generated - visit this to authorise: \n{url}")
        return url


    def exchange_code_for_token(self,code:str) -> str:
        """Exchange an OAuth authorisation code for an access token."""

        response = httpx.post(
            LINKEDIN_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code" : code,
                "redirect_uri" : settings.LINKEDIN_REDIRECT_URI,
                "client_secret" : settings.LINKEDIN_CLIENT_SECRET,
            },
            headers={"Content-Type" : "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()

        token_data = response.json()
        token = token_data["access_token"]
        expires_in = token_data.get("expires_in" , "unknown")

        logger.info(f"Access token received (expires in {expires_in}s).")
        self.access_token = token
        self._set_auth_header(token)
        return token


#     ============================================
#                   API Endpoint
#     ============================================


    def get_own_profile(self) -> dict:
        """
        Fetch the authenticated user's own basic profile (r_liteprofile).
        Returns: id, firstName, lastName, headline, profilePicture
        """

        rate_limiter.sync_wait()
        response = self._client.get(
            "/me",
            params = {
                "projection" : "(id,firstName,lastName,headline,profilePicture(displayImage~:playableStreams))"

            },
        )
        response.raise_for_status()
        data = response.json()
        logger.info(f"Profile fetched: {data.get('id')}")
        return data

    def get_own_email(self) -> str | None:
        """
        Fetch the authenticated user's email address (r_emailaddress).
        """
        rate_limiter.sync_wait()
        response = self._client.get(
            "/emailAddress",
            params={"q": "members", "projection": "(elements*(handle~))"},
        )
        response.raise_for_status()
        elements = response.json().get("elements", [])
        if elements:
            return elements[0].get("handle~", {}).get("emailAddress")
        return None

    def parse_name(self, profile_data: dict) -> str:
        """Helper to extract a full name from the API profile dict."""
        first = profile_data.get("firstName", {}).get("localized", {})
        last = profile_data.get("lastName", {}).get("localized", {})
        first_val = next(iter(first.values()), "")
        last_val = next(iter(last.values()), "")
        return f"{first_val} {last_val}".strip()

    def close(self):
        self._client.close()


