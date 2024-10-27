# 🐦 Mini-Twitter
Welcome to the selection project for backend developers at b2bit! This project has been created as a demonstration of my skills in web development, scalability, testing, and API design. Below, you will find a complete description and the requirements that guided the creation of this application.

# 🏁 Project Overview
Mini-Twitter provides a robust platform for users to:

- Register and authenticate.
- Create, edit, delete, and like posts.
- Follow and unfollow other users.
- View a personalized feed with posts from followed users.
This project showcases best practices in backend development, focusing on scalability, security, and testing.

# 📄 Languages and Technologies Used
- **Python 3.10**
- **Framework**: Django REST Framework
- **Authentication**: JWT (JSON Web Tokens)
- **Banco de Dados**: PostgreSQL
- **Cache**: Redis
- **Asynchronous Queues** : Celery
- **API Documentation**: Swagger
- **CI/CD**: GitHub Actions
- **Tests**: Django Test
- **IDE**: VSCode
- **Docker/Docker-compose**

# 📈 Diagrams
![image](https://github.com/user-attachments/assets/204bbbdd-2781-40a1-9701-ede5fdaa3837)

## Entity-Relationship Diagram (ERD)
The ERD shows five tables:

### users

- id: Primary key, unique identifier for each user.
- username: User's name.
- email: User's email address.
- password_hash: Encrypted password.
- created_at: Timestamp for when the user was created.

### posts

- id: Primary key, unique identifier for each post.
- user_id: Foreign key linking to the users table, indicating the author of the post.
- title: Title of the post.
- content: Content of the post.
- image_path: Path to any associated image.
- deleted_post: Boolean flag indicating if the post is deleted.
- created_at: Timestamp for when the post was created.
- updated_at: Timestamp for the last update to the post.

### likes

- id: Primary key, unique identifier for each like.
- user_id: Foreign key linking to the users table, indicating who liked the post.
- post_id: Foreign key linking to the posts table, indicating which post was liked.
- created_at: Timestamp for when the like was created.

### follows

- id: Primary key, unique identifier for each follow action.
- follower_id: Foreign key linking to the users table, indicating the user who is following another user.
- followed_id: Foreign key linking to the users table, indicating the user being followed.
- created_at: Timestamp for when the follow relationship was created.

## System Design Choices
Database Relationships:

### One-to-Many Relationship:
- users to posts: Each user can create multiple posts, so there is a one-to-many relationship between users and posts.
- posts to likes: Each post can have multiple likes, and each like belongs to a single post.

### Many-to-Many Relationship:
- users to follows: The follows table allows users to follow other users, creating a many-to-many self-referencing relationship within the users table.

### Deleted Post Flag:
- The posts table has a deleted_post boolean flag. Instead of physically deleting posts, this allows for "soft deletion" where a post is marked as deleted, preserving its data and enabling potential recovery.

### Database:
The database contains the schema as shown in the ERD, providing persistent storage for user data, posts, likes, and follow relationships.
Indexes on fields such as user_id in posts, post_id in likes, and follower_id/followed_id in follows can be implemented to improve query performance.

## Project Structure
```bash
├── apps
│   ├── authentication
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── authentication.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── twitter
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── management
│   │   │   └── commands
│   │   │       └── populate_models.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_post_image.py
│   │   │   ├── 0003_alter_like_post.py
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── signals.py
│   │   ├── tasks.py
│   │   ├── tests
│   │   │   ├── __init__.py
│   │   │   ├── test_authentication.py
│   │   │   ├── test_models.py
│   │   │   ├── test_redis_celery.py
│   │   │   ├── test_routes.py
│   │   │   └── test_serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   └── users
│       ├── admin.py
│       ├── apps.py
│       ├── __init__.py
│       ├── migrations
│       │   └── __init__.py
│       ├── models.py
│       ├── serializers.py
│       ├── tests.py
│       ├── urls.py
│       └── views.py
├── celerybeat-schedule
├── core
│   └── static
│       └── posts
│           └── img
│               └── default.png
├── docker-compose.yml
├── Dockerfile
├── LICENSE
├── manage.py
├── README.md
├── requirements.txt
├── setup
│   ├── asgi.py
│   ├── celery.py
│   ├── __init__.py
│   ├── middleware.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── wait-for-it.sh
```

# ⚙️ Instructions to Run the Project

### Installation Guide

1. Clone the repository:
   ```bash
   git clone https://github.com/JulioSoaresA/b2bit.git
2. Navigate to the project directory:
   ```bash
   cd mini_twitter

### Setting Up a Virtual Environment
  1. Download this repository and enter the project directory.
  2. Create a virtual environment using VirtualEnv:
     ```bash
     python -m venv venv
  3. Activate the virtual environment:
     - On Linux:
       ```bash
       source venv/bin/activate

      - On Windows:
        ```bash
        .\venv\Scripts\activate.ps1
  4. Activate the virtual environment:
     ```bash
     pip install -r requirements.txt
     ```
  5. Installing migrations
     ```bash
     python manage.py migrate
     ```
  6. Run server
     ```bash
     python manage.py runserver
     ```
  7. Access the api in:<br>
    `localhost:8000/api`

  ### Running the Project with Docker
  1. Simply execute:
  ```bash
  docker-compose up --build
  ```
  This will build and start the container, including the database, Celery and Redis server.
  2. Execute the container:
  ```bash
    docker exec -it b2bit_web_1 /bin/bash
  ```
  3. Installing migrations:
  ```bash
    dpython manage.py migrate
  ```
  4. Access the api in:<br>
    `localhost:8000/api`
  ---
# 📝 Endpoints

## Docs
- `/docs/`: Provides interactive API documentation.

## Auth
- `/auth/login/`: Logs in a user and returns an access token.
- `/auth/logout/`: Logs out a user, invalidating the current token.
- `/auth/register/`: Registers a new user.
- `/auth/token/refresh/`: Refreshes the user's access token.

## Posts
- `/posts/create/`: Creates a new post.
- `/posts/update/{id}/`: Updates an existing post by its ID.
- `/posts/delete/{id}`: Deletes a post by its ID.
- `/posts/like/`: Likes or unlikes a post.
- `/posts/feed/`: Retrieves a feed of posts.

## User
- `/user/follow/`: Follows or unfollows another user.
- `/user/followers/`: Retrieves a list of the current user's followers.
- `/user/following/`: Retrieves a list of users the current user is following.
- `/user/profile/`: Retrieves or updates the current user's profile information.
- `/user/user_list/`: Lists all users.

### Running Tests
1.
    ```bash
    docker exec -it b2bit_web_1 /bin/bash
    ```
2.
    ```bash
    python manage.py test twitter
    ```
  
# 📄 TECHNICAL REQUIREMENTS
## ⚙️ [TC.1] API Development:

- [x] Use Python 3 and a Python web framework of your choice (Django REST Framework preferred).
- [x] Implement the API following RESTful design principles.

## 🔐 [TC.2] Authentication:

- [x] Use JWT (JSON Web Tokens) for user authentication and session management.

## 💽 [TC.3] Database:

- [x] Use a relational database (preferably PostgreSQL).
- [x] Ensure the database design follows best practices, with attention to normalization and performance optimization.

## 🔋 [TC.3] Caching & Scalability:

- [x] Implement caching (e.g., using Redis) for the user feed or other high-read endpoints to ensure scalability.
- [x] Followers count in the user's profile using redis.
- [x] Like count for each post using redis.

## 📄 [TC.4.] Pagination

- [x] Implement pagination for the posts list

## 🧪 [TC.5] Testing:

- [x] Provide unit tests (this will be way easier using Django)
- [x] Ensure that both functional and edge cases are well-covered.

## 📝 [TC.6] Documentation:

- [x] API documentation using Swagger or Postman.

## 🐳 [TC.7] Docker:

- [x] The project should be containerized using Docker. Provide a Dockerfile and docker-compose.yml for easy setup.

# 🌟 BONUS POINTS
## 👮🏻 Advanced Security Features:

- [x] Implement rate limiting on API endpoints to prevent abuse.
- [x] Secure endpoints using best security practices (e.g., input validation, SQL injection prevention, and CSRF protection).

## 🔁 Asynchronous Tasks:

- [x] Use Celery or other task queues to handle tasks asynchronously (e.g., sending email notifications when a user follows another user).

## 🔎 Search Feature:

- [x] Add a search functionality to allow users to find posts by keyword or hashtags

## 🚀 CI/CD:

- [x] Set up basic CI/CD to run automated tests (using tools like GitLab CI, GitHub Actions, or Jenkins).

# 👨🏼‍🏫 USE CASES
## CASE 1: User Registration
- [x] Users should be able to sign up via the API by providing an email, username, and password.
- [x] Use JWT to handle authentication for login and session management.

## CASE 2: Post Creation
- [x] Authenticated users can create a post with text and one image as content
- [x] Posts can be liked by other users.

## CASE 3: Follow/Unfollow User
- [x] Users should be able to follow or unfollow others.
- [x] The feed should only show posts from users the authenticated user follows.

## CASE 4: Viewing Feed
- [x] The user can view a paginated list of posts from the users they follow.
- [x] Posts should be ordered by creation time, from most recent to oldest.

## 👷 Autor
* **Júlio Soares** - *Backend* - [@juliocsoaresa1](https://www.linkedin.com/in/juliocsoaresa1/)
