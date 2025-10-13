"""
Croom Integration Service for Workshop Sessions
Handles creating meetings, generating links, and managing recordings
"""
import requests
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)


class CroomService:
    """Service class for Croom API integration"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'CROOM_API_KEY', '')
        self.api_url = getattr(settings, 'CROOM_API_URL', '')
        self.api_base = self.api_url.rstrip('/') if self.api_url else ''
        
    def _get_headers(self):
        """Get headers for API requests"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
    
    def create_meeting(self, session_data):
        """
        Create a Croom meeting for a workshop session
        
        Args:
            session_data (dict): Session information including:
                - title: Meeting title
                - description: Meeting description
                - scheduled_datetime: When the meeting is scheduled
                - duration_minutes: Duration of the meeting
                - instructor_name: Name of the instructor
                - instructor_email: Email of the instructor
        
        Returns:
            dict: Meeting details including:
                - meeting_id: Unique meeting identifier
                - meeting_link: Join URL for the meeting
                - meeting_password: Password (if applicable)
                - host_link: Special link for the host
        """
        if not self.api_key or not self.api_url:
            logger.warning("Croom API credentials not configured")
            return {
                'success': False,
                'error': 'Croom API not configured'
            }
        
        try:
            url = f"{self.api_base}/meetings"
            payload = {
                'title': session_data.get('title'),
                'description': session_data.get('description', ''),
                'scheduled_at': session_data.get('scheduled_datetime').isoformat() if session_data.get('scheduled_datetime') else None,
                'duration': session_data.get('duration_minutes', 60),
                'host': {
                    'name': session_data.get('instructor_name', ''),
                    'email': session_data.get('instructor_email', ''),
                },
                'settings': {
                    'auto_recording': True,
                    'waiting_room': False,
                    'join_before_host': True,
                }
            }
            
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'meeting_id': data.get('meeting_id'),
                'meeting_link': data.get('join_url'),
                'meeting_password': data.get('password'),
                'host_link': data.get('host_url'),
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating Croom meeting: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error creating Croom meeting: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_meeting_link(self, meeting_id, user_data=None):
        """
        Get personalized meeting link for a user
        
        Args:
            meeting_id (str): The Croom meeting ID
            user_data (dict, optional): User information including:
                - name: User's full name
                - email: User's email
        
        Returns:
            str: Personalized join URL
        """
        if not meeting_id:
            return None
        
        if not self.api_key or not self.api_url:
            logger.warning("Croom API credentials not configured")
            return None
        
        try:
            url = f"{self.api_base}/meetings/{meeting_id}/join-url"
            params = {}
            
            if user_data:
                params['name'] = user_data.get('name', '')
                params['email'] = user_data.get('email', '')
            
            response = requests.get(url, params=params, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('join_url')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting meeting link: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting meeting link: {str(e)}")
            return None
    
    def get_recording_url(self, meeting_id):
        """
        Get recording URL for a completed meeting
        
        Args:
            meeting_id (str): The Croom meeting ID
        
        Returns:
            dict: Recording information including:
                - recording_url: URL to access the recording
                - duration: Duration of the recording
                - file_size: Size of the recording file
                - created_at: When the recording was created
        """
        if not meeting_id:
            return None
        
        if not self.api_key or not self.api_url:
            logger.warning("Croom API credentials not configured")
            return None
        
        try:
            url = f"{self.api_base}/meetings/{meeting_id}/recordings"
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            
            data = response.json()
            recordings = data.get('recordings', [])
            
            if recordings:
                # Return the first (or latest) recording
                recording = recordings[0]
                return {
                    'recording_url': recording.get('url'),
                    'duration': recording.get('duration'),
                    'file_size': recording.get('file_size'),
                    'created_at': recording.get('created_at'),
                }
            
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting recording URL: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting recording URL: {str(e)}")
            return None
    
    def update_meeting(self, meeting_id, updates):
        """
        Update an existing meeting
        
        Args:
            meeting_id (str): The Croom meeting ID
            updates (dict): Fields to update
        
        Returns:
            bool: Success status
        """
        if not meeting_id:
            return False
        
        if not self.api_key or not self.api_url:
            logger.warning("Croom API credentials not configured")
            return False
        
        try:
            url = f"{self.api_base}/meetings/{meeting_id}"
            response = requests.patch(url, json=updates, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating meeting: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating meeting: {str(e)}")
            return False
    
    def delete_meeting(self, meeting_id):
        """
        Delete a meeting
        
        Args:
            meeting_id (str): The Croom meeting ID
        
        Returns:
            bool: Success status
        """
        if not meeting_id:
            return False
        
        if not self.api_key or not self.api_url:
            logger.warning("Croom API credentials not configured")
            return False
        
        try:
            url = f"{self.api_base}/meetings/{meeting_id}"
            response = requests.delete(url, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting meeting: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting meeting: {str(e)}")
            return False
    
    def get_meeting_participants(self, meeting_id):
        """
        Get list of participants for a meeting
        
        Args:
            meeting_id (str): The Croom meeting ID
        
        Returns:
            list: List of participants with their details
        """
        if not meeting_id:
            return []
        
        if not self.api_key or not self.api_url:
            logger.warning("Croom API credentials not configured")
            return []
        
        try:
            url = f"{self.api_base}/meetings/{meeting_id}/participants"
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('participants', [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting meeting participants: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting meeting participants: {str(e)}")
            return []


# Singleton instance
croom_service = CroomService()

