"""Custom exceptions for the Jagriti API wrapper"""


class JagritiAPIException(Exception):
    """Base exception for Jagriti API related errors"""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class APITimeoutException(JagritiAPIException):
    """Raised when API request times out"""
    
    def __init__(self, message: str = "API request timed out"):
        super().__init__(message, 408)


class APIConnectionException(JagritiAPIException):
    """Raised when unable to connect to API"""
    
    def __init__(self, message: str = "Unable to connect to Jagriti API"):
        super().__init__(message, 503)


class StateNotFoundException(JagritiAPIException):
    """Raised when requested state is not found"""
    
    def __init__(self, state_name: str):
        message = f"State '{state_name}' not found"
        super().__init__(message, 404)


class CommissionNotFoundException(JagritiAPIException):
    """Raised when requested commission is not found"""
    
    def __init__(self, commission_name: str):
        message = f"Commission '{commission_name}' not found"
        super().__init__(message, 404)


class CategoryNotFoundException(JagritiAPIException):
    """Raised when requested category is not found"""
    
    def __init__(self, category_name: str):
        message = f"Category '{category_name}' not found"
        super().__init__(message, 404)


class JudgeNotFoundException(JagritiAPIException):
    """Raised when requested judge is not found"""
    
    def __init__(self, judge_name: str):
        message = f"Judge '{judge_name}' not found"
        super().__init__(message, 404)


class InvalidSearchTypeException(JagritiAPIException):
    """Raised when invalid search type is provided"""
    
    def __init__(self, search_type: str):
        message = f"Invalid search type '{search_type}'"
        super().__init__(message, 400)


class CaseDataException(JagritiAPIException):
    """Raised when case data processing fails"""
    
    def __init__(self, message: str = "Error processing case data"):
        super().__init__(message, 422)