from django.db import models


class TransactionWiths(models.Model):
    id = models.BigAutoField(primary_key=True)
    tran_with_name = models.CharField(max_length=255)
    user_role = models.BigIntegerField(blank=True, null=True, db_comment='roles')
    tran_type = models.BigIntegerField(db_comment='transaction__main__heads')
    tran_method = models.CharField(max_length=255)
    status = models.IntegerField(default=1)
    added_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transaction__withs'

    def __str__(self):
        return self.tran_with_name