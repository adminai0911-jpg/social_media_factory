import sys

with open('orchestrator/v32_dopamine_engine.py', 'r', encoding='utf-8') as f:
    code = f.read()

trend_func = '''
def get_daily_trend():
    """Asks Gemini for today's most controversial Indian financial trend/news."""
    logger.info("📰 Fetching today's controversial financial trend...")
    valid_keys = [k for k in GEMINI_KEYS if k]
    if not valid_keys: return ""
    try:
        client = genai.Client(api_key=valid_keys[0])
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="What is the most controversial, FOMO-inducing, or fearful financial news/trend in India today (e.g. taxes, stock market crash, inflation, job losses)? Reply with one short, aggressive sentence. Do not use markdown.",
            config=types.GenerateContentConfig(temperature=0.7)
        )
        trend = response.text.strip()
        logger.info(f"🔥 Daily Trend Acquired: {trend}")
        return f"CRITICAL CONTEXT FOR THIS SCRIPT: The video MUST be built around this trending news/fear: '{trend}'. Tie the advice back to this current event to induce FOMO and urgency."
    except Exception as e:
        logger.warning(f"Failed to fetch daily trend: {e}")
        return ""

def generate_dynamic_script():'''
code = code.replace('def generate_dynamic_script():', trend_func)

old_prompt_section = '''    # Analytics Feedback
    analytics_text = get_omni_analytics_feedback()

    prompt = f"""You are an elite TikTok/Reels/Shorts growth expert and dopamine-engineering copywriter.
    Your sole purpose is to write highly viral, 15-30 second scripts about wealth, dark psychology, or deep success.

    {analytics_text}

    LANGUAGE REQUIREMENT:'''
new_prompt_section = '''    # Analytics Feedback
    analytics_text = get_omni_analytics_feedback()
    
    # Daily Viral Trend Injection
    trend_text = get_daily_trend()

    prompt = f"""You are an elite TikTok/Reels/Shorts growth expert and dopamine-engineering copywriter.
    Your sole purpose is to write highly viral, 15-30 second scripts about wealth, dark psychology, or deep success.

    {analytics_text}
    {trend_text}

    LANGUAGE REQUIREMENT:'''
code = code.replace(old_prompt_section, new_prompt_section)

old_rules = '''- ZERO generic advice: Never say "work hard", "save money". Every insight MUST be counterintuitive.
- The numbered_list must teach a COMPLETE, ACTIONABLE mini-framework.'''
new_rules = '''- ZERO generic advice: Never say "work hard", "save money". Every insight MUST be counterintuitive.
- DOOM-SCROLL AGGRESSION: Ban all generic advice. Use "Us vs. Them" psychology (e.g. Banks vs You, Rich vs Middle Class, Secret Trap). Make the viewer feel intense urgency and FOMO.
- The numbered_list must teach a COMPLETE, ACTIONABLE mini-framework.'''
code = code.replace(old_rules, new_rules)

with open('orchestrator/v32_dopamine_engine.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Patch applied successfully.')
