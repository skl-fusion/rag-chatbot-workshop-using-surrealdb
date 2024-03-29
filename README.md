# Build a Simple RAG-Chatbot Using SurrealDB

This GitHub repository provides all the necessary code for setting up a chatbot using SurrealDB and OpenAI's API. The project demonstrates the integration of a versatile database system with artificial intelligence to manage queries and data. The project is designed a practical example for developers interested in advanced database and AI applications.

## Getting Started
To kick things off, ensure you have Docker and Docker Compose installed on your machine, as they are essential for running SurrealDB. Follow the official [Docker installation guide](https://docs.docker.com/get-docker/) and [Docker Compose installation instructions](https://docs.docker.com/compose/install/) if necessary.

Follow these steps to get the chatbot running:

### Step 1: Clone the Repository
Begin by cloning this repository to your local environment to access the project files.

```bash
git clone https://github.com/skl-fusion/rag-chatbot-workshop-using-surrealdb.git
```

### Step 2: Configure Environment Variables
Copy the `example.env` file to create a `.env` file at the root of your project. Update this file with your specific database and OpenAI API credentials.

```bash
cp example.env .env
# Edit .env with your credentials
```

### Step 3: Install Required Libraries
Install the Python dependencies specified in `requirements.txt`.

```bash
pip install -r requirements.txt
```

### Step 4: Upload Initial Data
We will use a "small dataset," such as the entire works of Shakespeare (only 5.33 MB), which can be found [here](https://raw.githubusercontent.com/borkabrak/markov/master/Complete-Works-of-William-Shakespeare.txt). There's no need to download it manually, simply execute `python upload-documents.py` to populate your SurrealDB instance with data. This script uploads the complete works of Shakespeare along with their embedding.

### Step 5: Start the Chatbot
Run `python chatbot.py` to initiate the chatbot. This script allows the chatbot to begin handling and responding to queries using the data stored in SurrealDB.

## About SurrealDB

SurrealDB was selected for this project owing to its support for multiple query languages and its capability to efficiently manage diverse data types. It offers a flexible and scalable solution for applications necessitating complex data interactions and integration with AI technologies. If you would like to learn more about SurrealDB, I encourage you to visit the [official homepage](https://surrealdb.com/).

## Conclusion

That's it, have fun! I hope you have enjoyed this tutorial!