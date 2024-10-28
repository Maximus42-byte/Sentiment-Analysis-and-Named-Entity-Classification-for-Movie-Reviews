# -*- coding: utf-8 -*-
"""NLP_HW4_NN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EoFLv7lSNz86NwpRGyD86AO1GUHRNSHz

**DATA Preparation**
"""

from google.colab import drive
drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
# %pip install pytreebank

import pytreebank
# load the sentiment treebank corpus in the parenthesis format,
# e.g. "(4 (2 very ) (3 good))"
dataset = pytreebank.load_sst()
# add Javascript and CSS to the Ipython notebook
pytreebank.LabeledTree.inject_visualization_javascript()
# select and example to visualize
example = dataset["test"][2000]
# display it in the page
example.display()

import pytreebank
dataset = pytreebank.load_sst()
# example = dataset["test"][1]

# extract spans from the tree.
for label, sentence in example.to_labeled_lines():
	print("%s has sentiment label %s" % (
		sentence,
		["very negative", "negative", "neutral", "positive", "very positive"][label]
	))

example.to_lines()[0]

len(example.to_lines()[0].split())

example.label

sst_train = dataset["train"]
sst_val = dataset["dev"]
sst_test = dataset["test"]

print(dataset["dev"][0].label)

# for i in range(len(dataset["train"])):
#   print(dataset["train"][i].to_lines()[0])
#   print(dataset["train"][i].label)
#   print("_"*100)
#   if (i == 10):
#     break

"""**Neural Network Model**

**calculating fasttext feature vector using tf-idf**

FastText and TF-IDF are two distinct techniques and you can't directly calculate FastText embeddings using TF-IDF. However, you can use the TF-IDF weights as features to train a FastText model for text classification tasks. The idea is to first calculate the TF-IDF weights for each word in a document, and then use these weights as input features for the FastText model
"""

# Commented out IPython magic to ensure Python compatibility.
# %pip install fasttext

import fasttext
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

# Load the SST-5 dataset into a pandas dataframe
#df = pd.read_csv("sst-5.csv")
df = pd.DataFrame(columns=['text', 'label'])
for i in range(len(dataset["train"])):
#for i in range(10):
  df = df.append({'text': dataset["train"][i].to_lines()[0], 'label': dataset["train"][i].label}, ignore_index=True)

df.head(25)

len(df)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df['text'], df['label'], test_size=0.2, random_state=42)

#reset indexing
X_train.reset_index(inplace = True,drop = True)
X_test.reset_index(inplace = True,drop = True)
y_train.reset_index(inplace = True,drop = True)
y_test.reset_index(inplace = True,drop = True)

# Calculate the TF-IDF weights
vectorizer = TfidfVectorizer()
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

print(X_train_tfidf[8])

# Convert the TF-IDF matrix into a FastText-compatible format
#labels = [... ] # list of sentiment labels (positive, negative, neutral)
with open('movie_comments_tfidf_train.txt', 'w') as f:
    for i in range(X_train_tfidf.shape[0]):
        comment = X_train_tfidf[i, :].toarray().flatten().tolist()
        comment_str = ' '.join(str(x) for x in comment)
        #label = df['label'][i]
        label = y_train[i]
        f.write(f'__label__{label} {comment_str}\n')

!mv movie_comments_tfidf_train.txt /content/drive/MyDrive/

# Train the FastText model
model = fasttext.train_supervised(
    input='/content/drive/MyDrive/movie_comments_tfidf_train.txt',
    epoch=25,
    lr=0.01,
    wordNgrams=3,
    verbose=2,
    minCount=1
)

# Save the FastText model to a file
model.save_model('fasttext_model_3.bin')

!mv fasttext_model_3.bin /content/drive/MyDrive/

# Load the FastText model from a file
model3 = fasttext.load_model('/content/drive/MyDrive/fasttext_model_3.bin')

# Convert the TF-IDF matrix into a FastText-compatible format
with open('movie_comments_tfidf_test.txt', 'w') as f:
    for i in range(X_test_tfidf.shape[0]):
        comment = X_test_tfidf[i, :].toarray().flatten().tolist()
        comment_str = ' '.join(str(x) for x in comment)
        label = y_test[i]
        f.write(f'__label__{label} {comment_str}\n')

!mv movie_comments_tfidf_test.txt /content/drive/MyDrive/

# Evaluate the model on the test set
result = model3.test('/content/drive/MyDrive/movie_comments_tfidf_test.txt')
print("Accuracy: {:.4f}".format(result[1]))

