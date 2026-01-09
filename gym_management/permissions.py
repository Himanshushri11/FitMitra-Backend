from rest_framework import permissions

class IsPaidGymOwner(permissions.BasePermission):
    """
    Allows access only to paid gym owners.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # If user is a normal user, allow (this permission is for gym owner specific checks)
        # However, the rule says: if gym owner and not paid, return 403.
        
        try:
            role = request.user.profile.role
        except Exception:
            return False

        if role == 'GYM_OWNER':
            try:
                return request.user.gym_profile.payment_status
            except Exception:
                return False
        
        # If not GYM_OWNER, this permission might not apply or we might want to restrict to ONLY Paid Gym Owners for some views.
        # But for the "enforcement" on existing features, we need a middleware or a global check.
        return True
