import json
jsonData = '{"name": "Frank", "age": 39}'
jsonToPython = json.loads(jsonData)
print(jsonToPython)
dictionaryToJson = json.dumps(jsonToPython)
print(dictionaryToJson)