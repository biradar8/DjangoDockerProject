# DjangoDockerProject
Django + Docker

A robust web application built with Django, Docker, and Strawberry GraphQL. 
Features a highly available database architecture with Primary/Replica PostgreSQL routing.

## Features

* **Django 5.0**: Backend web framework.
* **Strawberry GraphQL**: Async-first GraphQL API.
* **Dockerized**: Fully containerized environment for development and production.
* **Database Routing**: Custom middleware handling read/write distribution to PostgreSQL Primary/Replica nodes.
* **TinyMCE**: Rich text editing for the Django admin panel.
* **Pytest**: Comprehensive test suite for views and GraphQL mutations.

## Prerequisites

* [Docker](https://www.docker.com/) and Docker Compose
* Python 3.10+

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/biradar8/DjangoDockerProject.git
   ```
   ```bash
   cd DjangoDockerProject
   ```

2. **Configure Environment Variables:**
   Copy the sample environment file and adjust the variables.
   ```bash
   cp .env.example .env
   ```

3. **Build and Run with Docker:**
   ```bash
   docker-compose up --build
   ```

4. **Access the Application:**
   * Blog site: `http://localhost:8000/blog/`
   * Admin Panel: `http://localhost:8000/admin/`
   * GraphQL IDE: `http://localhost:8000/graphql/`
