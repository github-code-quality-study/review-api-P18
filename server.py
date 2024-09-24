import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from urllib.parse import parse_qs, urlparse
import json
import pandas as pd
from datetime import datetime
import uuid
import os
from typing import Callable, Any
from wsgiref.simple_server import make_server

nltk.download('vader_lexicon', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('stopwords', quiet=True)

adj_noun_pairs_count = {}
sia = SentimentIntensityAnalyzer()
stop_words = set(stopwords.words('english'))

reviews = pd.read_csv('data/reviews.csv').to_dict('records')

class ReviewAnalyzerServer:
    def __init__(self) -> None:
        # This method is a placeholder for future initialization logic
        pass

    def analyze_sentiment(self, review_body):
        sentiment_scores = sia.polarity_scores(review_body)
        return sentiment_scores

    def get_data_filter_by_location(self, location, reviews):
        """
        FIlter Data by Location
        """
        location_filter_list = []

        for review in reviews:
            if review['Location'] == location:
                location_filter_list.append(review)

        return location_filter_list

    def get_data_filter_by_start_date(self, start_date, reviews):
        """
        Filter Reviews by Start Time
        """
        start_date_filter_list = []

        for review in reviews:
            review_date_time = datetime.strptime(review['Timestamp'], "%Y-%m-%d %H:%M:%S")
            start_date_time = datetime.strptime(start_date, "%Y-%m-%d")

            if review_date_time >= start_date_time:
                start_date_filter_list.append(review)

        return start_date_filter_list

    
    def get_data_filter_by_end_date(self, end_date, reviews):
        """
        Filter Reviews by End Date
        """

        end_date_filter_list = []

        for review in reviews:
            review_date_time = datetime.strptime(review['Timestamp'], "%Y-%m-%d %H-%M-%S")
            end_date_time = datetime.strptime(end_date, "%Y-%m-%d")

            if review_date_time <= end_date_time:
                end_date_filter_list.append(review)

        return end_date_filter_list

    def get_data_filter_by_start_end_date(self, start_date, end_date):
        """
        Filter Reviews by Start Date & End Date
        """
        filter_start_date = self.get_data_filter_by_start_date(start_date, reviews)

        filter_end_date = self.get_data_filter_by_end_date(end_date, filter_start_date)

        return filter_end_date

    def sentimentize(self, reviews_list):
        """
        Sentimentize for adding Sentiments to Reviews
        """
        sentiment_reviews = []
        for review in reviews_list:
            review['sentiment'] = self.analyze_sentiment(review['ReviewBody'])

            sentiment_reviews.append(review)
        
        return sentiment_reviews


    def __call__(self, environ: dict[str, Any], start_response: Callable[..., Any]) -> bytes:
        """
        The environ parameter is a dictionary containing some useful
        HTTP request information such as: REQUEST_METHOD, CONTENT_LENGTH, QUERY_STRING,
        PATH_INFO, CONTENT_TYPE, etc.
        """

        if environ["REQUEST_METHOD"] == "GET":
            # Create the response body from the reviews and convert to a JSON byte string
            response_body = json.dumps(reviews, indent=2).encode("utf-8")
            
            # Write your code here
            
            # Get Query String
            query_string = str(environ['QUERY_STRING'])

            # Get Vals from Query String
            query_string_valz = parse_qs(query_string)

            # Filter Data by Location
            try:
                location = query_string_valz['location'][0]

                data_filter_by_location = self.sentimentize(self.get_data_filter_by_location(location, reviews))
                response_body = json.dumps(data_filter_by_location, index=2).encode("utf-8")
            except Exception as e:
                pass


            # FIlter Data by Start Date
            try:
                start_date = query_string_valz['start_date'][0]

                data_filter_by_start_date = self.sentimentize(this.get_data_filter_by_start_date(start_date, reviews))
                response_body = json.dumps(data_filter_by_start_date, indent=2).encode("utf-8")
            except Exception as e:
                pass

            
            # Filter Data bu End Date
            try:
                end_date = query_string_valz['end_date'][0]
                
                data_filter_by_end_date = self.sentimentize(self.get_data_filter_by_end_date(end_date, reviews))
                response_body = json.dumps(data_filter_by_end_date, indent=2).encode("utf-8")
            except Exception as e:
                pass

            
            # Filter Data by Start Date and End Date
            try:
                start_date = query_string_valz['start_date'][0]
                end_date = query_string_valz['end_date'][0]

                data_filter_by_start_end_date = self.sentimentize(self.get_data_filter_by_start_end_date(start_date, end_date, reviews))
                response_body = json.dumps(data_filter_by_start_end_date, index=2).encode('utf-8')
            except Exception as e:
                pass 


            # Set the appropriate response headers
            start_response("200 OK", [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(response_body)))
             ])
            
            return [response_body]


        if environ["REQUEST_METHOD"] == "POST":
            # Write your code here
            return

if __name__ == "__main__":
    app = ReviewAnalyzerServer()
    port = os.environ.get('PORT', 8000)
    with make_server("", port, app) as httpd:
        print(f"Listening on port {port}...")
        httpd.serve_forever()