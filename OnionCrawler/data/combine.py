import json

f1 = open("data.txt", "r")
f2 = open("ABCdata.txt", "r")
f3 = open("RNRNdata.txt", "r")

f = open("combined.txt", "w+")

for line in f1:
	jl = json.loads(line)
	s = str(jl["url"])
	f.write(s + "\n")

for line in f2:
        jl = json.loads(line)
        s = str(jl["url"])
        f.write(s + "\n")

for line in f3:
	if line.strip() != "":
		jl = json.loads(line)
        	s = str(jl["url"])
        	f.write(s + "\n")
