ALGORITHM = "RS256"

# There are no refresh tokens: a single access token is issued. A longer lived
# token means fewer logins but a larger window if it leaks (see backend/README.md).
ACCESS_TOKEN_LIFETIME_SECONDS = 60 * 60 * 24  # 24 hours
VERIFICATION_TOKEN_LIFETIME_SECONDS = 60 * 60 * 24  # 24 hours
RESET_PASSWORD_TOKEN_LIFETIME_SECONDS = 60 * 60  # 1 hour
