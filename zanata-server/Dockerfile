FROM jboss/wildfly:10.1.0.Final
MAINTAINER "Ding-Yi Chen" <dchen@redhat.com>

EXPOSE 8080
# Version should be assigned in build time
# Take care editing the ZANATA_VERSION line: just version numbers,
# otherwise runapp.sh cannot parse it.
ARG ZANATA_VERSION=4.0.0

# Fedora Containers Packaging may need this
LABEL Name="zanata-platform"\
    Version=$ZANATA_VERSION\
    Release="1"

USER root

ENV ZANATA_HOME /var/lib/zanata
RUN mkdir -p $ZANATA_HOME && chown -R jboss.jboss $ZANATA_HOME
VOLUME $ZANATA_HOME

USER jboss

RUN curl -L -o /opt/jboss/wildfly/standalone/deployments/mysql-connector-java.jar https://repo1.maven.org/maven2/mysql/mysql-connector-java/5.1.25/mysql-connector-java-5.1.25.jar

# Zanata war
RUN curl -L -o /opt/jboss/wildfly/standalone/deployments/zanata.war \
    https://github.com/zanata/zanata-platform/releases/download/platform-${ZANATA_VERSION}/zanata-war-${ZANATA_VERSION}.war \
    && chmod o+rw /opt/jboss/wildfly/standalone/deployments/zanata.war

ADD conf/standalone.xml /opt/jboss/wildfly/standalone/configuration/
