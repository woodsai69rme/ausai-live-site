"""
AI-Powered Content Analysis Module for YouTube Enhancement Tools
This module adds AI-powered content analysis including sentiment analysis,
content optimization suggestions, automatic tagging, and engagement prediction.
"""

import os
import openai
import requests
import json
from textblob import TextBlob
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    logger.warning("Could not download NLTK data. Some features may not work.")


class AIContentAnalyzer:
    """
    A class to perform AI-powered content analysis on video titles, descriptions, and transcripts
    """
    
    def __init__(self, openai_api_key=None):
        """
        Initialize the AI Content Analyzer
        
        Args:
            openai_api_key (str, optional): OpenAI API key for GPT-based analysis
        """
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # Initialize sentiment analyzer
        try:
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
        except:
            self.sentiment_analyzer = None
            logger.warning("Could not initialize VADER sentiment analyzer")
        
        # Initialize transformer-based sentiment analysis
        try:
            self.transformer_sentiment = pipeline("sentiment-analysis", 
                                               model="cardiffnlp/twitter-roberta-base-sentiment-latest")
        except:
            self.transformer_sentiment = None
            logger.warning("Could not initialize transformer sentiment analyzer")
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of the given text using multiple approaches
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Sentiment scores
        """
        results = {}
        
        # Use VADER if available
        if self.sentiment_analyzer:
            vader_scores = self.sentiment_analyzer.polarity_scores(text)
            results['vader'] = vader_scores
        
        # Use transformer model if available
        if self.transformer_sentiment:
            transformer_result = self.transformer_sentiment(text)[0]
            results['transformer'] = {
                'label': transformer_result['label'],
                'score': transformer_result['score']
            }
        
        # Use TextBlob as fallback
        blob = TextBlob(text)
        results['textblob'] = {
            'polarity': blob.sentiment.polarity,  # -1 to 1, negative to positive
            'subjectivity': blob.sentiment.subjectivity  # 0 to 1, objective to subjective
        }
        
        return results
    
    def generate_content_suggestions(self, title: str, description: str, transcript: str = "") -> List[str]:
        """
        Generate content optimization suggestions using AI
        
        Args:
            title (str): Video title
            description (str): Video description
            transcript (str, optional): Video transcript
            
        Returns:
            list: Content optimization suggestions
        """
        if not self.openai_api_key:
            logger.warning("OpenAI API key not available. Returning basic suggestions.")
            return [
                "Consider adding more specific keywords to your title",
                "Include timestamps in your description for better user experience",
                "Add relevant hashtags to increase discoverability",
                "Consider creating a series if this is a standalone video"
            ]
        
        try:
            # Combine all content for analysis
            combined_content = f"Title: {title}\n\nDescription: {description}"
            if transcript:
                combined_content += f"\n\nTranscript: {transcript[:2000]}"  # Limit transcript length
            
            prompt = f"""
            Analyze the following YouTube video content and provide specific, actionable suggestions for improvement:
            
            {combined_content}
            
            Provide suggestions in the following areas:
            1. Title optimization
            2. Description enhancement
            3. Keyword recommendations
            4. Engagement tactics
            5. Content structure improvements
            
            Format your response as a list of specific, actionable suggestions.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            suggestions_text = response.choices[0].message.content
            # Simple parsing of the suggestions
            suggestions = [s.strip() for s in suggestions_text.split('\n') if s.strip() and not s.strip().startswith(('1.', '2.', '3.', '4.', '5.'))]
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating content suggestions: {e}")
            return ["Could not generate AI suggestions. Please check your API key and connection."]
    
    def generate_tags(self, title: str, description: str, transcript: str = "") -> List[str]:
        """
        Generate relevant tags for the video content
        
        Args:
            title (str): Video title
            description (str): Video description
            transcript (str, optional): Video transcript
            
        Returns:
            list: Relevant tags for the video
        """
        if not self.openai_api_key:
            logger.warning("OpenAI API key not available. Returning basic tags.")
            # Basic tag generation based on content
            all_text = f"{title} {description} {transcript}".lower()
            words = all_text.split()
            # Filter out common stop words and return unique words as tags
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
            tags = list(set(word for word in words if len(word) > 3 and word not in stop_words))[:10]  # Limit to 10 tags
            return tags
        
        try:
            combined_content = f"Title: {title}\n\nDescription: {description}"
            if transcript:
                combined_content += f"\n\nTranscript: {transcript[:1500]}"  # Limit transcript length
            
            prompt = f"""
            Generate 10-15 relevant tags for the following YouTube video content. 
            Tags should be single words or short phrases that users might search for.
            Separate tags with commas.
            
            {combined_content}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.5
            )
            
            tags_text = response.choices[0].message.content
            # Parse tags from the response
            tags = [tag.strip().replace('"', '').replace("'", "") for tag in tags_text.split(',') if tag.strip()]
            
            return tags[:15]  # Limit to 15 tags
            
        except Exception as e:
            logger.error(f"Error generating tags: {e}")
            return ["Could not generate AI tags. Please check your API key and connection."]
    
    def predict_engagement(self, title: str, description: str, tags: List[str], 
                         upload_hour: int, day_of_week: int) -> Dict[str, float]:
        """
        Predict potential engagement metrics for the video
        
        Args:
            title (str): Video title
            description (str): Video description
            tags (list): Video tags
            upload_hour (int): Hour of day to upload (0-23)
            day_of_week (int): Day of week to upload (0=Monday, 6=Sunday)
            
        Returns:
            dict: Predicted engagement metrics
        """
        # This is a simplified model - in a real implementation, you'd use a trained ML model
        title_length_score = min(len(title) / 60, 1.0)  # Optimal title length around 60 chars
        desc_length_score = 1.0 if len(description) > 50 else len(description) / 50  # Longer descriptions tend to perform better
        
        # Sentiment analysis of title
        title_sentiment = self.analyze_sentiment(title)
        sentiment_score = title_sentiment.get('textblob', {}).get('polarity', 0)
        
        # Engagement prediction (simplified)
        base_engagement = 0.5  # Base engagement score
        title_factor = title_length_score * 0.3
        desc_factor = desc_length_score * 0.2
        sentiment_factor = abs(sentiment_score) * 0.2  # Strong emotions drive engagement
        time_factor = 0.3 if 14 <= upload_hour <= 16 else 0.1  # Peak hours for engagement
        
        predicted_engagement = min(base_engagement + title_factor + desc_factor + sentiment_factor + time_factor, 1.0)
        
        return {
            'predicted_view_rate': predicted_engagement,
            'estimated_views_first_day': int(predicted_engagement * 1000),  # Simplified estimation
            'engagement_score': predicted_engagement,
            'confidence': 0.7  # Confidence in prediction
        }
    
    def analyze_keywords(self, text: str, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Analyze and rank keywords in the text by importance
        
        Args:
            text (str): Text to analyze
            top_n (int): Number of top keywords to return
            
        Returns:
            list: Top keywords with their importance scores
        """
        try:
            # Simple TF-IDF based keyword extraction
            vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
            tfidf_matrix = vectorizer.fit_transform([text])
            
            feature_names = vectorizer.get_feature_names_out()
            dense_tfidf = tfidf_matrix.todense().tolist()[0]
            
            # Create keyword-score pairs
            keyword_scores = [(feature_names[i], dense_tfidf[i]) for i in range(len(feature_names))]
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            return keyword_scores[:top_n]
            
        except Exception as e:
            logger.error(f"Error analyzing keywords: {e}")
            return []


