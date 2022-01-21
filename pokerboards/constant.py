POKERBOARD_NAME_MAX_LENGTH = 50
ESTIMATE_MAX_DIGITS = 17
ESTIMATE_DECIMAL_PLACES = 3
ESTIMATE_MAX_VALUE = 1e+14
ESTIMATE_MIN_VALUE = 0.001
TIMER_DEFAULT_MINUTES = 20
PLAYER = 0
SPECTATOR = 1
TYPE = 'type'
MESSAGE = 'message'
USER_MESSAGE = 'user_message'
ADD_USER = 'add_user'
REMOVE_USER = 'remove_user'

USER_REMOVED = 'User removed successfully!.'
SUBMIT_ESTIMATE = "submit_estimate"
SUBMIT_FINAL_ESTIMATE = "submit_final_estimate"
START_ESTIMATING_ON_TICKET = "start_estimating_on_ticket"
SKIP_TICKET = "skip_ticket"
TYPE_CHOICES = [
    (SUBMIT_ESTIMATE, "submit_estimate"),
    (SUBMIT_FINAL_ESTIMATE, "submit_final_estimate"),
    (START_ESTIMATING_ON_TICKET, "start_estimating_on_ticket"),
    (SKIP_TICKET, "skip_ticket"),
]