# Test the FastText model
result = model3.test('/content/drive/MyDrive/movie_comments_tfidf_test.txt')
# Print the results
print("Number of samples:", result[0])
print("Number of correctly classified samples:", result[1])
print("Accuracy:", result[2])

# Extract the FastText embeddings for each movie comment
# comments = [...] # list of movie comments
import numpy as np
comments_vectors = []
for comment in X_train:
    comment_vector = model3.get_sentence_vector(comment)
    comments_vectors.append(comment_vector)
comments_vectors = np.array(comments_vectors)

comments_vectors[0] , len(comments_vectors)

# import tensorflow as tf
# # Define the Neural Network
# model = tf.keras.Sequential()
# model.add(tf.keras.layers.Dense(128, activation='relu', input_shape=(comments_vectors.shape[1],)))
# model.add(tf.keras.layers.Dense(64, activation='relu'))
# #model.add(tf.keras.layers.Dense(1, activation='sigmoid'))
# model.add(tf.keras.layers.Dense(5, activation='softmax'))

# Define the model architecture
import tensorflow as tf
number_of_classes = 5
model_NN = tf.keras.Sequential([
    tf.keras.layers.Dense(256, input_shape=(comments_vectors.shape[1],), activation='relu'),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(number_of_classes, activation='softmax')
])

print(tf. __version__)

# from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score

# def accuracy(y_true, y_pred):
#     return accuracy_score(y_true, y_pred)

# def recall(y_true, y_pred):
#     return recall_score(y_true, y_pred, average='macro')

# def precision(y_true, y_pred):
#     return precision_score(y_true, y_pred, average='macro')

# def f1(y_true, y_pred):
#     return f1_score(y_true, y_pred, average='macro')

# def f1_score(y_true, y_pred):
#     precision = tf.keras.metrics.Precision()
#     recall = tf.keras.metrics.Recall()

#     precision.update_state(y_true, y_pred)
#     recall.update_state(y_true, y_pred)

#     f1_score = 2 * (precision.result() * recall.result()) / (precision.result() + recall.result() + 1e-6)
#     return f1_score

# Compile the Neural Network
opt2 = tf.keras.optimizers.Adam(learning_rate=0.001)
#loss=tf.keras.losses.sparse_categorical_crossentropy,
# def f1_score(y_true, y_pred):
#     true_positives = tf.keras.backend.sum(tf.keras.backend.round(tf.keras.backend.clip(y_true * y_pred, 0, 1)))
#     predicted_positives = tf.keras.backend.sum(tf.keras.backend.round(tf.keras.backend.clip(y_pred, 0, 1)))
#     possible_positives = tf.keras.backend.sum(tf.keras.backend.round(tf.keras.backend.clip(y_true, 0, 1)))

#     precision = true_positives / (predicted_positives + tf.keras.backend.epsilon())
#     recall = true_positives / (possible_positives + tf.keras.backend.epsilon())
#     f1_score = 2 * (precision * recall) / (precision + recall + tf.keras.backend.epsilon())

#     return f1_score

from keras import losses, metrics
#model.compile(optimizer= 'adam', loss='categorical_crossentropy', metrics=[accuracy, recall, precision, f1])
model_NN.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=[metrics.CategoricalAccuracy(),
                       metrics.Precision(),
                       metrics.Recall(),
                       metrics.AUC()])

# Train the Neural Network
labels = y_train # list of sentiment labels (positive, negative, neutral , ...)
labels = np.array(labels)

type(labels[0]) , labels[0] , len(labels)

labels = labels.astype(np.float32)

labels[5:15]

import matplotlib.pyplot as plt
plt.hist(labels, bins=5, edgecolor='black', align='left')
plt.xlabel('Label')
plt.ylabel('Count')
plt.title('Label Distribution')
plt.show()

#one-hot encoding of the labels
from keras.utils import to_categorical
num_classes = 5
onehot__labels = to_categorical(labels, num_classes)

type(onehot__labels) , onehot__labels[0:5] , len(onehot__labels)

#labels = tf.convert_to_tensor(labels)
history = model_NN.fit(comments_vectors, onehot__labels, epochs=10, batch_size=20)

# Extract the FastText embeddings for each movie comment
# comments = [...] # list of movie comments
import numpy as np
comments_vectors_test = []
for comment in X_test:
    comment_vector = model3.get_sentence_vector(comment)
    comments_vectors_test.append(comment_vector)
