from datetime import timedelta

from django.core.cache import cache
from django.utils.timezone import now
from ipware import get_client_ip
from rest_framework.exceptions import Throttled
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from {{cookiecutter.project_slug}} import settings

"""
You are going to need a model for banned users,
implement it as desired and import it here:

    from core.models.user import ThrottleHistory
    
    class ThrottleHistory(models.Model):
        class TypeChoices(models.TextChoices):
            REQUEST = 'r', 'درخواست'
            LOGIN = 'l', 'لاگین'
    
        type = models.CharField(choices=TypeChoices.choices, default=TypeChoices.REQUEST, verbose_name='نوع مسدودی',
                                max_length=10)
        user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, verbose_name='کاربر',
                                 related_name='throttle_histories')
        username = models.CharField(max_length=20, verbose_name='نام کاربری', null=True, blank=True)
        ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='آیپی')
        timestamp = models.DateTimeField(auto_now_add=True, verbose_name='زمان مسدودی')
        is_released = models.BooleanField(default=False, verbose_name='آیا رفع مسدودیت شده است؟')
"""

class AdvancedAnonThrottle(AnonRateThrottle):
    """
    The basic logic behind this throttling system is this:

    1- Free User Cache: on each minute we set a cache key for the user's IP address if it's not blocked
    so user is allowed to send requests for the next 60 seconds without any limits, which can't be that much

    2- Ban User Cache: each time a user is banned permanently we set a cache for an hour so we don't have to
    check the database the banned user is sending requests. but the pitfall is the user won't be unbanned until
    maximum 1 hour after the unbanning process(which we don't care since it's the punishment for that user)
    """
    scope = 'anon'

    def get_ident(self, request):
        """
        Retrieving the IP address of the user (even if it's behind a proxy)
        """
        return get_client_ip(request)[0]

    def allow_request(self, request, view):
        self.rate = self.get_rate()
        if self.rate is None:
            return True

        self.key = self.get_cache_key(request, view)

        if self.key is None:
            return True

        self.history = self.cache.get(self.key, [])
        self.now = self.timer()

        ip_address = get_client_ip(request)[0]

        # if the user is blocked an this event is in our cache we return the failure
        if cache.get(f'ip_blocked_{ip_address}'):
            return self.advanced_throttle_failure(permanently_banned=True)

        # if the user is free and the event is not in our cache we allow the request
        if not cache.get(f'ip_free_{ip_address}'):
            if self.is_user_permanently_banned(request):
                # setting cache for permanent ban again
                cache.set(f'ip_blocked_{ip_address}', True, timeout=60 * 60)
                return self.advanced_throttle_failure(permanently_banned=True)

            # the basic logic of the throttle system
            if super().allow_request(request, view):
                cache.set(f'ip_free_{ip_address}', True, timeout=60)
                return True
            else:
                # creating a ban log event for the user
                self.log_throttle_event(request)
                return self.advanced_throttle_failure(permanently_banned=False)
        else:
            return self.throttle_success()

    def is_user_permanently_banned(self, request):
        # here the edge for getting ban in a month is 5 but you can change it easily
        ip_address = get_client_ip(request)[0]
        last_month = now() - timedelta(days=30)
        ban_count = ThrottleHistory.objects.filter(ip_address=ip_address, timestamp__gte=last_month,
                                                   is_released=False, type=ThrottleHistory.TypeChoices.REQUEST).count()

        return ban_count >= 5

    def log_throttle_event(self, request):
        # creating a ban log event for the user
        ip_address = get_client_ip(request)[0]
        ban_qs = ThrottleHistory.objects.filter(ip_address=ip_address).order_by('-timestamp')
        if ban_qs:
            if ban_qs.first().timestamp >= now() - timedelta(hours=1):
                return
        ThrottleHistory.objects.create(ip_address=ip_address)

    def advanced_throttle_failure(self, permanently_banned=False):
        # returning custom throttle failure message
        if permanently_banned:
            raise Throttled(
                detail="شما به علت ارسال بیش از اندازه درخواست به سامانه در بازه طولانی مسدود شدید. با پشتیبانان سامانه تماس بگیرید.")
        return super().throttle_failure()


class AdvancedUserThrottle(UserRateThrottle):
    scope = 'user'

    def get_ident(self, request):
        return get_client_ip(request)[0]

    def allow_request(self, request, view):
        if not request.user.is_authenticated:
            return True

        self.rate = self.get_rate()
        if self.rate is None:
            return True

        self.key = self.get_cache_key(request, view)
        if self.key is None:
            return True

        self.history = self.cache.get(self.key, [])
        self.now = self.timer()

        if cache.get(f'ip_blocked_{request.user.id}'):
            return self.advanced_throttle_failure(permanently_banned=True)

        if not cache.get(f'user_free_{request.user.id}'):
            if self.is_user_permanently_banned(request):
                cache.set(f'user_blocked_{request.user.id}', True, timeout=60 * 60)
                return self.advanced_throttle_failure(permanently_banned=True)

            if super().allow_request(request, view):
                cache.set(f'user_free_{request.user.id}', True, timeout=60)
                return True
            else:
                self.log_throttle_event(request)
                return self.advanced_throttle_failure(permanently_banned=False)
        else:
            return self.throttle_success()

    def is_user_permanently_banned(self, request):
        last_month = now() - timedelta(days=30)
        ban_count = ThrottleHistory.objects.filter(user=request.user, timestamp__gte=last_month,
                                                   is_released=False, type=ThrottleHistory.TypeChoices.REQUEST).count()

        return ban_count >= 5

    def log_throttle_event(self, request):
        ban_qs = ThrottleHistory.objects.filter(user=request.user).order_by('-timestamp')
        if ban_qs:
            if ban_qs.first().timestamp >= now() - timedelta(hours=1):
                return
        ThrottleHistory.objects.create(user=request.user)

    def advanced_throttle_failure(self, permanently_banned=False):
        if permanently_banned:
            raise Throttled(
                detail="شما به علت ارسال بیش از اندازه درخواست به سامانه در بازه طولانی مسدود شدید. با پشتیبانان سامانه تماس بگیرید.")
        return super().throttle_failure()


