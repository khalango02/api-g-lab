# api-g-lab

RUN

python3 app.py


---------------

# Cadastro de policy

curl --location 'localhost:8080/admin/policies' \
--header 'Content-Type: application/json' \
--data '{
  "name": "check_api_key"
}'


# Cadastro de API

curl --location 'localhost:8080/admin/routes' \
--header 'Content-Type: application/json' \
--data '{
  "path": "/minha-api",
  "method": "GET",
  "target_url": "http://localhost:5000/endpoint-real",
  "policy_id": 1
}'


# Teste de API

curl --location 'localhost:8080/minha-api'