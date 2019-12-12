
# Initialize postgres
postgres_init:
	-createuser -h localhost -U postgres books
	-createdb -h localhost -U books -O books books_test