#################################################3

class OTPThrottle:
    """
    A class designed to control the OTP request rate, to manage financial costs of sending SMS
    this class manages IP addresses working with the used API and the value as the key that user provides
    to receive OTP SMS. here we call it 'username'

    example usage:

    def check_otp_ban(request, username):
        otp_throttle = OTPThrottle(request, username)
        is_allowed, message = otp_throttle.allow_request()
        return is_allowed, message
    """
    DAY = 60 * 60 * 24

    def __init__(self, request, username, anon_rate=10, user_rate=20):
        rest_framework_settings = settings.REST_FRAMEWORK

        # dynamic variables
        self.request = request
        self.username = username
        self.ip_address = get_client_ip(request)[0]

        if anon_rate:
            self.daily_anon_rate_limit = anon_rate
        else:
            self.daily_anon_rate_limit = rest_framework_settings.get('DEFAULT_DAILY_SMS_RATE', {}).get('anon', 10)

        if user_rate:
            self.daily_user_rate_limit = user_rate
        else:
            self.daily_user_rate_limit = rest_framework_settings.get('DEFAULT_DAILY_SMS_RATE', {}).get('user', 20)

        # static settings
        self.monthly_rate_limit = 100
        self.permanent_ban_limit = 5

    def allow_request(self):
        """
        This is where we start
        """
        is_banned, message = self.is_user_banned()

        if is_banned:
            return False, message

        self.set_user_daily_cache()
        return True, message

    def get_cache_key(self, with_user_identifier=False, is_blocked=False):
        """
        Getting cache key based on user identifier or user ip
        Varies based on is_blocked as well
        """
        key_word = 'log' if not is_blocked else 'banned'
        identifier = 'ip' if not with_user_identifier else 'user'
        value = self.ip_address if not with_user_identifier else self.username

        return f"sms_{identifier}_{key_word}_{value}"

    def set_user_daily_cache(self):
        """
        Set 2 cache logs so we can keep track of the number of attempts in the last 24 hours
        1 for the ip
        1 for the requested username aka value
        """
        user_key = self.get_cache_key(with_user_identifier=True, is_blocked=False)
        anon_key = self.get_cache_key(with_user_identifier=False, is_blocked=False)

        user_value = cache.get(user_key) + 1 if cache.get(user_key) else 1
        anon_value = cache.get(anon_key) + 1 if cache.get(anon_key) else 1

        cache.set(anon_key, anon_value, timeout=1 * self.DAY)
        cache.set(user_key, user_value, timeout=1 * self.DAY)

    def check_for_permanent_ban(self):
        """
        Permanent ban system is the only part requiring database connection,
        based on the amount called permanent_ban_limit
        if it's more than the limit our user is banned forever
        """

        last_month = now() - timedelta(days=30)
        ip_address = self.ip_address

        base_throttle_qs = ThrottleHistory.objects.filter(timestamp__gte=last_month,
                                                          is_released=False,
                                                          type=ThrottleHistory.TypeChoices.LOGIN)

        anon_throttle_qs = base_throttle_qs.filter(ip_address=ip_address)
        user_throttle_qs = base_throttle_qs.filter(username=self.username)

        return len(anon_throttle_qs) > self.permanent_ban_limit or len(user_throttle_qs) > self.permanent_ban_limit

    def check_for_daily_ban(self):
        """
        We check our daily ban based on our cache value which is removed each 24 hours
        each time we add the default value of cache(1) by 1 so when it gets to our limit edge
        we'll know
        """
        ban_flag = False
        user_key = self.get_cache_key(with_user_identifier=True, is_blocked=False)
        anon_key = self.get_cache_key(with_user_identifier=False, is_blocked=False)

        if cache.get(anon_key):
            if cache.get(anon_key) > self.daily_anon_rate_limit:
                self.log_daily_ban_event(with_user_identifier=False)
                ban_flag = True
        elif cache.get(user_key):
            if cache.get(user_key) > self.daily_user_rate_limit:
                self.log_daily_ban_event(with_user_identifier=True)
            ban_flag = True

        return ban_flag

    def is_user_banned(self):
        """
        The main function for validating user request
        :return: tuple(bool, str)
        """
        is_permanent_banned = self.check_for_permanent_ban()
        is_daily_banned = self.check_for_daily_ban()

        if is_permanent_banned:
            return True, 'شما به علت ارسال بیش از اندازه درخواست پیامک مسدود شده اید. با پشتیبان سایت تماس بگیرید.'
        elif is_daily_banned:
            return True, 'شما به علت ارسال بیش از اندازه درخواست پیامک به مدت یک روز مسدود شده اید.'
        return False, 'OK'

    def log_daily_ban_event(self, with_user_identifier=False):
        """
        A place to create ban log for username or ip
        """
        if with_user_identifier:
            ThrottleHistory.objects.create(type=ThrottleHistory.TypeChoices.LOGIN, username=self.username)
        else:
            ThrottleHistory.objects.create(type=ThrottleHistory.TypeChoices.LOGIN, ip_address=self.ip_address)
