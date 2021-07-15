# Flask and MongoDB assignmnet
### Task: 
Create a flask application which will use below given project service endpint and make a GET API call to project service. From the response of the API, you have to extract the information related to associated datasets and models and make separate documents for all the datasets and all the models. \
Now create new database with your name inside below given Mongo and create new appropriate collections. Now store the new datasets and models documnets in these collections.

### Expectations: 
You have to give one API endpoint, which will take the project ID and will do all the above processing such that new documnets are stored in new collection.\
Now give two more API endpoints which can be used to fetch the informantion related to datasets and models based on following filters:
- project_id: give all the datasets and models related to a project
- database_id: give the info for that dataset_id
- model_id: give the info for that model_id

An API which will take dataset_id and give the list of models which have been trained using that dataset

### Submission:
Clone this repo in your local and make a new branch with your name, update the readme with the details related to how to use the application. Now commit the changes and push it. Please mention the information related to the implementation and used collections/document designs etc. Do not add any information above ------------ line of this readme file.

### Required Details:
#### Project Service Endpoint: 
``` http://sentenceapi2.servers.nferx.com:8015/tagrecorder/v3/projects/{project_id} ``` \
  e.g.: `http://sentenceapi2.servers.nferx.com:8015/tagrecorder/v3/projects/607e2bb4383fa0b9dc012ba6`

#### bMongoDB Related Info: 
- Host: mongo.servers.nferx.com/
- Credentials: use the credentials you have received in the mail.

#### Test Projects IDs: 
- 5fd1e3d98ba062dffa513175
- 5fd1ead68ba062dffa5204fc
- 601bcdbeb8a45f4f8185185f
- 605db7f1dd043f7dbfd6c4a1
- 607e2bb4383fa0b9dc012ba6

###### You can always reach out to Sairam Bade or Kuldeep on slack in case of any doubt. Good Luck!
---------------------------------------------
#Your readme goes here :)

### Database details

- Mongo server (host) : `mongo.servers.nferx.com`
- database name : `shahid`
- Collections : `projects`, `datasets`, `models`

The reason behind having three collections is because of the kind of queries we have on our database (`get_project_related_datasets_models`, `get_info`, `get_models_trained_with_dataset` APIs related queries)

#### User Credentials
Add ur user credentials to the code before running the app. (`MONGO_USER` and `MONGO_PASSWORD`)
Also modify port number, if necessary.

### Workflow for APIs
There are 4 APIs in total (excluding healthcheck and root page APIs)

**Optional** : Examples for all the 6 APIs are given in a postman collection (`Mongo-flask-assignment.postman_collection.json`). Import this collection and test the APIs

***Work flow for each API:***

#### import_project API
##### API details
API to import project details of requested project into my database
- Method supported : **POST**
- Request parameters :
  - **project_id** : ID of the project

##### API Workflow
- Make `GET` request to given service endpoint with requested `project_id`
- Two possible cases
  - If project information of requested `project_id` is already present then update our database if necessary (decided using last updated timestamp)
  - Else insert these details to our collections

**Note** : the `projects` collection is NOT inserted with the same information as the response received from service endpoint. The models and datasets information is removed and added to the respective collections. Only the names of models and datasets are stored in the `projects` collection.

#### get_project_related_datasets_models API
##### API details
API to get list of datasets and models associated to a given project
- Method supported : **GET**
- Request parameters :
  - **project_id** : ID of the project

##### API Workflow
- If project information of requested `project_id` is not present in our `projects` collection then make a `POST` call to `import_project` API with the same `project_id`
- If project information is in our collection, return the response accordingly.

#### get_info API
##### API details
API to get information of requested dataset OR model OR project
- Method supported : **POST**
- Request parameters :
  - **info_of** : information of what kind of entity (projects, models or datasets)
  - **id** : project ID for projects, dataset ID for datasets and model name for models ( as models don't have an ID in the response from service endpoint)

##### API Workflow
- For `info_of` == projects
  - If project information of requested `project_id` is not present in our `projects` collection then make a `POST` call to `import_project` API with the same `project_id`
  - If project information is in our collection, return the response accordingly.
- For other `info_of` categories
  - Query the respective collection and return the response

#### get_models_trained_with_dataset API
##### API details
API to get list of models trained with given dataset
- Method supported : **GET**
- Request parameters : 
  - **dataset_id** : ID of the dataset

##### API Workflow
- Query for the models having the requested `dataset_id` in the list of datasets used to train it