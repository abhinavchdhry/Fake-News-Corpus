import json, os
from gensim.models.doc2vec import TaggedDocument, Doc2Vec
import csv
import pandas as pd
import glob
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS as stop_words
from sklearn.model_selection import StratifiedShuffleSplit
import lightgbm as lgb
from sklearn.metrics import log_loss, accuracy_score, precision_recall_fscore_support
from sklearn.preprocessing import LabelEncoder
import random
import numpy as np
from itertools import product

print("### Reading data...")
f = open("data.json", "r")
data = json.load(f)

real_count = 0
fake_count = 0

documents = []

#print("Labeling documents...")
#for e in data:
#	document = e["text"]
#	_class = e["class"]
#	words = [w.strip() for w in document.split()]
#	if _class == "Fake":
#		documents.append(TaggedDocument(words=words, tags=["FAKE_" + str(fake_count)]))
#		fake_count += 1
#	else:
#		documents.append(TaggedDocument(words=words, tags=["REAL_" + str(real_count)]))
#		real_count += 1

text = []
_class = []
for e in data:
	text.append(e["text"])
	_class.append(e["class"])

df = pd.DataFrame({"text":text, "class":_class})

# Read the Kaggle dataset
print("### Reading Kaggle data...")
kaggle_df = pd.DataFrame.from_csv("kaggle-fake-news.csv")

print("Original data shape: " + str(df.shape))
df_real = df[df["class"] == "Real"]
df_fake = df[df["class"] == "Fake"]
print("Real count = " + str(df_real.shape[0]))
print("Fake count = " + str(df_fake.shape[0]))


print("Kaggle df shape: " + str(kaggle_df.shape))
df = df.append(kaggle_df)
print("Combined df shape: " + str(df.shape))

print("### Reading in BBC data...")
bbc_articles = []
## Reading in BBC dataset
bbc_categories = os.listdir("./bbc/")
for category in bbc_categories:
	filenames = os.listdir("./bbc/" + category)
	for fn in filenames:
		with open("./bbc/" + category + "/" + fn, "r") as f:
			lines = []
			for line in f:
				lines.append(line)
			bbc_articles.append(" ".join(lines))

bbc_df = pd.DataFrame({"text":bbc_articles})
bbc_df["class"] = "Real"

df = df.append(bbc_df)
print("Combined df shape with BBC data: " + str(df.shape))

df_real = df[df["class"] == "Real"]
df_fake = df[df["class"] == "Fake"]
print("Real count = " + str(df_real.shape[0]))
print("Fake count = " + str(df_fake.shape[0]))

### Add the NYTimes data here
NYTdocs = []
NYTfiles = glob.glob("./NYTdata/NYTstories_*")
for fname in NYTfiles:
	with open(fname, "r") as f:
		for line in f:
			art = json.loads(line)
			NYTdocs.append(art["text"])

NYTdf = pd.DataFrame({"text":NYTdocs})
NYTdf["class"] = "Real"

df = df.append(NYTdf)
print("Final total number of rows: " + str(df.shape[0]))
df_real = df[df["class"] == "Real"]
df_fake = df[df["class"] == "Fake"]
print("Real count = " + str(df_real.shape[0]))
print("Fake count = " + str(df_fake.shape[0]))


print("### Writing combined dataframe...")
df.to_csv("output.csv", index=False)
#exit(1)


## Random data learning verification
#df = df[df["class"] == "Fake"]
#idx = random.sample(df.index, len(df.index)/2)
#df.loc[idx, "class"] = "Real"

############################ Models ###############################

def vectorize(df, method='tfidf', n_features=250):
	if method == 'tfidf':
		corpus = df["text"].values.astype('U')
		tfidf = TfidfVectorizer(input='content', strip_accents='ascii', ngram_range=(1, 1), stop_words='english', max_features=n_features, norm="l2")
		print("### Fitting tfidf model...")
		tfidf.fit(corpus)
		print("### Transforming articles...")
		data = tfidf.transform(corpus)

		df_out = pd.DataFrame(data.todense())
		df_out["class"] = df["class"].values

	elif method == 'bow' or method == 'ngrams':
                corpus = df["text"].values.astype('U')
		if method == 'tfidf':
                        ngram_range = (1, 1)
                else:
                        ngram_range = (2, 2)
		bow = CountVectorizer(input='content', strip_accents='ascii', ngram_range=ngram_range, stop_words='english', max_features=n_features)
		print("### Fitting BoW model...")
                bow.fit(corpus)
                print("### Transforming articles...")
                data = bow.transform(corpus)

                df_out = pd.DataFrame(data.todense())
                df_out["class"] = df["class"].values

	return df_out

