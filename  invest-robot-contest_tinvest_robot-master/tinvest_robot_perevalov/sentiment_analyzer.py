"""Module for sentiment analyzer classes
"""
import os
from transformers import TFAutoModelForSequenceClassification
from transformers import AutoTokenizer
from scipy.special import softmax


class SentimentAnalyzer:
    """
    Sentiment Analyzer class for predicting sentiment of textual news
    """
    def __init__(self, model, threshold, labels) -> None:
        """
        SentimentAnalyzer constructor 

        Args:
            model (_type_): model name/path from huggingface
            threshold (_type_): threshold for sentiment classification (difference between positive and negative > threshold)
            labels (_type_): class labels for sentiment classification
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = TFAutoModelForSequenceClassification.from_pretrained(model)
        self.threshold = threshold
        self.labels = labels
        
        # caching
        if "data" not in model:
            self.model.save_pretrained(os.path.join("..", "data", model))
            self.tokenizer.save_pretrained(os.path.join("..", "data", model))
    

    def predict_sentiment(self, text) -> str:
        """
        Predict sentiment of text

        Args:
            text (_type_): text to predict sentiment

        Returns:
            str: one of the sentiment classes: positive, negative, neutral
        """
        encoded_input = self.tokenizer(text, return_tensors='tf')
        output = self.model(encoded_input)
        scores = output[0][0].numpy()
        scores = softmax(scores)

        if scores[0] > scores[2] and abs(scores[0] - scores[2]) > self.threshold: # negative
            return 'negative'
        elif scores[0] < scores[2] and abs(scores[0] - scores[2]) > self.threshold: # positive
            return 'positive'
        else: # neutral
            return 'neutral'