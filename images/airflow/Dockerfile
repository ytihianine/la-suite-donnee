# Define ARGS (Defaults, overridden in Git CI)
ARG AIRFLOW_VERSION=3.2.2
ARG PYTHON_VERSION=3.12

# ------------------------------------------
# Install apps and packages
# ------------------------------------------
FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}

USER root
WORKDIR /app

# Add Nubonyxia cert
COPY images/customCA.crt /usr/local/share/ca-certificates/customCA.crt
RUN update-ca-certificates

# Switch back to airflow user
USER airflow

# Install packages
COPY images/airflow/requirements.txt .
RUN pip install --no-cache-dir uv
RUN uv pip install -r requirements.txt
