import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI

# database
postions = [
    {
        "id": 1,
        "symbol": "AAPL",
        "quantity": 100,
        "price": 150.00
    },  
    {
        "id": 2,
        "symbol": "GOOG",
        "quantity": 200,
        "price": 250.00
    },
]

@strawberry.type
class Position:
    id: int
    symbol: str
    quantity: int
    price: float

@strawberry.type
class Query:
    @strawberry.field
    def positions(self) -> list[Position]:
        return [
            Position(
                id=p["id"],
                symbol=p["symbol"],
                quantity=p["quantity"],
                price=p["price"],
            )
            for p in postions
        ]


# Create the GraphQL schema
schema = strawberry.Schema(query=Query)

# Create FastAPI app
app = FastAPI()

# Add GraphQL route
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)