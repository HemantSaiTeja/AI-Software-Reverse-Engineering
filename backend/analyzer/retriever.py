from neo4j import GraphDatabase


# =============================
# Neo4j Connection
# =============================

URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"

# Your local Neo4j password
PASSWORD = "12345678"


driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


# =============================
# Get Graph Context
# =============================

def get_graph_context(function_name):

    query = """
    MATCH (f)
    WHERE (f:Function OR f:Method)
      AND (
          f.name = $name
          OR f.name ENDS WITH "." + $name
      )

    OPTIONAL MATCH (f)-[:CALLS]->(called)

    OPTIONAL MATCH (caller)-[:CALLS]->(f)

    RETURN
        collect(DISTINCT called.name) AS calls,
        collect(DISTINCT caller.name) AS callers
    """

    with driver.session() as session:

        result = session.run(
            query,
            name=function_name
        )

        record = result.single()

        return {
            "calls": record["calls"],
            "callers": record["callers"]
        }