import csv

outfile = open("negatives.csv", "w")

for i in range(11):
 data = open(f'./results_emily/{i:02}', 'r')
 latest = list(csv.reader(data))
 for entry in latest:
  if "-2" == entry[2]:
   outfile.write(str(entry) + "\n")

outfile.close()
