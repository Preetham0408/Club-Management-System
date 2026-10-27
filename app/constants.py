# All role and status constants used across the app

# Roles
ROLE_HEAD = 'Head'
ROLE_MEMBER = 'Member'

# Application statuses
STATUS_PENDING = 'Pending'
STATUS_SELECTED = 'Selected'
STATUS_REJECTED = 'Rejected'

# Event types
EVENT_PARTICIPATION = 'Participation'
EVENT_VIEW = 'View'

# Event statuses
EVENT_SCHEDULED = 'Scheduled'
EVENT_CANCELLED = 'Cancelled'

# Session keys
SESSION_LOGGED_IN = 'logged_in'
SESSION_ROLE = 'role'
SESSION_USER_ID = 'user_id'
SESSION_USER_NAME = 'user_name'
SESSION_CLUB_ID = 'head_club_id'  # Only set if role is 'Head'