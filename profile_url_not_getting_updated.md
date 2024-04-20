# profile_picture_url  not getting changed

## Cause: 
When a database is built, the variable is generated as a string attribute. However, we are giving the value as a url rather than a string when we update the value in the database. Type mismatch is the outcome.

## Fix: The problem has been fixed by changing the type from the URL to string.
>>> profile_picture_url: Optional[str] = Field(
        None,
        description="An updated URL to the user's profile picture.",
        example="https://example.com/profile_pictures/john_doe_updated.jpg"
    )
