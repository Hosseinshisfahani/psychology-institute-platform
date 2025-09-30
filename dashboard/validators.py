from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import (
    UserAttributeSimilarityValidator,
    MinimumLengthValidator,
    CommonPasswordValidator,
    NumericPasswordValidator
)
from django.utils.translation import gettext as _


class PersianUserAttributeSimilarityValidator(UserAttributeSimilarityValidator):
    """Persian version of UserAttributeSimilarityValidator"""
    
    def validate(self, password, user=None):
        if user is None:
            return
        
        try:
            super().validate(password, user)
        except ValidationError as e:
            # Translate the error message to Persian
            if "too similar" in str(e):
                raise ValidationError(
                    _("رمز عبور خیلی شبیه به اطلاعات شخصی شما است."),
                    code='password_too_similar',
                )
            else:
                raise e


class PersianMinimumLengthValidator(MinimumLengthValidator):
    """Persian version of MinimumLengthValidator"""
    
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError as e:
            # Translate the error message to Persian
            if "too short" in str(e):
                raise ValidationError(
                    _("این رمز عبور خیلی کوتاه است. باید حداقل %(min_length)d کاراکتر داشته باشد.") % {
                        'min_length': self.min_length
                    },
                    code='password_too_short',
                )
            else:
                raise e


class PersianCommonPasswordValidator(CommonPasswordValidator):
    """Persian version of CommonPasswordValidator"""
    
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError as e:
            # Translate the error message to Persian
            if "too common" in str(e):
                raise ValidationError(
                    _("این رمز عبور خیلی رایج است."),
                    code='password_too_common',
                )
            else:
                raise e


class PersianNumericPasswordValidator(NumericPasswordValidator):
    """Persian version of NumericPasswordValidator"""
    
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError as e:
            # Translate the error message to Persian
            if "entirely numeric" in str(e):
                raise ValidationError(
                    _("این رمز عبور کاملاً عددی است."),
                    code='password_entirely_numeric',
                )
            else:
                raise e
