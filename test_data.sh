curl -H "Content-Type: application/json" -X PUT -d '{"email":"johndoe@email.com","password":"password", "first_name": "John", "last_name": "Doe", "phone": "7777777777", "school":"UVA"}' http://localhost:8000/api/v1/accounts/user/
curl -H "Content-Type: application/json" -X PUT -d '{"driver":"1","password":"password", "first_name": "John", "last_name": "Doe", "phone": "7777777777", "school":"UVA"}' http://localhost:8000/api/v1/accounts/user/
