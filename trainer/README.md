# Model trainer API

Fast demo for edge-cloud interaction.

## Methods

| Route        | Method | Explanation                                                 |
| ------------ | ------ | ----------------------------------------------------------- |
| /            | GET    | Health check endpoint, only returns 200                     |
| /models      | GET    | GET currently available model IDs                           |
| /models      | POST   | Upload a new model for training, returns ID                 |
| /models/<id> | GET    | Download a model. Returns 202 if the model is being trained |
