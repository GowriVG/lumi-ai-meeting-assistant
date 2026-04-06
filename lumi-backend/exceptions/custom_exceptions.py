class LumiBaseException(Exception):
    """Base exception for all LUMI-related errors"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class OpenAIServiceError(LumiBaseException):
    """Raised when the OpenAI API fails (rate limits, auth, or down)"""
    pass

class GraphServiceError(LumiBaseException):
    """Raised when Microsoft Graph API fails to fetch transcripts"""
    pass

class MeetingNotFoundError(LumiBaseException):
    """Raised when a meeting ID is requested but not found in memory/DB"""
    pass

class PromptValidationError(LumiBaseException):
    """Raised when the AI returns invalid or unparseable JSON"""
    pass