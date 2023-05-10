from core.models import FriendRequests

def notifications(request):
    count = 0
    if request.user.is_authenticated:
        count = FriendRequests.objects.filter(to_user=request.user).count()
    return {'count': count}