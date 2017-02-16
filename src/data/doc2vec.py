import json
from gensim.models.doc2vec import TaggedDocument, Doc2Vec

f = open("data.json", "r")
data = json.load(f)

real_count = 0
fake_count = 0

documents = []

print("Labeling documents...")
for e in data:
	document = e["text"]
	_class = e["class"]
	words = [w.strip() for w in document.split()]
	if _class == "Fake":
		documents.append(TaggedDocument(words=words, tags=["FAKE_" + str(fake_count)]))
		fake_count += 1
	else:
		documents.append(TaggedDocument(words=words, tags=["REAL_" + str(real_count)]))
		real_count += 1

real_tags = ["REAL_" + str(i) for i in range(0, real_count)]
fake_tags = ["FAKE_" + str(i) for i in range(0, fake_count)]

print("Done")

print("Building model...")
model = Doc2Vec(size = 100, alpha = 0.025, min_alpha=0.025)
model.build_vocab(documents)
print("Done")

print("Training model...")
for epoch in range(10):
	print("Iteration " + str(epoch) + " ...")
	model.train(documents)
	model.alpha -= 0.002
	model.min_alpha = model.alpha
print("Done")

fake_docs = [list(i) for i in model.docvecs[fake_tags]]
real_docs = [list(i) for i in model.docvecs[real_tags]]
