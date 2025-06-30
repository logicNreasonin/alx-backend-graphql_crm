# alx-backend-graphql_crm/alx-backend-graphql_crm/schema.py

import graphene

class Query(graphene.ObjectType):
    """
    Defines the root queries for the GraphQL API.
    """
    hello = graphene.String(default_value="Hello, GraphQL!")

# The main schema for the project
schema = graphene.Schema(query=Query)