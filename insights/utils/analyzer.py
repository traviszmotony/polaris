import os
import json
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=OpenAIAPIKey)

# Map each pillar to a core maturity axis (Strategic or Operational)
pillar_to_axis = {
    "HR Expertise": "Operational",
    "Consultation": "Strategic",
    "Communication": "Operational",
    "Relationship Management": "Operational",
    "Leadership & Navigation": "Strategic",
    "Ethical Practice": "Operational",
    "Critical Evaluation": "Strategic",
    "Strategic Thinking": "Strategic",
    "People Leadership": "Strategic",
    "Execution Excellence": "Operational",
    "Influence and Collaboration": "Strategic",
    "Emotional Intelligence": "Operational",
    "Innovation and Change Management": "Strategic",
    "Resilience and Adaptability": "Operational"
}

# 1. Extract key phrases from input text using GPT
def extract_phrases_with_gpt(response_text: str):
    with open("keyword_pillar_map.json") as f:
        keyword_map = json.load(f)

    known_phrases = []
    for phrases in keyword_map.values():
        for item in phrases:
            known_phrases.append(item["phrase"])

    known_phrases_str = "\n- " + "\n- ".join(known_phrases)

    prompt = f"""
You are an HR AI assistant.

Your job is to extract exact keyword phrases that match the official maturity mapping list. Do NOT paraphrase or summarize. Only return exact matches from the provided list.

List of approved maturity phrases:
{known_phrases_str}

Given this survey response:
{response_text}

Return a Python list of all phrases (from the approved list above) that are found in the survey response.
If no match is found, return an empty list.

Example output:
["HR flagged this before it became an issue", "Exec team syncs", "We walked away from that deal"]
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    output_text = response.choices[0].message.content.strip()
    try:
        return eval(output_text)
    except Exception as e:
        print("❌ Failed to parse GPT output:", e)
        return []

# 2. Load keyword-pillar map from file
def load_keyword_map(filepath='keyword_pillar_map.json'):
    with open(filepath, 'r') as f:
        return json.load(f)

# 3. Analyze sentiment for extracted phrases using GPT
def analyze_sentiment_with_gpt(phrases):
    if not phrases:
        return {}

    phrases_str = "\n".join([f"- {p}" for p in phrases])

    prompt = f"""
You are a helpful HR AI assistant.

Below is a list of phrases pulled from a team feedback survey. For each phrase, return a sentiment score between -1 and 1.

- Negative sentiment: -1 (e.g., frustration, criticism)
- Neutral sentiment: 0 (e.g., facts, no emotion)
- Positive sentiment: +1 (e.g., optimism, support, praise)

Return the result as a Python dictionary with this format:
{{ "phrase1": score1, "phrase2": score2 }}

Phrases:
{phrases_str}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    output_text = response.choices[0].message.content.strip()

    try:
        sentiment_dict = eval(output_text)
        return sentiment_dict
    except Exception as e:
        print("❌ Failed to parse GPT sentiment output:", e)
        return {}

# 4. Match phrases to pillars and apply sentiment-adjusted scoring
def match_keywords_to_pillars_with_sentiment(extracted_keywords, keyword_map):
    scores = {}
    matches = []

    sentiment_scores = analyze_sentiment_with_gpt(extracted_keywords)

    print("\n→ GPT Sentiment Scores:")
    for phrase, score in sentiment_scores.items():
        print(f"  - \"{phrase}\": {score:.2f}")

    for category, items in keyword_map.items():
        for item in items:
            for keyword in extracted_keywords:
                if item['phrase'].lower() in keyword.lower():
                    sentiment = sentiment_scores.get(keyword, 0)
                    adjusted_score = item['score'] + (sentiment * 10)
                    scores[category] = scores.get(category, 0) + adjusted_score
                    matches.append({
                        'matched_phrase': item['phrase'],
                        'input_phrase': keyword,
                        'pillar': category,
                        'score': adjusted_score
                    })

    return {
        'pillar_scores': scores,
        'matches': matches
    }

