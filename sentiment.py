def get_sentiment(text):
    """
    Simple rule-based sentiment analysis for the AI Integration Layer.
    """
    pos_words = {'masterpiece', 'legendary', 'incredible', 'brilliant', 'beautiful', 'moving', 'spectacular', 'perfect', 'heartwarming', 'iconic', 'great', 'good', 'love', 'amazing'}
    neg_words = {'bad', 'terrible', 'waste', 'boring', 'awful', 'tragic', 'violent', 'horror', 'bleak', 'dark'}
    
    words = text.lower().split()
    score = 0
    for w in words:
        if w in pos_words: score += 1
        if w in neg_words: score -= 1
        
    if score > 0: return "Positive"
    if score < 0: return "Negative"
    return "Neutral"
