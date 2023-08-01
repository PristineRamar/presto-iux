import requests

url = "http://localhost:81/generate"
myobj = {"messages": ["somevalue", "someother", "sumthin"]}

x = requests.post(url, json=myobj)

print(x.text)
