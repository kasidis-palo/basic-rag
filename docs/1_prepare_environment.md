# Preparing Your Local Environment for this session
Welcome, PyCon community! Follow these steps to set up your environment for the session.

## 1. Install Python 3.12

- [Python 3.12 Downloads](https://www.python.org/downloads/)
- **macOS:**  
    ```sh
    brew install python@3.12
    ```
- **Linux:**  
    Refer to your distribution’s instructions or use the download page above.
- **Windows:**  
    Use the download page above.

## 2. Install Podman

- [Podman Installation Guide](https://podman.io/getting-started/installation)
- **macOS:**  
    ```sh
    brew install podman
    ```
- **Linux:**  
    Follow the installation guide for your distribution.
- **Windows:**  
    See the installation guide for details.

## 3. Install Ollama

- [Ollama Installation](https://ollama.com/download)
- Download and install for your OS.

Then pull the models:

```sh
ollama pull llama3.2
ollama pull mxbai-embed-large
```

## 4. Run Qdrant with Podman

Qdrant will run as a container using Podman (platform-agnostic):

```sh
# Pull the Qdrant image
podman pull qdrant/qdrant

# Run Qdrant container
podman run -p 6333:6333 -p 6334:6334 \
    -v qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```

The Qdrant service will be available at:
- REST API: http://localhost:6333
- gRPC API: http://localhost:6334

---

**Tip:** After installation, verify each tool by running its version command in your terminal (e.g., `python --version`, `podman --version`, etc.).

## 5. Document to use
PDF File
- [On the rheology of cats](https://drgoulu.com/wp-content/uploads/2017/09/Rheology-of-cats.pdf)

You're now ready for the session!