
## Database Overview

The system uses MongoDB as the database, consisting of two collections:

- **Users**: Stores details about librarians and members.
- **Books**: Stores information about books.

## Users collection 

```
{
  "_id": {
    "$oid": "6705558bdd160577877bede3"
  },
  "username": "kiran",
  "password": "$2b$12$g/262V.62amh3F5EZgFqH.moNVi4blmBKByDO96gIrljOo0GlgeG.",
  "user_type": "member",
  "address": "street sd",
  "email": "jdoe@example.com",
  "is_deleted": true
}
```

This is schema for users collection.
- `_id` is unique identifier
- username, password , email , address are user provided details.
- user_type can be member/ librarian
- `is_deleted` is boolean . when user is deleted it change to true.
## Books collection

```shell
{
  "_id": {
    "$oid": "670545fe67a516bacbdd74be"
  },
  "name": "Angels & demons",
  "description": "Fiction books",
  "created_ts": {
    "$numberLong": "1728398846515"
  },
  "author": "Dan brown",
  "genre": "Action",
  "is_deleted": false,
  "borrowed_by_id": {
    "$oid": "670544c1592a9eea5f6b71d8"
  },
  "borrowed_by_name": "kiran",
  "borrowed_ts": {
    "$numberLong": "1728399021440"
  },
  "returned_ts": {
    "$numberLong": "1728399040351"
  },
  "status": "AVAILABLE"
}
```
This is the schema of books collection.
- `_id` is unique identifier
- name, description , author , genre are books details.
- `is_deleted` is boolean . when user is deleted it change to true.
- `borrowed_by_id` is `ObjectId` that connect with users collection
- `borrowed_by_name` borrowed user name
- `returned_ts` and `borrowed_ts` are timestamps in milisecond
- `status` refer book status

