FROM jboss/wildfly:9.0.2.Final

USER root
RUN yum -y install mysql-connector-java wget && yum clean all

RUN ln -sf /usr/share/java/mysql-connector-java.jar /opt/jboss/wildfly/standalone/deployments/mysql-connector-java.jar

# Wildfly modules

RUN wget --no-verbose https://dl.bintray.com/sflanigan/generic/wildfly-module-hibernate-main-4.2.20.Final.zip \
    && unzip -q wildfly-module-hibernate-main-4.2.20.Final.zip -d /opt/jboss/wildfly

ENV ZANATA_VERSION 3.8.4

# Zanata war
RUN wget --no-verbose -O /opt/jboss/wildfly/standalone/deployments/zanata.war \
    https://github.com/zanata/zanata-server/releases/download/server-${ZANATA_VERSION}/zanata-war-${ZANATA_VERSION}.war \
    && chmod o+rw /opt/jboss/wildfly/standalone/deployments/zanata.war

# standalone.xml
ADD conf/standalone.xml /opt/jboss/wildfly/standalone/configuration/

USER jboss
