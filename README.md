# 📌 Como rodar o projeto

## 1. Instale o Python
- Baixe e instale o Python no site oficial: [https://www.python.org/](https://www.python.org/)

---

## 2. Clone o repositório
```bash
git clone <link-do-repositorio>
cd <nome-da-pasta>
```

---

## 3. Crie um ambiente virtual
Na pasta do projeto, execute:
```bash
python -m venv venv
```

### Ative o ambiente virtual
- **Windows (PowerShell ou CMD):**
  ```bash
  venv\Scripts\activate
  ```
- **Linux / macOS:**
  ```bash
  source venv/bin/activate
  ```

---

## 4. Instale as dependências
```bash
pip install -r requirements.txt
```

---

## 5. Inicie a API
```bash
python app.py
```

A API será iniciada e estará disponível em:
```
http://localhost:5000
```
