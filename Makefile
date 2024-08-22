db-up:
	docker run --name fake-checker -p 5432:5432 -e POSTGRES_PASSWORD=password -e POSTGRESQL_DATABASE=fake_checker bitnami/postgresql:latest
db-stop:
	docker stop fake-checker
db-down:
	docker stop fake-checker
	docker rm fake-checker

test-db-up:
	docker run --name fake-checker-test -p 5433:5432 -e POSTGRES_PASSWORD=password -e POSTGRESQL_DATABASE=fake_checker bitnami/postgresql:latest
test-db-stop:
	docker stop fake-checker-test
test-db-down:
	docker stop fake-checker-test
	docker rm fake-checker-test