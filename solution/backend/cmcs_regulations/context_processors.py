from django.conf import settings
from django.urls import reverse


def google_analytics(request):
    return {
        "GA_ID": settings.GA_ID
    }


def is_admin_user(request):
    return {
        "IS_ADMIN_USER": request.user.groups.filter(name='EREGS_ADMIN').exists()
    }


def custom_url(request):
    custom_url = settings.CUSTOM_URL
    host = request.get_host()

    # Use the host if it matches the allowed host from environment
    allowed_host = getattr(settings, 'ALLOWED_HOST_DOMAIN', None)
    if allowed_host and host == allowed_host:
        custom_url = host

    return {'CUSTOM_URL': custom_url}


def survey_url(request):
    return {
        "SURVEY_URL": settings.SURVEY_URL
    }


def demo_video_url(request):
    return {
        "DEMO_VIDEO_URL": settings.DEMO_VIDEO_URL
    }


def signup_url(request):
    return {
        "SIGNUP_URL": settings.SIGNUP_URL
    }


def automated_testing(request):
    return {
        "AUTOMATED_TEST": request.META.get("HTTP_X_AUTOMATED_TEST") == "true"
    }


def api_base(request):
    return {
        "API_BASE": f"{reverse('homepage')}{settings.API_BASE}"
    }


def deploy_number(request):
    return {
        "DEPLOY_NUMBER": settings.DEPLOY_NUMBER
    }
