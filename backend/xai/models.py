from django.db import models


class SHAPGlobal(models.Model):
    """SHAP global feature importance."""
    id = models.AutoField(primary_key=True)
    feature = models.CharField(max_length=50)
    shap_value = models.FloatField()  # mean |SHAP|
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'xai_shap_global'
        ordering = ['-shap_value']

    def __str__(self):
        return f"{self.feature}: {self.shap_value}"


class SHAPLocal(models.Model):
    """SHAP local explanation per record."""
    record_id = models.IntegerField(unique=True)
    shap_values = models.JSONField()  # {feature: shap_value}
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'xai_shap_local'

    def __str__(self):
        return f"SHAP Local {self.record_id}"


class LIMELocal(models.Model):
    """LIME local explanation per record."""
    record_id = models.IntegerField(unique=True)
    lime_weights = models.JSONField()  # [(feature, weight)]
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'xai_lime_local'

    def __str__(self):
        return f"LIME Local {self.record_id}"