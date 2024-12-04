from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import UserProfile
from django.shortcuts import render, redirect
from .decorators import role_required  # <- if it's in a separate file
from django.db import IntegrityError
from .utils.analyzer import analyze_response

from .utils.helpers import save_assessment_data
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import *
import datetime
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404

# 🔀 Redirect based on user role
@login_required
def dashboard_redirect(request):
    profile = request.user.userprofile

    if profile.role == 'consultant':
        return redirect('internal_dashboard')
    elif profile.role == 'client':
        return redirect('client_dashboard')
    else:
        return redirect('admin:index')

# 🛠️ Sample internal consultant dashboard
@login_required
@role_required('consultant')
def internal_dashboard(request):
    client_id = request.GET.get('client_id')
    all_clients = Client.objects.all()

    if client_id:
        selected_client = get_object_or_404(Client, id=client_id)
        assessments = Assessment.objects.filter(client=selected_client).order_by('-created_at')
        insights = Insight.objects.filter(assessment__client=selected_client).order_by('-id')[:10]
    else:
        selected_client = all_clients.first()  # Get the first client if no client_id is provided
        if selected_client:
            assessments = Assessment.objects.filter(client=selected_client).order_by('-created_at')
            insights = Insight.objects.filter(assessment__client=selected_client).order_by('-id')[:10]
        else:
            assessments = []
            insights = []

    return render(request, "insight/internal_dashboard.html", {
        "clients": assessments,
        "insights": insights,
        "all_clients": all_clients,
        "selected_client": selected_client,
    })

# 👤 Sample client-facing dashboard
@login_required
@role_required('client')
def client_dashboard(request):
    assessments = Assessment.objects.filter(client__user=request.user).order_by('-created_at')
    latest_assessment = assessments.first()

    if latest_assessment:
        pillar_scores = PillarScore.objects.filter(assessment=latest_assessment)
        print(f"Recommendations found: {pillar_scores}")  # Log the recommendations

        # ... existing code ...
        recommendations = Recommendation.objects.filter(assessment=latest_assessment)  # Fetch recommendations for a specific assessment
        print(f"Recommendations found: {recommendations}")  # Log the recommendations
        if not recommendations:
            print("No recommendations found for the latest assessment.")  # Log if none found
        # ... existing code ...
        # recommendations = Recommendation.objects.filter(assessment=latest_assessment)
        print(f"latest_assessment latest_assessment latest_assessment {recommendations}")

        quotes = Quote.objects.filter(assessment=latest_assessment)  # Fetch quotes for a specific assessment
        print(f"Quotes found: {quotes}") 

        milestones = ChangeMilestone.objects.filter(
            assessment__client__user=request.user
        ).order_by('date')

        # Determine quadrant
        quadrant = latest_assessment.maturity_level  # assuming field exists (Tactical, Strategic, etc.)
        summary_points = [
            "Strong execution capability",
            "Needs more strategic focus"
        ] if quadrant == "Tactical" else ["..."]

    else:
        pillar_scores = []
        recommendations = []
        summary_points = []
        quadrant = None
        quotes = []
        milestones = []

    return render(request, 'insight/client_dashboard.html', {
        'assessments': assessments,
        'latest_assessment': latest_assessment,
        'pillar_scores': pillar_scores,
        'recommendations': recommendations,
        'summary_points': summary_points,
        'quadrant': quadrant,
        'quotes': quotes,
        'milestones': milestones,
        'show_reports': True,
    })
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@permission_classes([IsAuthenticated])

def generate_assessment(request):
    user = request.user
    input_text = request.data.get('input_text')

    if not input_text:
        return Response({"error": "No input text provided"}, status=400)

    ai_response = analyze_response(input_text)

    # Get or create a client for this user
    client, _ = Client.objects.get_or_create(user=user, defaults={'name': f"{user.username}"})



    # Create the assessment
    assessment = Assessment.objects.create(
        client=client,
        type='interview',
        stage='completed',
        maturity_level=ai_response.get('maturity_level', 'Emerging'),
        strategy_score=ai_response.get('dimension_scores', {}).get('Strategic', 0),
        execution_score=ai_response.get('dimension_scores', {}).get('Operational', 0),
        total_score=(ai_response.get('dimension_scores', {}).get('Strategic', 0) + ai_response.get('dimension_scores', {}).get('Operational', 0)) / 2,
        created_at=timezone.now()
    )

    save_assessment_data(assessment.id, ai_response)

    # Redirect to the appropriate dashboard based on user role
    if user.userprofile.role == 'consultant':
        return redirect('internal_dashboard')
    elif user.userprofile.role == 'client':
        return redirect('client_dashboard')
    else:
        return Response({"error": "User role not recognized"}, status=403)

from django.http import JsonResponse
from collections import defaultdict
from datetime import datetime

from django.http import JsonResponse
from collections import defaultdict

@login_required
@role_required('consultant')
def pillar_score_trends_api(request):
    client_id = request.GET.get("client_id")
    if not client_id:
        return JsonResponse({"error": "Client ID required"}, status=400)

    scores = PillarScore.objects.filter(assessment__client__id=client_id).select_related('assessment')

    trends = defaultdict(list)
    labels_set = set()

    for score in scores:
        iso_date = score.assessment.created_at.isoformat()  # 🔁 Use ISO format
        labels_set.add(iso_date)
        trends[score.pillar].append((iso_date, score.score, str(score.assessment)))

    labels = sorted(list(labels_set))
    datasets = []

    for pillar, points in trends.items():
        data_map = {label: None for label in labels}
        for label, score_val, _ in points:
            data_map[label] = score_val
        datasets.append({
            "label": pillar,
            "data": [data_map[l] for l in labels],
            "borderColor": "#"+''.join([hex(hash(pillar + l) % 256)[2:].zfill(2) for l in "rgb"]),
            "tension": 0.4,
        })

    return JsonResponse({
        "labels": labels,
        "datasets": datasets
    })

# touched on 2025-05-27T15:28:51.115180Z
# touched on 2025-05-27T15:28:59.283951Z