def preprocess(text):
	tokens = text.lower().split(" ")
	return([t.strip() for t in tokens if (t.strip() != "" and t.strip() not in stop_words)])

def fit_xform_doc2vec(df_train, df_test, n_features=250, n_epochs=1):
	print("### Doc2vec process initiated...")
	train_fake = df_train[df_train["class"]=="Fake"]["text"].values.astype(str)
	train_real = df_train[df_train["class"] == "Real"]["text"].values.astype(str)

	fake_idx = []
	real_idx = []

	fake = []
	real = []
	docs = []
	counter = 0
	for doc in train_fake:
		idx = "Fake_" + str(counter)
		fake_idx.append(idx)
		docs.append(TaggedDocument(words=preprocess(doc), tags=[idx]))
		counter += 1
	for doc in train_real:
		idx = "Real_" + str(counter)
		real_idx.append(idx)
		docs.append(TaggedDocument(words=preprocess(doc), tags=[idx]))
		counter += 1

        print("## Building model...")
        model = Doc2Vec(size = n_features, alpha = 0.025, min_alpha=0.025)
        model.build_vocab(docs)

        print("## Training model...")
        for epoch in range(n_epochs):
                print("# Iteration " + str(epoch) + " ...")
                model.train(docs)
                model.alpha -= 0.002
                model.min_alpha = model.alpha

	fake_df = pd.DataFrame(model.docvecs[fake_idx])
	fake_df["class"] = "Fake"
	real_df = pd.DataFrame(model.docvecs[real_idx])
	real_df["class"] = "Real"

	train_out_df = fake_df.append(real_df)
	
	test_vecs = []
	test_docs = df_test["text"].values.astype(str)

	print("## Inferring test docs...")
	for test_doc in test_docs:
		vec = model.infer_vector(preprocess(test_doc))
		test_vecs.append(vec)

	test_vecs = np.array(test_vecs)
	df_test_out = pd.DataFrame(test_vecs)
	df_test_out["class"] = df_test["class"].values

	return(train_out_df, df_test_out)


ss = StratifiedShuffleSplit(n_splits=4, test_size=0.25)
if 0:
#for train_idx, test_idx in ss.split(df, df["class"].values):
	train_df = df.iloc[train_idx]
        test_df = df.iloc[test_idx]

	train_df, test_df = fit_xform_doc2vec(train_df, test_df, n_epochs=1)

        train_Y = train_df["class"].values
        train_X = train_df.drop('class', axis=1).values

        le = LabelEncoder()
        le.fit(train_Y)
        if le.classes_[0] == "Fake":
                pos_label = 0
        else:
                pos_label = 1

        train_Y = le.transform(train_Y)

        val_Y = test_df['class'].values
        val_X = test_df.drop('class', axis=1).values
        val_Y = le.transform(val_Y)

        model = lgb.LGBMClassifier(boosting_type='gbdt', objective='binary', num_leaves=60, max_depth=5, learning_rate=0.01, n_estimators=200, subsample=1, colsample_bytree=0.8, reg_lambda=0)
        model.fit(train_X, train_Y, eval_set=[(val_X, val_Y)], eval_metric='logloss', early_stopping_rounds=20)

        val_preds_proba = model.predict_proba(val_X)
        loss = log_loss(val_Y, val_preds_proba)

        val_preds = model.predict(val_X)
        print(accuracy_score(val_Y, val_preds))
        print(precision_recall_fscore_support(val_Y, val_preds, pos_label = pos_label, average='binary'))

        print("Validation log_loss: " + str(loss))


