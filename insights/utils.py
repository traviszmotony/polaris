from .models import PillarScore, Match, Quote, Recommendation, DimensionScore, Assessment

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

# touched on 2025-05-27T15:28:59.284746Z