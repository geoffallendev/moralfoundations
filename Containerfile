
FROM registry.redhat.io/rhel8/httpd-24

# Add application sources
ADD index.html /var/www/html/index.html

# The run script uses standard ways to run the application
CMD run-httpd
3.2. To use the Source-to-Image scripts and build an image using a Dockerfile, create a Dockerfile with this content:
FROM registry.redhat.io/rhel8/httpd-24

# Add application sources to a directory where the assemble script expects them
# and set permissions so that the container runs without the root access
USER 0
ADD index.html /tmp/src/index.html
RUN chown -R 1001:0 /tmp/src
USER 1001

# Let the assemble script install the dependencies
RUN /usr/libexec/s2i/assemble

# The run script uses standard ways to run the application
CMD /usr/libexec/s2i/run