FROM centos:@CENTOS_VERSION@
ARG CENTOS_VERSION=@CENTOS_VERSION@
ARG USER=builder
ARG UID=1000
ARG REPO_DIR="/repo"
ARG RPMBUILD_TOPDIR="/rpmbuild"
ARG RPMBUILD_SOURCEDIR="/rpmbuild/SOURCES"

## Override this if you want to test zanata-docker-files pull requests
ARG BRANCH=master

LABEL build="20180903" \
    description="Build EPEL RPMs and create repository for Fedora People repository"

ENV EXTRA_PACKAGES="java-1.8.0-openjdk-devel"

ENTRYPOINT ["/home/builder/build.py"]

RUN yum install -y createrepo openssh-clients openssh-server rpm-build rpmdevtools sudo rsync\
    yum-utils python-argparse $EXTRA_PACKAGES && yum clean all

# create the user and home
RUN useradd -m -G wheel -d /home/builder -u $UID $USER &&\
    mkdir -p $REPO_DIR $RPMBUILD_SOURCEDIR $RPMBUILD_TOPDIR &&\
    chown -R $USER $REPO_DIR $RPMBUILD_SOURCEDIR $RPMBUILD_TOPDIR &&\
    echo "$USER    ALL=(ALL)    NOPASSWD: /usr/bin/yum-builddep" >> /etc/sudoers.d/$USER &&\
    echo "Defaults lecture = never" >> /etc/sudoers.d/lecture

VOLUME $REPO_DIR $RPMBUILD_SOURCEDIR

WORKDIR /home/builder
ADD "https://raw.githubusercontent.com/zanata/zanata-docker-files/$BRANCH/centos-repo-builder/_rpmmacros" .rpmmacros
ADD "https://raw.githubusercontent.com/zanata/zanata-docker-files/$BRANCH/centos-repo-builder/build.py" build.py
RUN chown $USER .rpmmacros build.py && chmod 755 build.py

USER $USER

## Use @""CENTOS_VERSION@ to avoid it beening replaced by image-make
RUN for f in .rpmmacros build.py ; do\
	sed -i -e "s|@""CENTOS_VERSION@|$CENTOS_VERSION|g" $f &&\
	sed -i -e "s|@REPO_DIR@|$REPO_DIR|g" $f &&\
	sed -i -e "s|@RPMBUILD_TOPDIR@|$RPMBUILD_TOPDIR|g" $f &&\
	sed -i -e "s|@RPMBUILD_SOURCEDIR@|$RPMBUILD_SOURCEDIR|g" $f ;\
    done &&\
    mkdir -p $RPMBUILD_TOPDIR

