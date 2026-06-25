ARG TRINO_VERSION=482

FROM trinodb/trino:${TRINO_VERSION}

USER root

COPY images/customCA.crt /tmp/customCA.crt
RUN keytool -import -alias minio -file /tmp/customCA.crt -keystore $JAVA_HOME/lib/security/cacerts -storepass changeit -noprompt && \
    keytool -list -alias minio -keystore $JAVA_HOME/lib/security/cacerts -storepass changeit && \
    rm /tmp/customCA.crt

USER trino