def runXvalidation(model, df_features, eval_metric='logloss', early_stopping = 10):
	ss = StratifiedShuffleSplit(n_splits=4, test_size = 0.25)
	logloss_scores = []
	accuracy_scores = []
	precision_scores = []
	recall_scores = []
	f_scores = []

	for train_idx, test_idx in ss.split(df_features, df_features["class"].values):
		train_df = df_features.iloc[train_idx]
		test_df = df_features.iloc[test_idx]

		train_Y = train_df["class"].values
		train_X = train_df.drop('class', axis=1).values

		le = LabelEncoder()
		le.fit(train_Y)
		if le.classes_[0] == "Fake":
			pos_label = 0
		else:
			pos_label = 1

		train_Y = le.transform(train_Y)

		val_Y = test_df['class'].values
		val_X = test_df.drop('class', axis=1).values
		val_Y = le.transform(val_Y)

#		model = lgb.LGBMClassifier(boosting_type='gbdt', objective='binary', num_leaves=60, max_depth=5, learning_rate=0.01, n_estimators=200, subsample=1, colsample_bytree=0.8, reg_lambda=0)
		model.fit(train_X, train_Y, eval_set=[(val_X, val_Y)], eval_metric=eval_metric, early_stopping_rounds=early_stopping, verbose=False)

	        val_preds_proba = model.predict_proba(val_X)
	        loss = log_loss(val_Y, val_preds_proba)
		logloss_scores.append(loss)

		val_preds = model.predict(val_X)
		accuracy = accuracy_score(val_Y, val_preds)
		accuracy_scores.append(accuracy)

		p, r, fscore, __support = precision_recall_fscore_support(val_Y, val_preds, pos_label = pos_label, average='binary')
		precision_scores.append(p)
		recall_scores.append(r)
		f_scores.append(fscore)

#		print("Validation log_loss: " + str(loss))

	return(np.mean(logloss_scores), np.mean(accuracy_scores), np.mean(precision_scores), np.mean(recall_scores), np.mean(f_scores))


print("### Vectorization started...")
df_features = vectorize(df, method='tfidf', n_features=1000)

print("### Running validation tests...")
max_depth = (4, 5, 6, 7)
n_estimators = (500, 1000, 2000, 3000)
early_stopping = (5, 10, 20)
num_leaves = (25, 50, 100)
col_sample = (0.5, 0.75, 1)

res_file = open("results_tfidf_1000_lgb.txt", "w")
res_file.write("max_depth,n_trees,n_leaves,l,a,p,r,f\n")

param_iters = product(max_depth, n_estimators, num_leaves, early_stopping, col_sample)
for params in param_iters:
	max_d = params[0]
	n_est = params[1]
	n_leaves = params[2]
	early = params[3]
	c_sample = params[4]

	model = lgb.LGBMClassifier(boosting_type='gbdt', objective='binary', num_leaves=n_leaves, max_depth=max_d, learning_rate=0.01, n_estimators=n_est, subsample=1, colsample_bytree=c_sample, reg_lambda=0)
	l, a, p, r, f = runXvalidation(model, df_features, early_stopping=early)

	print("\n+++++++++++++++++++++++++++++++++++++")
	print("Model: depth = {}, n_trees = {}, n_leaves = {}, early_stopping = {}, col_sample: {}".format(max_d, n_est, n_leaves, early, c_sample))
	print("Logloss: {}, accuracy: {}, precision: {}, recall: {}, f-measure: {}".format(l, a, p, r, f))
	print("++++++++++++++++++++++++++++++++++++++\n")

#	res_file.write("\n++++++++++++++++++++++++++++++++")
#	res_file.write("Model: depth = {}, n_trees = {}, n_leaves = {}, early_stopping = {}, learning-rate: {}".format(max_d, n_est, n_leaves, early, l_rate))
#	res_file.write("Logloss: {}, accuracy: {}, precision: {}, recall: {}, f-measure: {}".format(l, a, p, r, f))
#	res_file.write("++++++++++++++++++++++++++++++++++++++\n")
	res_file.write("{},{},{},{},{},{},{},{},{},{}\n".format(max_d, n_est, n_leaves, early, c_sample, l, a, p, r, f))
	res_file.flush()
