from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    """
    Custom manager to handle user creation with phone number instead of username.
    """

    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError(_('The Phone Number field must be set'))

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model where phone_number is the unique identifier.
    """
    username = None  # حذف فیلد نام کاربری پیش‌فرض

    phone_regex = RegexValidator(
        regex=r'^09\d{9}$',
        message=_("Phone number must be entered in the format: '09123456789'.")
    )

    phone_number = models.CharField(
        _('phone number'),
        validators=[phone_regex],
        max_length=11,
        unique=True
    )
    email = models.EmailField(_('email address'), blank=True, null=True)

    # فیلدهای اضافی برای پروفایل
    full_name = models.CharField(_('full name'), max_length=150, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    # برای نقش‌ها
    is_verified = models.BooleanField(default=False, help_text=_("Is user phone verified?"))

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.phone_number or self.email



class Vendor(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending Approval')
        ACTIVE = 'active', _('Active')
        SUSPENDED = 'suspended', _('Suspended')

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='vendor_profile',
        verbose_name=_('Owner')
    )
    store_name = models.CharField(_('Store Name'), max_length=100, unique=True)
    slug = models.SlugField(max_length=150, unique=True, allow_unicode=True)
    description = models.TextField(_('Description'), blank=True)

    logo = models.ImageField(upload_to='vendor_logos/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='vendor_covers/', blank=True, null=True)

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )

    # تنظیمات مالی
    commission_rate = models.DecimalField(
        _('Commission Rate (%)'),
        max_digits=4,
        decimal_places=1,
        default=5.0,
        help_text=_("Percentage of sales taken by platform")
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Vendor')
        verbose_name_plural = _('Vendors')

    def __str__(self):
        return self.store_name


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField(_('Title'), max_length=50, help_text="مثال: خانه، محل کار")
    recipient_name = models.CharField(_('Recipient Name'), max_length=100)
    phone_number = models.CharField(_('Phone Number'), max_length=15)
    province = models.CharField(_('Province'), max_length=50)  # استان
    city = models.CharField(_('City'), max_length=50)  # شهر
    full_address = models.TextField(_('Full Address'))
    postal_code = models.CharField(_('Postal Code'), max_length=10)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.city}"