# Expense Tracker API

*Project from: [roadmap.sh](https://roadmap.sh/projects/expense-tracker-api)*

RESTful API for an expense tracker application, that allows users to create, read, update, and delete expenses.

### Tech Stack
FastAPI(Python framework), PostgreSQL(for databases), SQLModel(ORM)

## Features

 - Sign up as a new user.

 - Generate and validate JWTs for handling authentication and user session.

 - Add a new expense

 - Remove existing expenses

 - Update existing expenses

 - List, sort and filter your past expenses:

    - search parametrs (to filter expenses by categories)

    - Custom date filter (to specify a start and end date of your choosing).

    - You can also sort your expenses by amount and id

    - Response is paginated.


## Installation and Setup

### 1. Clone the repository:
```bash
git clone https://github.com/Ficserbiyy/expense-tracker-api.git
```

### 2. Create a .env file in the root directory and add Environment Variables:
```.env
DB_PASSWORD=password
DB_USER=postgres
DB_NAME=finance
DB_HOST=db
SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRE=30
```

### 3. Use [Docker](https://docs.docker.com/get-started/get-docker/) to Launch the application:
```bash
docker-compose up --build  # First launch
docker-compose up          # For regular use
```

## Usage

### Now Go to http://127.0.0.1:8000/docs to see the automatic interactive API documentation.

Sort parametrs:

    "amount_asc"
    "amount_desc"
    "id_asc"
    "id_desc"

Date filter parametrs. "Past month" filter example:

    start_date = "2026-06-26"
    end_date = "2026-07-26"