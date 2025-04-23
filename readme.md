# 🚀 Elasticsearch Integration with Ariadne (GraphQL Library)

This project demonstrates how to integrate [Ariadne](https://ariadnegraphql.org/) — a Python GraphQL library — with [Elasticsearch](https://www.elastic.co/).

---

## 🛠️ Prerequisites

Make sure the following tools are installed:

- Python 3.7 or above
- [Elasticsearch (local setup)](https://www.elastic.co/docs/deploy-manage/deploy/self-managed/local-development-installation-quickstart)
- Git

---

## 🔄 Getting Started

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd AriadneGraphQL-Elasticsearch-DemoApplication
```

### 2. Set Up Elasticsearch Locally

Follow the official Elasticsearch guide for local development:  
👉 [Install Elasticsearch Locally](https://www.elastic.co/docs/deploy-manage/deploy/self-managed/local-development-installation-quickstart)

Once Elasticsearch is running, you can verify it by visiting:  
[http://localhost:9200](http://localhost:9200)

---

## 🧪 Set Up Python Environment

### 3. Create a Virtual Environment

#### For Windows:

```bash
python -m venv myvenv
```

#### For macOS/Linux:

```bash
python3 -m venv myvenv
```

### 4. Activate the Virtual Environment

#### On Windows:

```bash
myvenv\Scripts\activate
```

#### On macOS/Linux:

```bash
source myvenv/bin/activate
```

---

### 5. Install Dependencies

Install all Python dependencies using:

```bash
pip install -r requirements.txt
```

---

## 🚀 Run the Application

Start the server using:

```bash
uvicorn server:app --reload
```

---

## 🔍 Access the GraphQL Playground

Once the server is running, open your browser and visit:  
[http://127.0.0.1:8000/graphql](http://127.0.0.1:8000/graphql)

This will open the GraphQL Playground where you can interact with the API.

---

## 📂 Project Structure

```bash
AriadneGraphQL-Elasticsearch-DemoApplication/
├── server.py                 # Main FastAPI app with Ariadne schema
├── schema.graphql            # GraphQL schema definition
├── resolvers.py              # Query/Mutation resolvers
├── queries.py                # Elasticsearch queries
├── requirements.txt
└── README.md
```



