apt update
apt install docker.io -y
apt install docker-compose -y
apt install make -y 

git submodule update --init --recursive
mv server_config/.env server/.env
mv server_config/docker-compose.yml server/docker-compose.yml
mv server_config/user_schema.json server/public/schemas/user_schema.json
mv server_config/cmd.go server/cmd/api/cmd.go
mv server_config/args.go server/cmd/api/args.go
mv server_config/scim.go server/cmd/internal/args/scim.go

# make docker compose