class EngagementPredictor:
    """
    A class to predict video engagement using machine learning models
    """
    
    def __init__(self):
        """
        Initialize the Engagement Predictor
        """
        self.model_trained = False
        self.model = None
    
    def train_model(self, training_data: List[Dict]):
        """
        Train the engagement prediction model
        
        Args:
            training_data (list): Training data with features and engagement metrics
        """
        # This would be a more complex implementation in a real scenario
        # For now, we'll just indicate that a model could be trained
        logger.info(f"Training engagement prediction model with {len(training_data)} samples")
        self.model_trained = True
    
    def predict(self, features: Dict) -> Dict[str, float]:
        """
        Predict engagement based on video features
        
        Args:
            features (dict): Video features to base prediction on
            
        Returns:
            dict: Engagement predictions
        """
        if not self.model_trained:
            logger.warning("Model not trained. Returning baseline prediction.")
            return {
                'predicted_view_rate': 0.5,
                'estimated_views_first_day': 500,
                'engagement_score': 0.5,
                'confidence': 0.5
            }
        
        # Placeholder for actual model prediction
        return {
            'predicted_view_rate': 0.6,
            'estimated_views_first_day': 600,
            'engagement_score': 0.6,
            'confidence': 0.8
        }


def analyze_video_content(title: str, description: str, transcript: str = "") -> Dict:
    """
    Comprehensive AI analysis of video content
    
    Args:
        title (str): Video title
        description (str): Video description
        transcript (str, optional): Video transcript
    
    Returns:
        dict: Comprehensive analysis results
    """
    analyzer = AIContentAnalyzer()
    
    # Perform all analyses
    sentiment_analysis = analyzer.analyze_sentiment(f"{title} {description} {transcript}")
    suggestions = analyzer.generate_content_suggestions(title, description, transcript)
    tags = analyzer.generate_tags(title, description, transcript)
    keywords = analyzer.analyze_keywords(f"{title} {description} {transcript}")
    
    # Predict engagement (using default values for time)
    engagement_prediction = analyzer.predict_engagement(
        title=title,
        description=description,
        tags=tags,
        upload_hour=15,  # 3 PM
        day_of_week=2  # Wednesday
    )
    
    return {
        'sentiment_analysis': sentiment_analysis,
        'content_suggestions': suggestions,
        'recommended_tags': tags,
        'keywords': keywords,
        'engagement_prediction': engagement_prediction
    }


# Example usage
if __name__ == "__main__":
    # Example usage of the AI content analyzer
    analyzer = AIContentAnalyzer()
    
    title = "Learn Python in 1 Hour - Beginner Tutorial"
    description = "In this tutorial, you'll learn Python programming basics in just 1 hour. Perfect for beginners!"
    transcript = "Welcome to this Python tutorial. Today we'll cover variables, loops, and functions..."
    
    # Analyze sentiment
    sentiment = analyzer.analyze_sentiment(f"{title} {description}")
    print("Sentiment Analysis:", sentiment)
    
    # Generate suggestions
    suggestions = analyzer.generate_content_suggestions(title, description, transcript)
    print("\nContent Suggestions:", suggestions)
    
    # Generate tags
    tags = analyzer.generate_tags(title, description, transcript)
    print("\nRecommended Tags:", tags)
    
    # Predict engagement
    engagement = analyzer.predict_engagement(
        title=title,
        description=description,
        tags=tags,
        upload_hour=15,
        day_of_week=2
    )
    print("\nEngagement Prediction:", engagement)
    
    # Comprehensive analysis
    comprehensive_analysis = analyze_video_content(title, description, transcript)
    print("\nComprehensive Analysis:", json.dumps(comprehensive_analysis, indent=2))