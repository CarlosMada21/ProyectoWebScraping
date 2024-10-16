# Usa una imagen base de Python
FROM python:3.9-slim

# Instala dependencias del sistema necesarias para Chrome, Chromedriver y otras utilidades
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libexpat1 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libdrm2 \
    libxcb1 \
    libxkbcommon0 \
    libasound2 \
    libgtk-3-0 \
    libudev1 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Descargar Chrome Headless Shell
RUN wget -O /tmp/chrome-headless-shell-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.100/linux64/chrome-headless-shell-linux64.zip && \
    unzip /tmp/chrome-headless-shell-linux64.zip -d /usr/local/bin/ && \
    rm /tmp/chrome-headless-shell-linux64.zip
# Descargar Google Chrome
RUN wget -O /tmp/chrome-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/130.0.6723.58/linux64/chrome-linux64.zip && \
    unzip /tmp/chrome-linux64.zip -d /usr/local/bin/ && \
    rm /tmp/chrome-linux64.zip
# Descargar ChromeDriver
RUN wget -O /tmp/chromedriver-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.100/linux64/chromedriver-linux64.zip && \
    unzip /tmp/chromedriver-linux64.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver-linux64.zip

# Asegura que los binarios sean ejecutables
RUN chmod +x /usr/local/bin/chrome-headless-shell-linux64/chrome-headless-shell && \
    chmod +x /usr/local/bin/chromedriver-linux64/chromedriver

# Establece el directorio de trabajo
WORKDIR /proyecto_web_scraping

# Instala las dependencias de Python
COPY requirements.txt . 
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Añade las rutas de los binarios de Chrome y Chromedriver al PATH
ENV PATH="/usr/local/bin/chromedriver-linux64:/usr/local/bin/chrome-headless-shell-linux64:$PATH"