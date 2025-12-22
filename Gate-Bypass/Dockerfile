FROM php:8.2-apache
# Install dependencies
RUN apt-get update && apt-get install -y \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*
RUN docker-php-ext-install pdo pdo_sqlite && \
    a2enmod rewrite
COPY config.apache /etc/apache2/sites-available/000-default.conf
COPY app/ /var/www/html/
RUN php /var/www/html/init_db.php && \
    chmod 666 /var/www/html/database.db

