FROM jboss/wildfly:10.0.0.Final
MAINTAINER "Ding-Yi Chen" <dchen@redhat.com>

EXPOSE 8080
# Version should be assigned in build time
# Take care editing the ZANATA_VERSION line: just version numbers,
# otherwise runapp.sh cannot parse it.
ARG ZANATA_VERSION=3.9.1

# Fedora Containers Packaging may need this
LABEL Name="zanata-server"\
    Version=$ZANATA_VERSION\
    Release="1"

USER root
RUN yum -y install mysql-connector-java wget && yum clean all

RUN ln -sf /usr/share/java/mysql-connector-java.jar /opt/jboss/wildfly/standalone/deployments/mysql-connector-java.jar

# Wildfly modules
RUN wget --no-verbose https://dl.bintray.com/sflanigan/generic/wildfly-module-hibernate-main-4.2.20.Final.zip \
    && unzip -q wildfly-module-hibernate-main-4.2.20.Final.zip -d /opt/jboss/wildfly

# Zanata war
RUN wget --no-verbose -O /opt/jboss/wildfly/standalone/deployments/zanata.war \
    https://github.com/zanata/zanata-server/releases/download/server-${ZANATA_VERSION}/zanata-war-${ZANATA_VERSION}.war \
    && chmod o+rw /opt/jboss/wildfly/standalone/deployments/zanata.war

USER jboss

ADD conf/standalone.xml /opt/jboss/wildfly/standalone/configuration/
