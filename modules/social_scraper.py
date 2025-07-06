def get_social_hype_score(telegram_group_size, twitter_followers, post_engagement_rate):
    score = 0

    if telegram_group_size > 1000:
        score += 30
    elif telegram_group_size > 300:
        score += 15

    if twitter_followers > 2000:
        score += 30
    elif twitter_followers > 500:
        score += 15

    if post_engagement_rate > 5:
        score += 30
    elif post_engagement_rate > 2:
        score += 15

    return min(100, score)
