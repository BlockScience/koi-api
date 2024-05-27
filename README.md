# koi-api
an api...

## API Specification

### (Knowledge) Objects

POST /object

```
{
    "rid": "string",
    "data": {}
}
```

GET /object


```
{
    "rid": "string"
}
```

DELETE /object

```
{
    "rid": "string"
}
```

## TODO
### Classes
- Base RID
    - `space/type:reference` format
    - dereference function
- Relations
    - Undirected Relation
    - Directed Relation
    - Undirected Assertion
    - Directed Assertion

### Endpoints
- Objects
    - graph actions
        - create (observe)
        - delete
    - stateless actions
        - dereference
    - cache actions
        - read cached data
- Query
    - set operations
        - intersection
        - union
        - difference
    - graph operations
        - neighbors
    - vector store
        - semantic similarity
    - text search
- Relations
    - create
    - read
    - update (assertions only)
    - update members (assertions only)
    - delete
    - *(removed fork, read transactions, update definition)*