import graphene
import crm.schema # Import Query and Mutation from your crm app's schema.py

class Query(
    crm.schema.Query, 
    # Add other app query classes here if you have them
    graphene.ObjectType
):
    pass

class Mutation(
    crm.schema.Mutation,
    # Add other app mutation classes here
    graphene.ObjectType
):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)