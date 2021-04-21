import csv

outfile = open("negatives.csv", "w")

for i in range(11):
 data = open(f'./results_emily/{i:02}', 'r').readlines()
 #latest = list(csv.reader(data))
 for i in range (len(data)):
  data_as_list = data[i].split(',')
  if "-2\n" == data_as_list[2]:
   outfile.writelines(data[i])

outfile.close()
