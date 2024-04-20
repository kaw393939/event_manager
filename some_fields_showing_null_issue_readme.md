# Some Fields return null when retrieving user details

## Cause:

Some fields are omitted when building the response from the database data.

## Fix:

The Missing fields are included in the response creation.
