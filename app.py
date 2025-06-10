#!pip install streamlit
from keras_vggface.utils import preprocess_input
from keras_vggface.vggface import VGGFace
import pickle
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
from PIL import Image
import os
import cv2
from mtcnn import MTCNN
import numpy as np

# Create required directories
os.makedirs("uploads", exist_ok=True)

detector = MTCNN()
model = VGGFace(model='resnet50', include_top=False, input_shape=(224,224,3), pooling='avg')

# Load data with error handling
try:
    feature_list = pickle.load(open('embedding.pkl', 'rb'))
    filenames = pickle.load(open('filenames.pkl', 'rb'))
except Exception as e:
    st.error(f"Error loading data files: {str(e)}")
    st.stop()

def save_uploaded_image(uploaded_image):
    try:
        with open(os.path.join('uploads', uploaded_image.name), 'wb') as f:
            f.write(uploaded_image.getbuffer())
        return True
    except Exception as e:
        st.error(f"Error saving image: {str(e)}")
        return False

def extract_features(img_path, model, detector):
    try:
        img = cv2.imread(img_path)
        if img is None:
            st.error("Failed to read image file")
            return None
            
        results = detector.detect_faces(img)
        if not results:
            st.error("No faces detected in the image")
            return None
            
        x, y, width, height = results[0]['box']
        face = img[y:y + height, x:x + width]
        
        image = Image.fromarray(face)
        image = image.resize((224, 224))
        face_array = np.asarray(image).astype('float32')
        
        expanded_img = np.expand_dims(face_array, axis=0)
        preprocessed_img = preprocess_input(expanded_img)
        result = model.predict(preprocessed_img).flatten()
        return result
    except Exception as e:
        st.error(f"Feature extraction failed: {str(e)}")
        return None

def recommend(feature_list, features):
    try:
        if features is None:
            return -1
            
        similarity = []
        for i in range(len(feature_list)):
            similarity.append(cosine_similarity(features.reshape(1, -1), feature_list[i].reshape(1, -1))[0][0])
        
        index_pos = sorted(list(enumerate(similarity)), reverse=True, key=lambda x: x[1])[0][0]
        return index_pos
    except Exception as e:
        st.error(f"Recommendation failed: {str(e)}")
        return -1

st.title('Which bollywood celebrity are you?')
uploaded_image = st.file_uploader('Choose an image', type=['jpg', 'jpeg', 'png'])

if uploaded_image is not None:
    if save_uploaded_image(uploaded_image):
        display_image = Image.open(uploaded_image)
        features = extract_features(os.path.join('uploads', uploaded_image.name), model, detector)
        index_pos = recommend(feature_list, features)
        
        if index_pos >= 0:
            predicted_actor = " ".join(Path(filenames[index_pos]).parts[-2].split('_'))
            
            col1, col2 = st.columns(2)
            with col1:
                st.header('Your uploaded image')
                st.image(display_image)
            with col2:
                st.header(f"Seems like {predicted_actor}")
                
                # Verify the file exists before displaying
                celeb_path = Path(filenames[index_pos])
                if celeb_path.exists():
                    st.image(str(celeb_path), width=300)
                else:
                    st.error(f"Image not found at: {str(celeb_path)}")
                    st.write("Trying to display from relative path:")
                    st.image(filenames[index_pos], width=300)  # Fallback attempt
        else:
            st.warning("Could not find a matching celebrity")