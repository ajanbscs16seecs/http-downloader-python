

no_of_threads = 5
file_size = 22

chunk = int(file_size /no_of_threads) 
temp = -1
while temp<file_size:
    print(str(temp+1)+"-"+str(temp+chunk if file_size>= (temp+chunk) else file_size-1 ))
    temp+=chunk





