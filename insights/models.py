from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# --- 1. Extend User Model ---
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('consultant', 'Consultant'),
        ('client', 'Client'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# --- 2. Client Company ---
class Client(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='clients')
    name = models.CharField(max_length=100)
    industry = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

# --- 3. Assessment ---
MATURITY_CHOICES = [
    ('Emerging', 'Emerging'),
    ('Tactical', 'Tactical'),
    ('Strategic', 'Strategic'),
    ('Transformational', 'Transformational'),
]

class Assessment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, choices=[('survey', 'Survey'), ('interview', 'Interview')])
    stage = models.CharField(max_length=50, choices=[('initiating', 'Initiating'), ('in_progress', 'In Progress'), ('completed', 'Completed')])
    maturity_level = models.CharField(max_length=20, choices=MATURITY_CHOICES, default='Emerging')
    strategy_score = models.FloatField(default=0)
    execution_score = models.FloatField(default=0)
    total_score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.name} - {self.type}"

# --- 4. Pillar Score (1 per pillar per assessment) ---
class PillarScore(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='pillar_scores')
    pillar = models.CharField(max_length=100)
    score = models.FloatField()

    def __str__(self):
        return f"{self.assessment.client.name} - {self.pillar}: {self.score}"

# --- 5. Insight (for consultant/internal view) ---
class Insight(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    insight_text = models.TextField()

    def __str__(self):
        return f"Insight for {self.assessment.client.name}"


# --- 6. Recommendations per Pillar (for client view) ---
class Recommendation(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='recommendations')
    pillar = models.CharField(max_length=100)
    recommendation_text = models.TextField()

    def __str__(self):
        return f"{self.assessment.client.name} - {self.pillar}: {self.recommendation_text}"


# --- 7. Quotes per Pillar (new model) ---
class Quote(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='quotes')
    pillar = models.CharField(max_length=100)
    quote_text = models.TextField()

    def __str__(self):
        return f"Quote for {self.assessment.client.name} - {self.pillar}"

class Match(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='matches')
    pillar = models.CharField(max_length=100)
    matched_phrase = models.CharField(max_length=255)
    input_phrase = models.CharField(max_length=255)
    score = models.FloatField()

    def __str__(self):
        return f"{self.pillar} match: {self.matched_phrase} ({self.score})"

class DimensionScore(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='dimension_scores')
    dimension = models.CharField(max_length=100)  # e.g., 'Strategic', 'Operational'
    score = models.FloatField()

    def __str__(self):
        return f"{self.assessment.client.name} - {self.dimension}: {self.score}"

class ChangeMilestone(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='change_milestones')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='change_milestones')
    date = models.DateField()
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.assessment.client.name} - {self.title} ({self.date}) by {self.user.username if self.user else 'System'}"

# touched on 2025-05-27T15:29:05.129171Z