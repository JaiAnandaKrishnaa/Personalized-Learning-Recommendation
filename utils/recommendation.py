import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import streamlit as st

def load_courses():
    return pd.read_csv('data/courses.csv')

def get_recommendations(interests, courses_df):
    # Create a new column that combines all the text data
    courses_df['content'] = courses_df['course_name'] + ' ' + courses_df['interest'] + ' ' + courses_df['description']

    # Add the user's interests as a new 'course' to the DataFrame
    user_interests = ' '.join(interests)
    user_df = pd.DataFrame({'course_name': ['User Interests'], 'interest': ['User Interests'], 'description': [user_interests], 'content': [user_interests]})
    combined_df = pd.concat([user_df, courses_df], ignore_index=True)

    # Use TF-IDF Vectorizer to transform the text data into vectors
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(combined_df['content'])

    # Calculate cosine similarity between the user's interests and the courses
    cosine_similarities = linear_kernel(tfidf_matrix[0:1], tfidf_matrix).flatten()

    # Get the top courses based on cosine similarity scores
    top_courses_indices = cosine_similarities.argsort()[::-1][1:9]  # Skip the first one as it is the user interests itself
    top_courses = combined_df.iloc[top_courses_indices]

    return top_courses

def display_recommendations(recommendations):
    for index, row in recommendations.iterrows():
        st.markdown(f"""
        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2); margin-bottom: 20px;">
            <h3 style="color: #333;">{row['course_name']}</h3>
            <h4 style="color: #555;">Interest: {row['interest']}</h4>
            <p>{row['description']}</p>
            <img src='img/bg.jpg' alt='Course Image' style='width:100%;height:auto;border-radius:5px;'/>
        </div>
        """, unsafe_allow_html=True)

# Example usage in Streamlit
if __name__ == "__main__":
    st.title('Course Recommendations')
    
    courses_df = load_courses()
    interests = st.multiselect('Select your interests', courses_df['interest'].unique())

    if interests:
        recommendations = get_recommendations(interests, courses_df)
        
        st.subheader('Recommended Courses:')
        display_recommendations(recommendations)
