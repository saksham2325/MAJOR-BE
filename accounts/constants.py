BASE_URL = 'http://localhost:3000'
VERIFY_INVITATION_TOKEN = 'verify-invitation-token'
EMAIL_VERIFICATION_SUBJECT = 'Poker Planner email verification'
GROUP_INVITATION_SUBJECT = 'Poker Planner Group Invitation'
POKERBOARD_INVITATION_SUBJECT = 'Pokerbard Invitation'
GREETING = 'Hi '
SIGNUP_MESSAGE = ', Welcome to Poker Planner. Please visit to the below link to verify your account.\n'
LINK_NOT_WORK = '\n Copy the link and paste in your browser in case link does not work.'
GROUP_INVITATION_MESSAGE = 'Welcome to Poker Planner. Please visit to the below link to join the  group.\n'
POKERBOARD_INVITATION_MESSAGE = 'Hi, Welcome to Poker Planner.You are invited in a Pokerboard for the role of {}.Please visit to the below link to accept the invitation.\n {} \n Copy the link and paste in your browser in case link does not work.'

SIGNUP_PURPOSE = 0
GROUP_INVITATION_PURPOSE = 1
POKERBOARD_INVITATION_PURPOSE = 2
INVITATION_STATUS_PENDING = 0
INVITATION_STATUS_ACCEPTED = 1
INVITATION_STATUS_DECLINED = 2
INVITATION_STATUS_CANCELLED = 3
EXPIRY_TIME = 30

FIRST_NAME_LAST_NAME_MAX_LENGTH = 30
GROUP_TITLE_MAX_LENGTH = 150
GROUP_DESCRIPTION_MAX_LENGTH = 1000
JIRA_TOKEN_MAX_LENGTH = 100

INVALID_CREDENTIALS = 'INVALID_CREDENTIALS'
EMAIL_CANNOT_UPDATE = 'Email cannot be updated'
ADMIN_CANNOT_UPDATE = 'Admin cannot be changed'
USER_REMOVED_FROM_GROUP = 'User removed successfully!'
USER_SUCCESSFULLY_LOGOUT = 'User log out successfully'

INVALID_TOKEN = 'Invalid Token, Please request for another token'
TOKEN_EXPIRED_OR_ALREADY_USED = 'Token is expired or used already'
SUCCESSFULLY_VERIFY_ACCOUNT = 'account verified successfully.Please Register now'
USER_ALREADY_EXIST = 'Already Registered with this email, Please login.'

SUCCESSFULLY_GROUP_LEFT = 'Group left successfully!'
USER_ADDED = 'Added successfully.Please Login.'
ADD_AFTER_SIGNUP = 'Do not have account.You will automatically added to the successul after signup.'
WRONG_PASSWORD = 'Current password is wrong.'
PASSWORD_UPDATED = 'Password Updated succesfully.'
TOKEN_SENT = 'Verification link send at email.'
INVITED = 'User Invited successfully.'
INVITATION_CANCELLED = 'Cannot joined,invitation cancelled.'
INVITATION_DECLINED = 'Cannot Joined, You have already declined the invitation.'
ALREADY_INVITED = 'Already Invited'

USER_ROLE = {
    '0': 'Player',
    '1': 'Spectator',
}
