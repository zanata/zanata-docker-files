FROM jboss/wildfly

USER root
RUN yum -y install mysql-connector-java mysql wget

# Wildfly modules
RUN wget http://sourceforge.net/projects/zanata/files/wildfly/wildfly-8.1.0.Final-module-hibernate-main-4.2.19.Final.zip \
    && unzip wildfly-8.1.0.Final-module-hibernate-main-4.2.19.Final.zip -d /opt/jboss/wildfly
RUN wget http://sourceforge.net/projects/zanata/files/wildfly/wildfly-8.1.0.Final-module-mojarra-2.1.29-01.zip \
    && unzip wildfly-8.1.0.Final-module-mojarra-2.1.29-01.zip -d /opt/jboss/wildfly

# Zanata war
RUN wget -O /opt/jboss/wildfly/standalone/deployments/zanata.war \ 
    https://github.com/zanata/zanata-server/releases/download/server-3.7.1/zanata-war-3.7.1.war \
    && chmod o+rw /opt/jboss/wildfly/standalone/deployments/zanata.war

# standalone.xml
ADD conf/standalone.xml /opt/jboss/wildfly/standalone/configuration/
RUN ln -sf /usr/share/java/mysql-connector-java.jar /opt/jboss/wildfly/standalone/deployments/mysql-connector-java.jar

USER jboss
