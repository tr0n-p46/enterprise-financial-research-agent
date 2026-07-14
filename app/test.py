users = [
    {
        "name": "Alice",
        "age": 23
    },
    {
        "name": "Tom",
        "age": 12
    },
    {
        "name": "hwand",
        "age": 24
    },
    {
        "name": "Emily",
        "age": 18
    }
]

results = sorted(users, key=lambda user: user['age'])
print(list(results))