comments_vectors_test = np.array(comments_vectors_test)

X_test[0]

labels_test = y_test # list of sentiment labels (positive, negative, neutral , ...)
labels_test = np.array(labels_test)

labels_test = labels_test.astype(np.float32)

num_classes = 5

onehot__test_labels = to_categorical(labels_test, num_classes)

# evaluate the model on your test data
test_loss, test_accuracy, test_precision, test_recall , test_auc= model_NN.evaluate(comments_vectors_test, onehot__test_labels, verbose=0)

# print the evaluation metrics
print('Test Loss:', test_loss)
print('Test Accuracy:', test_accuracy)
print('Test Precision:', test_precision)
print('Test Recall:', test_recall)
#print('Test F1 Score:', test_f1_score)

#save the model and transfer it to google drive

from sklearn.metrics import f1_score
predictions = model_NN.predict(comments_vectors_test)
# Convert the predictions to a class label
predicted_classes = np.argmax(predictions, axis=1)

comments_vectors_test[15]

model_NN.predict(comments_vectors_test[15].reshape(1, -1))

import pickle
# Save the model
def save_model(model, filename):
    with open(filename, 'wb') as file:
        pickle.dump(model, file)

# Load the model
def load_model(filename):
    with open(filename, 'rb') as file:
        model = pickle.load(file)
    return model

save_model(model_NN, 'NN_Sentimentmodel.bin')

!mv NN_Sentimentmodel.bin /content/drive/MyDrive/

model5 = load_model('/content/drive/MyDrive/NN_Sentimentmodel.bin')

predicted_classes[145:289]

# Calculate the F1-score
f1 = f1_score(onehot__test_labels, predicted_classes, average='micro')

text1 = 'i really love this movie'
text2 = 'i have it it was horibble'
text3 = 'it was not a bad movie'

def test_NN(input_text, NN_model, fasttextmodel):
  input_features = input_text
  input_text_vector = fasttextmodel.get_sentence_vector(input_features)
  input_text_vector_NN = input_text_vector.reshape(1, -1)
  prediction = NN_model.predict(input_text_vector_NN)
  predicted_label = np.argmax(prediction)

  return predicted_label , prediction

# input_features = vectorizer.transform([text2])
# # input_text_vector = model3.get_sentence_vector(input_features)

test_NN(text1, model5, model3)

"""**THE Logistic Regression**"""

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Create the TF-IDF feature vectors for the training and test data
#tfidf_vectorizer = TfidfVectorizer()
train_features = X_train_tfidf.astype(np.float32)
test_features = X_test_tfidf.astype(np.float32)
train_labels = y_train.astype(np.float32)
test_labels = y_test.astype(np.float32)

#astype(np.float32)

# Train a logistic regression model on the training data
clf = LogisticRegression()
clf.fit(train_features, train_labels)

# Use the trained model to make predictions on the test data
predictions = clf.predict(test_features)

# Calculate the accuracy of the model
accuracy = accuracy_score(test_labels, predictions)
print("Accuracy:", accuracy)

from sklearn.model_selection import cross_val_score

# Perform 5-fold cross-validation
model = clf
X = train_features
y = train_labels
scores = cross_val_score(model, X, y, cv=5)

# Calculate mean score and standard deviation
mean_score = np.mean(scores)
std_dev = np.std(scores)

print("Mean score:", mean_score)
print("Standard deviation:", std_dev)

import numpy as np

def predict_label(input_text, vectorizer, classifier):
    input_features = vectorizer.transform([input_text])
    prediction = classifier.predict(input_features)
    prediction_probabilities = classifier.predict_proba(input_features)
    predicted_label = prediction[0]
    predicted_probabilities = prediction_probabilities[0]
    
    return predicted_label, predicted_probabilities

text1 = 'i really love this movie'

text2 = 'i have it it was horibble'

predict_label(text2,vectorizer,clf)

"""**Downloading with gdown from the google drive**"""

!pip install --upgrade --no-cache-dir gdown

#uploading models and data with gdwon
!gdown 1-2nV4Za-2lbhxSyHRvrdDUPXq3Cne1Y-

!gdown 1ANIGzY5hLWLrVn3spk45QBBudb5LjJu-

!gdown 13ZXX0jvW9WN4ol3qE2vjlNdE7VKxMwk9

!gdown 1w_FZzhytWIkU23C9244tlvCGPsjkObzV

!gdown 1-1yGMjrTuGJE3A47PyaJYfVpRJxpUZWX