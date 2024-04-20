# Issue with Updating Profile Picture URLs

## Root Cause:
During database setup, the profile_picture_url attribute was defined as a string. However, during updates, URL values were being passed instead of strings, leading to a type mismatch error.

## Solution:
To resolve the issue, the URL type is converted to a string, ensuring compatibility with the database attribute.
>>> profile_picture_url: Optional[str] = Field(
        None,
        description="An updated URL to the user's profile picture.",
        example="https://example.com/profile_pictures/john_doe_updated.jpg"
    )
