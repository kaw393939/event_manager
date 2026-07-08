import re
from typing import Optional
import pytest
from pydantic import ValidationError
from app.schemas.user_schemas import UserBase, UserUpdate

class TestURLValidation:
    
    @pytest.mark.parametrize("github_url", [
        "https://github.com/validuser",
        "https://github.com/valid-user",
        "https://github.com/valid_user123",
        None
    ])
    def test_valid_github_urls(self, github_url):
        """Test that valid GitHub URLs are accepted."""
        user = UserBase(email="test@example.com", github_profile_url=github_url)
        assert user.github_profile_url == github_url
    
    @pytest.mark.parametrize("github_url", [
        "https://githb.com/invaliduser",  # Typo in domain
        "http://github.com/invalid/user",  # Extra path segment
        "https://github",  # Missing username
        "gitlab.com/user",  # Wrong domain and missing scheme
        "https://github.com/",  # Missing username
        "https://github.com/invalid user"  # Space in username
    ])
    def test_invalid_github_urls(self, github_url):
        """Test that invalid GitHub URLs are rejected."""
        with pytest.raises(ValidationError):
            UserBase(email="test@example.com", github_profile_url=github_url)
    
    @pytest.mark.parametrize("linkedin_url", [
        "https://linkedin.com/in/validuser",
        "https://www.linkedin.com/in/valid-user",
        "https://linkedin.com/in/valid_user123",
        None
    ])
    def test_valid_linkedin_urls(self, linkedin_url):
        """Test that valid LinkedIn URLs are accepted."""
        user = UserBase(email="test@example.com", linkedin_profile_url=linkedin_url)
        assert user.linkedin_profile_url == linkedin_url
    
    @pytest.mark.parametrize("linkedin_url", [
        "https://linkdin.com/in/invaliduser",  # Typo in domain
        "http://linkedin.com/profile/invalid",  # Wrong path format
        "https://linkedin",  # Missing path and username
        "linkedin.com/in/user",  # Missing scheme
        "https://linkedin.com/",  # Missing path and username
        "https://linkedin.com/in/invalid user"  # Space in username
    ])
    def test_invalid_linkedin_urls(self, linkedin_url):
        """Test that invalid LinkedIn URLs are rejected."""
        with pytest.raises(ValidationError):
            UserBase(email="test@example.com", linkedin_profile_url=linkedin_url)
    
    @pytest.mark.parametrize("profile_picture_url", [
        "https://example.com/image.jpg",
        "https://cdn.site.io/images/profile.png",
        "https://static.images.com/photos/user123.jpeg",
        None
    ])
    def test_valid_profile_picture_urls(self, profile_picture_url):
        """Test that valid profile picture URLs are accepted."""
        user = UserBase(email="test@example.com", profile_picture_url=profile_picture_url)
        assert user.profile_picture_url == profile_picture_url
    
    @pytest.mark.parametrize("profile_picture_url", [
        "ftp://example.com/image.jpg",  # Invalid scheme
        "htp://example.com/image.jpg",  # Typo in scheme
        "example.com/image.jpg",  # Missing scheme
        "https://example.com/image.jpg invalid",  # Space in URL
    ])
    def test_invalid_profile_picture_urls(self, profile_picture_url):
        """Test that invalid profile picture URLs are rejected."""
        with pytest.raises(ValidationError):
            UserBase(email="test@example.com", profile_picture_url=profile_picture_url)

    def test_update_multiple_urls(self):
        """Test that updating multiple URLs works correctly."""
        user_update = UserUpdate(
            github_profile_url="https://github.com/newuser",
            linkedin_profile_url="https://linkedin.com/in/newuser",
            profile_picture_url="https://example.com/newimage.jpg"
        )
        assert user_update.github_profile_url == "https://github.com/newuser"
        assert user_update.linkedin_profile_url == "https://linkedin.com/in/newuser"
        assert user_update.profile_picture_url == "https://example.com/newimage.jpg"