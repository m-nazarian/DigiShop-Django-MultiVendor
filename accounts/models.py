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
        validators=[phone_regex],
        max_length=11,
        unique=True,
        verbose_name='شماره موبایل'
    )
    email = models.EmailField(blank=True, null=True, verbose_name='ایمیل')

    # فیلدهای اضافی برای پروفایل
    full_name = models.CharField(max_length=150, blank=True, verbose_name='نام و نام خانوادگی')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    # برای نقش‌ها
    is_verified = models.BooleanField(default=False, help_text=_("Is user phone verified?"))

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربرها'

    def __str__(self):
        return self.phone_number or self.email



class Vendor(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _('در انتظار تأیید')
        ACTIVE = 'active', _('فعال')
        SUSPENDED = 'suspended', _('توقف فعالیت')

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='vendor_profile',
        verbose_name=_('مالک')
    )
    store_name = models.CharField(_('نام فروشگاه'), max_length=100, unique=True)
    slug = models.SlugField(_('اسلاگ'), max_length=150, unique=True, allow_unicode=True)
    description = models.TextField(_('توضیحات'), blank=True)

    logo = models.ImageField(_('لوگو'), upload_to='vendor_logos/', blank=True, null=True)
    cover_image = models.ImageField(_('تصویر کاور'), upload_to='vendor_covers/', blank=True, null=True)

    status = models.CharField(
        _('وضعیت'),
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )

    # تنظیمات مالی
    commission_rate = models.DecimalField(
        _('نرخ کمیسیون (%)'),
        max_digits=4,
        decimal_places=1,
        default=5.0,
        help_text=_("درصد فروش انجام شده توسط پلتفرم")
    )

    created_at = models.DateTimeField(_('زمان ایجاد'), auto_now_add=True)

    class Meta:
        verbose_name = _('فروشنده')
        verbose_name_plural = _('فروشنده ها')

    def __str__(self):
        return self.store_name


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField(max_length=50, help_text="مثال: خانه، محل کار", verbose_name='عنوان آدرس')
    recipient_name = models.CharField(max_length=100, verbose_name='نام گیرنده')
    phone_number = models.CharField(max_length=15, verbose_name='شماره تماس')
    province = models.CharField(max_length=50, verbose_name='استان')
    city = models.CharField(max_length=50, verbose_name='شهر')
    full_address = models.TextField(verbose_name='آدرس کامل')
    postal_code = models.CharField(max_length=10, verbose_name='کد پستی')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'آدرس'
        verbose_name_plural = 'آدرس‌ها'

    def __str__(self):
        return f"{self.title} - {self.city}"