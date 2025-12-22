FROM php:8.1-apache

RUN a2enmod rewrite
COPY flag.txt /var/flag.txt
RUN chmod 444 /var/flag.txt
RUN chown -R www-data:www-data /var/www/html
RUN chmod -R 755 /var/www/html
RUN echo "allow_url_fopen = On" >> /usr/local/etc/php/php.ini
RUN echo "allow_url_include = Off" >> /usr/local/etc/php/php.ini

EXPOSE 80

