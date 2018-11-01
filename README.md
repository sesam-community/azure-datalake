# Avro files in Azure Datalake

Example system config:
```
{
  "_id": "my-datalake",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "TENANT": "c317fa72-b393-44ea-a87c-ea272e8d963d",
      "CLIENT_ID": "5329c2e3-6454-43e4-ab89-c17f547546ce",
      "CLIENT_SECRET": "...",
      "STORE_NAME": "svvpoc2"
      "AVRO_SCHEMA": {
        "type": "record",
        "name": "Weather",
        "doc": "A weather reading.",
        "fields": [
          {
           "type": "string",
           "name": "station"
          },
          {
           "type": "long",
           "name": "time"
          },
          {
           "type": "int",
           "name": "temp"
          }
        ],
        "namespace": "test"
      }
    },
    "image": "sesamcommunity/azure-datalake",
    "port": 5000
  }
}
```

Example sink pipe:
```
{
  "transform": {
    "type": "dtl"
    [ make sure the outgoing entities match the AVRO_SCHEMA specified, otherwise it will fail ]
  }
  "sink": {
    "type": "json",
    "system": "my-datalake"
  }
}
```

## Limitations

* Only Azure Datalake Gen 1 is supported
* All files are treated as Avro with the configured schema