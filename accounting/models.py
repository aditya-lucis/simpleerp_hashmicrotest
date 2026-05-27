from django.db import models

# 1. abstract base model
class BaseAuditModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# 2. coa model
class Account(BaseAuditModel):
    ACCOUNT_TYPES = [
        ('Asset', 'Asset'),
        ('Liability', 'Liability'),
        ('Equity', 'Equity'),
        ('Revenue', 'Revenue'),
        ('Expense', 'Expense'),
    ]
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPES)

    def __str__(self):
        return f"[{self.code}] {self.name}"
    
# 3. journal header entry model
class JournalHeader(BaseAuditModel):
    date = models.DateField()
    reference = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.reference} - {self.date}"
    
# 4. journal detail entry model
class JournalDetail(BaseAuditModel):
    header = models.ForeignKey(JournalHeader, on_delete=models.CASCADE, related_name='lines')
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.header.reference} - {self.account.name}"