from insights.models import PillarScore, Match, Quote, Recommendation, DimensionScore, Assessment, ChangeMilestone
from django.utils import timezone

def save_assessment_data(assessment_id, response_data):
    assessment = Assessment.objects.get(id=assessment_id)
    print(f"jkfjkj jkjkj jkjkjk ")
    # Pillar Scores
    for pillar, score in response_data.get('pillar_scores', {}).items():
        PillarScore.objects.create(assessment=assessment, pillar=pillar, score=score)

    # Matches
    for match in response_data.get('matches', []):
        Match.objects.create(
            assessment=assessment,
            pillar=match['pillar'],
            matched_phrase=match['matched_phrase'],
            input_phrase=match['input_phrase'],
            score=match['score']
        )

    # Dimension Scores
    for dimension, score in response_data.get('dimension_scores', {}).items():
        DimensionScore.objects.create(
            assessment=assessment,
            dimension=dimension,
            score=score
        )

    # Quotes & Recommendations
    for pillar, content in response_data.get('recommendations', {}).items():
        for quote in content.get('quotes', []):
            Quote.objects.create(assessment=assessment, pillar=pillar, quote_text=quote)
        for rec in content.get('recommendations', []):
            Recommendation.objects.create(assessment=assessment, pillar=pillar, recommendation_text=rec)

    # Optional: Update maturity level again if needed
    assessment.maturity_level = response_data.get('maturity_level', 'Emerging')
    assessment.save()

    ChangeMilestone.objects.create(
        assessment=assessment,
        user=assessment.client.user,  # Attach the client's user (you could also pass consultant from the view if needed)
        date=timezone.now().date(),
        title="AI Assessment Analysis Completed",
        description=assessment.maturity_level
    )

# touched on 2025-05-27T15:28:48.240457Z
# touched on 2025-05-27T15:28:53.860392Z
# touched on 2025-05-27T15:28:56.616949Z
# touched on 2025-05-27T15:29:02.329686Z
# touched on 2025-05-27T15:29:10.580877Z