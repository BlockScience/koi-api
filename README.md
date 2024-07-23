# KOI API

## Setup
First we need to setup the Python environment by running the following commands. So far this has only been tested on Python 3.12.
```bash
# create and activate virtual environment 'venv/'
python -m venv venv

# on Windows
.\venv\Scripts\activate
# on Linux
source /venv/bin/activate

# install dependencies
pip install -r requirements.txt
```

Next we will setup all of the necessary API keys. Create a file named `.env` in the root directory of the repository and copy and paste the following in:

```bash
# .env

OPENAI_API_KEY=
PINECONE_API_KEY=
VOYAGE_API_KEY=

SLACK_BOT_TOKEN=
SLACK_SIGNING_SECRET=

PUBPUB_USERNAME=
PUBPUB_PASSWORD=
```

The current version requires [OpenAI](https://platform.openai.com/), [Pinecone](https://www.pinecone.io/), and [VoyageAI](https://www.voyageai.com/) API keys to function. Slack and PubPub are not required, but will throw errors if you attempt to dereference corresponding RID objects server side. (Even if you aren't using them, keep the definition with the empty string in the `.env` file or you will get an error.)


The final component is to connect to Neo4j. If you already have a local or remote database instance setup, you can change the configured URI, authorization, and database name in `koi/config.py`.

Otherwise, you can follow the instructions for your operating system here: https://neo4j.com/docs/operations-manual/current/installation/ 

If you want to use the default configuration, create a local DBMS with the default name and password set to `koi-pond`.

Everything is configured now, and the API server can be run with the following command:
```bash
python -m koi.server
```

If everything worked correctly, you should see a development server running on `http://127.0.0.1:8000`. Auto generated API documentation can be viewed at http://127.0.0.1:8000/docs.




### Note on external services
This system is configured to use the following external platforms (but they can be fairly easily swapped out): OpenAI's GPT-4o, Voyage AI's voyage-2 embedding model, and Pinecone's serverless vectorstore. As per OpenAI's [data privacy page](https://openai.com/enterprise-privacy/), business data is not used for training and the user retains ownership of both inputs and outputs. According to Pinecone's [trust and security page](https://www.pinecone.io/security/), their data privacy policies are compliant with a wide range of standards including CCPA, GDPR, HIPAA, and SOC 2. Voyage AI allows opting out of data training for future models on the [dashboard terms of service page](https://dash.voyageai.com/terms-of-service) (must be logged in to view), but by default applies the following data policy:
> You retain ownership of all data and other information you provide to Voyage AI or otherwise load into the Service (including, for clarity, data provided for ‘fine tuning’ artificial intelligence models) (“Customer Content”). Unless you ‘opt out’ as described below, you grant Voyage AI (and its successors and assigns) a worldwide, irrevocable, perpetual, royalty-free, fully paid-up, right and license to use, copy, reproduce, distribute, prepare derivative works of, display and perform the Customer Content: (i) to maintain and provide you with the Service, (ii) to exercise its rights and obligations, and otherwise enforce, this Agreement, and (iii) to train, improve, and otherwise further develop the Service (such as by training the artificial intelligence models we use). Notwithstanding the foregoing, other than to our sub-processors and subcontractor acting on our behalf, we will not disclose your Customer Content to third parties other than in an aggregate and anonymized manner that does not identify you. You may opt out of our use rights in Section 3(iii) above via the opt-out functionality on the Website. If you choose to opt out, it will apply only to Customer Content you submit after the time at which you out opt. If you opt out, your Customer Content provided after such opt out will be immediately deleted by Voyage AI after it is processed for you. For clarity, any data provided prior to your opt out may continue to be subject to Section 3(iii). If you opt out, any credits or tokens for free usage of the Service may be automatically void (as determined by Voyage AI in its sole discretion).In the event you use the Service to create any Fine-Tuned Models, Voyage AI will own such models (unless otherwise agreed to by the parties in writing), but Voyage AI will not sell or otherwise share such models with third parties (but, for clarity, may share them as appropriate for Sections 3(i) and (ii) above). “Fine-Tuned Model” means an artificial intelligence neural network model that is based on parameters that are trained using data submitted by you in order to customize the model for Customer Content.

If you are replicating this project, it is highly recommended that you opt-out before embedding any data.

## OLD (TODO: Update)

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

### TODO
#### Classes
- Base RID
    - `space/type:reference` format
    - dereference function
- Relations
    - Undirected Relation
    - Directed Relation
    - Undirected Assertion
    - Directed Assertion

#### Endpoints
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