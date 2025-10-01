n = int(input())
s = []
for i in range(n+1):
    row=[1]*(i+1)
    for j in range(i+1):
        if j!=i and j!=0: row[j] = s[i-1][j-1]+s[i-1][j]
    s.append(row)
print(s[n] if n!=0 else [1])