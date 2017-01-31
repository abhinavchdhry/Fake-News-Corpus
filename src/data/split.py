f = open("combined.txt", "r")

f1 = open("data_part1.txt", "w+")
f2 = open("data_part2.txt", "w+")
f3 = open("data_part3.txt", "w+")
f4 = open("data_part4.txt", "w+")

l = []
for line in f:
	l.append(line.strip())

l1 = l[0:850]
l2 = l[850:1700]
l3 = l[1700:2550]
l4 = l[2550:len(l)]

for url in l1:
	f1.write(url + "\n")
f1.close()

for url in l2:
	f2.write(url + "\n")
f2.close()

for url in l3:
	f3.write(url + "\n")
f3.close()

for url in l4:
	f4.write(url + "\n")
f4.close()
