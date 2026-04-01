from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import EwasteRequest, UserProfile,  EwastePhoto
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from django.utils.html import format_html
from django.shortcuts import render

class EwastePhotoInline(admin.TabularInline):
    model = EwastePhoto
    extra = 0
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "-"
    image_preview.short_description = "Preview"

@admin.register(EwasteRequest)
class EwasteRequestAdmin(admin.ModelAdmin):
    inlines = [EwastePhotoInline]
    def has_add_permission(self, request):
     if request.user.userprofile.is_recycler:
        return False
     return super().has_add_permission(request)
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
     if db_field.name == "assigned_agent":
        from django.contrib.auth.models import User
        kwargs["queryset"] = User.objects.filter(userprofile__is_agent=True)
     return super().formfield_for_foreignkey(db_field, request, **kwargs)

    list_display = (
        "item_name",
        "user",
        "quantity",
        "condition",
        "estimated_amount",
        "status",
        "assigned_agent",
        "created_at",
    )

    list_filter = ("status", "condition", "created_at")
    search_fields = ("item_name", "user__username")
    list_editable = ("status","assigned_agent")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if request.user.userprofile.is_recycler:
            if "assigned_agent" in form.base_fields:
                widget = form.base_fields["assigned_agent"].widget
                widget.can_add_related = False
                widget.can_change_related = False
                widget.can_view_related = False

        return form
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "get_email", "is_recycler", "is_agent")

    def get_email(self, obj):
        return obj.user.email
    
class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

    fieldsets = (
    (None, {'fields': ('username', 'password')}),

    ('Personal info', {'fields': ('email',)}),

    ('Permissions', {
        'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
    }),

    ('Important dates', {
        'fields': ('last_login', 'date_joined'),
    }),
    
    )
    def save_model(self, request, obj, form, change):
        if not obj.email:
            from django.core.exceptions import ValidationError
            raise ValidationError("Email is required")
        super().save_model(request, obj, form, change)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)