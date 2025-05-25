# api-g-lab

RUN

docker-compose up -d --build

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
  "target_url": "http://host.docker.internal:5001/endpoint-real",
  "policy_id": 1
}'


# Teste de API

curl --location 'localhost:8080/minha-api' \
--header 'X-Api-Key: secret123'



# Subir API de teste

python3 test.py
