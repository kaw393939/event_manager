# Use an official lightweight Python image.
# 3.12-slim variant is chosen for a balance between size and utility.
FROM python:3.12-slim-bullseye as base

# Set environment variables to configure Python and pip.
ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=true \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    QR_CODE_DIR=/myapp/qr_codes \
    LD_LIBRARY_PATH=/usr/local/lib

# Set the working directory inside the container
WORKDIR /myapp

# Install system dependencies including SQLite
RUN apt-get update \
    && apt-get install -y build-essential libpq-dev wget gcc make tcl \
    # Replace the existing SQLite with a newer version
    && apt-get install -y sqlite3 \
    && wget https://www.sqlite.org/2024/sqlite-autoconf-3450200.tar.gz \
    && tar xzf sqlite-autoconf-3450200.tar.gz \
    && cd sqlite-autoconf-3450200 \
    && ./configure --prefix=/usr/local \
    && make \
    && make install \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /sqlite-autoconf-3450200 /sqlite-autoconf-3450200.tar.gz

# Check SQLite version
RUN sqlite3 --version

# Upgrade pip and install Python dependencies from requirements file
COPY ./requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Add a non-root user and switch to it
RUN useradd -m myuser
USER myuser

# Copy the rest of your application's code with appropriate ownership
COPY --chown=myuser:myuser . .

# Inform Docker that the container listens on the specified port at runtime.
EXPOSE 8000

# Use ENTRYPOINT to specify the executable when the container starts.
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