# 5. Generate recommendations using GPT
def generate_recommendations(matches):
    if not matches:
        return {}

    # Group matched phrases by pillar
    pillar_to_phrases = {}
    for m in matches:
        pillar = m['pillar']
        phrase = m['input_phrase']
        if pillar not in pillar_to_phrases:
            pillar_to_phrases[pillar] = []
        pillar_to_phrases[pillar].append(phrase)

    # Construct prompt input
    grouped_text = "\n".join([
        f"{pillar}:\n" + "\n".join([f"- \"{phrase}\"" for phrase in phrases])
        for pillar, phrases in pillar_to_phrases.items()
    ])

    prompt = f"""
You are an expert HR AI consultant.

Based on the grouped feedback phrases per pillar below, generate for each pillar:
1. 1–2 strategic, actionable recommendations
2. A representative list of quotes (directly from the phrases given)

Format your answer like this:
{{
  "Pillar": {{
    "quotes": ["quote1", "quote2"],
    "recommendations": ["Rec 1", "Rec 2"]
  }}
}}

Grouped Feedback Phrases:
{grouped_text}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    try:
        return eval(response.choices[0].message.content.strip())
    except Exception as e:
        print("❌ Failed to parse GPT recommendation output:", e)
        return {}

# 6. Compute Strategic and Operational scores
def compute_dimension_scores(pillar_scores):
    dimensions = {"Strategic": 0, "Operational": 0}
    for pillar, score in pillar_scores.items():
        axis = pillar_to_axis.get(pillar)
        if axis:
            dimensions[axis] += score
    return dimensions

# 7. Map the 2x2 quadrant based on scores
def map_to_maturity_quadrant(scores, threshold=50):
    strategic = scores["Strategic"]
    operational = scores["Operational"]

    if strategic < threshold and operational < threshold:
        return "Emerging"
    elif strategic < threshold and operational >= threshold:
        return "Tactical"
    elif strategic >= threshold and operational < threshold:
        return "Strategic"
    else:
        return "Transformational"

# 8. Main detection + recommendation + quadrant mapping flow
def analyze_response(response_text):
    print("\nSurvey Response:", response_text)
    print("\n→ Extracting themes using GPT...")
    extracted = extract_phrases_with_gpt(response_text)
    print("→ Extracted Themes:", extracted)

    print("\n→ Matching to maturity pillars with GPT sentiment adjustment...")
    keyword_map = load_keyword_map()
    result = match_keywords_to_pillars_with_sentiment(extracted, keyword_map)

    print("\nMatched Phrases and Scores:")
    for match in result['matches']:
        print(f"  - [{match['pillar']}] \"{match['input_phrase']}\" → \"{match['matched_phrase']}\" (score: {match['score']:.2f})")

    print("\nPillar Scores Summary:")
    for pillar, score in result['pillar_scores'].items():
        print(f"  - {pillar}: {score:.2f}")

    print("\n→ Calculating Strategic and Operational dimension scores...")
    dimension_scores = compute_dimension_scores(result['pillar_scores'])
    print(f"  - Strategic: {dimension_scores['Strategic']:.2f}")
    print(f"  - Operational: {dimension_scores['Operational']:.2f}")

    quadrant = map_to_maturity_quadrant(dimension_scores)
    print("\n🧭 Maturity Level (2x2 Grid Quadrant):", quadrant)

    print("\n→ Generating Recommendations using GPT...")
    recommendations = generate_recommendations(result["matches"])

    print("\nRecommendations:")
    for pillar, details in recommendations.items():
        print(f"  - {pillar}:")
        quotes = details.get("quotes", [])
        for quote in quotes:
            print(f"    🗨️  \"{quote}\"")
        recs = details.get("recommendations", [])
        for rec in recs:
            print(f"    • {rec}")

    result["dimension_scores"] = dimension_scores
    result["maturity_level"] = quadrant
    result["recommendations"] = recommendations

    return result

# touched on 2025-05-27T15:29:13.443097Z