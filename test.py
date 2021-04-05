import base64

contents = list()
contents2 = list()
with open("sample.txt","r") as f:
    contents = f.read()
    contents2 = [ch for ch in f.read()]
print(contents[0])
print(contents2)