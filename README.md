# ALX Backend GraphQL CRM

A simple Customer Relationship Management (CRM) backend built with GraphQL. This project is part of the ALX Software Engineering curriculum and demonstrates how to build a backend API using GraphQL, Node.js, and MongoDB.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [GraphQL Schema](#graphql-schema)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

- Manage customers, projects, and users
- CRUD operations via GraphQL queries and mutations
- MongoDB integration for data persistence
- Modular and scalable codebase

## Tech Stack

- **Node.js** (JavaScript runtime)
- **Express.js** (web framework)
- **GraphQL** (API query language)
- **MongoDB** (database)
- **Mongoose** (ODM for MongoDB)

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (v14+)
- [MongoDB](https://www.mongodb.com/) (local or Atlas)

### Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/alx-backend-graphql_crm.git
    cd alx-backend-graphql_crm
    ```

2. **Install dependencies:**
    ```bash
    npm install
    ```

3. **Set up environment variables:**
    - Create a `.env` file in the root directory.
    - Add your MongoDB connection string:
      ```
      MONGODB_URI=mongodb://localhost:27017/crm
      PORT=4000
      ```

4. **Start the server:**
    ```bash
    npm start
    ```
    The server will run on `http://localhost:4000/graphql`.

## Project Structure

```
alx-backend-graphql_crm/
├── models/         # Mongoose models
├── resolvers/      # GraphQL resolvers
├── schema/         # GraphQL schema definitions
├── index.js        # Entry point
├── package.json
└── README.md
```

## GraphQL Schema

Example types:

```graphql
type Customer {
  id: ID!
  name: String!
  email: String!
  phone: String
  projects: [Project]
}

type Project {
  id: ID!
  name: String!
  description: String
  customer: Customer
}

type Query {
  customers: [Customer]
  customer(id: ID!): Customer
  projects: [Project]
  project(id: ID!): Project
}

type Mutation {
  addCustomer(name: String!, email: String!, phone: String): Customer
  updateCustomer(id: ID!, name: String, email: String, phone: String): Customer
  deleteCustomer(id: ID!): Customer
}
```

## Usage

- Access the GraphQL Playground at `http://localhost:4000/graphql`.
- Example query:
  ```graphql
  query {
     customers {
        id
        name
        email
     }
  }
  ```
- Example mutation:
  ```graphql
  mutation {
     addCustomer(name: "Jane Doe", email: "jane@example.com", phone: "1234567890") {
        id
        name
     }
  }
  ```

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements.

## License

This project is licensed under the [MIT License](LICENSE).
